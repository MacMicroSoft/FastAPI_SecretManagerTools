# 🔐 FastAPI Secret Manager Tools

A comprehensive, production-ready FastAPI application for secure note management with advanced authentication, authorization, and sharing capabilities. This project demonstrates modern Python web development practices with FastAPI, PostgreSQL, Redis, and Docker containerization.

## Features

### Authentication & Authorization
- **JWT-based authentication** with access tokens
- **Email verification** for user registration
- **Password reset** functionality via email
- **Role-based access control** (RBAC) system
- **Session management** with secure cookies
- **Redis integration** for caching and session storage

### Note Management
- **Create, read, update, delete** personal notes
- **Secure note sharing** between users
- **Permission-based access** control for shared notes
- **Note ownership** validation
- **Real-time note updates**

### Security Features
- **Password hashing** with bcrypt
- **SQL injection protection** with SQLAlchemy ORM
- **CORS protection** and secure headers
- **Input validation** with Pydantic models
- **Environment-based configuration**

### Admin Panel
- **Starlette Admin** integration
- **Database management** interface
- **User role management**
- **Permission configuration**
- **Real-time data monitoring**

## Architecture

```
FastAPI Secret Manager Tools/
├── app/
│   ├── models/          
│   ├── routes/          
│   ├── crud/           
│   ├── schemas/        
│   ├── config.py      
│   └── main.py         
├── migrations/        
├── tests/             
├── docker-compose.yml
├── Dockerfile        
└── poetry            
```

## Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- PostgreSQL 12+
- Redis 6.2+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/FastAPI_SecretManagerTools.git
   cd FastAPI_SecretManagerTools
   ```

2. **Environment Configuration**
   Create a `.env` file in the `app/` directory:
   ```env
   POSTGRESQL_HOST=localhost
   POSTGRESQL_PORT=5432
   POSTGRESQL_NAME=postgres
   POSTGRESQL_PASSWORD=postgres
   POSTGRESQL_USER=postgres
   
   SECRET_KEY=your-secret-key-here
   JWT_REFRESH_SECRET_KEY=your-refresh-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_MINUTES=60
   
   adminapikey=your-admin-api-key
   SERVER=localhost
   ```

3. **Docker Deployment**
   ```bash
   docker-compose up --build
   ```

4. **Database Migration**
   ```bash
   docker-compose exec alembic alembic upgrade head
   ```

5. **Access the Application**
   - **API Documentation**: http://localhost:8000/docs
   - **Admin Panel**: http://localhost:8000/admin
   - **API Base URL**: http://localhost:8000

## API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | User login |
| GET | `/auth/logout` | User logout |
| GET | `/auth/confirm-email` | Email verification |
| POST | `/auth/forgot-password` | Request password reset |
| POST | `/auth/reset-password` | Reset password |
| GET | `/auth/users/me/` | Get current user info |

### Note Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/note/create/` | Create new note |
| GET | `/note/list/me/` | List user's notes |
| PUT | `/note/{note_id}` | Update note |
| DELETE | `/note/{note_id}` | Delete note |
| POST | `/note/share/` | Share note with user |
| GET | `/note/shared/to/others/` | List shared notes (sent) |
| GET | `/note/shared/from/others/` | List shared notes (received) |

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Alembic** - Database migration tool
- **Pydantic** - Data validation and settings management
- **JWT** - JSON Web Token authentication
- **Passlib** - Password hashing utilities

### Database & Caching
- **PostgreSQL** - Primary database
- **Redis** - Caching and session storage
- **AsyncPG** - Asynchronous PostgreSQL driver

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Uvicorn** - ASGI server

### Development Tools
- **Pytest** - Testing framework
- **Poetry** - Dependency management
- **Starlette Admin** - Admin interface

## Development

### Local Development Setup

1. **Install Poetry**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install Dependencies**
   ```bash
   poetry install
   ```

3. **Run Database Migrations**
   ```bash
   alembic upgrade head
   ```

4. **Start Development Server**
   ```bash
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_notes/test_routes/test_routers_notes.py
```

## 📊 Database Schema

### Core Tables
- **users** - User accounts and authentication
- **notes** - Personal notes and content
- **roles** - User roles and permissions
- **permissions** - Granular access controls
- **shared_notes** - Note sharing relationships
- **user_roles** - Many-to-many user-role mapping
- **role_permissions** - Many-to-many role-permission mapping

## Security Considerations

- **Password Security**: Bcrypt hashing with salt
- **Token Security**: JWT with configurable expiration
- **SQL Injection**: Protected by SQLAlchemy ORM
- **CORS**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic model validation
- **Environment Variables**: Sensitive data in environment

## Deployment

### Production Deployment

1. **Environment Variables**
   - Set production database credentials
   - Configure secure JWT secrets
   - Set up email service credentials

2. **Database Setup**
   - Create production PostgreSQL database
   - Run migrations: `alembic upgrade head`
   - Configure Redis for caching

3. **Docker Production**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Performance Features

- **Async/Await**: Non-blocking I/O operations
- **Connection Pooling**: Efficient database connections
- **Redis Caching**: Fast data retrieval
- **Database Indexing**: Optimized query performance
- **Lazy Loading**: Efficient relationship loading

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Star this repository if you found it helpful!**

**Connect with me on LinkedIn for professional opportunities**
