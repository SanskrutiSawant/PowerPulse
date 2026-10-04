import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# =========================================================
# DATABASE
# =========================================================

connection = sqlite3.connect("powerpulse.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    month TEXT NOT NULL,
    previous REAL NOT NULL,
    current REAL NOT NULL,
    units REAL NOT NULL,
    bill REAL NOT NULL,
    UNIQUE(name, month)
)
""")

connection.commit()


# =========================================================
# BILL CALCULATION
# =========================================================

def calculate_bill(units):
    if units <= 100:
        return units * 3
    elif units <= 200:
        return units * 5
    else:
        return units * 7


# =========================================================
# ADD BILL
# =========================================================

def add_bill():
    name = name_entry.get().strip()
    month = month_combo.get()
    previous_text = previous_entry.get().strip()
    current_text = current_entry.get().strip()

    # Check empty fields
    if name == "" or month == "" or previous_text == "" or current_text == "":
        messagebox.showwarning(
            "Missing Information",
            "Please enter all bill details."
        )
        return

    # Check numeric readings
    try:
        previous = float(previous_text)
        current = float(current_text)
    except ValueError:
        messagebox.showerror(
            "Invalid Reading",
            "Meter readings must be numbers."
        )
        return

    # Check negative values
    if previous < 0 or current < 0:
        messagebox.showerror(
            "Invalid Reading",
            "Meter readings cannot be negative."
        )
        return

    # Check meter reading order
    if current < previous:
        messagebox.showerror(
            "Invalid Reading",
            "Current reading cannot be less than previous reading."
        )
        return

    # Prevent duplicate customer + month
    cursor.execute("""
        SELECT id
        FROM bills
        WHERE LOWER(name) = LOWER(?) AND month = ?
    """, (name, month))

    if cursor.fetchone() is not None:
        messagebox.showwarning(
            "Duplicate Bill",
            f"A bill for {name} in {month} already exists."
        )
        return

    # Calculate units and bill
    units = current - previous
    bill = calculate_bill(units)

    # Save to database
    cursor.execute("""
        INSERT INTO bills
        (name, month, previous, current, units, bill)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, month, previous, current, units, bill))

    connection.commit()

    # Display result
    result_label.config(
        text=f"Units Used: {units:.0f} units\n"
             f"Bill Amount: ₹{bill:.2f}"
    )

    messagebox.showinfo(
        "Bill Saved",
        f"Bill calculated successfully.\n\n"
        f"Customer: {name}\n"
        f"Month: {month}\n"
        f"Units Used: {units:.0f}\n"
        f"Bill Amount: ₹{bill:.2f}"
    )


# =========================================================
# BILL HISTORY
# =========================================================

def view_history():

    history_window = tk.Toplevel(root)
    history_window.title("PowerPulse - Bill History")
    history_window.geometry("900x500")
    history_window.configure(bg="#f4f7fb")

    tk.Label(
        history_window,
        text="Bill History",
        font=("Arial", 18, "bold"),
        bg="#f4f7fb",
        fg="#1f3c88"
    ).pack(pady=(15, 5))

    tk.Label(
        history_window,
        text="View and delete saved electricity bills",
        font=("Arial", 10),
        bg="#f4f7fb",
        fg="#666666"
    ).pack(pady=(0, 10))

    frame = tk.Frame(
        history_window,
        bg="#f4f7fb"
    )
    frame.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=5
    )

    columns = (
        "id",
        "name",
        "month",
        "previous",
        "current",
        "units",
        "bill"
    )

    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        height=15
    )

    headings = {
        "id": "ID",
        "name": "Customer",
        "month": "Month",
        "previous": "Previous",
        "current": "Current",
        "units": "Units",
        "bill": "Bill (₹)"
    }

    widths = {
        "id": 50,
        "name": 180,
        "month": 100,
        "previous": 100,
        "current": 100,
        "units": 80,
        "bill": 100
    }

    for column in columns:
        tree.heading(
            column,
            text=headings[column]
        )

        tree.column(
            column,
            width=widths[column],
            anchor="center"
        )

    scrollbar = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(
        yscrollcommand=scrollbar.set
    )

    tree.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    # Load records
    def load_history():
        for item in tree.get_children():
            tree.delete(item)

        cursor.execute("""
            SELECT id, name, month, previous, current, units, bill
            FROM bills
            ORDER BY id DESC
        """)

        rows = cursor.fetchall()

        for row in rows:
            tree.insert(
                "",
                tk.END,
                values=(
                    row[0],
                    row[1],
                    row[2],
                    f"{row[3]:.0f}",
                    f"{row[4]:.0f}",
                    f"{row[5]:.0f}",
                    f"₹{row[6]:.2f}"
                )
            )

    load_history()

    # Delete selected record
    def delete_selected_bill():

        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select Bill",
                "Please select a bill to delete."
            )
            return

        values = tree.item(
            selected[0],
            "values"
        )

        bill_id = values[0]
        customer = values[1]
        month = values[2]

        answer = messagebox.askyesno(
            "Confirm Delete",
            f"Do you want to delete the bill for\n"
            f"{customer} - {month}?"
        )

        if answer:

            cursor.execute(
                "DELETE FROM bills WHERE id = ?",
                (bill_id,)
            )

            connection.commit()

            tree.delete(selected[0])

            messagebox.showinfo(
                "Deleted",
                "The selected bill was deleted successfully."
            )

    tk.Button(
        history_window,
        text="Delete Selected Bill",
        command=delete_selected_bill,
        font=("Arial", 11, "bold"),
        bg="#d9534f",
        fg="white",
        activebackground="#c9302c",
        activeforeground="white",
        padx=15,
        pady=8,
        relief="flat"
    ).pack(pady=12)


