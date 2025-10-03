import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, get_db, app
import os
from fastapi import status
import json


# Use sqlite for database
SQL_DATABASE_URI = "sqlite:///./test.db"

engine = create_engine(SQL_DATABASE_URI, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user():
    """Sample user data for testing"""
    return {
        "name": "Rajesh",
        "email": "rajeshsammingi@gmail.com",
        "password": "Test@123"
    }

@pytest.fixture
def auth_headers(client, sample_user):
    """Create user and return authentication headers"""

    # Create user
    client.post("/user", json = sample_user)

    # Login user
    response = client.post("/login", json = {
        "email": sample_user['email'],
        "password": sample_user['password']
    })

    token = response.json()['token']

    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_question():
    """sample question data for testing"""
    return {
        "category": "SCIENCE",
        "question": "What is the capital of France?",
        "options": {
            "A": "London",
            "B": "Paris",
            "C": "Berlin",
            "D": "Madrid"
        },
        "answer": "Paris"
    }


class TestUserCreation:
    """Test user registration"""

    def test_create_user_success(self, client, sample_user):
        """Test successfull user creation"""
        response = client.post("/user", json = sample_user)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["status"]  ==  True
        assert data["message"] == "User created succesfully"
        assert data["email"]   ==  sample_user["email"]
        assert "id" in data

    def test_create_user_duplicate_email(self, client, sample_user):
        """ Test user creation with duplicate email"""

        # Create first user
        client.post("/user", json = sample_user)

        response = client.post("/user", json = sample_user)

        assert response.status_code      == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Email already registered"

    def test_create_user_invalid_email(self, client, sample_user):
        """Test user creation with invalid email"""

        sample_user["email"] = "invalid-email"

        response = client.post("/user", json = sample_user)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

class TestUserLogin:
    """Test user login functionality"""

    def test_login_success(self, client, sample_user):
        """Test succesfull login"""

        # Create user first
        client.post("/user", json = sample_user)

        response = client.post("/login", json = {
            "email": sample_user["email"],
            "password": sample_user["password"]
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status']  == True
        assert data['message'] == "Login succesfull"
        assert data['email']   == sample_user['email']
        assert "token" in data

    def test_login_invalid_email(self, client):
        "Test login with non-existing email"

        response = client.post("/login", json = {
            "email": "nonexisted@example.com",
            "password": "Test@123"
        })

        assert response.status_code      == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Invalid credentials"
    
    def test_login_wrong_password(self, client, sample_user):
        "Test login with wrong password"

        client.post("/user", json = sample_user)

        response = client.post("/login", json = {
            "email": sample_user["email"],
            "password": "wrongpassword@123"
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()['detail']

    def test_login_inactive_user(self, client, sample_user, auth_headers):
        """ Test login with inactive user"""

        # Create user
        client.post("/user", json = sample_user)

        client.delete("user", headers = auth_headers)

        response = client.post("/login", json = {
            "email": sample_user['email'],
            "password": sample_user['password']
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized account" in response.json()['detail']

class TestUserProfile:
    """Test user profile operations"""

    def test_get_user_profile(self, client, sample_user,auth_headers):
        """Test getting user profile"""
        response = client.get("/user", headers = auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["name"]         == sample_user["name"]
        assert data['email']        == sample_user["email"]

    def test_get_user_profile_without_auth(self, client):
        """Test getting profile without authentication"""

        response = client.get("/user")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_user_profile(self, client, auth_headers):
        """Test updating user profile"""
        update_data = {"name": "Updated Name", "email":"rajesammingi@gmail.com", "status": "active", "total_amount": 0.00}
        response = client.put("/user", json = update_data, headers = auth_headers)


        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Updated Name"
    def test_user_delete(self, client, auth_headers):
        """Test user deletion (soft delete)"""
        response = client.delete("/user", headers = auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["detail"] == "user deleted successfully"

class TestUserList:
    """Test user list endpoint"""
    def test_user_list(self, client, auth_headers):
        """test active user list"""
        response = client.get("/user", headers = auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), dict)
        assert len(response.json()) > 0

    def test_user_list_without_auth(self, client):
        """Test user list without authentication"""
        response = client.get("/user")

        assert response.status_code  == status.HTTP_401_UNAUTHORIZED

class TestQuestionManagement:
    """Test CRUD operations of Quetions"""

    def test_add_question_success(self, client, auth_headers, sample_question):
        """Test add creation success endpoint"""
        response = client.post("add_question", json = sample_question, headers = auth_headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['detail'] == "Question added successfully"
        assert "question_id" in data
    def test_add_question_without_auth(self, client, sample_question):
        """Test add question endpoint without authentication"""
        response = client.post("/add_question", json = sample_question)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    def test_add_question_with_duplicate(self, client, auth_headers, sample_question):
        """Test add question endpoint with duplicate input"""
        # add first time
        client.post("/add_question", json = sample_question, headers = auth_headers)

        # add same question again
        response = client.post("add_question", json = sample_question, headers = auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "question already existed"
    def test_get_categories(self, client, auth_headers, sample_question):
        """Test gettig categories endpoint"""

        client.post("/add_question", json = sample_question, headers = auth_headers)

        response = client.get("categories")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "categories" in data
        assert "category_count" in data
        assert sample_question["category"] in data['categories']

    def test_get_categories_with_empty(self, client):
        """Test get empty categories"""
        response = client.get("/categories")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data['detail']      == "categories are empty"

class TestQuestionDisplay:
    """Test get question functional flow"""
    def test_get_question_success(self, client, sample_question, auth_headers):
        """testing get random question endpoint"""

        # Add a question
        client.post("/add_question", json = sample_question, headers = auth_headers)

        # Get a question
        response = client.get(f"/question?category={sample_question["category"]}" )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "category" in data
        assert data['category'] == sample_question['category']
        assert "question" in data
        assert "options" in data
        assert data['success'] == True
        assert "id" in data
    def test_get_question_invalid_category(self, client):
        """get question with invalid category"""

        response = client.get("/question?category=nonExisted")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()['detail'] == "Questions not found for the selected category"

class TestAnswerValidation:
    """Test answer validation and scoring"""

    def test_correct_answer(self, client, sample_question, auth_headers):
        """Test submitting correct answer"""
        # Add question
        add_response = client.post("/add_question", json = sample_question, headers = auth_headers)

        # Answer the question
        response = client.post("/answer", json = {
            "id": add_response.json()["question_id"],
            "answer": sample_question['answer']
        }, headers = auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['correct'] == True
        assert "Correct answer!" in data['message']
        assert data['amount_earned'] == 100
        assert "total_balance" in data
    def test_wrong_answer(self, client, sample_question, auth_headers):
        """Test submitting wrong answer"""
        # Add question
        add_response = client.post("add_question", json= sample_question, headers = auth_headers)
        question_id = add_response.json()["question_id"]

        # answer the question
        response = client.post("/answer", json ={
            "id": question_id,
            "answer": "wrongAnswer"
        }, headers = auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["correct"] == False
        assert "correct_answer" in data
        assert data['correct_answer'] == sample_question["answer"]
    def test_duplicate_answer_attempt(self, client, sample_question, auth_headers):
        """Test attempting same question twice"""

        # Add question
        add_response = client.post("add_question", json = sample_question, headers = auth_headers)
        question_id = add_response.json()['question_id']

        # First attempt
        client.post("/answer", json = {
            "id": question_id,
            "answer": sample_question['answer']
        }, headers = auth_headers)
        
        # Second attempt
        response = client.post("/answer", json = {
            "id": question_id,
            "answer": sample_question['answer']
        }, headers = auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert  "already attempted" in response.json()['detail']
    def test_answer_without_auth(self, client):
        """Test hitting the answer api without authentication"""
        response = client.post("/answer", json = {
            "id": 1,
            "answer": "A"
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestUserStats:
    """Test user statistics endpoint"""
    def test_get_user_stats(self, client, sample_question, auth_headers):
        """Test getting user quiz stats"""

        # Add Question
        add_response = client.post("/add_question", json = sample_question, headers = auth_headers)

        question_id = add_response.json()["question_id"]

        # answer the question
        client.post("/answer", json = {
            "id": question_id,
            "answer": sample_question["answer"]
        }, headers = auth_headers)

        response = client.get("/user_stats", headers = auth_headers)
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data['success'] == True
        assert data['total_attempted'] == 1
        assert data['correct_count'] == 1
        assert "wrong_count" in data
        assert "total_earnings" and "accuracy_percentage" in data

    def test_get_user_stats_no_attempts(self, client,auth_headers):
        """Test get user stats with no answer attempts"""

        response = client.get("/user_stats", headers = auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Not yet started" in response.json()['detail']
    def test_accuracy_calculation(self, client, auth_headers):
        """Test accuracy percentage calculation"""

        # Add multiple questions
        questions = [
            {
                "category": "Science",
                "question": f"Question {i}",
                "options": {
                    "A": "1",
                    "B": "2"
                },
                "answer": "2"
            }
            for i in range(3)
        ]

        question_ids = []
        for q in questions:
            response = client.post("/add_question", json = q, headers = auth_headers)
            question_ids.append(response.json()["question_id"])
        
        # Answer 2 correct and 1 wrong
        client.post("/answer", json = {
            "id": question_ids[0],
            "answer": "2"
        }, headers = auth_headers)
        client.post("/answer", json = {
            "id": question_ids[1],
            "answer": "2"
        }, headers = auth_headers)
        client.post("/answer", json = {
            "id": question_ids[2],
            "answer": "1"
        }, headers = auth_headers)

        response = client.get("/user_stats", headers = auth_headers)
        data = response.json()

        assert data['total_attempted'] == 3
        assert data['correct_count'] == 2
        assert data['wrong_count'] == 1
        assert data['accuracy_percentage'] == 66.67

class TestTokenValidation:
    """Test jwt token validation"""
    def test_access_protected_route_with_valid_token(self, client, auth_headers):
        """Test accessing protected root with valid token"""
        response = client.get("/user", headers = auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_access_protected_route_without_token(self, client):
        """Test accessing protected route without token"""
        response = client.get("/user")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()['detail'] == "Token is missing"
    def test_access_protected_route_with_invalid_token(self, client):
        "Test accessing protected route with invalid token"
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/user", headers = headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    def test_access_protected_route_malformed_header(self, client):
        """Test accessing protedted route with malformed header"""
        header = {"Authorization": "InvalidFormat Token123"}
        response = client.get("/user", headers = header)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED





        



    












