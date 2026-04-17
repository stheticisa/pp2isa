from connect import connect

conn = connect()
cur = conn.cursor()

print("Connected to PostgreSQL!")

# ---------------- FUNCTIONS ---------------- #

def search_pattern(pattern):
    cur.execute("SELECT * FROM get_contacts_by_pattern(%s)", (pattern,))
    rows = cur.fetchall()
    for row in rows:
        print(row)


def upsert(name, phone):
    cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
    conn.commit()


def show_paginated(limit, offset):
    cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
    rows = cur.fetchall()
    for row in rows:
        print(row)


def delete_contact(value):
    cur.execute("CALL delete_contact(%s)", (value,))
    conn.commit()


def bulk_insert():
    names = input("Enter names (comma separated): ")
    phones = input("Enter phones (comma separated): ")

    name_list = [n.strip() for n in names.split(",")]
    phone_list = [p.strip() for p in phones.split(",")]

    cur.execute(
        "SELECT * FROM bulk_insert_contacts(%s, %s)",
        (name_list, phone_list)
    )

    rows = cur.fetchall()

    print("\nInvalid data:")
    for row in rows:
        print(row)

    conn.commit()


# ---------------- MENU ---------------- #

def menu():
    while True:
        print("\n--- Practice 8 Menu ---")
        print("1. Search (pattern)")
        print("2. Upsert contact")
        print("3. Paginated view")
        print("4. Delete by name/phone")
        print("5. Bulk insert contacts")
        print("6. Exit")

        choice = input("Choose: ")

        if choice == "1":
            pattern = input("Enter pattern: ")
            search_pattern(pattern)

        elif choice == "2":
            name = input("Name: ")
            phone = input("Phone: ")
            upsert(name, phone)

        elif choice == "3":
            limit = int(input("Enter limit: "))
            offset = int(input("Enter offset: "))
            show_paginated(limit, offset)

        elif choice == "4":
            value = input("Enter name or phone: ")
            delete_contact(value)

        elif choice == "5":
            bulk_insert()

        elif choice == "6":
            break

        else:
            print("Invalid choice")


menu()