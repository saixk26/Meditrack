-- =============================================================================
-- MediTrack Database Schema
-- Smart Medical Expiry and Inventory Management System
--
-- This SQL file is provided for documentation / evaluation purposes.
-- It can also be used to inspect or recreate the schema outside Django.
-- =============================================================================

CREATE DATABASE IF NOT EXISTS meditrack_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE meditrack_db;


-- =============================================================================
-- CATEGORY
-- =============================================================================

CREATE TABLE IF NOT EXISTS core_category (
    category_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE,
    description VARCHAR(100) NOT NULL DEFAULT '',
    created_at DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =============================================================================
-- SUPPLIER
-- =============================================================================

CREATE TABLE IF NOT EXISTS core_supplier (
    supplier_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    contact_person VARCHAR(30) NOT NULL DEFAULT '',
    phone VARCHAR(12) NOT NULL,
    email VARCHAR(30) NOT NULL DEFAULT '',
    address LONGTEXT NOT NULL,
    gst_number VARCHAR(20) NOT NULL DEFAULT '',
    is_active TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =============================================================================
-- CUSTOMER
-- =============================================================================

CREATE TABLE IF NOT EXISTS core_customer (
    customer_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    phone VARCHAR(12) NOT NULL,
    email VARCHAR(30) NOT NULL DEFAULT '',
    address LONGTEXT NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =============================================================================
-- MEDICINE
-- =============================================================================

CREATE TABLE IF NOT EXISTS core_medicine (
    medicine_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    code VARCHAR(10) NOT NULL UNIQUE,
    batch_number VARCHAR(30) NOT NULL,
    category_id BIGINT NULL,
    supplier_id BIGINT NULL,
    manufacturer VARCHAR(50) NOT NULL,
    manufacture_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    purchase_price DECIMAL(10,2) NOT NULL,
    selling_price DECIMAL(10,2) NOT NULL,
    gst_percentage DECIMAL(5,2) NOT NULL DEFAULT 5.00,
    quantity INT UNSIGNED NOT NULL DEFAULT 0,
    minimum_stock INT UNSIGNED NOT NULL DEFAULT 10,
    rack_number VARCHAR(20) NOT NULL DEFAULT '',
    image VARCHAR(100),
    status VARCHAR(10) NOT NULL DEFAULT 'active',
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,

    CONSTRAINT fk_medicine_category
        FOREIGN KEY (category_id)
        REFERENCES core_category (category_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_medicine_supplier
        FOREIGN KEY (supplier_id)
        REFERENCES core_supplier (supplier_id)
        ON DELETE SET NULL,

    INDEX idx_medicine_expiry_date (expiry_date),
    INDEX idx_medicine_code (code)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =============================================================================
-- NOTE ON EXPIRY STATUS
-- =============================================================================
-- MediTrack does NOT store an expiry_status or stock_status column.
-- These values are calculated dynamically by Django using:
--
--     expiry_date
--     quantity
--     minimum_stock
--
-- Therefore, the Smart Expiry Alert Center always uses current data.


-- =============================================================================
-- BILL
-- =============================================================================

CREATE TABLE IF NOT EXISTS core_bill (
    bill_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    bill_number VARCHAR(30) NOT NULL UNIQUE,

    customer_id BIGINT NULL,
    created_by_id INT NULL,

    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0,
    discount_percent DECIMAL(5,2) NOT NULL DEFAULT 0,
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    gst_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    grand_total DECIMAL(12,2) NOT NULL DEFAULT 0,

    payment_method VARCHAR(10) NOT NULL DEFAULT 'cash',
    payment_status VARCHAR(10) NOT NULL DEFAULT 'paid',

    created_at DATETIME(6) NOT NULL,

    CONSTRAINT fk_bill_customer
        FOREIGN KEY (customer_id)
        REFERENCES core_customer (customer_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_bill_created_by
        FOREIGN KEY (created_by_id)
        REFERENCES auth_user (id)
        ON DELETE SET NULL

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =============================================================================
-- BILL ITEM
-- =============================================================================

CREATE TABLE IF NOT EXISTS core_billitem (
    bill_item_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    bill_id BIGINT NOT NULL,
    medicine_id BIGINT NOT NULL,

    quantity INT UNSIGNED NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    gst_percent DECIMAL(5,2) NOT NULL DEFAULT 0,

    CONSTRAINT fk_billitem_bill
        FOREIGN KEY (bill_id)
        REFERENCES core_bill (bill_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_billitem_medicine
        FOREIGN KEY (medicine_id)
        REFERENCES core_medicine (medicine_id)
        ON DELETE RESTRICT

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =============================================================================
-- ACTIVITY LOG
-- =============================================================================

CREATE TABLE IF NOT EXISTS core_activitylog (
    activity_log_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    action VARCHAR(30) NOT NULL,
    description VARCHAR(100) NOT NULL,
    timestamp DATETIME(6) NOT NULL,

    user_id INT NULL,

    CONSTRAINT fk_activitylog_user
        FOREIGN KEY (user_id)
        REFERENCES auth_user (id)
        ON DELETE SET NULL

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =============================================================================
-- DEFAULT ADMINISTRATOR
-- =============================================================================
-- The default administrator account is created/reset through:
--
--     python manage.py seed_admin
--
-- Django securely hashes the password using PBKDF2.
-- Passwords should NOT be inserted directly into this SQL file.
-- =============================================================================