# 🎯 Quiz Application API

> A modern FastAPI-based quiz application with user authentication, wallet rewards system, and comprehensive quiz management.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### 👤 User Management
- ✅ User registration with email validation
- ✅ Secure password hashing (Werkzeug)
- ✅ JWT-based authentication (30-min expiry)
- ✅ Profile management & soft delete

### 📝 Quiz System
- ✅ Multiple choice questions (JSON-based options)
- ✅ Category organization
- ✅ Random question selection
- ✅ Duplicate attempt prevention
- ✅ Real-time statistics tracking (views, correct/wrong counts)

### 💰 Wallet & Rewards
- ✅ Earn 100 points per correct answer
- ✅ Transaction history logging
- ✅ Wallet balance tracking

### 📊 Analytics
- ✅ Personal quiz statistics
- ✅ Accuracy percentage calculation
- ✅ Total earnings dashboard

---

## 🛠 Tech Stack

| Category       | Technology       |
|----------------|------------------|
| **Framework**  | FastAPI          |
| **Language**   | Python 3.8+      |
| **Database**   | PostgreSQL       |
| **ORM**        | SQLAlchemy       |
| **Auth**       | JWT (PyJWT)      |
| **Password**   | Werkzeug         |
| **Testing**    | pytest, httpx    |

---

## 🚀 Quick Start

### Prerequisites

Make sure you have the following installed:

- ✅ Python 3.8 or higher  
- ✅ PostgreSQL 12 or higher  
- ✅ pip (Python package manager)  

### 1️⃣ Clone & Setup

Clone the repository
git clone https://github.com/yourusername/quiz-application.git
cd quiz-application

Create a virtual environment
python -m venv venv

Activate the virtual environment
Windows
venv\Scripts\activate

macOS/Linux
source venv/bin/activate

Install dependencies
pip install -r requirements.txt

text

### 2️⃣ Configuration

Create a `.env` file in the root directory with the following:

Database settings
USER_NAME=your_db_username
PASSWORD=your_db_password
HOST=localhost
PORT=5432
DATABASE=quiz_app_db

Security
SECRET_KEY=your_super_secret_key_here_min_32_characters

text

Generate a secret key (run in Python shell):

import secrets
print(secrets.token_urlsafe(32))

text

### 3️⃣ Database Setup

Create the PostgreSQL database:

CREATE DATABASE quiz_app_db;

text

Tables are created automatically on app startup.

### 4️⃣ Run the Application

For development (with auto reload):

uvicorn main:app --reload --host 0.0.0.0 --port 8000

text

For production:

uvicorn main:app --host 0.0.0.0 --port 8000

text

---

## 📚 API Documentation

Visit the auto-generated API docs:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔑 API Endpoints

### Authentication
| Endpoint           | Method | Description               |
|--------------------|--------|---------------------------|
| `/auth/register`   | POST   | Register a new user        |
| `/auth/login`      | POST   | User login                 |

### User Profile
| Endpoint           | Method | Description               |
|--------------------|--------|--------------------------|
| `/users/me`        | GET    | Get current user profile  |
| `/users/me`        | PUT    | Update user profile       |
| `/users/me`        | DELETE | Soft delete user account  |

### Quiz Operations
| Endpoint            | Method | Description              |
|---------------------|--------|--------------------------|
| `/quizzes`          | GET    | Fetch quizzes (filtered/random) |
| `/quizzes/attempt`  | POST   | Submit quiz answers       |

### Wallet
| Endpoint               | Method | Description              |
|------------------------|--------|--------------------------|
| `/wallet/balance`      | GET    | Get wallet balance        |
| `/wallet/transactions` | GET    | List transaction history  |

### Analytics
| Endpoint            | Method | Description              |
|---------------------|--------|--------------------------|
| `/analytics/stats`  | GET    | User quiz performance     |

---

## 🧪 Testing

Run the test suite:

pytest

text

---

## ⚠️ Troubleshooting

- Ensure PostgreSQL service is running  
- Confirm `.env` variables are correctly set  
- Check Python version is 3.8+ (`python --version`)  
- Use virtual environment to avoid package conflicts  

---

## 🤝 Contributing

Contributions are welcome! Please feel free to fork the repository and submit pull requests.


---

⭐️ If this project helped, please give it a star!
