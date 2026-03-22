# Employee & Company Core API

Welcome to the **Employee Data Project**. This system is a robust FastAPI-based backend designed to manage the core relationships between employees and their respective companies.

## 🚀 What is this System?

This is a **Core API System** built specifically to handle CRUD (Create, Read, Update, Delete) operations for employees and companies. It features:
- **FastAPI Framework**: High-performance, modern web framework for building APIs.
- **Relational Database Management**: Uses SQLAlchemy to manage complex relationships between companies and their employees.
- **Automated Audit Logging**: Integrated middleware that captures every API request and logs it to MongoDB for security and monitoring.
- **Dynamic Dashboard**: A Jinja2-templated HTML dashboard that provides real-time insights into company performance and employee metrics.
- **Database Migrations**: Powered by Alembic to ensure smooth schema evolution.

## 💡 Why was this Built?

The primary purpose of this project is **Learning and Experimentation**. It serves as a practical playground for:
1. **Understanding AI in Development**: Exploring how AI-driven coding assistants (like Antigravity) can accelerate the building of complex systems.
2. **Backend Architecture**: Mastering the "Separated CRUD with Connected Keys" pattern.
3. **Advanced Integrations**: Learning how to bridge SQL (SQLAlchemy) and NoSQL (MongoDB) databases within a single application.
4. **Middleware Logic**: Implementing custom audit trails to track system usage.

## 🛠️ What to do? (Getting Started)

To get the system up and running on your local machine, follow these steps:

### 1. Prerequisites
Ensure you have Python 3.9+ and MongoDB installed.

### 2. Setup Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configuration
Create a `.env` file in the root directory (refer to `.env.example` if available) with your database credentials and MongoDB URI.

### 5. Run Migrations
```powershell
alembic upgrade head
```

### 6. Start the Server
```powershell
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`. You can access the interactive docs at `/docs` and the visual dashboard at `/dashboard`.

