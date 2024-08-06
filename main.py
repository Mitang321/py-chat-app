# Stage 7: Add User Roles

import os
from datetime import datetime
from cryptography.fernet import Fernet


class User:
    def __init__(self, username, password, role='member'):
        self.username = username
        self.password = password
        self.role = role


class ChatRoom:
    def __init__(self):
        self.users = {}
        self.messages = []
        self.chat_history_file = "chat_history.txt"
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.load_chat_history()

    def add_user(self, username, password, role='member'):
        self.users[username] = User(username, password, role)

    def authenticate_user(self, username, password):
        user = self.users.get(username)
        if user and user.password == password:
            return user
        return None

    def add_message(self, username, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        encrypted_message = self.cipher.encrypt(message.encode())
        self.messages.append((username, encrypted_message, timestamp))
        self.save_chat_history()

    def display_messages(self):
        for username, encrypted_message, timestamp in self.messages:
            message = self.cipher.decrypt(encrypted_message).decode()
            print(f"{timestamp} - {username}: {message}")

    def save_chat_history(self):
        with open(self.chat_history_file, 'wb') as file:
            for username, encrypted_message, timestamp in self.messages:
                file.write(
                    f"{timestamp} - {username}: {encrypted_message.decode()}\n".encode())

    def load_chat_history(self):
        if os.path.exists(self.chat_history_file):
            with open(self.chat_history_file, 'rb') as file:
                for line in file:
                    timestamp, rest = line.strip().split(b" - ", 1)
                    username, encrypted_message = rest.split(b": ", 1)
                    self.messages.append(
                        (username.decode(), encrypted_message, timestamp.decode()))


def main():
    chat_room = ChatRoom()
    print("Welcome to the Chat Room!")
    while True:
        choice = input("Do you have an account? (yes/no): ").strip().lower()
        if choice == 'no':
            username = input("Choose a username: ")
            password = input("Choose a password: ")
            role = input("Enter role (admin/member): ").strip().lower()
            chat_room.add_user(username, password, role)
            print("Account created successfully!")
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        user = chat_room.authenticate_user(username, password)
        if user:
            print(f"Login successful! Role: {user.role}")
            message = input("Enter your message: ")
            chat_room.add_message(username, message)
            chat_room.display_messages()
        else:
            print("Invalid username or password. Try again.")


if __name__ == "__main__":
    main()
