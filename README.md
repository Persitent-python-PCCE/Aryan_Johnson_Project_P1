# Online Ticket Booking System

A Flask-based Online Ticket Booking System that allows customers to browse events, view seat availability, book tickets, view booking history, and cancel bookings.

The system also provides an admin interface for managing categories, venues, events, and bookings. In addition to the web application, the project includes REST API endpoints that return JSON responses and can be tested using Postman.

The application is containerized using Docker and deployed using Kubernetes. A Jenkins CI/CD pipeline is also configured to automatically run tests, build Docker images, and push them to Docker Hub.

## Tech Stack

- Python
- Flask
- SQLAlchemy
- Flask-Migrate
- MySQL
- HTML / CSS / JavaScript
- Pytest
- Postman
- Docker
- Kubernetes
- Jenkins
- Docker Hub

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

The application is packaged as a Docker container and can be deployed using Kubernetes.

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

The health endpoint is also used by Kubernetes for application liveness and readiness checks.

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

The current CI pipeline successfully executes:

```text
51 passing tests
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

## Docker

The application is containerized using Docker.

### Build the Docker Image

From the project root:

```bash
docker build -t aryanjohnson/ticket-booking-app:latest .
```

### Run the Docker Container

```bash
docker run -p 5000:5000 aryanjohnson/ticket-booking-app:latest
```

The application can then be accessed at:

```text
http://localhost:5000
```

### Docker Image

The application image is published to Docker Hub:

```text
aryanjohnson/ticket-booking-app
```

The repository contains versioned image tags as well as the `latest` tag.

## Kubernetes Deployment

The application can be deployed using Kubernetes.

The Kubernetes configuration is available inside the `k8s/` directory.

The deployment includes:

- Flask application deployment
- MySQL deployment
- MySQL persistent volume
- MySQL service
- Flask service
- Kubernetes Secret for database configuration
- ConfigMap for application configuration

### Kubernetes Application Deployment

The Flask application runs with multiple replicas to provide basic availability and self-healing.

The deployment uses a rolling update strategy so that application updates can be performed without stopping all replicas at once.

Kubernetes also uses the application's `/health` endpoint for:

- Liveness checks
- Readiness checks

### Kubernetes Resources

```text
k8s/
├── app-config.yaml
├── flask-deployment.yaml
├── flask-service.yaml
├── mysql-deployment.yaml
├── mysql-pvc.yaml
├── mysql-secret.yaml
└── mysql-service.yaml
```

### Useful Kubernetes Commands

Check running pods:

```bash
kubectl get pods
```

Check services:

```bash
kubectl get services
```

Check deployments:

```bash
kubectl get deployments
```

Check deployment status:

```bash
kubectl rollout status deployment/flask-deployment
```

View application logs:

```bash
kubectl logs <pod-name>
```

The Flask service can be accessed through the configured Kubernetes service and port.

## Jenkins CI/CD Pipeline

The project includes a Jenkins CI/CD pipeline defined in:

```text
Jenkinsfile
```

The pipeline automatically performs the following steps:

```text
GitHub
   ↓
Checkout Source Code
   ↓
Install Python Dependencies
   ↓
Run Pytest
   ↓
Build Docker Image
   ↓
Tag Docker Image
   ↓
Login to Docker Hub
   ↓
Push Versioned Image
   ↓
Push latest Image
```

### Jenkins Pipeline Stages

The pipeline contains the following stages:

```text
1. Checkout
2. Install Dependencies
3. Test
4. Build Docker Image
5. Push to Docker Hub
```

The Docker image is tagged using the Jenkins build number.

For example:

```text
aryanjohnson/ticket-booking-app:3
```

The same image is also tagged as:

```text
aryanjohnson/ticket-booking-app:latest
```

This allows each Jenkins build to have its own versioned Docker image while maintaining a `latest` tag.

### CI/CD Result

A successful Jenkins build verifies that:

```text
Source Code
     ↓
Dependencies Installed
     ↓
Tests Passed
     ↓
Docker Image Built
     ↓
Docker Image Pushed
```

The current pipeline successfully completed with all automated tests passing and the Docker images pushed to Docker Hub.

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
├── k8s/
│   ├── app-config.yaml
│   ├── flask-deployment.yaml
│   ├── flask-service.yaml
│   ├── mysql-deployment.yaml
│   ├── mysql-pvc.yaml
│   ├── mysql-secret.yaml
│   └── mysql-service.yaml
│
├── migrations/
├── tests/
├── scripts/
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── Jenkinsfile
├── docker-compose.yml
├── README.md
├── requirements.txt
└── run.py
```

## Development and Deployment Workflow

The overall development workflow is:

```text
Developer
    ↓
Git Commit
    ↓
GitHub
    ↓
Jenkins CI/CD
    ↓
Automated Tests
    ↓
Docker Build
    ↓
Docker Hub
    ↓
Kubernetes Deployment
    ↓
Running Flask Application
```

This project demonstrates a complete application development workflow covering backend development, database integration, REST APIs, automated testing, containerization, Kubernetes deployment, and CI/CD automation.