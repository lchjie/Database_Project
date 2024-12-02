# School Cafeteria Database Management System

## Project Overview
A comprehensive database management system designed for Newcomb Hall's school cafeteria, built with Django. This system efficiently manages restaurant data, student orders, and financial transactions to streamline cafeteria operations.

## Demo Video
https://www.youtube.com/watch?v=NgTMrLiHwJI

## Features

### 1. Order Management
- Create, edit, and delete student food orders
- Real-time balance checking and validation
- Order history tracking
- Multiple item selection with quantity management

### 2. Student Management
- Complete student profile management
- Computing ID integration with UVA email system
- Account balance tracking
- Order history viewing
- Search functionality by Computing ID or name

### 3. Restaurant Management
- Restaurant profile creation and management
- Menu and pricing management
- Operating hours tracking
- Restaurant search functionality

### 4. Financial Overview
- Total revenue tracking
- Restaurant-wise revenue breakdown
- Popular items analysis
- Student ordering statistics
- Average order value calculations

## Technical Stack
- Backend: Django
- Frontend: Bootstrap 5
- Database: SQLite (development) / PostgreSQL (production)
- JavaScript for dynamic interactions

## Installation

1. Clone the repository

2. Create and activate a virtual environment:
bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

3. Install dependencies:
bash
pip install -r requirements.txt

4. Apply migrations:
bash
python manage.py migrate

5. Load initial data:
bash
python manage.py loaddata initial_data.json

6. Run the server:
bash
python manage.py runserver


## Project Structure
- `core/`: Main application directory
  - `models.py`: Database models for Restaurant, Menu, Item, Student, and Order
  - `views.py`: View functions for handling requests
  - `templates/`: HTML templates for the frontend
  - `fixtures/`: Initial data for testing
- `student_order_project/`: Project settings and configuration

## API Endpoints
- `/api/student/<id>/details/`: Get student details
- `/api/restaurant/<id>/menu-items/`: Get restaurant menu items
- `/api/order/<id>/`: Get order details
- `/api/students/search/`: Search students
- `/api/restaurants/search/`: Search restaurants

## Security Features
- CSRF protection
- Form validation
- Balance verification for orders
- Computing ID format validation

## Contributors
- Lijie Chen
- Jiayu Li
- Celine Zhou
- Linda Mu

## License
This project is licensed under the MIT License - see the LICENSE file for details.
