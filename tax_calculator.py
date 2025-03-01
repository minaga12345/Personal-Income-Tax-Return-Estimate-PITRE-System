import Pyro5.api
import csv
import os
from tax_database import TaxDatabaseServer
from validator import Validator
from mysql.connector import Error


@Pyro5.api.expose
class TaxCalculator:
    def __init__(self):
        self.db = TaxDatabaseServer()
        self.validator = Validator()  # Make sure the validator is properly initialized

    def view_detailed_schema(self):
        """Expose the detailed schema view through the TaxCalculator class."""
        # Call the method from the db (TaxDatabaseServer instance)
        if not self.db.connection:
            return "Database connection failed. Please try again later."
        return self.db.view_detailed_schema()
    
    def view_all_records(self, table_name):
        """Expose the method to view all records in a given table."""
        return self.db.view_all_records(table_name)

    def authenticate_user(self, person_id, password):
        if not self.db.connection:
            return "Database connection failed. Please try again later."
        cursor = self.db.connection.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE person_id = %s AND password = %s"
        cursor.execute(query, (person_id, password))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return result
        else:
            return None
        
    def register_user(self, person_id, password, name=None, email=None, tfn=None):
        if not self.db.connection:
            return "Database connection failed. Please try again later."

        # Check if the user already exists in either table
        if self.db.get_user_by_person_id(person_id) or self.db.get_tfn_free_user_by_person_id(person_id):
            return f"Error: User with person_id '{person_id}' already exists."

        try:
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
                    'email': email
                })
            return f"User '{person_id}' registered successfully."
        except Exception as e:
            return f"An error occurred during registration: {e}"

    def get_tfn_free_user_by_person_id(self, person_id):
        self.ensure_connection()
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM tfn_free_users WHERE person_id = %s"
            cursor.execute(query, (person_id,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            print(f"Error fetching TFN-free user by person ID: {e}")
            return None



    def register_tfn(self, person_id, tfn, gross_income, tax_withheld, net_income, pay_period_start, pay_period_end, has_insurance):
        if not self.db.connection:
            return "Database connection failed. Please try again later."

        # Check if the user already has a TFN
        existing_user = self.db.get_user_by_person_id(person_id)
        if existing_user and existing_user['tfn']:
            return "Error: You already have a TFN and cannot register a new one."

        try:
            # Validate inputs
            self.validator.validate_tfn(tfn)
            self.validator.validate_wage(gross_income)
            self.validator.validate_wage(tax_withheld)
            self.validator.validate_wage(net_income)
            self.validator.validate_date(pay_period_start)
            self.validator.validate_date(pay_period_end)
            self.validator.validate_pay_period(pay_period_start, pay_period_end)

            # Update the TFN in the users table
            cursor = self.db.connection.cursor()
            query = """
                UPDATE users 
                SET tfn = %s, has_health_insurance = %s
                WHERE person_id = %s
            """
            cursor.execute(query, (tfn, has_insurance, person_id))
        
            # Insert the payroll record in the payroll_records table
            query_payroll = """
                INSERT INTO payroll_records (person_id, pay_period_start, pay_period_end, gross_income, tax_paid)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query_payroll, (person_id, pay_period_start, pay_period_end, gross_income, tax_withheld))
        
            self.db.connection.commit()
            cursor.close()
            return f"TFN {tfn} and tax record registered successfully."
        except ValueError as e:
            return str(e)
        except Exception as e:
            return f"An error occurred while registering the TFN: {e}"


    def calculate_tax(self, person_id):
        if not self.db.connection:
            return "Database connection failed. Please try again later."

        cursor = self.db.connection.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE person_id = %s"
        cursor.execute(query, (person_id,))
        user = cursor.fetchone()
        cursor.close()

        if not user or not user['tfn']:
            return "Error: TFN not registered."

        # Convert the database values to float
        annual_income = float(user['annual_income'])
        tax_withheld = float(user['tax_withheld'])
        has_insurance = user['has_health_insurance']

        medicare_levy = self.calculate_medicare_levy(annual_income)
        mls = self.calculate_medicare_levy_surcharge(annual_income, has_insurance)
        total_tax = annual_income * 0.325 + medicare_levy + mls - tax_withheld

        if total_tax > 0:
            self.log_tax_calculation(person_id, annual_income, tax_withheld, total_tax, False)
            return f"You owe additional tax: ${total_tax:.2f}"
        else:
            self.log_tax_calculation(person_id, annual_income, tax_withheld, -total_tax, True)
            return f"You will receive a refund: ${-total_tax:.2f}"

    def calculate_tax_without_tfn(self, person_id, biweekly_wages, tax_withheld, annual_income, has_insurance):
        try:
            # Calculate total net wages based on biweekly wages (assuming 26 pay periods in a year)
            total_net_wages = biweekly_wages * 26
        
            # Validate inputs
            self.validator.validate_wage(total_net_wages)
            self.validator.validate_wage(tax_withheld)
            self.validator.validate_wage(annual_income)

            medicare_levy = self.calculate_medicare_levy(annual_income)
            mls = self.calculate_medicare_levy_surcharge(annual_income, has_insurance)

            # Calculate total tax due based on the inputs
            total_tax_due = (total_net_wages * 0.325) + medicare_levy + mls - tax_withheld

            if total_tax_due > 0:
                self.log_tax_calculation(person_id, annual_income, tax_withheld, total_tax_due, False)
                return f"You owe additional tax: ${total_tax_due:.2f}"
            else:
                self.log_tax_calculation(person_id, annual_income, tax_withheld, -total_tax_due, True)
                return f"You will receive a refund: ${-total_tax_due:.2f}"
        except ValueError as e:
            return str(e)

    def log_tax_calculation(self, person_id, annual_income, tax_withheld, tax_amount, is_refund):
        if not self.db.connection:
            return "Database connection failed. Please try again later."
        try:
            cursor = self.db.connection.cursor()
            query = """
                INSERT INTO tax_history (person_id, calculation_date, annual_income, tax_withheld, tax_amount, is_refund)
                VALUES (%s, NOW(), %s, %s, %s, %s)
            """
            cursor.execute(query, (person_id, annual_income, tax_withheld, tax_amount, is_refund))
            self.db.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Error logging tax calculation: {e}")

    def view_tax_history(self, person_id):
        if not self.db.connection:
            return "Database connection failed. Please try again later."
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = "SELECT * FROM tax_history WHERE person_id = %s ORDER BY calculation_date DESC"
            cursor.execute(query, (person_id,))
            history = cursor.fetchall()
            cursor.close()
            if not history:
                return "No tax history found for this user."
            return history
        except Exception as e:
            return f"Error retrieving tax history: {e}"

    def view_payroll_records(self, person_id=None):
        if not self.db.connection:
            return "Database connection failed. Please try again later."
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            if person_id:
                query = "SELECT * FROM payroll_records WHERE person_id = %s ORDER BY pay_period_start DESC"
                cursor.execute(query, (person_id,))
            else:
                query = "SELECT * FROM payroll_records ORDER BY pay_period_start DESC"
                cursor.execute(query)

            records = cursor.fetchall()
            cursor.close()
            if not records:
                return "No payroll records found."
            return records
        except Exception as e:
            return f"Error retrieving payroll records: {e}"


    def update_profile(self, person_id, new_email=None, new_password=None):
        if not self.db.connection:
            return "Database connection failed. Please try again later."
        try:
            if new_email is not None:
                cursor = self.db.connection.cursor()
                query = "UPDATE users SET email = %s WHERE person_id = %s"
                cursor.execute(query, (new_email, person_id))
                self.db.connection.commit()
                cursor.close()

            if new_password is not None:
                cursor = self.db.connection.cursor()
                query = "UPDATE users SET password = %s WHERE person_id = %s"
                cursor.execute(query, (new_password, person_id))
                self.db.connection.commit()
                cursor.close()

            return "Profile updated successfully."
        except Exception as e:
            return f"Error updating profile: {e}"

    def insert_record(self, table, fields):
        if not self.db.connection:
            return "Database connection failed. Please try again later."
        try:
            cursor = self.db.connection.cursor()
            placeholders = ', '.join(['%s'] * len(fields))
            query = f"INSERT INTO {table} ({', '.join(fields.keys())}) VALUES ({placeholders})"
            cursor.execute(query, list(fields.values()))
            self.db.connection.commit()
            cursor.close()
            return "Record inserted successfully."
        except Exception as e:
            return f"Error inserting record: {e}"

    def update_record(self, table, record_id, updates):
        if not self.db.connection:
            return "Database connection failed. Please try again later."
        try:
            cursor = self.db.connection.cursor()
            set_clause = ', '.join([f"{key} = %s" for key in updates.keys()])
            query = f"UPDATE {table} SET {set_clause} WHERE id = %s"
            cursor.execute(query, list(updates.values()) + [record_id])
            self.db.connection.commit()
            cursor.close()
            return "Record updated successfully."
        except Exception as e:
            return f"Error updating record: {e}"

    def delete_record(self, table, record_id):
        if not self.db.connection:
            return "Database connection failed. Please try again later."
        try:
            cursor = self.db.connection.cursor()
            query = f"DELETE FROM {table} WHERE id = %s"
            cursor.execute(query, (record_id,))
            self.db.connection.commit()
            cursor.close()
            return "Record deleted successfully."
        except Exception as e:
            return f"Error deleting record: {e}"
    


    def calculate_tax_with_pay_period(self, person_id):
        if not self.db.connection:
            return "Database connection failed. Please try again later."
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM payroll_records WHERE person_id = %s
                ORDER BY pay_period_start DESC
            """
            cursor.execute(query, (person_id,))
            records = cursor.fetchall()
            cursor.close()

            if not records:
                return "No payroll records found for this user."

            total_gross_income = sum(record['gross_income'] for record in records)
            total_tax_paid = sum(record['tax_paid'] for record in records)

            medicare_levy = self.calculate_medicare_levy(total_gross_income)
            mls = self.calculate_medicare_levy_surcharge(total_gross_income, self.has_health_insurance(person_id))
            total_tax_due = (total_gross_income * 0.325) + medicare_levy + mls - total_tax_paid

            if total_tax_due > 0:
                self.log_tax_calculation(person_id, total_gross_income, total_tax_paid, total_tax_due, False)
                return f"Total tax due based on payroll records: ${total_tax_due:.2f}"
            else:
                self.log_tax_calculation(person_id, total_gross_income, total_tax_paid, -total_tax_due, True)
                return f"You will receive a refund based on payroll records: ${-total_tax_due:.2f}"
        except Exception as e:
            return f"Error calculating tax: {e}"

    def has_health_insurance(self, person_id):
        if not self.db.connection:
            return False
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = "SELECT has_health_insurance FROM users WHERE person_id = %s"
            cursor.execute(query, (person_id,))
            result = cursor.fetchone()
            cursor.close()

            if result and result['has_health_insurance']:
                return True
            return False
        except Exception as e:
            print(f"Error checking health insurance status: {e}")
            return False


    def add_user(self, person_id, name, email, password, role='user', tfn=None, annual_income=None, tax_withheld=None, has_health_insurance=False):
        if not self.db.connection:
            return "Database connection failed. Please try again later."
        try:
            cursor = self.db.connection.cursor()
            query = """
                INSERT INTO users (person_id, name, email, password, role, tfn, annual_income, tax_withheld, has_health_insurance)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (person_id, name, email, password, role, tfn, annual_income, tax_withheld, has_health_insurance))
            self.db.connection.commit()
            cursor.close()
            return "User added successfully."
        except Exception as e:
            return f"Error adding user: {e}"


    def update_user(self, person_id, new_email=None, new_password=None, new_role=None, new_tfn=None, new_annual_income=None, new_tax_withheld=None, has_health_insurance=None):
        if not self.db.connection:
            return "Database connection failed. Please try again later."
        try:
            # Update fields if new values are provided
            if new_email:
                cursor = self.db.connection.cursor()
                query = "UPDATE users SET email = %s WHERE person_id = %s"
                cursor.execute(query, (new_email, person_id))
                self.db.connection.commit()
                cursor.close()

            if new_password:
                cursor = self.db.connection.cursor()
                query = "UPDATE users SET password = %s WHERE person_id = %s"
                cursor.execute(query, (new_password, person_id))
                self.db.connection.commit()
                cursor.close()

            if new_role:
                cursor = self.db.connection.cursor()
                query = "UPDATE users SET role = %s WHERE person_id = %s"
                cursor.execute(query, (new_role, person_id))
                self.db.connection.commit()
                cursor.close()

            if new_tfn:
                cursor = self.db.connection.cursor()
                query = "UPDATE users SET tfn = %s WHERE person_id = %s"
                cursor.execute(query, (new_tfn, person_id))
                self.db.connection.commit()
                cursor.close()

            if new_annual_income:
                cursor = self.db.connection.cursor()
                query = "UPDATE users SET annual_income = %s WHERE person_id = %s"
                cursor.execute(query, (new_annual_income, person_id))
                self.db.connection.commit()
                cursor.close()

            if new_tax_withheld:
                cursor = self.db.connection.cursor()
                query = "UPDATE users SET tax_withheld = %s WHERE person_id = %s"
                cursor.execute(query, (new_tax_withheld, person_id))
                self.db.connection.commit()
                cursor.close()

            if has_health_insurance is not None:
                cursor = self.db.connection.cursor()
                query = "UPDATE users SET has_health_insurance = %s WHERE person_id = %s"
                cursor.execute(query, (has_health_insurance, person_id))
                self.db.connection.commit()
                cursor.close()

            return "User updated successfully."
        except Exception as e:
            return f"Error updating user: {e}"


    def delete_user(self, person_id):
        if not self.db.connection:
            return "Database connection failed. Please try again later."
        try:
            cursor = self.db.connection.cursor()
            query = "DELETE FROM users WHERE person_id = %s"
            cursor.execute(query, (person_id,))
            self.db.connection.commit()
            cursor.close()
            return "User deleted successfully."
        except Exception as e:
            return f"Error deleting user: {e}"

    def view_all_tax_history(self):
        if not self.db.connection:
            return "Database connection failed. Please try again later."
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = "SELECT * FROM tax_history ORDER BY calculation_date DESC"
            cursor.execute(query)
            history = cursor.fetchall()
            cursor.close()
            if not history:
                return "No tax history found."
            return history
        except Exception as e:
            return f"Error retrieving tax history: {e}"

    def search_users(self, person_id=None, email=None, role=None):
        if not self.db.connection:
            return "Database connection failed. Please try again later."
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE TRUE"
            params = []

            if person_id:
                query += " AND person_id = %s"
                params.append(person_id)

            if email:
                query += " AND email = %s"
                params.append(email)

            if role:
                query += " AND role = %s"
                params.append(role)

            cursor.execute(query, params)
            users = cursor.fetchall()
            cursor.close()
            if not users:
                return "No users found matching the criteria."
            return users
        except Exception as e:
            return f"Error searching users: {e}"


    def export_users_to_csv(self, file_path="exported_users.csv"):
        if not self.db.connection:
            return "Database connection failed. Please try again later."
        try:
            # If the file path is a directory, set a default filename
            if os.path.isdir(file_path):
                file_path = os.path.join(file_path, "exported_users.csv")

            cursor = self.db.connection.cursor(dictionary=True)
            query = "SELECT * FROM users"
            cursor.execute(query)
            users = cursor.fetchall()
            cursor.close()

            if not users:
                return "No user data found."

            # Export data to CSV
            with open(file_path, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=users[0].keys())
                writer.writeheader()
                writer.writerows(users)
        
            return f"User data exported successfully to {file_path}."
        except Exception as e:
            return f"Error exporting user data: {e}"


    def export_tax_history_to_csv(self, file_path="exported_tax_history.csv"):
        if not self.db.connection:
            return "Database connection failed. Please try again later."
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = "SELECT * FROM tax_history"
            cursor.execute(query)
            history = cursor.fetchall()
            cursor.close()

            if not history:
                return "No tax history data found."

            # Export data to CSV
            with open(file_path, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=history[0].keys())
                writer.writeheader()
                writer.writerows(history)
        
            return f"Tax history data exported successfully to {file_path}."
        except Exception as e:
            return f"Error exporting tax history data: {e}"
        
    def admin_view_users(self):
        users = self.db.view_all_users()
        return users

    def admin_view_schema(self, table_name):
        schema = self.db.view_schema(table_name)
        return schema

    def calculate_medicare_levy(self, annual_income):
        return annual_income * 0.02

    def calculate_medicare_levy_surcharge(self, annual_income, has_insurance):
        if not has_insurance and annual_income > 90000:
            if annual_income <= 105000:
                return annual_income * 0.01
            elif annual_income <= 140000:
                return annual_income * 0.0125
            else:
                return annual_income * 0.015
        return 0
