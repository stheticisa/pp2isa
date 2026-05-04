"""
phonebook.py  —  TSIS 1: Extended PhoneBook Console Application
================================================================
Builds on Practice 7 & 8 (CRUD, CSV import, pattern search, upsert,
bulk-insert, pagination, delete procedures).

New features in TSIS 1:
  3.1  Extended schema: phones table, groups, email, birthday
  3.2  Filter by group, search by email, sort, paginated navigation
  3.3  Export to JSON, import from JSON, extended CSV import
  3.4  Procedures: add_phone, move_to_group, search_contacts (via SQL)
"""

import csv
import json
import sys
from datetime import datetime, date

import psycopg2
from connect import get_connection


# ─────────────────────────────────────────────────────────────────────────────
# DISPLAY HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def print_header(text):
    print(f"\n{'─' * 60}")
    print(f"  {text}")
    print(f"{'─' * 60}")


def print_row(row):
    """Pretty-print a contact row (tuple from DB functions)."""
    # Columns: id, first_name, last_name, email, birthday, group_name, phones
    cid, fname, lname, email, bday, group, phones = row
    print(f"  [{cid:>3}]  {fname or ''} {lname or ''}")
    print(f"         📞  {phones or '—'}")
    print(f"         ✉   {email  or '—'}   🎂 {bday or '—'}   👥 {group or '—'}")


def print_contacts(rows):
    if not rows:
        print("  (no contacts found)")
        return
    for r in rows:
        print_row(r)
        print()


# ─────────────────────────────────────────────────────────────────────────────
# 3.1 / 3.4  DATABASE OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

def add_contact(conn):
    """Add a new contact with optional email, birthday, group."""
    print_header("Add Contact")
    fname  = input("  First name : ").strip()
    lname  = input("  Last name  : ").strip() or None
    email  = input("  Email      : ").strip() or None
    bday   = input("  Birthday (YYYY-MM-DD) : ").strip() or None
    phone  = input("  Phone number : ").strip()
    ptype  = input("  Phone type [home/work/mobile] : ").strip() or "mobile"
    group  = input("  Group [Family/Work/Friend/Other] : ").strip() or None

    with conn.cursor() as cur:
        # Resolve or create group
        group_id = None
        if group:
            cur.execute(
                "INSERT INTO groups(name) VALUES(%s) ON CONFLICT(name) DO NOTHING RETURNING id",
                (group,)
            )
            row = cur.fetchone()
            if row:
                group_id = row[0]
            else:
                cur.execute("SELECT id FROM groups WHERE name=%s", (group,))
                group_id = cur.fetchone()[0]

        # Insert contact
        cur.execute(
            """INSERT INTO contacts(first_name, last_name, email, birthday, group_id)
               VALUES (%s,%s,%s,%s,%s) RETURNING id""",
            (fname, lname, email, bday, group_id)
        )
        contact_id = cur.fetchone()[0]

        # Insert phone
        if phone:
            cur.execute(
                "INSERT INTO phones(contact_id, phone, type) VALUES(%s,%s,%s)",
                (contact_id, phone, ptype)
            )
        conn.commit()
    print(f"  ✅ Contact '{fname}' added (id={contact_id}).")


def view_all(conn):
    """View all contacts with pagination."""
    print_header("All Contacts (paginated)")
    page_size = 5
    offset    = 0

    while True:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_page(%s, %s)", (page_size, offset))
            rows = cur.fetchall()
            # Get total count
            cur.execute("SELECT COUNT(*) FROM contacts")
            total = cur.fetchone()[0]

        page_num = offset // page_size + 1
        total_pages = max(1, (total + page_size - 1) // page_size)
        print(f"\n  Page {page_num} / {total_pages}  (total contacts: {total})")
        print_contacts(rows)

        if total_pages <= 1:
            break
        cmd = input("  [n]ext  [p]rev  [q]uit : ").strip().lower()
        if cmd == 'n' and offset + page_size < total:
            offset += page_size
        elif cmd == 'p' and offset > 0:
            offset -= page_size
        elif cmd == 'q':
            break


def search_menu(conn):
    """3.2 — Search by name/phone/email using the DB function search_contacts."""
    print_header("Search Contacts")
    query = input("  Search query (name / phone / email) : ").strip()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", (query,))
        rows = cur.fetchall()
    print_contacts(rows)


def filter_by_group(conn):
    """3.2 — Filter contacts by group."""
    print_header("Filter by Group")
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM groups ORDER BY name")
        groups = cur.fetchall()

    for gid, gname in groups:
        print(f"  [{gid}] {gname}")
    choice = input("  Select group id : ").strip()

    try:
        gid = int(choice)
    except ValueError:
        print("  Invalid choice.")
        return

    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday,
                   g.name AS group_name,
                   STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones
            FROM   contacts c
            LEFT   JOIN groups g ON g.id = c.group_id
            LEFT   JOIN phones p ON p.contact_id = c.id
            WHERE  c.group_id = %s
            GROUP  BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
        """, (gid,))
        rows = cur.fetchall()
    print_contacts(rows)


def sort_contacts(conn):
    """3.2 — Sort contacts by name, birthday, or date added."""
    print_header("Sort Contacts")
    print("  [1] By first name")
    print("  [2] By birthday")
    print("  [3] By date added")
    choice = input("  Choice : ").strip()
    order  = {
        "1": "c.first_name",
        "2": "c.birthday   NULLS LAST",
        "3": "c.created_at NULLS LAST",
    }.get(choice, "c.first_name")

    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday,
                   g.name AS group_name,
                   STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones
            FROM   contacts c
            LEFT   JOIN groups g ON g.id = c.group_id
            LEFT   JOIN phones p ON p.contact_id = c.id
            GROUP  BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name, c.created_at
            ORDER  BY {order}
        """)
        rows = cur.fetchall()
    print_contacts(rows)


