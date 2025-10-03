# Database schema

User(id,Name,mail,password,user_role,total_amount, status, created_at,updated_at)
user_wallet(id, user_id, amount,timestamp)
quiz_data(id,category,question,options,answer,views,correct_guess_count,wrong_guess_count,created_at,updated_at)
user_quizes(id,user_id,quiz_id,timestamp)

# API Docs:

>> api/user POST:
create user with name, mail, password, data will be stored in users table

>> api/user GET:
get all users list from users table and if he mentioned id then display particular user data only

>> api/user PUT:
update user details from users table

>> api/user DELETE:
delete user from the database, change the status column is inactive(soft delete)

>> api/add_question:
add new question from admin with all the details

>> api/categories GET:
display all the categories from quiz_date table

>> api/question GET:
display a question and options from the quiz_data table

>> api/choose POST:
choose one option then validate the answer and get the message from quiz_data table
if the question right add the amount to the user_wallet with id, amount and also update total amount in users table
and also update views, correct_count, wrong_count and also update user_quizes table with ids and status(0,1)

>> api/user_quizes/id
display all the quizes he attempted like count and correct count and wrong count with status column if status is 0 they are correct and if status is 1 they are wrong


# Running tests

>> Run all tests
$ pytest

>> Run with coverage
$ pytest --cov=main --cov-report=html

>> Run specific test file
$ pytest tests/test_users.py

>> Run specific test class
$ pytest tests/test_users.py::TestUserCreation

>> Run specifc test
$ pytest tests/test_users.py::TestUserCreation::test_create_user_success

>> Run with verbose output
$ pytest -v

>> Run and stop at first failure
$ pytest -x

>> Run tests in parallel (install pytest-xdist)
$ pytest -n auto

# Best Practices for Your Tests

Use fixtures for common setup (users, auth tokens, sample data)
Test both success and failure cases
Test edge cases (empty data, invalid data, duplicates)
Test authentication on protected endpoints
Use descriptive test names that explain what's being tested
Organize tests into logical classes
Keep tests independent - each test should set up and tear down its own data
Test database transactions - ensure rollbacks work properly



