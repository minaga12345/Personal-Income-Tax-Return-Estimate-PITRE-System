# test_db_connection.py
from tax_database import TaxDatabaseServer

db = TaxDatabaseServer()
if db.connection:
    print("Database connection successful")
else:
    print("Database connection failed")
