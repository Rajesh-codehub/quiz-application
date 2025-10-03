# Quiz Application API

A FastAPI-based quiz application with user authentication, wallet system, and comprehensive quiz management features.

# Table of Contents

Features
Tech Stack
Prerequisites
Installation
Configuration
Database Setup
Running the Application
API Documentation
Testing
Project Structure
API Endpoints
Contributing
License

# Features

User Management

User registration with email validation
Secure password hashing
JWT-based authentication
User profile management
Soft delete functionality


Quiz System

Multiple choice questions with JSON-based options
Category-based question organization
Random question selection
Duplicate attempt prevention
Question statistics tracking (views, correct/wrong counts)


Wallet System

Reward points for correct answers
Transaction history tracking
User balance management


Analytics

User quiz statistics
Accuracy percentage calculation
Total earnings tracking

# Tech Stack

Backend Framework: Python (FastAPI)
Database: PostgreSQL
ORM: SQLAlchemy
Authentication: JWT (PyJWT)
Password Hashing: Werkzeug
Environment Management: python-dotenv
CORS: FastAPI CORS Middleware
Testing: pytest, httpx

# Prerequisites

Python 3.8+
PostgreSQL 12+
pip (Python package manager)

# Installation

1.Clone the repository

$ git clone https://github.com/yourusername/quiz-application.git
$ cd quiz-application

2.Create virtual environment

$ python -m venv venv
   
# On Windows
$ venv\Scripts\activate

# On macOS/Linux
$ source venv/bin/activate

Install dependencies

$ pip install -r requirements.txt

# Configuration

# Create .env file in the root directory:
  
>> Database Configuration

USER_NAME=your_db_username
PASSWORD=your_db_password
HOST=localhost
PORT=5432
DATABASE=quiz_app_db
   
# Security
SECRET_KEY=your_super_secret_key_here_min_32_characters

# Generate SECRET_KEY (Python):

import secrets
print(secrets.token_urlsafe(32))

# Database Setup

Create PostgreSQL database

$ CREATE DATABASE quiz_app_db;

Tables are created automatically when you run the application for the first time through SQLAlchemy's create_all() method.

# Database Schema
Users Table

- id (Primary Key)
- name
- email (Unique)
- password (Hashed)
- user_role (default: "user")
- total_amount (default: 0.00)
- status (default: "active")
- created_at
- updated_at

QuizData Table

- id (Primary Key)
- category
- question (Unique)
- options (JSON)
- answer
- views
- correct_guess_count
- wrong_guess_count
- created_at
- updated_at

UserWallet Table

- id (Primary Key)
- user_id (Foreign Key -> Users)
- amount
- timestamp

UserQuizes Table

- id (Primary Key)
- user_id (Foreign Key -> Users)
- quiz_id (Foreign Key -> QuizData)
- status (1: correct, 0: wrong)
- timestamp

Running the Application

Development mode

bash   uvicorn main:app --reload --host 0.0.0.0 --port 8000

Production mode

bash   uvicorn main:app --host 0.0.0.0 --port 8000

Access the application

API: http://localhost:8000
Interactive API docs: http://localhost:8000/docs
Alternative API docs: http://localhost:8000/redoc

