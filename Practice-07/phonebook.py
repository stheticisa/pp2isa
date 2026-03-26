# phonebook.py
import csv
from connect import connect

# ------------------------
# CRUD FUNCTIONS
# ------------------------

def insert_contact(name, phone):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO contacts (name, phone) VALUES (%s, %s)", (name, phone))
    conn.commit()
    cur.close()
    conn.close()
    print("Contact added!")

def get_contacts():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM contacts ORDER BY id")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    cur.close()
    conn.close()

def update_contact(contact_id, new_name=None, new_phone=None):
    conn = connect()
    cur = conn.cursor()
    if new_name:
        cur.execute("UPDATE contacts SET name = %s WHERE id = %s", (new_name, contact_id))
    if new_phone:
        cur.execute("UPDATE contacts SET phone = %s WHERE id = %s", (new_phone, contact_id))
    conn.commit()
    cur.close()
    conn.close()
    print("Contact updated!")

def delete_contact(contact_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))
    conn.commit()
    cur.close()
    conn.close()
    print("Contact deleted!")

# ------------------------
# CSV IMPORT
# ------------------------

def import_contacts_from_csv(file_path):
    conn = connect()
    cur = conn.cursor()
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cur.execute(
                "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
                (row['name'], row['phone'])
            )
    conn.commit()
    cur.close()
    conn.close()
    print(f"Contacts imported from {file_path}!")

# ------------------------
# INTERACTIVE MENU
# ------------------------

def menu():
    while True:
        print("\n--- PhoneBook Menu ---")
        print("1. Show all contacts")
        print("2. Add new contact")
        print("3. Update contact")
        print("4. Delete contact")
        print("5. Import contacts from CSV")
        print("6. Exit")
        choice = input("Enter choice (1-6): ")

        if choice == "1":
            get_contacts()
        elif choice == "2":
            name = input("Enter name: ")
            phone = input("Enter phone: ")
            insert_contact(name, phone)
        elif choice == "3":
            contact_id = int(input("Enter contact ID to update: "))
            new_name = input("Enter new name (leave blank to skip): ").strip()
            new_phone = input("Enter new phone (leave blank to skip): ").strip()
            update_contact(contact_id, new_name if new_name else None, new_phone if new_phone else None)
        elif choice == "4":
            contact_id = int(input("Enter contact ID to delete: "))
            delete_contact(contact_id)
        elif choice == "5":
            file_path = input("Enter CSV file path: ").strip()
            import_contacts_from_csv(file_path)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice! Please enter 1-6.")

# ------------------------
# MAIN
# ------------------------

if __name__ == "__main__":
    menu()