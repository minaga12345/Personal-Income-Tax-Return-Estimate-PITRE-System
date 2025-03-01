import re
from datetime import datetime

class Validator:
    def validate_tfn(self, tfn):
        if re.fullmatch(r'\d{8,9}', str(tfn)):
            return True
        raise ValueError("Invalid TFN: TFN must be an 8 or 9-digit number.")

    def validate_date(self, date_str):
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}', date_str):
            return True
        raise ValueError("Invalid date format: Date must be in the format YYYY-MM-DD.")

    def validate_wage(self, wage):
        return self.validate_positive_number(wage, "wage")

    def validate_income(self, income):
        return self.validate_positive_number(income, "income")

    def validate_tax(self, tax):
        return self.validate_positive_number(tax, "tax amount")

    def validate_positive_number(self, value, field_name="value"):
        try:
            number = float(value)
            if number > 0:
                return True
            raise ValueError(f"Invalid {field_name}: It must be a positive number.")
        except ValueError:
            raise ValueError(f"Invalid {field_name}: It must be a numeric value.")

    def validate_pay_period(self, start_date, end_date):
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            if end >= start:
                return True
            raise ValueError("Invalid pay period: End date cannot be earlier than the start date.")
        except ValueError:
            raise ValueError("Invalid pay period: Ensure both dates are in the format YYYY-MM-DD.")

    def validate_boolean_input(self, value):
        if value.lower() in ['yes', 'no']:
            return True
        raise ValueError("Invalid input: Please enter 'yes' or 'no'.")
