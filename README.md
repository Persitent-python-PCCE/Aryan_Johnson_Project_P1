# Online Ticket Booking System

A Flask-based Online Ticket Booking System that allows customers to browse events, view seat availability, book tickets, view booking history, and cancel bookings.

The system also provides an admin interface for managing categories, venues, events, and bookings. In addition to the web application, the project includes REST API endpoints that return JSON responses and can be tested using Postman.

## Tech Stack

- Python
- Flask
- SQLAlchemy
- Flask-Migrate
- MySQL
- HTML / CSS / JavaScript
- Pytest
- Postman

## Project Architecture

The application follows a layered architecture:

```text
Controller / API
       ↓
Service Layer
       ↓
Repository Layer
       ↓
SQLAlchemy Models
       ↓
MySQL Database
```

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Persitent-python-PCCE/Aryan_Johnson_Project_P1.git
cd Aryan_Johnson_Project_P1
```

### 2. Create a Virtual Environment

Create a Python virtual environment:

```bash
python -m venv venv
```

#### Windows

Activate the virtual environment:

```bash
venv\Scripts\activate
```

#### macOS / Linux

```bash
source venv/bin/activate
```

After activation, your terminal should show something similar to:

```text
(venv)
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Configure MySQL

Make sure MySQL Server is installed and running.

Create a database for the application:

```sql
CREATE DATABASE ticket_booking;
```

You can use any database name you prefer.

### 5. Configure Environment Variables

Create a file named `.env` in the root directory of the project.

Add:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://USERNAME:PASSWORD@localhost:3306/ticket_booking
```

Replace:

- `USERNAME` with your MySQL username
- `PASSWORD` with your MySQL password
- `ticket_booking` with your database name if you used a different name

Example:

```env
SECRET_KEY=my-development-secret
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/ticket_booking
```

**Do not commit the `.env` file to Git.**

### 6. Initialize the Database

The project uses Flask-Migrate for database migrations.

Run:

```bash
flask db upgrade
```

This creates and updates the required database tables using the existing migration files.

If Flask cannot locate the application automatically, use:

```bash
flask --app run.py db upgrade
```

### 7. Run the Application

Start the Flask application:

```bash
python run.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```

Open the address in your browser.

## Testing the Application

### Main Application

Open:

```text
http://127.0.0.1:5000
```

### Health Check

Open:

```text
http://127.0.0.1:5000/health
```

The application should return a successful health-check response.

## REST API

The REST API uses the following base URL:

```text
http://127.0.0.1:5000/api/v1
```

### Customer APIs

```text
GET  /api/v1/health

POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout

GET  /api/v1/events
GET  /api/v1/events/<event_id>
GET  /api/v1/events/<event_id>/seats

POST /api/v1/bookings
GET  /api/v1/bookings
GET  /api/v1/bookings/<booking_id>
POST /api/v1/bookings/<booking_id>/cancel
```

### Admin APIs

Admin APIs are available under:

```text
/api/v1/admin/
```

Examples:

```text
GET    /api/v1/admin/categories
POST   /api/v1/admin/categories
GET    /api/v1/admin/categories/<category_id>
PUT    /api/v1/admin/categories/<category_id>
DELETE /api/v1/admin/categories/<category_id>

GET    /api/v1/admin/venues
POST   /api/v1/admin/venues
GET    /api/v1/admin/venues/<venue_id>
PUT    /api/v1/admin/venues/<venue_id>
DELETE /api/v1/admin/venues/<venue_id>

GET    /api/v1/admin/events
POST   /api/v1/admin/events
GET    /api/v1/admin/events/<event_id>
PUT    /api/v1/admin/events/<event_id>
DELETE /api/v1/admin/events/<event_id>
```

The APIs return JSON responses and can be tested using Postman.

## Automated Testing

The project includes automated tests using Pytest.

Make sure the virtual environment is activated, then run:

```bash
python -m pytest -q
```

The current test suite contains:

```text
158 passing tests
```

The tests cover:

- Authentication
- Controllers
- Services
- Repositories
- REST APIs
- Admin APIs
- Booking operations
- Seat availability
- Authorization
- Input validation
- Error handling

## Recommended Booking API Workflow

The complete customer booking workflow can be tested in the following order:

```text
Register Customer
       ↓
Login
       ↓
Browse Published Events
       ↓
View Event Details
       ↓
View Available Seats
       ↓
Create Booking
       ↓
View Booking
       ↓
Cancel Booking
```

## Recommended Admin API Workflow

```text
Login as Admin
       ↓
Manage Categories
       ↓
Manage Venues
       ↓
Create / Manage Events
       ↓
View Events
       ↓
Manage Bookings
```

## Project Structure

```text
Aryan_Johnson_Project_P1/
│
├── app/
│   ├── controllers/
│   │   ├── api/
│   │   │   ├── admin_api.py
│   │   │   ├── auth_api.py
│   │   │   ├── booking_api.py
│   │   │   ├── event_api.py
│   │   │   ├── health_api.py
│   │   │   └── seat_api.py
│   │   │
│   │   ├── admin_controller.py
│   │   ├── auth_controller.py
│   │   ├── customer_controller.py
│   │   └── main_controller.py
│   │
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── config.py
│   ├── extensions.py
│   └── __init__.py
│
├── migrations/
├── tests/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── run.py
```

## Troubleshooting

### MySQL Connection Error

Make sure:

1. MySQL Server is running.
2. The database exists.
3. The username and password in `.env` are correct.
4. `DATABASE_URL` contains the correct database name.

Example:

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/ticket_booking
```

### `ModuleNotFoundError`

Make sure the virtual environment is activated:

```bash
venv\Scripts\activate
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

### Database Tables Are Missing

Run:

```bash
flask db upgrade
```

### Port Already in Use

Stop the existing Flask process or run the application on another available port.

## Project Status

The application currently includes:

- Flask web application
- Layered architecture
- MySQL database integration
- Authentication and session management
- Role-based authorization
- Customer booking workflow
- Admin management functionality
- REST API endpoints
- JSON responses
- Postman API testing
- Automated Pytest test suite
- Database migrations
- Input validation
- Seat availability protection
- Booking cancellation
- Booking ownership validation

**Current automated test status: 158 tests passing.**