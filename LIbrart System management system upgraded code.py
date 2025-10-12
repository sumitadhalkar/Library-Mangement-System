import tkinter as tk
from tkinter import messagebox
import sqlite3
import csv

# --- Database Setup ---
conn = sqlite3.connect("library.db")
cursor = conn.cursor()

def setup_database():
    # Add 'price' column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE books ADD COLUMN price REAL NOT NULL DEFAULT 0.0")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
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

# --- Utility Functions ---
def is_valid_price(price):
    try:
        float(price)
        return True
    except ValueError:
        return False

# --- Add Book ---
def add_book():
    title = entry_title.get()
    author = entry_author.get()
    quantity = entry_quantity.get()
    price = entry_price.get()

    if title and author and quantity.isdigit() and is_valid_price(price):
        cursor.execute("INSERT INTO books (title, author, quantity, price) VALUES (?, ?, ?, ?)",
                       (title, author, int(quantity), float(price)))
        conn.commit()
        messagebox.showinfo("Success", "Book added successfully!")
        entry_title.delete(0, tk.END)
        entry_author.delete(0, tk.END)
        entry_quantity.delete(0, tk.END)
        entry_price.delete(0, tk.END)
        view_books()
    else:
        messagebox.showerror("Error", "Please enter valid book details.")

# --- View Books ---
def view_books():
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    book_list.delete(0, tk.END)
    for book in books:
        book_list.insert(tk.END, f"ID: {book[0]} | {book[1]} by {book[2]} | Qty: {book[3]} | Price: ${book[4]:.2f}")

# --- Search Books ---
def search_books():
    query = entry_search.get().lower()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    book_list.delete(0, tk.END)
    for book in books:
        if query in book[1].lower() or query in book[2].lower():
            book_list.insert(tk.END, f"ID: {book[0]} | {book[1]} by {book[2]} | Qty: {book[3]} | Price: ${book[4]:.2f}")

# --- Delete Book ---
def delete_book():
    selected = book_list.curselection()
    if selected:
        selected_text = book_list.get(selected[0])
        book_id = selected_text.split('|')[0].strip().split(':')[1].strip()
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete book ID {book_id}?")
        if confirm:
            cursor.execute("DELETE FROM books WHERE book_id=?", (book_id,))
            conn.commit()
            view_books()
            messagebox.showinfo("Deleted", "Book deleted successfully.")
    else:
        messagebox.showwarning("No selection", "Please select a book to delete.")

# --- Edit Book ---
def edit_book():
    selected = book_list.curselection()
    if not selected:
        messagebox.showwarning("No selection", "Please select a book to edit.")
        return

    selected_text = book_list.get(selected[0])
    book_id = int(selected_text.split('|')[0].split(':')[1].strip())

    # Fetch book info
    cursor.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()

    if not book:
        messagebox.showerror("Error", "Book not found.")
        return

    # Pop-up window
    edit_win = tk.Toplevel(root)
    edit_win.title("Edit Book")

    tk.Label(edit_win, text="Title:").grid(row=0, column=0)
    entry_edit_title = tk.Entry(edit_win, width=30)
    entry_edit_title.insert(0, book[1])
    entry_edit_title.grid(row=0, column=1)

    tk.Label(edit_win, text="Author:").grid(row=1, column=0)
    entry_edit_author = tk.Entry(edit_win, width=30)
    entry_edit_author.insert(0, book[2])
    entry_edit_author.grid(row=1, column=1)

    tk.Label(edit_win, text="Quantity:").grid(row=2, column=0)
    entry_edit_quantity = tk.Entry(edit_win, width=10)
    entry_edit_quantity.insert(0, str(book[3]))
    entry_edit_quantity.grid(row=2, column=1)

    tk.Label(edit_win, text="Price:").grid(row=3, column=0)
    entry_edit_price = tk.Entry(edit_win, width=10)
    entry_edit_price.insert(0, str(book[4]))
    entry_edit_price.grid(row=3, column=1)

    def save_changes():
        new_title = entry_edit_title.get()
        new_author = entry_edit_author.get()
        new_quantity = entry_edit_quantity.get()
        new_price = entry_edit_price.get()

        if new_title and new_author and new_quantity.isdigit() and is_valid_price(new_price):
            cursor.execute("""
                UPDATE books
                SET title = ?, author = ?, quantity = ?, price = ?
                WHERE book_id = ?
            """, (new_title, new_author, int(new_quantity), float(new_price), book_id))
            conn.commit()
            messagebox.showinfo("Success", "Book updated successfully.")
            edit_win.destroy()
            view_books()
        else:
            messagebox.showerror("Error", "Please enter valid book details.")

    tk.Button(edit_win, text="Save Changes", command=save_changes).grid(row=4, column=1, sticky="e", pady=10)

# --- Export to CSV ---
def export_to_csv():
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    with open("books_export.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Book ID", "Title", "Author", "Quantity", "Price"])
        writer.writerows(books)

    messagebox.showinfo("Exported", "Book list exported to 'books_export.csv'.")

# --- GUI Setup ---
setup_database()
root = tk.Tk()
root.title("📚 Library Management System")
root.geometry("800x600")

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

tk.Label(frame_add, text="Price ($):").grid(row=3, column=0)
entry_price = tk.Entry(frame_add, width=10)
entry_price.grid(row=3, column=1, sticky="w")

tk.Button(frame_add, text="Add Book", command=add_book).grid(row=4, column=1, sticky="e", pady=5)

# --- Book List Section --- #
frame_view = tk.LabelFrame(root, text="📖 Available Books", padx=10, pady=10)
frame_view.pack(fill="both", expand=True, padx=10, pady=5)

book_list = tk.Listbox(frame_view, width=100, height=15)
book_list.pack(pady=5)

# --- Search Section --- #
frame_search = tk.Frame(root)
frame_search.pack(pady=5)

tk.Label(frame_search, text="🔍 Search:").pack(side="left")
entry_search = tk.Entry(frame_search, width=30)
entry_search.pack(side="left", padx=5)
tk.Button(frame_search, text="Search", command=search_books).pack(side="left")
tk.Button(frame_search, text="Clear", command=view_books).pack(side="left", padx=5)

# --- Buttons Section --- #
tk.Button(root, text="🔄 Refresh Book List", command=view_books).pack(pady=5)
tk.Button(root, text="✏️ Edit Selected Book", command=edit_book).pack(pady=5)
tk.Button(root, text="🗑 Delete Selected Book", command=delete_book).pack(pady=5)
tk.Button(root, text="📄 Export to CSV", command=export_to_csv).pack(pady=5)

# --- Load Books on Start ---
view_books()

# --- Run App ---
root.mainloop()
