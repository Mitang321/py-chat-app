import os
import sqlite3
from datetime import datetime
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import simpledialog, messagebox


class User:
    def __init__(self, username, password, role='member'):
        self.username = username
        self.password = password
        self.role = role


class ChatRoom:
    def __init__(self):
        self.database_file = "chat.db"
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self._setup_database()

    def _setup_database(self):
        self.conn = sqlite3.connect(self.database_file)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                username TEXT PRIMARY KEY,
                                password TEXT,
                                role TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT,
                                message TEXT,
                                timestamp TEXT)''')
        self.conn.commit()

    def add_user(self, username, password, role='member'):
        self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                            (username, password, role))
        self.conn.commit()

    def authenticate_user(self, username, password):
        self.cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = self.cursor.fetchone()
        if user:
            return User(*user)
        return None

    def add_message(self, username, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        encrypted_message = self.cipher.encrypt(message.encode())
        self.cursor.execute("INSERT INTO messages (username, message, timestamp) VALUES (?, ?, ?)",
                            (username, encrypted_message.decode(), timestamp))
        self.conn.commit()

    def get_messages(self):
        self.cursor.execute(
            "SELECT id, username, message, timestamp FROM messages")
        messages = self.cursor.fetchall()
        return [(msg_id, username, self.cipher.decrypt(encrypted_message.encode()).decode(), timestamp)
                for msg_id, username, encrypted_message, timestamp in messages]

    def delete_message(self, message_id):
        self.cursor.execute("DELETE FROM messages WHERE id=?", (message_id,))
        self.conn.commit()


class ChatGUI:
    def __init__(self, chat_room):
        self.chat_room = chat_room
        self.current_user = None
        self.root = tk.Tk()
        self.root.title("Chat Room")
        self.root.geometry("400x500")

        self.login_frame = tk.Frame(self.root)
        self.chat_frame = tk.Frame(self.root)

        self.setup_login_frame()
        self.setup_chat_frame()

        self.show_login_frame()

        self.root.mainloop()

    def setup_login_frame(self):
        tk.Label(self.login_frame, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack(pady=5)
        tk.Label(self.login_frame, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.pack(pady=5)
        tk.Button(self.login_frame, text="Login",
                  command=self.login).pack(pady=5)
        tk.Button(self.login_frame, text="Create Account",
                  command=self.create_account).pack(pady=5)

    def setup_chat_frame(self):
        self.message_listbox = tk.Listbox(self.chat_frame, width=50, height=20)
        self.message_listbox.pack(pady=5)
        self.message_entry = tk.Entry(self.chat_frame, width=40)
        self.message_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(self.chat_frame, text="Send",
                  command=self.send_message).pack(side=tk.LEFT)
        tk.Button(self.chat_frame, text="Logout",
                  command=self.logout).pack(side=tk.LEFT)

    def show_login_frame(self):
        self.chat_frame.pack_forget()
        self.login_frame.pack()

    def show_chat_frame(self):
        self.login_frame.pack_forget()
        self.chat_frame.pack()
        self.update_messages()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = self.chat_room.authenticate_user(username, password)
        if user:
            self.current_user = user
            self.show_chat_frame()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def create_account(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = simpledialog.askstring("Role", "Enter role (admin/member):")
        self.chat_room.add_user(username, password, role)
        messagebox.showinfo("Success", "Account created successfully")

    def send_message(self):
        message = self.message_entry.get()
        self.chat_room.add_message(self.current_user.username, message)
        self.message_entry.delete(0, tk.END)
        self.update_messages()

    def update_messages(self):
        self.message_listbox.delete(0, tk.END)
        messages = self.chat_room.get_messages()
        for msg_id, username, message, timestamp in messages:
            self.message_listbox.insert(
                tk.END, f"{timestamp} - {username}: {message}")
            if self.current_user.role == 'admin':
                self.message_listbox.insert(
                    tk.END, f"    [Delete] (id: {msg_id})")

    def logout(self):
        self.current_user = None
        self.show_login_frame()


def main():
    chat_room = ChatRoom()
    ChatGUI(chat_room)


if __name__ == "__main__":
    main()
