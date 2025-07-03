## Project Overview
This project presents the design and implementation of a comprehensive e-commerce website utilizing an SQL database backend. The project was completed in two development sprints to demonstrate agile development practices. Sprint 1 established the core e-commerce functionality, including user registration and authentication, product catalog, shopping cart functionality, and customer review system. Sprint 2 expanded the system with administrative capabilities to enable complete order lifecycle management.

## System Architecture
The system follows a three-tier architecture pattern consisting of the presentation layer, the application layer, and the data layer. This separation provides modularity, scalability, and maintainability.

1. **Presentation Layer**
   - HTML templates using Jinja2 templating engine
   - Bootstrap CSS framework for responsive design
   - JavaScript for client-side interactions
   - RESTful API endpoints for AJAX requests

2. **Application Layer**  
   - Flask web framework as the main application server
   - SQLAlchemy ORM for database abstraction
   - Flask-Login for user session management
   - Flask-WTF for form handling and CSRF protection

3. **Data Layer**
   - MySQL relational database for data persistence
   - Database connection pooling for performance
   - Proper indexing for query optimization
   - Transaction management for data consistency

## Technology Stack

1. **Backend Technologies**
   - Python 3.8+ as a programming language
   - Flask 2.0+ as a web framework
   - SQLAlchemy 1.4+ as ORM
   - MySQL 8.0+ as a database system
   - Gunicorn as WSGI server

2. **Frontend Technologies**  
   - HTML5 for markup
   - CSS3 with Bootstrap 5 for styling
   - JavaScript for client-side functionality
   - Jinja2 for server-side templating

3. **Infrastructure**
   - Amazon EC2 for application hosting
   - Ubuntu 20.04 LTS as operating system
   - Nginx as reverse proxy
   - MySQL server for database


