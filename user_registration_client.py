import Pyro5.api

def main():
    tax_server = Pyro5.api.Proxy("PYRONAME:Aus.taxcalculator")
    print("Welcome to the User Registration Portal")

    # Collect user information
    person_id = input("Enter your Person ID: ").strip()
    password = input("Enter your password: ").strip()
    name = input("Enter your name (optional): ").strip() or None
    email = input("Enter your email (optional): ").strip() or None
    tfn = input("Enter your TFN (optional, leave blank if you don't have one): ").strip() or None

    # Call the server function to register the user
    response = tax_server.register_user(person_id, password, name, email, tfn)
    print(response)

if __name__ == "__main__":
    main()
