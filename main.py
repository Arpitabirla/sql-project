import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from db_handler import create_table, add_transaction, delete_transaction, view_all, get_summary

# ------------------------------------------------------------------
# 🧱 INITIAL SETUP
# ------------------------------------------------------------------
root = tk.Tk()
root.title("Mini Budget Manager 💰")
root.geometry("950x600")
root.resizable(False, False)

# ensure database table exists
create_table()

# ------------------------------------------------------------------
# 📦 ADD TRANSACTION SECTION
# ------------------------------------------------------------------

tk.Label(root, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=10)
date_entry = tk.Entry(root, width=25)
date_entry.grid(row=0, column=1)

tk.Label(root, text="Category:").grid(row=1, column=0, padx=10, pady=10)
category_entry = tk.Entry(root, width=25)
category_entry.grid(row=1, column=1)

tk.Label(root, text="Description:").grid(row=2, column=0, padx=10, pady=10)
description_entry = tk.Entry(root, width=25)
description_entry.grid(row=2, column=1)

tk.Label(root, text="Amount:").grid(row=3, column=0, padx=10, pady=10)
amount_entry = tk.Entry(root, width=25)
amount_entry.grid(row=3, column=1)

tk.Label(root, text="Type:").grid(row=4, column=0, padx=10, pady=10)
type_var = tk.StringVar(value="Expense")
type_menu = ttk.Combobox(root, textvariable=type_var, values=["Income", "Expense"], width=22, state="readonly")
type_menu.grid(row=4, column=1)

# ------------------------------------------------------------------
# 🧩 TREEVIEW (TABLE TO SHOW RECORDS)
# ------------------------------------------------------------------
columns = ("id", "date", "category", "description", "amount", "type")
tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
tree.grid(row=0, column=3, rowspan=10, padx=25, pady=10)

for col in columns:
    tree.heading(col, text=col.title())
    tree.column(col, width=130)

# Scrollbar
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.grid(row=0, column=4, rowspan=10, sticky="ns")

# ------------------------------------------------------------------
# 🔘 BUTTON FUNCTIONS
# ------------------------------------------------------------------

def clear_inputs():
    date_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    type_var.set("Expense")

def load_data_to_treeview():
    """Reload all rows from DB to treeview"""
    for row in tree.get_children():
        tree.delete(row)
    rows = view_all()
    for r in rows:
        tree.insert("", "end", iid=r[0], values=r)

def add_transaction_gui():
    date = date_entry.get()
    category = category_entry.get()
    description = description_entry.get() or None
    amount = amount_entry.get()
    t_type = type_var.get().lower()

    if not (date and category and amount and t_type):
        messagebox.showwarning("Missing Info", "Please fill all required fields.")
        return

    try:
        add_transaction(date, category, amount, t_type, description)
        messagebox.showinfo("Success", "Transaction added successfully!")
        clear_inputs()
        load_data_to_treeview()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add transaction:\n{e}")

def delete_selected_transaction():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a transaction to delete.")
        return

    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction?")
    if not confirm:
        return

    try:
        delete_transaction(selected)
        messagebox.showinfo("Deleted", "Transaction deleted successfully!")
        load_data_to_treeview()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete transaction:\n{e}")

def show_summary():
    try:
        income, expense = get_summary()
        balance = income - expense
        messagebox.showinfo("Summary", f"💰 Total Income: {income}\n💸 Total Expense: {expense}\n📊 Balance: {balance}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not fetch summary:\n{e}")

def visualize_expenses():
    try:
        rows = view_all()
        if not rows:
            messagebox.showinfo("No Data", "No transactions to visualize.")
            return

        categories = {}
        for r in rows:
            cat = r[2]
            amt = float(r[4])
            typ = r[5]
            if typ == "expense":
                categories[cat] = categories.get(cat, 0) + amt

        if not categories:
            messagebox.showinfo("No Expenses", "No expense data to visualize.")
            return

        plt.figure(figsize=(8, 6))
        plt.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%')
        plt.title("Expense Distribution by Category")
        plt.show()
    except Exception as e:
        messagebox.showerror("Error", f"Could not visualize data:\n{e}")

# ------------------------------------------------------------------
# 🖱️ BUTTONS
# ------------------------------------------------------------------
tk.Button(root, text="Add Transaction", bg="#4CAF50", fg="white", width=18, command=add_transaction_gui).grid(row=5, column=1, pady=10)
tk.Button(root, text="Delete Selected", bg="#f44336", fg="white", width=18, command=delete_selected_transaction).grid(row=6, column=1, pady=10)
tk.Button(root, text="View All Records", bg="#2196F3", fg="white", width=18, command=load_data_to_treeview).grid(row=7, column=1, pady=10)
tk.Button(root, text="Show Summary", bg="#FF9800", fg="white", width=18, command=show_summary).grid(row=8, column=1, pady=10)
tk.Button(root, text="Visualize Expense", bg="#9C27B0", fg="white", width=18, command=visualize_expenses).grid(row=9, column=1, pady=10)

# ------------------------------------------------------------------
# 🚀 LOAD DATA ON STARTUP
# ------------------------------------------------------------------
load_data_to_treeview()

root.mainloop()
