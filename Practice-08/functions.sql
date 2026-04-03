CREATE OR REPLACE FUNCTION get_contacts_by_pattern(p text)
RETURNS TABLE(id INT, name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT id, name, phone
    FROM contacts
    WHERE name ILIKE '%' || p || '%'
       OR phone ILIKE '%' || p || '%';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(id INT, name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT id, name, phone
    FROM contacts
    ORDER BY id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;