# =========================================================
# CONSUMPTION ANALYSIS
# =========================================================

def consumption_analysis():

    cursor.execute("""
        SELECT COUNT(*), SUM(units), AVG(units)
        FROM bills
    """)

    count, total_units, average_units = cursor.fetchone()

    if count == 0:
        messagebox.showinfo(
            "Consumption Analysis",
            "No bill records are available yet."
        )
        return

    cursor.execute("""
        SELECT name, month, units
        FROM bills
        ORDER BY units DESC
    """)

    rows = cursor.fetchall()

    high_usage = []

    for row in rows:
        if row[2] > average_units:
            high_usage.append(row)

    message = (
        f"Total Bill Records: {count}\n"
        f"Total Units Consumed: {total_units:.0f}\n"
        f"Average Consumption: {average_units:.2f} units\n\n"
        f"High Usage Records: {len(high_usage)}"
    )

    if high_usage:

        message += "\n\nHigh Usage:\n"

        for name, month, units in high_usage:
            message += (
                f"{name} - {month}: "
                f"{units:.0f} units\n"
            )

    messagebox.showinfo(
        "Consumption Analysis",
        message
    )


# =========================================================
# MONTHLY GRAPHS
# =========================================================

def view_monthly_graphs():

    cursor.execute("""
        SELECT month, SUM(units), SUM(bill)
        FROM bills
        GROUP BY month
        ORDER BY CASE month
            WHEN 'January' THEN 1
            WHEN 'February' THEN 2
            WHEN 'March' THEN 3
            WHEN 'April' THEN 4
            WHEN 'May' THEN 5
            WHEN 'June' THEN 6
            WHEN 'July' THEN 7
            WHEN 'August' THEN 8
            WHEN 'September' THEN 9
            WHEN 'October' THEN 10
            WHEN 'November' THEN 11
            WHEN 'December' THEN 12
        END
    """)

    rows = cursor.fetchall()

    if not rows:
        messagebox.showinfo(
            "Monthly Graphs",
            "No bill records are available to create graphs."
        )
        return

    months = [row[0] for row in rows]
    units = [row[1] for row in rows]
    bills = [row[2] for row in rows]

    graph_window = tk.Toplevel(root)
    graph_window.title(
        "PowerPulse - Monthly Graphs"
    )
    graph_window.geometry("1000x780")
    graph_window.configure(bg="#f4f7fb")

    tk.Label(
        graph_window,
        text="Monthly Electricity Usage & Bill",
        font=("Arial", 18, "bold"),
        bg="#f4f7fb",
        fg="#1f3c88"
    ).pack(pady=(12, 3))

    tk.Label(
        graph_window,
        text="Monthly totals from all saved customer bills",
        font=("Arial", 10),
        bg="#f4f7fb",
        fg="#666666"
    ).pack(pady=(0, 8))

    figure, axes = plt.subplots(
        2,
        1,
        figsize=(9, 7)
    )

    # Graph 1 - Units
    axes[0].bar(
        months,
        units,
        color="#2E86DE",
        edgecolor="#1f3c88"
    )

    axes[0].set_title(
        "Monthly Electricity Consumption",
        fontweight="bold"
    )

    axes[0].set_xlabel("Month")
    axes[0].set_ylabel("Units Consumed")

    axes[0].grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )

    # Graph 2 - Bill
    axes[1].bar(
        months,
        bills,
        color="#28B463",
        edgecolor="#1b7f3a"
    )

    axes[1].set_title(
        "Monthly Electricity Bill",
        fontweight="bold"
    )

    axes[1].set_xlabel("Month")
    axes[1].set_ylabel("Bill Amount (₹)")

    axes[1].grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )

    figure.tight_layout()

    canvas = FigureCanvasTkAgg(
        figure,
        master=graph_window
    )

    canvas.draw()

    canvas.get_tk_widget().pack(
        fill="both",
        expand=True,
        padx=15,
        pady=10
    )

    def close_graph():

        plt.close(figure)
        graph_window.destroy()

    tk.Button(
        graph_window,
        text="Close",
        command=close_graph,
        font=("Arial", 11, "bold"),
        bg="#1f3c88",
        fg="white",
        activebackground="#17306d",
        activeforeground="white",
        padx=20,
        pady=7,
        relief="flat"
    ).pack(pady=10)


