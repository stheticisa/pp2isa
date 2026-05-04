-- procedures.sql
-- New stored procedures / functions for TSIS 1
-- (Procedures from Practice 8 are NOT repeated here)
-- Run:  psql -U postgres -d phonebook -f procedures.sql

-- ── 3.4.1  add_phone ─────────────────────────────────────────────────────────
-- Adds a phone number to an existing contact identified by first_name.
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR DEFAULT 'mobile'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_id INTEGER;
BEGIN
    -- Find the contact (match on first_name; extend if needed)
    SELECT id INTO v_id
    FROM   contacts
    WHERE  first_name ILIKE p_contact_name
    LIMIT  1;

    IF v_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_id, p_phone, p_type);
END;
$$;


-- ── 3.4.2  move_to_group ─────────────────────────────────────────────────────
-- Moves a contact to a group; creates the group if it doesn't exist.
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    -- Resolve or create the group
    INSERT INTO groups (name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    -- Resolve the contact
    SELECT id INTO v_contact_id
    FROM   contacts
    WHERE  first_name ILIKE p_contact_name
    LIMIT  1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
END;
$$;


-- ── 3.4.3  search_contacts ───────────────────────────────────────────────────
-- Searches first_name, last_name, email AND all phone numbers.
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id         INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR,
    phones     TEXT          -- comma-separated list of phone numbers
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.first_name,
        c.last_name,
        c.email,
        c.birthday,
        g.name  AS group_name,
        STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones
    FROM   contacts c
    LEFT   JOIN groups g ON g.id = c.group_id
    LEFT   JOIN phones p ON p.contact_id = c.id
    WHERE
        c.first_name ILIKE '%' || p_query || '%'
        OR c.last_name  ILIKE '%' || p_query || '%'
        OR c.email      ILIKE '%' || p_query || '%'
        OR p.phone      ILIKE '%' || p_query || '%'
    GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name;
END;
$$;


-- ── Paginated query function (referenced in console) ─────────────────────────
-- (Already created in Practice 8 — included here for completeness if missing)
CREATE OR REPLACE FUNCTION get_contacts_page(p_limit INT, p_offset INT)
RETURNS TABLE (
    id         INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR,
    phones     TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.first_name,
        c.last_name,
        c.email,
        c.birthday,
        g.name AS group_name,
        STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones
    FROM   contacts c
    LEFT   JOIN groups g ON g.id = c.group_id
    LEFT   JOIN phones p ON p.contact_id = c.id
    GROUP  BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
    ORDER  BY c.first_name
    LIMIT  p_limit
    OFFSET p_offset;
END;
$$;