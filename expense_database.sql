-- CREATE DATABASE IF NOT EXISTS  expense_tracker;

-- USE expense_tracker;

-- DROP TABLE IF EXISTS expenses; 
-- DROP TABLE IF EXISTS users;

-- CREATE TABLE users (
-- 	id INT AUTO_INCREMENT PRIMARY KEY,
--     name VARCHAR(100) NOT NULL,
--     email VARCHAR(150) NOT NULL UNIQUE,
--     password VARCHAR(255) NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- CREATE TABLE expenses (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     user_id INT NOT NULL,
--     date DATE NOT NULL,
--     time TIME NOT NULL,
--     label VARCHAR(100) NOT NULL,
--     description VARCHAR(255),
--     amount DECIMAL(10, 2) NOT NULL,

--     FOREIGN KEY (user_id)
--         REFERENCES users(id)
--         ON DELETE CASCADE
-- );