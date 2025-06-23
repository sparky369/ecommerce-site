-- MySQL Database Setup
CREATE DATABASE ecommerce_db;
USE ecommerce_db;

-- Create database user
CREATE USER 'ecommerce_user'@'localhost' IDENTIFIED BY 'mysql123';
GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'ecommerce_user'@'localhost';
FLUSH PRIVILEGES;

-- Tables will be created by SQLAlchemy models
