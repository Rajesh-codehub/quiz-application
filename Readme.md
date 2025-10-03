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
- ✅ Real-time statistics tracking

### 💰 Wallet & Rewards
- ✅ Earn 100 points per correct answer
- ✅ Transaction history
- ✅ Balance tracking

### 📊 Analytics
- ✅ Personal quiz statistics
- ✅ Accuracy percentage
- ✅ Total earnings dashboard

---

## 🛠 Tech Stack

| Category | Technology |
|----------|-----------|
| **Framework** | FastAPI |
| **Language** | Python 3.8+ |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy |
| **Auth** | JWT (PyJWT) |
| **Testing** | pytest, httpx |

---

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have:
- ✅ Python 3.8 or higher
- ✅ PostgreSQL 12 or higher
- ✅ pip package manager

### 1️⃣ Clone & Setup
```bash