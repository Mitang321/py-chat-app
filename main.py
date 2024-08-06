import os
from datetime import datetime
from cryptography.fernet import Fernet


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password


class ChatRoom:
    def __init__(self):
        self.users = {}
        self.messages = []
        self.chat_history_file = "chat_history.txt"
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
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
                # Base64 encode the encrypted message for safe storage
                encoded_message = encrypted_message.decode('utf-8')
                file.write(
                    f"{timestamp} - {username}: {encoded_message}\n".encode('utf-8'))

    def load_chat_history(self):
        if os.path.exists(self.chat_history_file):
            with open(self.chat_history_file, 'rb') as file:
                for line in file:
                    line = line.decode('utf-8').strip()
                    timestamp, rest = line.split(" - ", 1)
                    username, encoded_message = rest.split(": ", 1)
                    encrypted_message = encoded_message.encode('utf-8')
                    self.messages.append(
                        (username, encrypted_message, timestamp))


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
