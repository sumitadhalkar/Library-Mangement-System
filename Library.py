import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# DB setup
conn = sqlite3.connect("library.db")
cursor = conn.cursor()

def setup_database():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS issue_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            member_id INTEGER,
            issue_date TEXT,
            return_date TEXT,
            FOREIGN KEY(book_id) REFERENCES books(book_id),
            FOREIGN KEY(member_id) REFERENCES members(member_id)
        )
    ''')
    conn.commit()

# Add book function
def add_book():
    title = entry_title.get()
    author = entry_author.get()
    quantity = entry_quantity.get()

    if title and author and quantity.isdigit():
        cursor.execute("INSERT INTO books (title, author, quantity) VALUES (?, ?, ?)",
                       (title, author, int(quantity)))
        conn.commit()
        messagebox.showinfo("Success", "Book added successfully!")
        entry_title.delete(0, tk.END)
        entry_author.delete(0, tk.END)
        entry_quantity.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Please enter valid book details.")

# View books
def view_books():
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    book_list.delete(0, tk.END)
    for book in books:
        book_list.insert(tk.END, f"ID: {book[0]} | {book[1]} by {book[2]} | Qty: {book[3]}")

# GUI Setup
setup_database()
root = tk.Tk()
root.title("📚 Library Management System - GUI")
root.geometry("600x400")

# --- Add Book Section --- #
frame_add = tk.LabelFrame(root, text="Add Book", padx=10, pady=10)
frame_add.pack(fill="x", padx=10, pady=5)

tk.Label(frame_add, text="Title:").grid(row=0, column=0)
entry_title = tk.Entry(frame_add, width=30)
entry_title.grid(row=0, column=1)

tk.Label(frame_add, text="Author:").grid(row=1, column=0)
entry_author = tk.Entry(frame_add, width=30)
entry_author.grid(row=1, column=1)

tk.Label(frame_add, text="Quantity:").grid(row=2, column=0)
entry_quantity = tk.Entry(frame_add, width=10)
entry_quantity.grid(row=2, column=1, sticky="w")

tk.Button(frame_add, text="Add Book", command=add_book).grid(row=3, column=1, sticky="e", pady=5)

# --- View Books Section --- #
frame_view = tk.LabelFrame(root, text="Available Books", padx=10, pady=10)
frame_view.pack(fill="both", expand=True, padx=10, pady=5)

book_list = tk.Listbox(frame_view, width=80, height=10)
book_list.pack(pady=5)

tk.Button(root, text="🔄 Refresh Book List", command=view_books).pack(pady=5)

# Initial book list load
view_books()

# Start GUI loop
root.mainloop()
