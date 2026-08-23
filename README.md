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

## 1. Clone the Repository
```bash
git clone https://github.com/Persitent-python-PCCE/Aryan_Johnson_Project_P1.git

Move into the project directory:
```bash
cd Aryan_Johnson_Project_P1

## 2. Create a Virtual Environment

Create a Python virtual environment:

```bash
python -m venv venv
Windows

Activate it using:
```bash
venv\Scripts\activate
macOS / Linux
source venv/bin/activate

After activation, your terminal should show something similar to:

(venv)
3. Install Dependencies

Install the required Python packages:
```bash
pip install -r requirements.txt
4. Configure MySQL

Make sure MySQL Server is installed and running.

Create a database for the application.

For example:
```bash
CREATE DATABASE ticket_booking;

You can use any database name you prefer.

5. Configure Environment Variables

Create a file named:

.env

in the root directory of the project.

Add:
```bash
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://USERNAME:PASSWORD@localhost:3306/ticket_booking

Replace:

USERNAME with your MySQL username
PASSWORD with your MySQL password
ticket_booking with your database name if you used a different name

Example:

SECRET_KEY=my-development-secret
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/ticket_booking

Do not commit the .env file to Git.

6. Initialize the Database

The project uses Flask-Migrate for database migrations.

Run:
```bash
flask db upgrade

This creates/updates the required database tables using the existing migration files.

If Flask cannot locate the application automatically, use:
```bash
flask --app run.py db upgrade
7. Run the Application

Start the Flask application:
```bash
python run.py

The application should start at:
```bash
http://127.0.0.1:5000

Open the address in your browser.

8. Test the Application
Main Application

Open:
```bash
http://127.0.0.1:5000
Health Check

Open:
```bash
http://127.0.0.1:5000/health

The application should return a successful health-check response.

9. Testing the REST API

The REST API uses the following base URL:
```bash
http://127.0.0.1:5000/api/v1

Examples:

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

Admin APIs are available under:

/api/v1/admin/

For example:

GET    /api/v1/admin/categories
POST   /api/v1/admin/categories

GET    /api/v1/admin/venues
POST   /api/v1/admin/venues

GET    /api/v1/admin/events
POST   /api/v1/admin/events

The APIs return JSON responses and can be tested using Postman.

10. Running Automated Tests

The project includes automated tests using Pytest.

Make sure the virtual environment is activated, then run:
```bash
python -m pytest -q

The project currently contains:

158 passing tests

The tests cover areas including:

Authentication
Controllers
Services
Repositories
REST APIs
Admin APIs
Booking operations
Seat availability
Authorization
Validation
Error handling