# =========================================================
# CUSTOMER ANALYSIS
# =========================================================

def customer_analysis():

    customer_window = tk.Toplevel(root)
    customer_window.title(
        "PowerPulse - Customer Analysis"
    )
    customer_window.geometry("950x700")
    customer_window.configure(bg="#f4f7fb")

    tk.Label(
        customer_window,
        text="Customer Analysis",
        font=("Arial", 18, "bold"),
        bg="#f4f7fb",
        fg="#1f3c88"
    ).pack(pady=(15, 3))

    tk.Label(
        customer_window,
        text="Search a customer to view, analyze and delete their bills",
        font=("Arial", 10),
        bg="#f4f7fb",
        fg="#666666"
    ).pack(pady=(0, 12))

    # Search frame
    search_frame = tk.Frame(
        customer_window,
        bg="white",
        bd=1,
        relief="solid"
    )

    search_frame.pack(
        fill="x",
        padx=25,
        pady=5
    )

    tk.Label(
        search_frame,
        text="Customer Name",
        font=("Arial", 11, "bold"),
        bg="white"
    ).grid(
        row=0,
        column=0,
        padx=15,
        pady=15
    )

    search_entry = tk.Entry(
        search_frame,
        font=("Arial", 11),
        width=35
    )

    search_entry.grid(
        row=0,
        column=1,
        padx=10,
        pady=15
    )

    result_text = tk.StringVar()

    result_text.set(
        "Enter a customer name and click Search."
    )

    tk.Label(
        search_frame,
        textvariable=result_text,
        font=("Arial", 10),
        bg="white",
        fg="#555555"
    ).grid(
        row=1,
        column=0,
        columnspan=3,
        pady=(0, 12)
    )

    # Table
    table_frame = tk.Frame(
        customer_window,
        bg="#f4f7fb"
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=10
    )

    columns = (
        "id",
        "name",
        "month",
        "previous",
        "current",
        "units",
        "bill"
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=12
    )

    headings = {
        "id": "ID",
        "name": "Customer",
        "month": "Month",
        "previous": "Previous",
        "current": "Current",
        "units": "Units",
        "bill": "Bill (₹)"
    }

    widths = {
        "id": 50,
        "name": 180,
        "month": 100,
        "previous": 100,
        "current": 100,
        "units": 80,
        "bill": 100
    }

    for column in columns:

        tree.heading(
            column,
            text=headings[column]
        )

        tree.column(
            column,
            width=widths[column],
            anchor="center"
        )

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(
        yscrollcommand=scrollbar.set
    )

    tree.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    current_customer = {
        "name": ""
    }

    # =====================================================
    # SEARCH CUSTOMER
    # =====================================================

    def search_customer():

        search_name = search_entry.get().strip()

        if search_name == "":
            messagebox.showwarning(
                "Search Customer",
                "Please enter a customer name."
            )
            return

        # Clear old records
        for item in tree.get_children():
            tree.delete(item)

        cursor.execute("""
            SELECT id, name, month, previous, current, units, bill
            FROM bills
            WHERE LOWER(name) = LOWER(?)
            ORDER BY id DESC
        """, (search_name,))

        rows = cursor.fetchall()

        if not rows:

            current_customer["name"] = ""

            result_text.set(
                "No records found for this customer."
            )

            messagebox.showinfo(
                "Customer Search",
                f"No bill records found for '{search_name}'."
            )
            return

        current_customer["name"] = rows[0][1]

        total_units = 0
        total_bill = 0

        for row in rows:
            total_units += row[5]
            total_bill += row[6]

        average_units = total_units / len(rows)

        result_text.set(
            f"Customer: {current_customer['name']}   |   "
            f"Records: {len(rows)}   |   "
            f"Total Units: {total_units:.0f}   |   "
            f"Total Bill: ₹{total_bill:.2f}   |   "
            f"Average: {average_units:.2f} units"
        )

        for row in rows:

            tree.insert(
                "",
                tk.END,
                values=(
                    row[0],
                    row[1],
                    row[2],
                    f"{row[3]:.0f}",
                    f"{row[4]:.0f}",
                    f"{row[5]:.0f}",
                    f"₹{row[6]:.2f}"
                )
            )

    # =====================================================
    # CUSTOMER GRAPH
    # =====================================================

    def customer_graph():

        customer_name = current_customer["name"]

        if customer_name == "":
            messagebox.showwarning(
                "Customer Graph",
                "Please search for a customer first."
            )
            return

        cursor.execute("""
            SELECT month, units, bill
            FROM bills
            WHERE LOWER(name) = LOWER(?)
            ORDER BY CASE month
                WHEN 'January' THEN 1
                WHEN 'February' THEN 2
                WHEN 'March' THEN 3
                WHEN 'April' THEN 4
                WHEN 'May' THEN 5
                WHEN 'June' THEN 6
                WHEN 'July' THEN 7
                WHEN 'August' THEN 8
                WHEN 'September' THEN 9
                WHEN 'October' THEN 10
                WHEN 'November' THEN 11
                WHEN 'December' THEN 12
            END
        """, (customer_name,))

        rows = cursor.fetchall()

        if not rows:

            messagebox.showinfo(
                "Customer Graph",
                "No data is available for this customer."
            )
            return

        months = [row[0] for row in rows]
        units = [row[1] for row in rows]
        bills = [row[2] for row in rows]

        graph_window = tk.Toplevel(
            customer_window
        )

        graph_window.title(
            f"PowerPulse - {customer_name} Graphs"
        )

        graph_window.geometry(
            "1000x780"
        )

        graph_window.configure(
            bg="#f4f7fb"
        )

        tk.Label(
            graph_window,
            text=f"Customer Analysis - {customer_name}",
            font=("Arial", 18, "bold"),
            bg="#f4f7fb",
            fg="#1f3c88"
        ).pack(
            pady=(12, 3)
        )

        tk.Label(
            graph_window,
            text="Monthly usage and bill amount",
            font=("Arial", 10),
            bg="#f4f7fb",
            fg="#666666"
        ).pack(
            pady=(0, 8)
        )

        figure, axes = plt.subplots(
            2,
            1,
            figsize=(9, 7)
        )

        # Customer units graph
        axes[0].bar(
            months,
            units,
            color="#F39C12",
            edgecolor="#B9770E"
        )

        axes[0].set_title(
            "Customer Monthly Electricity Consumption",
            fontweight="bold"
        )

        axes[0].set_xlabel("Month")
        axes[0].set_ylabel("Units Consumed")

        axes[0].grid(
            axis="y",
            linestyle="--",
            alpha=0.4
        )

        # Customer bill graph
        axes[1].bar(
            months,
            bills,
            color="#8E44AD",
            edgecolor="#6C3483"
        )

        axes[1].set_title(
            "Customer Monthly Electricity Bill",
            fontweight="bold"
        )

        axes[1].set_xlabel("Month")
        axes[1].set_ylabel("Bill Amount (₹)")

        axes[1].grid(
            axis="y",
            linestyle="--",
            alpha=0.4
        )

        figure.tight_layout()

        canvas = FigureCanvasTkAgg(
            figure,
            master=graph_window
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        def close_customer_graph():

            plt.close(figure)
            graph_window.destroy()

        tk.Button(
            graph_window,
            text="Close",
            command=close_customer_graph,
            font=("Arial", 11, "bold"),
            bg="#1f3c88",
            fg="white",
            activebackground="#17306d",
            activeforeground="white",
            padx=20,
            pady=7,
            relief="flat"
        ).pack(
            pady=10
        )

    # =====================================================
    # DELETE CUSTOMER RECORD
    # =====================================================

    def delete_customer_bill():

        selected = tree.selection()

        if not selected:

            messagebox.showwarning(
                "Select Bill",
                "Please select a customer bill to delete."
            )
            return

        values = tree.item(
            selected[0],
            "values"
        )

        bill_id = values[0]
        customer = values[1]
        month = values[2]

        answer = messagebox.askyesno(
            "Confirm Delete",
            f"Do you want to delete the bill for\n"
            f"{customer} - {month}?"
        )

        if answer:

            cursor.execute(
                "DELETE FROM bills WHERE id = ?",
                (bill_id,)
            )

            connection.commit()

            tree.delete(selected[0])

            # Refresh summary
            search_customer()

            messagebox.showinfo(
                "Deleted",
                "The selected customer bill was deleted successfully."
            )

    # =====================================================
    # BUTTONS
    # =====================================================

    button_frame = tk.Frame(
        customer_window,
        bg="#f4f7fb"
    )

    button_frame.pack(
        pady=10
    )

    tk.Button(
        search_frame,
        text="Search",
        command=search_customer,
        font=("Arial", 10, "bold"),
        bg="#1f3c88",
        fg="white",
        activebackground="#17306d",
        activeforeground="white",
        padx=18,
        pady=7,
        relief="flat"
    ).grid(
        row=0,
        column=2,
        padx=15,
        pady=15
    )

    tk.Button(
        button_frame,
        text="View Customer Graphs",
        command=customer_graph,
        font=("Arial", 10, "bold"),
        bg="#20A36A",
        fg="white",
        activebackground="#178653",
        activeforeground="white",
        padx=15,
        pady=8,
        relief="flat"
    ).grid(
        row=0,
        column=0,
        padx=5
    )

    tk.Button(
        button_frame,
        text="Delete Selected Bill",
        command=delete_customer_bill,
        font=("Arial", 10, "bold"),
        bg="#d9534f",
        fg="white",
        activebackground="#c9302c",
        activeforeground="white",
        padx=15,
        pady=8,
        relief="flat"
    ).grid(
        row=0,
        column=1,
        padx=5
    )

    tk.Button(
        button_frame,
        text="Close",
        command=customer_window.destroy,
        font=("Arial", 10, "bold"),
        bg="#555555",
        fg="white",
        activebackground="#333333",
        activeforeground="white",
        padx=25,
        pady=8,
        relief="flat"
    ).grid(
        row=0,
        column=2,
        padx=5
    )

    search_entry.focus()

    customer_window.bind(
        "<Return>",
        lambda event: search_customer()
    )


# =========================================================
# MAIN WINDOW
# =========================================================

root = tk.Tk()

root.title(
    "PowerPulse - Electricity Billing System"
)

root.geometry(
    "700x760"
)

root.configure(
    bg="#eef3f8"
)

root.resizable(
    False,
    False
)


# =========================================================
# STYLE
# =========================================================

style = ttk.Style()

try:
    style.theme_use("clam")
except:
    pass

style.configure(
    "TCombobox",
    padding=5,
    font=("Arial", 11)
)

style.configure(
    "Treeview.Heading",
    font=("Arial", 10, "bold")
)

style.configure(
    "Treeview",
    font=("Arial", 10),
    rowheight=28
)


# =========================================================
# TITLE
# =========================================================

title_label = tk.Label(
    root,
    text="POWERPULSE",
    font=("Arial", 25, "bold"),
    bg="#eef3f8",
    fg="#1f3c88"
)

title_label.pack(
    pady=(20, 3)
)

subtitle_label = tk.Label(
    root,
    text="Electricity Usage, Billing & Consumption Analytics System",
    font=("Arial", 11),
    bg="#eef3f8",
    fg="#555555"
)

subtitle_label.pack(
    pady=(0, 18)
)


# =========================================================
# INPUT FORM
# =========================================================

form = tk.Frame(
    root,
    bg="white",
    bd=1,
    relief="solid"
)

form.pack(
    padx=35,
    pady=5,
    fill="x"
)


# Customer Name
tk.Label(
    form,
    text="Customer Name",
    font=("Arial", 11, "bold"),
    bg="white"
).grid(
    row=0,
    column=0,
    padx=20,
    pady=12,
    sticky="w"
)

name_entry = tk.Entry(
    form,
    font=("Arial", 11),
    width=32
)

name_entry.grid(
    row=0,
    column=1,
    padx=20,
    pady=12
)


# Month
tk.Label(
    form,
    text="Month",
    font=("Arial", 11, "bold"),
    bg="white"
).grid(
    row=1,
    column=0,
    padx=20,
    pady=12,
    sticky="w"
)

month_combo = ttk.Combobox(
    form,
    values=[
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ],
    state="readonly",
    width=30
)

month_combo.grid(
    row=1,
    column=1,
    padx=20,
    pady=12
)


# Previous Reading
tk.Label(
    form,
    text="Previous Meter Reading",
    font=("Arial", 11, "bold"),
    bg="white"
).grid(
    row=2,
    column=0,
    padx=20,
    pady=12,
    sticky="w"
)

previous_entry = tk.Entry(
    form,
    font=("Arial", 11),
    width=32
)

previous_entry.grid(
    row=2,
    column=1,
    padx=20,
    pady=12
)


# Current Reading
tk.Label(
    form,
    text="Current Meter Reading",
    font=("Arial", 11, "bold"),
    bg="white"
).grid(
    row=3,
    column=0,
    padx=20,
    pady=12,
    sticky="w"
)

current_entry = tk.Entry(
    form,
    font=("Arial", 11),
    width=32
)

current_entry.grid(
    row=3,
    column=1,
    padx=20,
    pady=12
)


# =========================================================
# CALCULATE BUTTON
# =========================================================

calculate_button = tk.Button(
    root,
    text="Calculate & Save Bill",
    command=add_bill,
    font=("Arial", 12, "bold"),
    bg="#1f3c88",
    fg="white",
    activebackground="#17306d",
    activeforeground="white",
    padx=30,
    pady=10,
    relief="flat"
)

calculate_button.pack(
    pady=17
)


# =========================================================
# RESULT
# =========================================================

result_label = tk.Label(
    root,
    text="",
    font=("Arial", 12, "bold"),
    bg="#eef3f8",
    fg="#1b7f3a"
)

result_label.pack(
    pady=3
)


# =========================================================
# MAIN MENU
# =========================================================

button_frame = tk.Frame(
    root,
    bg="#eef3f8"
)

button_frame.pack(
    pady=12
)


# Bill History
tk.Button(
    button_frame,
    text="View Bill History",
    command=view_history,
    font=("Arial", 10, "bold"),
    bg="#5B8DEF",
    fg="white",
    activebackground="#426FBE",
    activeforeground="white",
    width=22,
    pady=8,
    relief="flat"
).grid(
    row=0,
    column=0,
    padx=7,
    pady=7
)


# Consumption Analysis
tk.Button(
    button_frame,
    text="Consumption Analysis",
    command=consumption_analysis,
    font=("Arial", 10, "bold"),
    bg="#7A5AF8",
    fg="white",
    activebackground="#6040D0",
    activeforeground="white",
    width=22,
    pady=8,
    relief="flat"
).grid(
    row=0,
    column=1,
    padx=7,
    pady=7
)


# Monthly Graphs
tk.Button(
    button_frame,
    text="View Monthly Graphs",
    command=view_monthly_graphs,
    font=("Arial", 10, "bold"),
    bg="#20A36A",
    fg="white",
    activebackground="#178653",
    activeforeground="white",
    width=22,
    pady=8,
    relief="flat"
).grid(
    row=1,
    column=0,
    padx=7,
    pady=7
)


# Customer Analysis
tk.Button(
    button_frame,
    text="Customer Analysis",
    command=customer_analysis,
    font=("Arial", 10, "bold"),
    bg="#E67E22",
    fg="white",
    activebackground="#C76512",
    activeforeground="white",
    width=22,
    pady=8,
    relief="flat"
).grid(
    row=1,
    column=1,
    padx=7,
    pady=7
)


# =========================================================
# EXIT
# =========================================================

tk.Button(
    root,
    text="Exit",
    command=root.destroy,
    font=("Arial", 10, "bold"),
    bg="#d9534f",
    fg="white",
    activebackground="#c9302c",
    activeforeground="white",
    width=22,
    pady=8,
    relief="flat"
).pack(
    pady=10
)


# =========================================================
# START PROGRAM
# =========================================================

root.mainloop()

connection.close()