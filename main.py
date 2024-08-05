
import os
from datetime import datetime


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password


class ChatRoom:
    def __init__(self):
        self.users = {}
        self.messages = []
        self.chat_history_file = "chat_history.txt"
        self.load_chat_history()

    def add_user(self, username, password):
        self.users[username] = User(username, password)

    def authenticate_user(self, username, password):
        user = self.users.get(username)
        if user and user.password == password:
            return True
        return False

    def add_message(self, username, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.messages.append((username, message, timestamp))
        self.save_chat_history()

    def display_messages(self):
        for username, message, timestamp in self.messages:
            print(f"{timestamp} - {username}: {message}")

    def save_chat_history(self):
        with open(self.chat_history_file, 'w') as file:
            for username, message, timestamp in self.messages:
                file.write(f"{timestamp} - {username}: {message}\n")

    def load_chat_history(self):
        if os.path.exists(self.chat_history_file):
            with open(self.chat_history_file, 'r') as file:
                for line in file:
                    timestamp, rest = line.strip().split(" - ", 1)
                    username, message = rest.split(": ", 1)
                    self.messages.append((username, message, timestamp))


def main():
    chat_room = ChatRoom()
    print("Welcome to the Chat Room!")
    while True:
        choice = input("Do you have an account? (yes/no): ").strip().lower()
        if choice == 'no':
            username = input("Choose a username: ")
            password = input("Choose a password: ")
            chat_room.add_user(username, password)
            print("Account created successfully!")
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        if chat_room.authenticate_user(username, password):
            print("Login successful!")
            message = input("Enter your message: ")
            chat_room.add_message(username, message)
            chat_room.display_messages()
        else:
            print("Invalid username or password. Try again.")


if __name__ == "__main__":
    main()
