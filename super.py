# Imports
import argparse
import csv
from datetime import datetime, date, timedelta
from rich.console import Console
from rich.table import Table
from rich.text import Text
import os
import matplotlib.pyplot as plt

# Do not change these lines.
__winc_id__ = "a2bc36ea784242e4989deb157d527ba0"
__human_name__ = "superpy"

# Your code below this line.
TIME_FILE = "current_time.txt"  # Filename for time

def get_current_time():
    """
    Retrieves the current date from the 'current_time.txt' file or uses the current system date if the file doesn't exist.
    """
    try:
        with open(TIME_FILE, "r") as time_file:
            current_time_str = time_file.read().strip()
            return datetime.strptime(current_time_str, "%Y-%m-%d").date()
    except FileNotFoundError:
        # If the file doesn't exist, use current time
        return datetime.now().date()

def save_current_time(current_time):
    """
    Saves the provided current_time to the 'current_time.txt' file in the format '%Y-%m-%d'.
    """
    with open(TIME_FILE, "w") as time_file:
        time_file.write(current_time.strftime("%Y-%m-%d"))

def is_product_sold(bought_id):
    """
    Checks if a product with the given bought_id has been sold by searching in the 'sold.csv' file.
    """
    with open("sold.csv", mode="r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["bought_id"] == bought_id:
                return True
    return False

def sell_product(product_name, sell_price):
    """
    Sells a product by checking if it's in stock, not expired, and not already sold.
    If conditions are met, records the sale in 'sold.csv'.
    """
    # Check if product is bought
    with open("bought.csv", mode="r") as csvfile:
        reader = csv.DictReader(csvfile)
        found_products = []

        for row in reader:
            if row["product_name"] == product_name:
                found_products.append(row)

        if not found_products:
            print(f"ERROR: Product '{product_name}' not in stock.")
            return

        # Check if any of the found products are already sold
        for found_product in found_products:
            bought_id = found_product["id"]
            if not is_product_sold(bought_id):
                # Check if product is expired
                expiration_date = datetime.strptime(found_product["expiration_date"], "%Y-%m-%d").date()
                current_date = get_current_time()

                if expiration_date < current_date:
                    print(f"ERROR: Product '{product_name}' has expired and cannot be sold.")
                    return

                # Execute sale
                sell_date = current_date.strftime("%Y-%m-%d")

                # Write to sold.csv
                file_exists = False
                fieldnames = ["id", "bought_id", "sell_date", "sell_price"]
                try:
                    # Try to open file to check if it exists
                    with open("sold.csv", "r") as csvfile:
                        reader = csv.DictReader(csvfile)
                        if reader.fieldnames == fieldnames:
                            file_exists = True
                except FileNotFoundError:
                    pass

                # Open file in the right mode
                with open("sold.csv", mode="a", newline="") as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    # Write the header if file does not exist or is empty
                    if not file_exists:
                        writer.writeheader()

                    # Generate unique ID for sale
                    sell_id = int(datetime.now().timestamp())

                    # Write the data
                    writer.writerow({
                        "id": sell_id,
                        "bought_id": bought_id,
                        "sell_date": sell_date,
                        "sell_price": sell_price
                    })

                print(f"OK: Product '{product_name}' (ID: {bought_id}) sold successfully for {sell_price}.")
                return

        print(f"ERROR: Product '{product_name}' has already been sold.")

def get_inventory_at_date(products, target_date):
    """
    Retrieves a list of products from 'bought.csv' that are not sold and were bought on or before the target_date.
    """
    inventory = []

    for product in products:
        # Check if product is not sold
        bought_id = product["id"]
        buy_date = datetime.strptime(product["buy_date"], "%Y-%m-%d").date()
        
        if not is_product_sold(bought_id) and buy_date <= target_date:
            inventory.append(product)

    return inventory

def report_inventory(args):
    """
    Generates a Rich-table displaying the inventory at a specified date based on the 'bought.csv' file.
    """
    # Read bought products
    with open("bought.csv", mode="r") as csvfile:
        reader = csv.DictReader(csvfile)
        products = list(reader)

    # Define date by arguments
    if args.now:
        current_date = get_current_time()
    elif args.yesterday:
        current_date = get_current_time() - timedelta(days=1)
    elif args.date:
        current_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    else:
        current_date = get_current_time()  # Default naar huidige datum als geen datum is opgegeven

    # Get relevant inventory
    inventory = get_inventory_at_date(products, current_date)

    # Use Rich for better output
    console = Console()

    if not inventory:
        console.print(f"No inventory at {current_date.strftime('%Y-%m-%d')}.")
    else:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Product Name", style="dim", width=15)
        table.add_column("Count", justify="center", style="dim")
        table.add_column("Buy Price", justify="center", style="dim")
        table.add_column("Expiration Date", style="dim")
        table.add_column("Buy Date", style="dim")

        for product in inventory:
            product_name = product["product_name"]
            buy_price = product["buy_price"]
            expiration_date = product["expiration_date"]
            buy_date = product["buy_date"]

            table.add_row(product_name, "1", buy_price, expiration_date, buy_date)

        console.print(table)

def get_sold_products_on_date(target_date):
    """
    Retrieves a list of products sold on a specific target_date from 'sold.csv'.
    """
    sold_products = []

    with open("sold.csv", mode="r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sell_date = datetime.strptime(row["sell_date"], "%Y-%m-%d").date()

            if sell_date == target_date:
                sold_products.append(row)

    return sold_products

def get_sold_products_in_period(end_date):
    """
    Retrieves a list of products sold within a specific period until the end_date from 'sold.csv'.
    """
    sold_products = []

    with open("sold.csv", mode="r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sell_date = datetime.strptime(row["sell_date"], "%Y-%m-%d").date()

            if sell_date == end_date:
                sold_products.append(row)

    return sold_products

def get_date_range_description(end_date):
    """
    Returns a formatted string description for a given end_date, typically used for displaying in reports.
    """
    return f"{end_date.year}" if end_date.day == 1 and end_date.month == 1 else end_date.strftime('%Y-%m-%d')

def get_sold_products_in_month(target_month):
    """
    Retrieves a list of products sold in a specific target_month from 'sold.csv'.
    """
    sold_products = []

    with open("sold.csv", mode="r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sell_date = datetime.strptime(row["sell_date"], "%Y-%m-%d").date()

            if sell_date.year == target_month.year and sell_date.month == target_month.month:
                sold_products.append(row)

    return sold_products

def get_sold_products_in_year(target_year):
    """
    Retrieves a list of products sold in a specific target_year from 'sold.csv'.
    """
    sold_products = []

    with open("sold.csv", mode="r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sell_date = datetime.strptime(row["sell_date"], "%Y-%m-%d").date()

            if sell_date.year == target_year.year:
                sold_products.append(row)

    return sold_products

def report_revenue(args):
    """
    Generates revenue reports based on specified time periods and displays the results using matplotlib.
    """
    # Define date by arguments
    if args.today:
        target_date = get_current_time()
    elif args.yesterday:
        target_date = get_current_time() - timedelta(days=1)
    elif args.date:
        target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    elif args.month:
        # Define first day of given moment
        target_date = datetime.strptime(args.month, "%Y-%m").date()
        # Define last day of month by going to first day of next month and then one day back
        target_date = (target_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif args.year:
        # Define first day of given year
        target_date = datetime.strptime(args.year, "%Y").date().replace(month=1, day=1)
        # Define last day of year by going to first day of next year and then one day back
        target_date = (target_date.replace(year=target_date.year + 1) - timedelta(days=1))
    else:
        target_date = get_current_time()  # Default to current date if not given any

    # Get sold products in given period
    sold_products = (
        get_sold_products_on_date(target_date) if args.date else
        get_sold_products_in_period(target_date)
    )

    # Calculate total revenue en show sold products
    total_revenue = sum(float(product["sell_price"]) for product in sold_products)

    # Maak lege lijsten voor productnamen en bijbehorende omzetten
    product_names = []
    revenues = []

    for product in sold_products:
        bought_id = product["bought_id"]
        sell_price = float(product["sell_price"])

        # Find the corresponding product in bought.csv
        with open("bought.csv", mode="r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["id"] == bought_id:
                    product_name = row["product_name"]
                    product_names.append(product_name)
                    revenues.append(sell_price)
                    break

    # Create a bar chart of the revenue per product
    plt.bar(product_names, revenues, color='blue')
    plt.xlabel('Producten')
    plt.ylabel('Omzet')
    plt.title(f'Omzet per product op {target_date.strftime("%Y-%m-%d")}')
    plt.show()

    # Show total revenue
    console = Console()
    console.print(f"Total revenue of {target_date.strftime('%Y-%m-%d')}: [bold green]{total_revenue}[/bold green]")

def report_profit(args):
    """
    Generates profit reports based on specified time periods and displays the results using Rich console tables.
    """
    # Define current date by arguments
    if args.today:
        target_date = get_current_time()
    elif args.yesterday:
        target_date = get_current_time() - timedelta(days=1)
    elif args.date:
        specified_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        target_date = specified_date
    elif args.month:
        specified_date = datetime.strptime(args.month, "%Y-%m").date()
        target_date = specified_date
    elif args.year:
        specified_date = datetime.strptime(args.year, "%Y").date()
        target_date = specified_date
    else:
        target_date = get_current_time()  # Default to current date when no date is given

    # Get sold products in given period
    sold_products = (
        get_sold_products_on_date(target_date) if args.date else
        get_sold_products_in_period(target_date)
    )

    # Calculate the total profit and display a summary of sold products with profit per product
    total_profit = 0

    # Use Rich for better output
    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Product Name", style="dim", width=15)
    table.add_column("Sold Price", justify="center", style="dim")
    table.add_column("Cost", justify="center", style="dim")
    table.add_column("Profit", style="dim")

    for product in sold_products:
        bought_id = product["bought_id"]
        sell_price = float(product["sell_price"])

        # Find the corresponding product in bought.csv
        with open("bought.csv", mode="r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["id"] == bought_id:
                    product_name = row["product_name"]
                    buy_price = float(row["buy_price"])

                    # Calculate profit for this product
                    profit = sell_price - buy_price
                    total_profit += profit

                    # Add data to Rich-table
                    table.add_row(product_name, f"{sell_price:.2f}", f"{buy_price:.2f}", f"{profit:.2f}")
                    break

    console.print(table)

    console.print(f"Total profit: [bold green]{total_profit:.2f}[/bold green]")


def main():
    """
    The main entry point for the SuperPy program, responsible for parsing command-line arguments and executing corresponding commands.
    """
    console = Console()

    # Check if the welcome message has already been displayed
    welcome_file = "welcome_shown.txt"

    if not os.path.exists(welcome_file):
        # Welcome message
        console.print("[bold cyan]=== SuperPy - Inventory Management System ===[/bold cyan]")
        console.print("[italic]Welcome to SuperPy, your friendly neighborhood inventory manager![/italic]")
        console.print()

        # Usage possibilities
        console.print("[underline]Usage Examples:[/underline]")
        console.print("  - To buy a product:")
        console.print("    [cyan]$ python super.py buy --product-name orange --price 0.8 --expiration-date 2022-01-01[/cyan]")
        console.print("  - To sell a product:")
        console.print("    [cyan]$ python super.py sell --product-name orange --price 2[/cyan]")
        console.print("  - To view current inventory:")
        console.print("    [cyan]$ python super.py inventory --now[/cyan]")
        console.print("  - To advance time by 2 days:")
        console.print("    [cyan]$ python super.py advance-time 2[/cyan]")
        console.print("  - To set the date:")
        console.print("    [cyan]$ python super.py advance-time --set-date 2023-01-31[/cyan]")
        console.print()

        # Functions
        console.print("[underline]Key Functions:[/underline]")
        console.print("  - [bold]buy:[/bold] Add a new product to the inventory.")
        console.print("  - [bold]sell:[/bold] Sell a product from the inventory.")
        console.print("  - [bold]inventory:[/bold] View the current or past inventory.")
        console.print("  - [bold]advance-time:[/bold] Move the current date forward or reset it.")
        console.print("  - [bold]report-revenue:[/bold] Generate revenue reports for specific periods.")
        console.print("  - [bold]report-profit:[/bold] Generate profit reports for specific periods.")
        console.print()

        # Indicate that the welcome message has been displayed
        with open(welcome_file, "w") as file:
            file.write("Delete this text file if you want to see the welcome message again when you run the beautiful Superpy tool")

    global current_time  # Make the global variable available for modifications.

    current_time = get_current_time()  # Get current time

    parser = argparse.ArgumentParser(description="SuperPy - Inventory Management System")

    # Subparsers 
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Buy command
    buy_parser = subparsers.add_parser("buy", help="Buy products")
    buy_parser.add_argument("--product-name", required=True, help="Name of the product")
    buy_parser.add_argument("--price", type=float, required=True, help="Price of the product")
    buy_parser.add_argument("--expiration-date", required=True, help="Expiration date of the product (format: YYYY-MM-DD)")

    # Sell command
    sell_parser = subparsers.add_parser("sell", help="Sell products")
    sell_parser.add_argument("--product-name", required=True, help="Name of the product")
    sell_parser.add_argument("--price", type=float, required=True, help="Price at which the product is sold")

    # Inventory command
    inventory_parser = subparsers.add_parser("inventory", help="View inventory")
    inventory_parser.add_argument("--now", action="store_true", help="View current inventory")
    inventory_parser.add_argument("--yesterday", action="store_true", help="View inventory as of yesterday")
    inventory_parser.add_argument("--date", help="Inventory for a specific date (format: YYYY-MM-DD)")

    # Report revenue command
    revenue_parser = subparsers.add_parser("report-revenue", help="Generate revenue reports")
    revenue_parser.add_argument("--yesterday", action="store_true", help="Revenue from yesterday")
    revenue_parser.add_argument("--today", action="store_true", help="Revenue so far today")
    revenue_parser.add_argument("--date", help="Revenue for a specific day (format: YYYY-MM-DD)")
    revenue_parser.add_argument("--month", help="Revenue for a specific month (format: YYYY-MM)")
    revenue_parser.add_argument("--year", help="Revenue for a specific year (format: YYYY)")

    # Advance-time command
    advance_time_parser = subparsers.add_parser("advance-time", help="Advance or reset the current date")
    advance_time_parser.add_argument("days", type=int, default=0, nargs="?", help="Number of days to advance (default: 0)")
    advance_time_parser.add_argument("--reset", action="store_true", help="Reset the date to the current date")
    advance_time_parser.add_argument("--set-date", help="Set a specific date (format: YYYY-MM-DD)")

    # Report profit command
    profit_parser = subparsers.add_parser("report-profit", help="Generate profit reports")
    profit_parser.add_argument("--today", action="store_true", help="Profit so far today")
    profit_parser.add_argument("--yesterday", action="store_true", help="Yesterday's profit")
    profit_parser.add_argument("--date", help="Profit for a specific date (format: YYYY-MM-DD)")

    args = parser.parse_args()

    if args.command == "advance-time":
        if args.reset:
            # Reset to current date
            current_time = datetime.now().date()
            save_current_time(current_time)
            print(f"OK: Date reset to the current date ({current_time.strftime('%Y-%m-%d')}).")
        elif args.set_date:
            # Set a specific date
            try:
                current_time = datetime.strptime(args.set_date, "%Y-%m-%d").date()
                save_current_time(current_time)
                print(f"OK: Date set to {args.set_date}.")
            except ValueError:
                print("ERROR: Invalid date format. Please use the format YYYY-MM-DD.")
        else:
            # Advance date
            days_to_advance = args.days
            current_time += timedelta(days=days_to_advance)
            save_current_time(current_time)
            print(f"OK: Time advanced by {days_to_advance} days. Current date is now {current_time.strftime('%Y-%m-%d')}.")

        return

    if args.command == "buy":
        # Generate unique ID
        product_id = int(datetime.now().timestamp())

        # Format date 
        buy_date = current_time.strftime("%Y-%m-%d")

        # Initializing product_name with a default value
        product_name = ""

        try:
            # Extracting values from the arguments
            product_name = args.product_name
            buy_price = args.price
            expiration_date = args.expiration_date

            # Write to bought.csv
            with open("bought.csv", mode="a", newline="") as csvfile:
                fieldnames = ["id", "product_name", "buy_date", "buy_price", "expiration_date"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write header if file is empty
                if csvfile.tell() == 0:
                    writer.writeheader()

                # Write data
                writer.writerow({
                    "id": product_id,
                    "product_name": product_name,
                    "buy_date": buy_date,
                    "buy_price": buy_price,
                    "expiration_date": expiration_date
                })

            # Show summary
            summary_message = f"Product '{product_name}' (ID: {product_id}) bought for {buy_price} on {buy_date}. Expires on {expiration_date}."
            print("OK")
            print(summary_message)

        except Exception as e:
            print(f"ERROR: {e}")


    if args.command == "sell":
        # Extracting values from the arguments
        product_name = args.product_name
        sell_price = args.price

        # Attempt to sell the product
        sell_product(product_name, sell_price)

    if args.command == "inventory":
        report_inventory(args)

    if args.command == "report-revenue":
        report_revenue(args)

    if args.command == "report-profit":
        report_profit(args)

if __name__ == "__main__":
    main()