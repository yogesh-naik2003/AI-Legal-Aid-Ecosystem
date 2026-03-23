-- 1. Create the database
CREATE DATABASE IF NOT EXISTS legalaid_db;

-- 2. Use the database
USE legalaid_db;

-- 3. Create the 'users' table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('client', 'lawyer') NOT NULL,
    
    -- Client-specific fields (nullable)
    location VARCHAR(255),
    language VARCHAR(50),
    case_type VARCHAR(100),
    
    -- Lawyer-specific fields (nullable)
    bar_id VARCHAR(100),
    experience INT,
    specialization VARCHAR(100),
    document_path VARCHAR(255),
    
    -- Step 3 fields
    enable_2fa BOOLEAN DEFAULT 0,
    how_did_you_hear VARCHAR(100),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT * FROM users;


