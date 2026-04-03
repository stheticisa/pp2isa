from connect import connect

def search_pattern(pattern):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_contacts_by_pattern(%s)", (pattern,))
    for row in cur.fetchall():
        print(row)
    cur.close()
    conn.close()

def upsert(name, phone):
    conn = connect()
    cur = conn.cursor()
    cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
    conn.commit()
    cur.close()
    conn.close()
    print("Upsert done!")

def get_paginated(limit, offset):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
    for row in cur.fetchall():
        print(row)
    cur.close()
    conn.close()

def delete_by_value(value):
    conn = connect()
    cur = conn.cursor()
    cur.execute("CALL delete_contact_by_value(%s)", (value,))
    conn.commit()
    cur.close()
    conn.close()
    print("Deleted!")

def menu():
    while True:
        print("\n--- Practice 8 Menu ---")
        print("1. Search (pattern)")
        print("2. Upsert contact")
        print("3. Paginated view")
        print("4. Delete by name/phone")
        print("5. Exit")

        choice = input("Choose: ")

        if choice == "1":
            p = input("Enter pattern: ")
            search_pattern(p)

        elif choice == "2":
            name = input("Name: ")
            phone = input("Phone: ")
            upsert(name, phone)

        elif choice == "3":
            limit = int(input("Limit: "))
            offset = int(input("Offset: "))
            get_paginated(limit, offset)

        elif choice == "4":
            val = input("Enter name or phone: ")
            delete_by_value(val)

        elif choice == "5":
            break

        else:
            print("Invalid choice")

if __name__ == "__main__":
    menu()
