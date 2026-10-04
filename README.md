\# PowerPulse ⚡



\## Electricity Usage, Billing \& Consumption Analytics System



PowerPulse is a Python-based electricity billing and consumption analytics system. It calculates electricity usage from meter readings, calculates the bill using predefined tariff rates, stores bill records in an SQLite database, and provides consumption analysis and graphical visualization.



\## Features



\- Calculate electricity units from previous and current meter readings

\- Calculate electricity bills using fixed tariff rates

\- Store bill records using SQLite

\- Prevent duplicate bills for the same customer and month

\- View complete bill history

\- Delete selected bill records

\- Analyze total and average electricity consumption

\- Identify high-usage records

\- View monthly electricity usage graphs

\- View monthly electricity bill graphs

\- Search for a particular customer

\- View customer-wise bill records

\- View customer-wise usage and bill graphs

\- Delete a selected customer bill



\## Technologies Used



\- \*\*Programming Language:\*\* Python

\- \*\*GUI:\*\* Tkinter

\- \*\*Data Visualization:\*\* Matplotlib

\- \*\*Database:\*\* SQLite



\## How It Works



1\. Enter the customer name.

2\. Select the month.

3\. Enter the previous meter reading.

4\. Enter the current meter reading.

5\. The system calculates the units consumed.

6\. The electricity bill is calculated using predefined tariff rates.

7\. The bill record is stored in the SQLite database.

8\. Users can view bill history and delete selected records.

9\. Users can analyze electricity consumption.

10\. Users can view monthly and customer-wise graphs.



\## Tariff Rates



\- Up to 100 units: ₹3 per unit

\- 101 to 200 units: ₹5 per unit

\- Above 200 units: ₹7 per unit



\## Project Structure



```text

PowerPulse/

│

├── powerpulse.py

├── README.md

└── .gitignore

