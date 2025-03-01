import Pyro5.api
from tax_calculator import TaxCalculator

def main():
    daemon = Pyro5.api.Daemon()
    ns = Pyro5.api.locate_ns()
    uri = daemon.register(TaxCalculator)
    ns.register("Aus.taxcalculator", uri)
    print("Server is running with database integration...")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
