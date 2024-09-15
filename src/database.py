import sqlite3

class Database:
    def __init__(self, path: str) -> None:
        self.connection = sqlite3.connect(path)

    def __del__(self):
        self.close()

    def close(self):
        self.connection.close()

    def execute(sql_command: str, *args):
        pass