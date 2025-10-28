
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, status, Request
import jwt
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from dotenv import load_dotenv
from typing import Callable
from functools import wraps
import logging
from sqlalchemy.sql.expression import func
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, TEXT, JSON
from sqlalchemy.sql import func
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware







# ----------------- SCHEMAS ------------------------


class UserCreate(BaseModel):
    name : str
    email : EmailStr
    password : str

class UserLogin(BaseModel):
    email: str
    password: str

class UserList(BaseModel):
    name: str
    email: str
    status: str
    total_amount: float
    created_at : datetime
    updated_at : datetime

class UpdateUser(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    total_amount: Optional[float] = None

class AddQuestion(BaseModel):
    category: str
    question: str
    options : dict
    answer : str

class DisplayQuestionInput(BaseModel):
    category: str

class DisplayAnswerInput(BaseModel):
    answer: str
    id : int






# ------------------------ MODELS --------------------------



Base = declarative_base()



class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    name = Column(String(225), nullable=False)
    email = Column(String(225), nullable=False, unique=True, index=True)
    password = Column(String(225), nullable=False)
    user_role = Column(String(100), nullable=False, default="user")
    total_amount = Column(DECIMAL(10,2), default=0.00, nullable=False)
    status = Column(String(100), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserWallet(Base):
    __tablename__ = "user_wallet"

    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(Users.id), nullable=False)
    amount = Column(DECIMAL(10, 2), default=0.00, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class QuizData(Base):
    __tablename__ = "quiz_data"

    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    category = Column(String(100), nullable=False)
    question = Column(TEXT, unique=True, nullable=False)
    options = Column(JSON, nullable=False)
    answer = Column(TEXT, nullable=False)
    views = Column(Integer, default=0, nullable=False)
    correct_guess_count = Column(Integer, default=0, nullable=False)
    wrong_guess_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserQuizes(Base):
    __tablename__ = "user_quizes"

    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(Users.id), nullable=False)
    quiz_id = Column(Integer, ForeignKey(QuizData.id), nullable=False)
    status = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())




load_dotenv()



# ---------------------- DATABASE CONNECTION ------------------------

password = os.getenv("PASSWORD", "")
user = os.getenv("USER_NAME", "")
host = os.getenv("HOST", "")
port = os.getenv("PORT", "")
database = os.getenv("DATABASE", "")
DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit = False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# ------------------- LOGS ------------------------

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)



ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY_MINUTES = 30  #min




# ------------------- UTILS -------------------------

def token_required(func: Callable):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing",
                                 headers={"WWW-Authenticate": "Bearer"},)
        
        logger.info(f"Auth Header: {auth_header}")

        token = auth_header.split(" ")[1]
        logger.info(f"Token: {token}")

        try:
            SECRET_KEY = os.getenv("SECRET_KEY")
            if not SECRET_KEY:
                raise ValueError("SECRET KEY must be set in environment variables")
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            logger.info(f"Payload: {payload}")
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail = "User id is not found in the token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        new_user_id = int(user_id)
        kwargs["current_user_id"] = new_user_id
        return await func(request, *args, **kwargs)
    return wrapper



    


def generate_password(password: str) -> str:

    return generate_password_hash(password)

def verify_password(hashed_password: str, plain_password: str) -> bool:

    return check_password_hash(hashed_password, plain_password)



def get_user_by_email(db: Session, email: str):
    """ retrive user by the email id"""
    db_user = db.query(Users).filter(Users.email == email).first()
    return db_user


def create_user_db(db: Session, user: UserCreate):
    """
    create new user with name, email, password
    """
    try:
        hashed_password = generate_password(user.password)
        db_user = Users(name = user.name, email = user.email, password = hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Transaction failed")
    
    return db_user


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ["*"]
)

# create database tables based on the models.py
Base.metadata.create_all(bind=engine)


#    ------------------------- CREATE USER ----------------------------

