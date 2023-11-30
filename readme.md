SUPERPY
Welcome to the usage guide of SuperPy!

SuperPy is a Command Line Interface for managing the inventory of a supermarket. It is written in Python and utilizes CSV files to store data.

Read the welcoming message when you run the file to get a quick start. 

Usage Examples
Buying
To register a purchase, use the following command:

    python super.py buy --product-name <Product Name> --price <Price per Unit> --expiration-date <Expiration Date>

Examples:
    python super.py buy --product-name Banana --price 10 --expiration-date 2023-06-18

The action will be recorded in a dedicaded CSV file; bought.csv 

Selling
To register a sale, use the following command:

    python super.py sell --product-name <Product Name> --price <Price> 

Example:
    python super.py sell --product-name Apple --price 8 

The action will be recorded in a dedicaded CSV file; sold.csv

Advancing Time
To advance or reset the current date, use the following command:

    python super.py advance-time <days> 
    python super.py advance-time --reset
    python super.py advance-time --set-date <Date>

Examples:
    python super.py advance-time 20
    python super.py advance-time --reset
    python super.py advance-time --set-date 2023-12-12

Reporting
There are three types of reports: Inventory, Revenue, and Profit.

Inventory Report
To generate an inventory report for a certain moment in time, use the following command:

    python super.py report inventory --now
    python super.py report inventory --yesterday
    python super.py report inventory --date <Date> 

Examples:
    python super.py report inventory --now
    python super.py report inventory --yesterday
    python super.py report inventory --date 2023-04-17

Revenue Report
To generate revenue reports for a certain period, use the following command:

    python super.py report-revenue --today
    python super.py report-revenue --yesterday
    python super.py report-revenue --date <Date>
    python super.py report-revenue --month <Year-Month>
    python super.py report-revenue --year <Year>

Examples:
    python super.py report-revenue --today
    python super.py report-revenue --yesterday
    python super.py report-revenue --date 2023-11-28
    python super.py report-revenue --month 2023-11
    python super.py report-revenue --year 2023

Profit Report
To generate a profit report for a certain period, use the following command:

    python super.py report-profit --today
    python super.py report-profit --yesterday
    python super.py report-profit --date <Date>

Examples:
    python super.py report-profit --today
    python super.py report-profit --yesterday
    python super.py report-profit --date 2023-11-27

Additional Notes
All input data is stored in CSV files: bought.csv & sold.csv

Advanced time impacts the current date for all actions. 
