# Deck of Cards Backend

A robust, production-ready FastAPI backend service for card game management and user authentication. Built with Python, SQLAlchemy ORM, and PostgreSQL, this API provides comprehensive user management, game orchestration, and secure authentication.

## Overview

The Deck of Cards Backend is a RESTful API that powers the Deck of Cards application ecosystem. It manages user accounts with soft-delete functionality, handles game sessions, tracks player statistics (chip counts), and provides role-based access control for administrative operations. The system is designed for scalability, security, and reliability.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Architecture](#architecture)
- [Development](#development)
- [Deployment](#deployment)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Features

- **User Management**: Complete CRUD operations with soft-delete functionality
- **Secure Authentication**: JWT-based token authentication with bcrypt password hashing
- **Role-Based Access Control**: User and admin roles with protected endpoints
- **Soft Delete System**: Preserve data integrity with timestamp-based soft deletes and username mutation
- **Game Session Management**: Create, manage, and query game sessions
- **Chip Tracking**: Real-time user chip balance management and statistics
- **Audit Trail**: Track user creation dates and soft delete timestamps
- **Database Migrations**: Automatic schema management on startup
- **Error Handling**: Comprehensive error responses with appropriate HTTP status codes
- **CORS Support**: Cross-origin request handling for frontend integration

## Technology Stack

| Category | Technology |
|----------|-----------|
| **Framework** | FastAPI 0.104+ |
| **Language** | Python 3.9+ |
| **ORM** | SQLAlchemy 2.0+ |
| **Database** | PostgreSQL 14+ |
| **Authentication** | JWT (PyJWT), bcrypt |
| **Server** | Uvicorn ASGI |
| **Validation** | Pydantic |
| **API Docs** | Swagger UI, ReDoc |
| **Package Manager** | pip, Poetry, or pipenv |

## Project Structure

```
DeckOfCardsBE/
├── src/
│   └── app/
│       ├── main.py              # FastAPI application entry point
│       ├── core/
│       │   └── database.py      # Database connection and session management
│       ├── models/              # SQLAlchemy ORM models
│       │   ├── chips.py         # User chip balances model
│       │   └── user.py          # User account model with timestamps
│       └── routers/             # API endpoint handlers
│           ├── chips.py         # Chip management endpoints
│           ├── games.py         # Game session endpoints
│           ├── items.py         # Generic items endpoints
│           ├── models.py        # System models endpoints
│           └── users.py         # User management & authentication
├── pyproject.toml              # Project metadata and dependencies
├── requirements.txt            # Python package dependencies
└── README.md                   # This file
```

## Getting Started

### Prerequisites

- **Python** 3.9 or higher
- **PostgreSQL** 14 or higher
- **pip** or **Poetry** for dependency management
- Git for version control

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/DeckOfCardsBE.git
   cd DeckOfCardsBE
   ```

2. **Create a Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment configuration**
   Create a `.env` file in the project root:
   ```env
   # Database Configuration
   DATABASE_URL=postgresql://username:password@localhost:5432/deckofcards_db
   
   # JWT Configuration
   SECRET_KEY=your_secret_key_here_change_in_production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Server Configuration
   DEBUG=True
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

5. **Initialize the database**
   ```bash
   python -c "from src.app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

6. **Start the server**
   ```bash
   uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT signing secret key | Required |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 |
| `DEBUG` | Debug mode enabled | False |
| `API_HOST` | API server host | 0.0.0.0 |
| `API_PORT` | API server port | 8000 |
| `CORS_ORIGINS` | Allowed CORS origins | http://localhost:5173 |

### Database Configuration

The system uses PostgreSQL with the following connection requirements:

```python
DATABASE_URL=postgresql://username:password@hostname:port/database_name
```

**Ensure the database exists before starting the application.**

## API Documentation

### Interactive API Docs

Once the server is running, access interactive documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Authentication

All protected endpoints require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <your_jwt_token>
```

### Core Endpoints

#### Authentication

- `POST /users/register` — Register new user account
- `POST /users/login` — Authenticate and receive JWT token

#### User Management

- `GET /users/` — List all active users (admin)
- `GET /users/{user_id}` — Get specific user
- `GET /users/chip-counts` — Get all users with chip counts and roles
- `POST /users/` — Create new user
- `PUT /users/{user_id}` — Update user profile
- `DELETE /users/{user_id}` — Soft delete user account
- `PUT /users/{user_id}/update-password` — Change user password

#### Admin Operations

- `POST /users/{user_id}/make-admin` — Promote user to admin role

#### Chip Management

- `GET /chips/` — List chip records
- `GET /chips/{user_id}` — Get user chip balance
- `POST /chips/` — Create chip record
- `PUT /chips/{chip_id}` — Update chip balance

#### Games

- `GET /games/` — List active game sessions
- `POST /games/` — Create new game
- `GET /games/{game_id}` — Get game details
- `PUT /games/{game_id}` — Update game status

### Request/Response Examples

#### Register User

```http
POST /users/register HTTP/1.1
Content-Type: application/json

{
  "username": "player1",
  "password": "securepassword123"
}
```

**Response (201)**:
```json
{
  "user_id": 1,
  "username": "player1",
  "role": "user",
  "created_at": "2026-06-25T10:30:00+00:00",
  "deleted_at": null
}
```

#### Login

```http
POST /users/login HTTP/1.1
Content-Type: application/json

{
  "username": "player1",
  "password": "securepassword123"
}
```

**Response (200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "username": "player1",
    "role": "user"
  }
}
```

#### Get Users with Chip Counts

```http
GET /users/chip-counts HTTP/1.1
Authorization: Bearer <token>
```

**Response (200)**:
```json
[
  {
    "user_id": 1,
    "username": "player1",
    "role": "user",
    "created_at": "2026-06-25T10:30:00+00:00",
    "chip_count": 1000.00
  },
  {
    "user_id": 2,
    "username": "admin_user",
    "role": "admin",
    "created_at": "2026-06-20T15:00:00+00:00",
    "chip_count": 5000.00
  }
]
```

## Database Schema

### Users Table

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| `id` | Integer | PK | User unique identifier |
| `username` | String(255) | UNIQUE, NOT NULL | Account username |
| `hashed_password` | String(255) | NOT NULL | Bcrypt hashed password |
| `role` | String(50) | NOT NULL, Default: "user" | User role (user/admin) |
| `created_at` | Timestamp | NOT NULL, Server Default: NOW | Account creation timestamp |
| `deleted_at` | Timestamp | Nullable | Soft delete timestamp |

### Soft Delete Behavior

When a user is deleted:

1. `deleted_at` timestamp is set to current time
2. Username is mutated to `{original_username}_deleted_{ddmmyy}` 
3. Numeric suffix added if collision detected: `{original_username}_deleted_{ddmmyy}_{counter}`
4. User is excluded from all lookups (queries filter `deleted_at IS NULL`)
5. Account data preserved for audit trail

### Chips Table

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| `id` | Integer | PK | Chip record ID |
| `user_id` | Integer | FK(users.id) | Associated user |
| `balance` | Decimal | NOT NULL | Current chip balance |
| `updated_at` | Timestamp | Server Default: NOW | Last update timestamp |

### Games Table

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| `id` | Integer | PK | Game session ID |
| `name` | String(255) | NOT NULL | Game name/type |
| `status` | String(50) | Default: "active" | Game status |
| `created_at` | Timestamp | Server Default: NOW | Creation timestamp |
| `ended_at` | Timestamp | Nullable | Game end timestamp |

## Architecture

### Request Flow

```
Client Request
    ↓
FastAPI Route Handler
    ↓
Request Validation (Pydantic)
    ↓
Authentication Check (JWT)
    ↓
Authorization Check (Role)
    ↓
Business Logic / Database Query
    ↓
Response Serialization
    ↓
HTTP Response
```

### Key Design Patterns

1. **Router-Based Organization**: Each resource type has dedicated router module
2. **Dependency Injection**: FastAPI's `Depends()` for database session management
3. **Model Validation**: Pydantic models for request/response validation
4. **Soft Delete Pattern**: Logical deletion preserving historical data
5. **Username Mutation**: Enables account reuse without hard delete constraints

### Security Implementation

- **Password Hashing**: bcrypt with automatic salt generation
- **JWT Tokens**: Signed tokens with expiration validation
- **SQL Injection Protection**: SQLAlchemy parameterized queries
- **CORS Management**: Configurable cross-origin policies

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Run linting
flake8 src/

# Format code
black src/

# Type checking
mypy src/
```

### Hot Reload Development

```bash
uvicorn src.app.main:app --reload
```

## Deployment

### Production Deployment

1. **Set secure environment variables**
   ```bash
   export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
   export DEBUG=False
   export CORS_ORIGINS=https://yourdomain.com
   ```

2. **Run database migrations**
   ```bash
   python -c "from src.app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

3. **Start with Gunicorn (recommended for production)**
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.app.main:app --bind 0.0.0.0:8000
   ```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t deckofcards-api .
docker run -p 8000:8000 --env-file .env deckofcards-api
```

### Platform Options

- **Heroku**: Push with Procfile
- **AWS**: EC2 or Elastic Beanstalk
- **Google Cloud**: Cloud Run or App Engine
- **DigitalOcean**: Droplets or App Platform
- **Self-Hosted**: VPS with Docker/systemd

## Testing

### Unit Tests

```bash
pytest tests/test_users.py
pytest tests/test_auth.py
pytest tests/test_chips.py
```

### Integration Tests

```bash
pytest tests/integration/
```

### Test Coverage

```bash
pytest --cov=src tests/
```

## Contributing

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/description`
3. Follow code style with `black` and `flake8`
4. Add tests for new functionality
5. Ensure all tests pass: `pytest`
6. Commit with descriptive message: `git commit -m 'Add feature: description'`
7. Push to branch: `git push origin feature/description`
8. Submit Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and returns
- Document complex business logic with docstrings
- Keep functions focused and testable

## License

This project is provided for educational and demonstration purposes.