@app.post("/user", tags = ["Users"], status_code=status.HTTP_201_CREATED)
def create_user(user : UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail= "Email already registered")
    
    db_user = create_user_db(db = db, user = user)

    return {"status": True, "message": "User created succesfully", "id": db_user.id, "email": db_user.email}

# ----------------------- DELETE USER -------------------------------
@app.delete("/user", tags = ["Users"], status_code=status.HTTP_200_OK)
@token_required
async def delete_user(request: Request, db: Session = Depends(get_db), current_user_id : int = None):
    user = db.query(Users).filter(Users.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not available")

    try:
        user.status = "inactive"
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Transaction failed")
    return {"detail": "user deleted successfully"}


# --------------------------- USER LOGIN -------------------------------------

@app.post("/login", tags = ["Users"], status_code=status.HTTP_200_OK)
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(Users).filter(Users.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")

    if db_user.status == "inactive":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized account")
    
    
    
    
    if not verify_password(db_user.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    payload = {"sub": str(db_user.id)}

    expire = datetime.utcnow()+ timedelta(minutes=int(ACCESS_TOKEN_EXPIRY_MINUTES))
    payload.update({"exp": expire})

    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        raise ValueError("SECRET KEY must be set in environmental variables")

    token = jwt.encode(payload,SECRET_KEY, algorithm=ALGORITHM)
    
    return {"status": True, "message": "Login succesfull", "email": db_user.email, "token": token}


# ------------------------------ USERS LIST ----------------------------------

@app.get("/users", tags = ["Users"],response_model=List[UserList], status_code=status.HTTP_200_OK)
@token_required
async def user_list(request: Request, db: Session = Depends(get_db), current_user_id : int = None):
    users_data = db.query(Users).filter(Users.status == "active").all()
    return users_data



# --------------------------- USER PROFILE -------------------------------------

@app.get("/user", tags = ["Users"], status_code=status.HTTP_200_OK)
@token_required
async def get_user_by_id(request: Request, db: Session = Depends(get_db), current_user_id : int = None) :

    user_data = db.query(Users).filter(Users.id == current_user_id).first()

    return {"data": user_data}


# -------------------------- UPDATE USER ---------------------

@app.put("/user", tags = ["Users"], status_code=status.HTTP_200_OK)
@token_required
async def update_user(request: Request, userRequest: UpdateUser, db : Session = Depends(get_db), current_user_id : int = None):
    #logger.info(f"current_user_id : {current_user_id}")
    user_query = db.query(Users).filter(Users.id == current_user_id)
    user_data = user_query.first()
    #logger.info(f"user_data: {user_data}")
    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    try:
        user_query.update(userRequest.dict(), synchronize_session = False)
        logger.info("query completed")
        db.commit()
        db.refresh(user_data)
    except Exception as e:
        db.rollback()
        logger.error(f"Update failed: {e}")
        raise HTTPException(status_code=500, detail="Transaction failed")
    
    return user_data


# --------------------------- ADD QUESTION ----------------------------------------

@app.post("/add_question", tags = ["Questions"], status_code=status.HTTP_201_CREATED)
@token_required
async def add_question(request: Request, addQuestion: AddQuestion, db: Session = Depends(get_db), current_user_id: int = None):
    existing_question = db.query(QuizData).filter(QuizData.question == addQuestion.question).first()

    if existing_question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="question already existed")
    try:
        db_question = QuizData(category = addQuestion.category,
                                   question = addQuestion.question, 
                                   options = (addQuestion.options),
                                     answer = addQuestion.answer)
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Transaction failed")
    
    return {"detail": "Question added successfully", "question_id": db_question.id}

# --------------------------- CATEGORIES LIST ------------------------------

@app.get("/categories", tags = ["Questions"], status_code=status.HTTP_200_OK)
def category_list(db: Session = Depends(get_db)):
    category_query = db.query(QuizData.category).distinct().all()
    if not category_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="categories are empty")
    category_list = [category[0] for category in category_query]

    return {"categories": category_list, "category_count": len(category_list)}

# -------------------------- DISPLAY QUESTION ----------------------------


@app.get("/question",tags = ["Questions"],status_code=status.HTTP_200_OK)
def display_question(category : str, db:Session = Depends(get_db)):
    questions_list = db.query(QuizData).filter(QuizData.category == category).order_by(func.random()).first()
    if not questions_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questions not found for the selected category")
    logger.info(f"one question: {questions_list.question}, options: {questions_list.options}")
    return {"category": questions_list.category, "question": questions_list.question,
            "options": questions_list.options, "success": True, "id": questions_list.id}


# ---------------------------- Choose answer -----------------------------------
@app.post("/answer", tags = ["Questions"], status_code=status.HTTP_200_OK)
@token_required
async def validate_answer(request: Request, inputAnswer: DisplayAnswerInput,
                           db: Session = Depends(get_db),
                             current_user_id : int = None):
    
    # Get the question
    question_entry = db.query(QuizData).filter(QuizData.id == inputAnswer.id).first()
    if not question_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    
    # Check if the user already answered this question
    existing_attempt = db.query(UserQuizes).filter(
        UserQuizes.user_id == current_user_id,
        UserQuizes.quiz_id == question_entry.id).first()
    
    if existing_attempt:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = " You have already attempted this question")
    
    # Check if answer is correct
    is_correct = question_entry.answer == inputAnswer.answer

    

    if is_correct:
        try:
             # Award money for correct answer
            amount = 100

            # Add wallet entry
            user_wallet = UserWallet(user_id = current_user_id, amount = amount)
            db.add(user_wallet)

            # Update users total amount
            user_data = db.query(Users).filter(Users.id == current_user_id).first()

            if not user_data:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
            user_data.total_amount = user_data.total_amount + amount

            # Record quiz amount as correct
            user_quizes = UserQuizes(user_id = current_user_id, quiz_id = question_entry.id, status = 1)
            db.add(user_quizes)

            # Update question stats
            question_entry.correct_guess_count = question_entry.correct_guess_count + 1

            question_entry.views += 1

            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Transaction failed")

       

        return{
            "correct": True,
            "message": "Correct answer! you earned 100.",
            "amount_earned": amount,
            "total_balance": user_data.total_amount
        }
    else:
        # Record wrong answer (status = 0 for wrong)
        try:
            user_quizes = UserQuizes(user_id = current_user_id, quiz_id = question_entry.id, status = 0)
            db.add(user_quizes)

            # Update question stats
            question_entry.wrong_guess_count = question_entry.wrong_guess_count + 1

            question_entry.views += 1

            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Transaction failed")
        

        return {
            "correct": False,
            "message": "Wrong answer! Better luck next time.",
            "correct_answer": question_entry.answer
        }
    


# -------------------------- USER STATS ----------------------------------

@app.get('/user_stats',tags = ["Questions"], status_code=status.HTTP_200_OK)
@token_required
async def user_quizes(request: Request, db : Session = Depends(get_db), current_user_id : int = None):

    # Get all user's quiz attemts
    user_quizes_attempted = db.query(UserQuizes).filter(UserQuizes.user_id == current_user_id).all()

    if not user_quizes_attempted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not yet started")

    # calculate stats
    total_attempted = len(user_quizes_attempted)
    correct_count = len([q for q in user_quizes_attempted if q.status == 1])
    wrong_count = len([q for q in user_quizes_attempted if q.status == 0])

    # get user's total balance
    user_balance = db.query(Users).filter(Users.id == current_user_id).first()

    return {
        "success": True,
        "total_attempted": total_attempted,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "accuracy_percentage": round(correct_count/total_attempted *100, 2) if total_attempted > 0 else 0,
        "total_earnings": user_balance.total_amount if user_balance else 0
    }


    

    




    
    









