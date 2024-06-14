CREATE DATABASE `webdav_auth`;
USE mysql;
CREATE USER 'webdav'@'localhost' IDENTIFIED BY 'QAHQhgSWa5wMq1Arteob6DMyZocR2x3g';
GRANT ALL PRIVILEGES ON webdav_auth.* TO 'webdav'@'localhost';
FLUSH PRIVILEGES;
USE webdav_auth;
CREATE TABLE users (
   id INT AUTO_INCREMENT PRIMARY KEY,
   username VARCHAR(255) NOT NULL UNIQUE,
   password VARCHAR(255) NOT NULL
);