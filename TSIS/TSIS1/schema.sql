-- schema.sql
-- Extended PhoneBook schema for TSIS 1
-- Run this file once against your database:
--   psql -U postgres -d phonebook -f schema.sql

-- ── Groups / categories ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Seed default groups
INSERT INTO groups (name) VALUES
    ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;

-- ── Contacts (base table from Practice 7) ────────────────────────────────────
CREATE TABLE IF NOT EXISTS contacts (
    id         SERIAL PRIMARY KEY,
    first_name VARCHAR(50)  NOT NULL,
    last_name  VARCHAR(50),
    email      VARCHAR(100),
    birthday   DATE,
    group_id   INTEGER REFERENCES groups(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add new columns if upgrading from Practice 7 schema
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS email      VARCHAR(100);
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS birthday   DATE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS group_id   INTEGER REFERENCES groups(id) ON DELETE SET NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();

-- ── Phones (1-to-many) ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(20)  NOT NULL,
    type       VARCHAR(10)  CHECK (type IN ('home', 'work', 'mobile')) DEFAULT 'mobile'
);