def update_contact(conn):
    """Update email, birthday, or group of an existing contact."""
    print_header("Update Contact")
    name = input("  Enter first name of contact to update : ").strip()

    with conn.cursor() as cur:
        cur.execute("SELECT id FROM contacts WHERE first_name ILIKE %s LIMIT 1", (name,))
        row = cur.fetchone()
        if not row:
            print(f"  Contact '{name}' not found.")
            return
        cid = row[0]

        email = input("  New email (leave blank to skip) : ").strip() or None
        bday  = input("  New birthday YYYY-MM-DD (leave blank to skip) : ").strip() or None
        group = input("  New group (leave blank to skip) : ").strip() or None

        if email:
            cur.execute("UPDATE contacts SET email=%s WHERE id=%s", (email, cid))
        if bday:
            cur.execute("UPDATE contacts SET birthday=%s WHERE id=%s", (bday, cid))
        if group:
            cur.callproc("move_to_group", (name, group))  # uses our procedure
        conn.commit()
    print("  ✅ Contact updated.")


def delete_contact(conn):
    """Delete a contact by name."""
    print_header("Delete Contact")
    name = input("  First name to delete : ").strip()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM contacts WHERE first_name ILIKE %s", (name,))
        deleted = cur.rowcount
        conn.commit()
    print(f"  ✅ Deleted {deleted} contact(s) named '{name}'.")


def add_phone_menu(conn):
    """3.4.1 — Call add_phone procedure."""
    print_header("Add Phone Number")
    name  = input("  Contact first name : ").strip()
    phone = input("  Phone number       : ").strip()
    ptype = input("  Type [home/work/mobile] : ").strip() or "mobile"
    with conn.cursor() as cur:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()
    print("  ✅ Phone added.")


def move_group_menu(conn):
    """3.4.2 — Call move_to_group procedure."""
    print_header("Move Contact to Group")
    name  = input("  Contact first name : ").strip()
    group = input("  Group name         : ").strip()
    with conn.cursor() as cur:
        cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()
    print(f"  ✅ '{name}' moved to '{group}'.")


# ─────────────────────────────────────────────────────────────────────────────
# 3.3  IMPORT / EXPORT
# ─────────────────────────────────────────────────────────────────────────────

def _upsert_contact(cur, fname, lname, email, bday, group_name, phone, phone_type):
    """Insert or update a single contact with one phone number."""
    # Resolve group
    group_id = None
    if group_name:
        cur.execute(
            "INSERT INTO groups(name) VALUES(%s) ON CONFLICT(name) DO NOTHING", (group_name,)
        )
        cur.execute("SELECT id FROM groups WHERE name=%s", (group_name,))
        group_id = cur.fetchone()[0]

    # Upsert contact (by first_name match for simplicity)
    cur.execute("SELECT id FROM contacts WHERE first_name ILIKE %s LIMIT 1", (fname,))
    row = cur.fetchone()
    if row:
        cid = row[0]
        cur.execute(
            "UPDATE contacts SET last_name=%s, email=%s, birthday=%s, group_id=%s WHERE id=%s",
            (lname, email, bday, group_id, cid)
        )
    else:
        cur.execute(
            "INSERT INTO contacts(first_name,last_name,email,birthday,group_id) VALUES(%s,%s,%s,%s,%s) RETURNING id",
            (fname, lname, email, bday, group_id)
        )
        cid = cur.fetchone()[0]

    # Add phone if provided
    if phone:
        cur.execute(
            "INSERT INTO phones(contact_id,phone,type) VALUES(%s,%s,%s) "
            "ON CONFLICT DO NOTHING",
            (cid, phone, phone_type or "mobile")
        )
    return cid


