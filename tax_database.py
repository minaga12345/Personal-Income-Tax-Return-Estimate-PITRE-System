import mysql.connector
from mysql.connector import Error

class TaxDatabaseServer:
    def __init__(self):
        self.connection = self.create_connection()

    def create_connection(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="mysql",
                database="tax_system"
            )
            if connection.is_connected():
                print("Connected to MySQL Database")
            return connection
        except Error as e:
            print(f"Error connecting to the database: {e}")
            return None

    def ensure_connection(self):
        if not self.connection or not self.connection.is_connected():
            self.connection = self.create_connection()

    def user_exists(self, person_id):
        self.ensure_connection()
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT 1 FROM users WHERE person_id = %s"
            cursor.execute(query, (person_id,))
            user = cursor.fetchone()
            cursor.close()
            return user is not None
        except Error as e:
            print(f"Error checking if user exists: {e}")
            return False

    def get_user_by_person_id(self, person_id):
        self.ensure_connection()
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE person_id = %s"
            cursor.execute(query, (person_id,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            print(f"Error fetching user by person ID: {e}")
            return None

    def register_tfn(self, person_id, tfn):
        self.ensure_connection()
        try:
            cursor = self.connection.cursor()
            query = "UPDATE users SET tfn = %s WHERE person_id = %s"
            cursor.execute(query, (tfn, person_id))
            self.connection.commit()
            cursor.close()
            print(f"TFN {tfn} registered for person ID {person_id}")
        except Error as e:
            print(f"Error registering TFN: {e}")

    def register_user(self, person_id, password, name=None, email=None, tfn=None):
        if not self.db.connection:
            return "Database connection failed. Please try again later."

        # Check if the user already exists
        if self.db.get_user_by_person_id(person_id):
            return f"Error: User with person_id '{person_id}' already exists."

        try:
            # Decide which table to insert into based on the presence of a TFN
            if tfn:
                # Insert into the main users table
                self.db.insert_record('users', {
                    'person_id': person_id,
                    'password': password,
                    'name': name,
                    'email': email,
                    'tfn': tfn,
                    'role': 'user'
                })
            else:
                # Insert into the TFN-free users table
                self.db.insert_record('tfn_free_users', {
                    'person_id': person_id,
                    'password': password,
                    'name': name,
                    'email': email,
                    'role': 'user'
                })
            return f"User '{person_id}' registered successfully."
        except Exception as e:
            return f"An error occurred during registration: {e}"


    def insert_tfn_free_user(self, person_id, password, name=None, email=None):
        """Insert a user into the TFN-free_users table."""
        self.ensure_connection()
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO TFN_free_users (person_id, password, name, email)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (person_id, password, name, email))
            self.connection.commit()
            cursor.close()
            return "TFN-free user registered successfully."
        except Error as e:
            return f"Error registering TFN-free user: {e}"

    def get_tfn_free_user_by_person_id(self, person_id):
        """Fetch a TFN-free user by person_id."""
        self.ensure_connection()
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM TFN_free_users WHERE person_id = %s"
            cursor.execute(query, (person_id,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            print(f"Error fetching TFN-free user by person ID: {e}")
            return None

    def get_payroll_records(self, person_id):
        self.ensure_connection()
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM payroll_records WHERE person_id = %s"
            cursor.execute(query, (person_id,))
            records = cursor.fetchall()
            cursor.close()
            return records
        except Error as e:
            print(f"Error fetching payroll records: {e}")
            return None

    def view_all_users(self):
        self.ensure_connection()
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM users"
            cursor.execute(query)
            users = cursor.fetchall()
            cursor.close()
            return users
        except Error as e:
            print(f"Error fetching all users: {e}")
            return None

    def view_schema(self, table_name):
        self.ensure_connection()
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = f"DESCRIBE {table_name}"
            cursor.execute(query)
            schema = cursor.fetchall()
            cursor.close()
            return schema
        except Error as e:
            print(f"Error fetching schema for table {table_name}: {e}")
            return None

    def insert_record(self, table, fields):
        self.ensure_connection()
        try:
            if table == "users" and "person_id" not in fields:
                return "Error: 'person_id' is required for users table."

            if table == "payroll_records" and "person_id" in fields:
                person_id = fields["person_id"]
                if not self.user_exists(person_id):
                    return f"Error: User with person_id '{person_id}' does not exist. Please add the user first."

                cursor = self.connection.cursor(dictionary=True)
                query = "SELECT COUNT(*) AS record_count FROM payroll_records WHERE person_id = %s"
                cursor.execute(query, (person_id,))
                record_count = cursor.fetchone()["record_count"]
                cursor.close()

                # Debug print for checking record count
                print(f"Record count for {person_id}: {record_count}")

                # Check if the record count exceeds 26
                if record_count >= 26:
                    return f"Error: Cannot exceed 26 payroll records for taxpayer {person_id}."

            cursor = self.connection.cursor()
            placeholders = ', '.join(['%s'] * len(fields))
            query = f"INSERT INTO {table} ({', '.join(fields.keys())}) VALUES ({placeholders})"
            cursor.execute(query, list(fields.values()))
            self.connection.commit()
            cursor.close()
            return f"Record inserted into {table}."
        except Error as e:
            return f"Error inserting record into {table}: {e}"



    def update_record(self, table, record_id, updates):
        self.ensure_connection()
        try:
            if not updates:
                return "Error: No updates provided."

            cursor = self.connection.cursor(dictionary=True)
            check_query = f"SELECT 1 FROM {table} WHERE id = %s"
            cursor.execute(check_query, (record_id,))
            if cursor.fetchone() is None:
                return f"Error: Record with ID {record_id} does not exist in {table}."

            set_clause = ', '.join([f"{key} = %s" for key in updates.keys()])
            query = f"UPDATE {table} SET {set_clause} WHERE id = %s"
            cursor.execute(query, list(updates.values()) + [record_id])
            self.connection.commit()
            cursor.close()
            return f"Record updated in {table} with ID {record_id}."
        except Error as e:
            return f"Error updating record in {table}: {e}"

    def delete_record(self, table, record_id):
        self.ensure_connection()
        try:
            cursor = self.connection.cursor(dictionary=True)
            check_query = f"SELECT 1 FROM {table} WHERE id = %s"
            cursor.execute(check_query, (record_id,))
            if cursor.fetchone() is None:
                return f"Error: Record with ID {record_id} does not exist in {table}."

            delete_query = f"DELETE FROM {table} WHERE id = %s"
            cursor.execute(delete_query, (record_id,))
            self.connection.commit()
            cursor.close()
            return f"Record deleted from {table} with ID {record_id}."
        except Error as e:
            return f"Error deleting record from {table}: {e}"

    def view_detailed_schema(self):
        self.ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            schema_info = {}
            for (table_name,) in tables:
                cursor.execute(f"DESCRIBE {table_name}")
                table_description = cursor.fetchall()
                schema_info[table_name] = table_description

            cursor.close()
            return schema_info
        except Error as e:
            print(f"Error fetching database schema: {e}")
            return None

    def view_all_records(self, table_name):
        self.ensure_connection()
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()
            return records
        except Error as e:
            print(f"Error fetching records from table {table_name}: {e}")
            return f"Error fetching records from table {table_name}: {e}"

