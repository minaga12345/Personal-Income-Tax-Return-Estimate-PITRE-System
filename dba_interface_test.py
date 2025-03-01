from tax_database import TaxDatabaseServer

def main():
    db = TaxDatabaseServer()
    print("Connected to MySQL Database\n")

    # Check schema
    schema = db.view_detailed_schema()
    print("--- Database Schema ---")
    for table_name, table_info in schema.items():
        print(f"\nTable: {table_name}")
        for column in table_info:
            print(column)

    # Test inserting a payroll record with a non-existent user
    print("\n--- Test Insert into 'payroll_records' with non-existent user ---")
    non_existent_record = {
        "person_id": "nonexistent123",  # This person_id should not exist in the users table
        "pay_period_start": "2023-01-01",
        "pay_period_end": "2023-01-15",
        "gross_income": 2000.00,
        "tax_paid": 300.00
    }
    db.insert_record("payroll_records", non_existent_record)

    # Test inserting a payroll record with a valid user
    print("\n--- Test Insert into 'payroll_records' with valid user ---")
    valid_record = {
        "person_id": "123456",  # Replace with a valid person_id from your users table
        "pay_period_start": "2023-02-01",
        "pay_period_end": "2023-02-15",
        "gross_income": 2500.00,
        "tax_paid": 350.00
    }
    db.insert_record("payroll_records", valid_record)

    # Test inserting beyond the record limit for the same user
    print("\n--- Test Record Limit Constraint ---")
    for _ in range(26):  # Adjust based on current records for the user
        db.insert_record("payroll_records", valid_record)

if __name__ == "__main__":
    main()