def export_json(conn):
    """3.3.1 — Export all contacts to contacts_export.json."""
    print_header("Export to JSON")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email,
                   c.birthday::TEXT, g.name,
                   COALESCE(
                       JSON_AGG(
                           JSON_BUILD_OBJECT('phone', p.phone, 'type', p.type)
                       ) FILTER (WHERE p.phone IS NOT NULL),
                       '[]'::JSON
                   ) AS phones
            FROM   contacts c
            LEFT   JOIN groups g ON g.id = c.group_id
            LEFT   JOIN phones p ON p.contact_id = c.id
            GROUP  BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
            ORDER  BY c.first_name
        """)
        rows = cur.fetchall()

    contacts = []
    for cid, fname, lname, email, bday, group, phones in rows:
        contacts.append({
            "id":         cid,
            "first_name": fname,
            "last_name":  lname,
            "email":      email,
            "birthday":   bday,
            "group":      group,
            "phones":     phones,   # already a list from JSON_AGG
        })

    filename = f"contacts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)
    print(f"  ✅ Exported {len(contacts)} contacts → {filename}")


def import_json(conn):
    """3.3.2 — Import contacts from a JSON file with duplicate handling."""
    print_header("Import from JSON")
    filename = input("  JSON filename : ").strip()
    try:
        with open(filename, encoding="utf-8") as f:
            contacts = json.load(f)
    except FileNotFoundError:
        print(f"  File '{filename}' not found.")
        return
    except json.JSONDecodeError as e:
        print(f"  Invalid JSON: {e}")
        return

    inserted = skipped = overwritten = 0

    with conn.cursor() as cur:
        for c in contacts:
            fname = c.get("first_name", "").strip()
            if not fname:
                continue

            cur.execute(
                "SELECT id FROM contacts WHERE first_name ILIKE %s LIMIT 1", (fname,)
            )
            existing = cur.fetchone()

            if existing:
                answer = input(
                    f"  '{fname}' already exists — [s]kip / [o]verwrite? "
                ).strip().lower()
                if answer != "o":
                    skipped += 1
                    continue
                overwritten += 1
            else:
                inserted += 1

            phones = c.get("phones", [])
            first_phone = phones[0] if phones else {}
            _upsert_contact(
                cur,
                fname,
                c.get("last_name"),
                c.get("email"),
                c.get("birthday"),
                c.get("group"),
                first_phone.get("phone"),
                first_phone.get("type", "mobile"),
            )
            # Add extra phones
            for ph in phones[1:]:
                cur.execute(
                    "INSERT INTO phones(contact_id,phone,type) "
                    "SELECT id,%s,%s FROM contacts WHERE first_name ILIKE %s LIMIT 1",
                    (ph.get("phone"), ph.get("type","mobile"), fname)
                )

        conn.commit()
    print(f"  ✅ Done — inserted:{inserted}  overwritten:{overwritten}  skipped:{skipped}")


def import_csv(conn):
    """3.3.3 — Extended CSV import supporting new fields."""
    print_header("Import from CSV")
    filename = input("  CSV filename [contacts.csv] : ").strip() or "contacts.csv"

    try:
        with open(filename, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows   = list(reader)
    except FileNotFoundError:
        print(f"  File '{filename}' not found.")
        return

    ok = errors = 0
    with conn.cursor() as cur:
        for row in rows:
            try:
                _upsert_contact(
                    cur,
                    row.get("first_name","").strip(),
                    row.get("last_name","").strip() or None,
                    row.get("email","").strip()     or None,
                    row.get("birthday","").strip()  or None,
                    row.get("group","").strip()     or None,
                    row.get("phone","").strip()     or None,
                    row.get("phone_type","mobile").strip(),
                )
                ok += 1
            except Exception as e:
                print(f"  ⚠  Row skipped ({e}): {row}")
                errors += 1
        conn.commit()
    print(f"  ✅ CSV import — ok:{ok}  errors:{errors}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────────────────────────────────────

MENU = """
╔══════════════════════════════════╗
║       PhoneBook — TSIS 1        ║
╠══════════════════════════════════╣
║  1. View all (paginated)        ║
║  2. Search (name/phone/email)   ║
║  3. Filter by group             ║
║  4. Sort contacts               ║
║  5. Add contact                 ║
║  6. Update contact              ║
║  7. Delete contact              ║
║  8. Add phone to contact        ║
║  9. Move contact to group       ║
║  ─────────────────────────────  ║
║  E. Export to JSON              ║
║  I. Import from JSON            ║
║  C. Import from CSV             ║
║  ─────────────────────────────  ║
║  Q. Quit                        ║
╚══════════════════════════════════╝
"""

ACTIONS = {
    "1": view_all,
    "2": search_menu,
    "3": filter_by_group,
    "4": sort_contacts,
    "5": add_contact,
    "6": update_contact,
    "7": delete_contact,
    "8": add_phone_menu,
    "9": move_group_menu,
    "e": export_json,
    "i": import_json,
    "c": import_csv,
}


def main():
    try:
        conn = get_connection()
    except Exception as e:
        print(f"❌ Cannot connect to database: {e}")
        sys.exit(1)

    print("✅ Connected to database.")

    while True:
        print(MENU)
        choice = input("  Your choice : ").strip().lower()
        if choice == "q":
            print("  Goodbye!")
            break
        action = ACTIONS.get(choice)
        if action:
            try:
                action(conn)
            except Exception as e:
                conn.rollback()
                print(f"  ❌ Error: {e}")
        else:
            print("  Unknown option.")

    conn.close()


if __name__ == "__main__":
    main()