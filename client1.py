import Pyro5.api

def main():
    tax_server = Pyro5.api.Proxy("PYRONAME:Aus.taxcalculator")
    print("Welcome to the Tax System")

    while True:
        print("\nMain Menu:")
        print("1. User Login")
        print("2. Admin Login")
        print("3. User Registration")
        print("4. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            user_login(tax_server)
        elif choice == "2":
            admin_login(tax_server)
        elif choice == "3":
            user_registration(tax_server)
        elif choice == "4":
            print("Exiting the system...")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

def user_registration(tax_server):
    print("\nUser Registration:")
    person_id = input("Enter your Person ID: ").strip()
    password = input("Enter your password: ").strip()
    name = input("Enter your name (optional): ").strip() or None
    email = input("Enter your email (optional): ").strip() or None
    tfn = input("Enter your TFN (optional, leave blank if you don't have one): ").strip() or None

    response = tax_server.register_user(person_id, password, name, email, tfn)
    print(response)




def user_login(tax_server):
    person_id = input("Enter your Person ID: ").strip()
    password = input("Enter your password: ").strip()
    user = tax_server.authenticate_user(person_id, password)
    
    if user:
        print(f"Welcome, {user['name']}!")
        user_menu(tax_server, person_id)
    else:
        print("Invalid credentials. Please try again.")

def update_profile(tax_server, person_id):
    print("\nUpdate Profile:")
    update_email = input("Do you want to update your email? (yes/no): ").strip().lower() == "yes"
    update_password = input("Do you want to update your password? (yes/no): ").strip().lower() == "yes"

    new_email = None
    new_password = None

    if update_email:
        new_email = input("Enter your new email: ").strip()

    if update_password:
        new_password = input("Enter your new password: ").strip()

    if new_email or new_password:
        response = tax_server.update_profile(person_id, new_email, new_password)
        print(response)
    else:
        print("No changes were made to your profile.")


def user_menu(tax_server, person_id):
    while True:
        print("\nUser Menu:")
        print("1. Register a new TFN")
        print("2. Calculate tax with TFN")
        print("3. Calculate tax without TFN")
        print("4. View tax history")
        print("5. View payroll records")  # Display user-specific payroll records
        print("6. Update profile")
        print("7. Logout")

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            tfn = input("Enter your new TFN: ").strip()
            gross_income = float(input("Enter your gross income: "))
            tax_withheld = float(input("Enter your tax withheld: "))
            net_income = float(input("Enter your net income: "))
            pay_period_start = input("Enter pay period start date (YYYY-MM-DD): ").strip()
            pay_period_end = input("Enter pay period end date (YYYY-MM-DD): ").strip()
            has_insurance = input("Do you have private health insurance (yes/no)? ").strip().lower() == "yes"

            response = tax_server.register_tfn(person_id, tfn, gross_income, tax_withheld, net_income, pay_period_start, pay_period_end, has_insurance)
            print(response)
        elif choice == "2":
            response = tax_server.calculate_tax(person_id)
            print(response)
        elif choice == "3":
            biweekly_wages = float(input("Enter your biweekly net wages: "))
            tax_withheld = float(input("Enter your tax withheld: "))
            annual_income = float(input("Enter your estimated annual income: "))
            has_insurance = input("Do you have private health insurance (yes/no)? ").strip().lower() == "yes"
            response = tax_server.calculate_tax_without_tfn(person_id, biweekly_wages, tax_withheld, annual_income, has_insurance)
            print(response)
        elif choice == "4":
            history = tax_server.view_tax_history(person_id)
            if isinstance(history, str):
                print(history)
            else:
                for record in history:
                    print(f"Date: {record['calculation_date']}, Tax Amount: {record['tax_amount']}, Refund: {record['is_refund']}")
        elif choice == "5":
            view_user_payroll_records(tax_server, person_id)
        elif choice == "6":
            update_profile(tax_server, person_id)
        elif choice == "7":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")


def admin_login(tax_server):
    admin_id = input("Enter Admin ID: ").strip()
    password = input("Enter Admin password: ").strip()
    
    admin = tax_server.authenticate_user(admin_id, password)
    if admin and admin['role'] == 'admin':
        print(f"Welcome, Admin {admin['name']}!")
        admin_menu(tax_server)
    else:
        print("Invalid admin credentials. Please try again.")

def add_user(tax_server):
    print("\nAdd New User:")
    person_id = input("Enter the person ID: ").strip()
    name = input("Enter the name: ").strip()
    email = input("Enter the email: ").strip()
    password = input("Enter the password: ").strip()
    role = input("Enter the role (user/admin): ").strip().lower()
    tfn = input("Enter the TFN (optional): ").strip() or None
    annual_income = input("Enter the annual income (optional): ").strip()
    tax_withheld = input("Enter the tax withheld (optional): ").strip()
    has_health_insurance = input("Do you have private health insurance (yes/no): ").strip().lower() == "yes"

    # Convert optional inputs to None if empty
    annual_income = float(annual_income) if annual_income else None
    tax_withheld = float(tax_withheld) if tax_withheld else None
    
    response = tax_server.add_user(person_id, name, email, password, role, tfn, annual_income, tax_withheld, has_health_insurance)
    print(response)


def view_user_payroll_records(tax_server, person_id):
    print("\nView Your Payroll Records:")
    response = tax_server.view_payroll_records(person_id)

    if isinstance(response, str):
        print(response)
    else:
        for record in response:
            print(f"Start: {record['pay_period_start']}, End: {record['pay_period_end']}, "
                  f"Gross Income: {record['gross_income']}, Tax Paid: {record['tax_paid']}")

            
def update_user(tax_server):
    print("\nUpdate User:")
    person_id = input("Enter the person ID of the user to update: ").strip()
    new_email = input("Enter the new email (leave blank to keep unchanged): ").strip()
    new_password = input("Enter the new password (leave blank to keep unchanged): ").strip()
    new_role = input("Enter the new role (user/admin, leave blank to keep unchanged): ").strip().lower()
    new_tfn = input("Enter the new TFN (leave blank to keep unchanged): ").strip()
    new_annual_income = input("Enter the new annual income (leave blank to keep unchanged): ").strip()
    new_tax_withheld = input("Enter the new tax withheld (leave blank to keep unchanged): ").strip()
    has_health_insurance = input("Do you have private health insurance (yes/no, leave blank to keep unchanged): ").strip().lower()
    
    # Convert inputs to appropriate types or None
    new_annual_income = float(new_annual_income) if new_annual_income else None
    new_tax_withheld = float(new_tax_withheld) if new_tax_withheld else None
    has_health_insurance = True if has_health_insurance == "yes" else False if has_health_insurance == "no" else None

    response = tax_server.update_user(person_id, new_email or None, new_password or None, new_role or None,
                                      new_tfn or None, new_annual_income, new_tax_withheld, has_health_insurance)
    print(response)



def delete_user(tax_server):
    print("\nDelete User:")
    person_id = input("Enter the person ID of the user to delete: ").strip()
    confirm = input("Are you sure you want to delete this user? (yes/no): ").strip().lower()
    if confirm == "yes":
        response = tax_server.delete_user(person_id)
        print(response)

def search_users(tax_server):
    print("\nSearch Users:")
    person_id = input("Enter person ID (leave blank for any): ").strip()
    email = input("Enter email (leave blank for any): ").strip()
    role = input("Enter role (user/admin, leave blank for any): ").strip().lower()

    response = tax_server.search_users(person_id or None, email or None, role or None)
    if isinstance(response, str):
        print(response)
    else:
        for user in response:
            print(user)

def view_all_payroll_records(tax_server):
    print("\nView All Payroll Records:")
    person_id = input("Enter person ID to filter (leave blank to view all records): ").strip()

    if person_id:
        response = tax_server.view_payroll_records(person_id)
    else:
        response = tax_server.view_payroll_records()

    if isinstance(response, str):
        print(response)
    else:
        for record in response:
            print(f"Person ID: {record['person_id']}, Start: {record['pay_period_start']}, "
                  f"End: {record['pay_period_end']}, Gross Income: {record['gross_income']}, Tax Paid: {record['tax_paid']}")

def insert_record(tax_server):
    print("\nInsert Record:")
    table = input("Enter the table name: ").strip()
    fields = {}
    
    # Assuming we need to gather fields and values
    while True:
        field = input("Enter field name (or 'done' to finish): ").strip()
        if field.lower() == 'done':
            break
        value = input(f"Enter value for '{field}': ").strip()
        fields[field] = value
     
    response = tax_server.insert_record(table, fields)
    print(response)

def update_record(tax_server):
    print("\nUpdate Record:")
    table = input("Enter the table name: ").strip()
    record_id = input("Enter the record ID to update: ").strip()
    updates = {}

    while True:
        field = input("Enter field name to update (or 'done' to finish): ").strip()
        if field.lower() == 'done':
            break
        value = input(f"Enter new value for '{field}': ").strip()
        updates[field] = value

    response = tax_server.update_record(table, record_id, updates)
    print(response)

def delete_record(tax_server):
    print("\nDelete Record:")
    table = input("Enter the table name: ").strip()
    record_id = input("Enter the record ID to delete: ").strip()
    response = tax_server.delete_record(table, record_id)
    print(response)

def display_database_schema(tax_server):
    schema = tax_server.view_detailed_schema()
    if schema:
        print("\n--- Database Schema ---")
        for table, details in schema.items():
            print(f"\nTable: {table}")
            for column in details:
                col_name = column[0]
                col_type = column[1]
                col_key = f"(Key: {column[3]})" if column[3] else "(Key: )"
                print(f"  {col_name} - {col_type} {col_key}")
    else:
        print("Error fetching schema.")

def view_all_records(tax_server):
    table_name = input("Enter the table name to view records: ").strip()
    records = tax_server.view_all_records(table_name)

    if isinstance(records, str):
        print(records)
    else:
        print(f"\n--- Database Records ---\nTable: {table_name}")
        if records:
            # Extract and print the column names
            columns = records[0].keys()
            col_headers = " | ".join(columns)
            header_line = "-" * len(col_headers)
            print(f"{col_headers}\n{header_line}")

            # Print each row of data
            for record in records:
                row_data = " | ".join(str(value) for value in record.values())
                print(f"{row_data}")
        else:
            print("No records found.")


def admin_menu(tax_server):
    while True:
        print("\nAdmin Menu:")
        print("1. View all users")
        print("2. Add a new user")
        print("3. Update a user")
        print("4. Delete a user")
        print("5. View all tax history")
        print("6. Search users")
        print("7. Display payroll records of users")
        print("8. Insert record")
        print("9. Update record")
        print("10. Delete record")
        print("11. Export user data to CSV")
        print("12. Export tax history to CSV")
        print("13. View Database Schema")
        print("14. View All Records in a Table")
        print("15. Exit Admin Menu")

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            users = tax_server.admin_view_users()
            for user in users:
                print(user)
        elif choice == "2":
            add_user(tax_server)
        elif choice == "3":
            update_user(tax_server)
        elif choice == "4":
            delete_user(tax_server)
        elif choice == "5":
            history = tax_server.view_all_tax_history()
            if isinstance(history, str):
                print(history)
            else:
                for record in history:
                    print(f"Person ID: {record['person_id']}, Date: {record['calculation_date']}, Tax Amount: {record['tax_amount']}, Refund: {record['is_refund']}")
        elif choice == "6":
            search_users(tax_server)
        elif choice == "7":
            view_all_payroll_records(tax_server)
        elif choice == "8":
            insert_record(tax_server)  # Call the newly defined function
        elif choice == "9":
            update_record(tax_server)  # Call the newly defined function
        elif choice == "10":
            delete_record(tax_server)  # Call the newly defined function
        elif choice == "11":
            file_path = input("Enter the file path for the CSV export (default: exported_users.csv): ").strip()
            file_path = file_path or "exported_users.csv"
            response = tax_server.export_users_to_csv(file_path)
            print(response)
        elif choice == "12":
            file_path = input("Enter the file path for the CSV export (default: exported_tax_history.csv): ").strip()
            file_path = file_path or "exported_tax_history.csv"
            response = tax_server.export_tax_history_to_csv(file_path)
            print(response)
        elif choice == "13":
            display_database_schema(tax_server)
        elif choice == "14":
            table_name = input("Enter the table name to view records: ").strip()
            records = tax_server.view_all_records(table_name)
            if isinstance(records, str):
                print(records)
            else:
                for record in records:
                    print(record)
        elif choice == "15":
            print("Exiting Admin Menu...")
            break
        else:
            print("Invalid choice. Please try again.")



if __name__ == "__main__":
    main()
