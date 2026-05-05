-- ИНФОРМАЦИОННАЯ СИСТЕМА «ЛИЧНЫЙ ФИНАНСОВЫЙ УЧЁТ»
-- Создание базы данных и таблиц
CREATE DATABASE finance_db;

-- 3. Переключаемся на неё
USE finance_db;

-- Таблица 1: users (пользователи)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица 2: currency (валюты)
CREATE TABLE currency (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(3) UNIQUE NOT NULL,
    symbol VARCHAR(5),
    name VARCHAR(50)
);

-- Таблица 3: accounts (счета)
CREATE TABLE accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    currency_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    balance DECIMAL(12,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (currency_id) REFERENCES currency(id)
);

-- Таблица 4: categories (категории)
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type ENUM('income', 'expense') NOT NULL,
    parent_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- Таблица 5: operations (финансовые операции)
CREATE TABLE operations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    account_id INT NOT NULL,
    category_id INT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Таблица 6: tags (метки/теги)
CREATE TABLE tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Таблица 7: operation_tags (связь операций с метками)
CREATE TABLE operation_tags (
    operation_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (operation_id, tag_id),
    FOREIGN KEY (operation_id) REFERENCES operations(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Таблица 8: budget_limits (бюджетные лимиты)
CREATE TABLE budget_limits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    month DATE NOT NULL,
    limit_amount DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);