from typing import Union
from typing_extensions import Literal
import sqlite3

class Database:
    def __init__(self, path: str) -> None:
        self.connection = sqlite3.connect(path)

    def __del__(self):
        self.close()

    def create_db(self):
        cursor = self.connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS roles(
                     id INTEGER PRIMARY KEY,
                     role TEXT UNIQUE
                     )
            """)
        cursor.execute("""CREATE UNIQUE INDEX IF NOT EXISTS idx_roles
                     ON roles(role)
            """)
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS user(
                     id INTEGER PRIMARY KEY,
                     discord_id TEXT UNIQUE,
                     discord_username TEXT,
                     display_name TEXT,
                     role INTEGER REFERENCES roles
                     )
            """)
        cursor.execute("""CREATE UNIQUE INDEX IF NOT EXISTS idx_user_discord_id
                     ON user(discord_id)
            """)
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_user_discord_username
                     ON user(discord_username)
            """)
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_user_display_name
                     ON user(display_name)
            """)
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS entry_types(
                     id INTEGER PRIMARY KEY,
                     type TEXT UNIQUE
                     )
            """)
        cursor.execute("""CREATE UNIQUE INDEX IF NOT EXISTS idx_entry_type
                     ON entry_types(type)
            """)
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS state_types(
                     id INTEGER PRIMARY KEY,
                     state TEXT UNIQUE
                     )
            """)
        cursor.execute("""CREATE UNIQUE INDEX IF NOT EXISTS idx_state_type
                     ON state_types(state)
            """)
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS entry_data(
                     id INTEGER PRIMARY KEY,
                     type INTEGER REFERENCES entry_types,
                     state INTEGER REFERENCES state_types,
                     role INTEGER REFERENCES roles,
                     author INTEGER REFERENCES user,
                     creation_date INTEGER,
                     deadline INTEGER,
                     title TEXT,
                     content TEXT
                     )
            """)
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_entry_data_title
                     ON entry_data(title)
            """)
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_entry_data_author
                     ON entry_data(author)
            """)
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_entry_data_state
                     ON entry_data(state)
            """)
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_entry_data_type
                     ON entry_data(type)
            """)
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS vote_store(
                     caster INTEGER REFERENCES user,
                     entry INTEGER REFERENCES entry_data,
                     vote TEXT CHECK(vote IN ("approve", "disapprove", "abstain"))
                     )
            """)
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_vote
                     ON vote_store(entry)
            """)
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS repeal_store(
                     entry_id INTEGER PRIMARY KEY,
                     repealed_id INTEGER REFERENCES entry_data,
                     FOREIGN KEY(entry_id) REFERENCES entry_data
                     )
            """)
        
        self.insert("state_types", {"state": "proposed"}, ignore=True)
        self.insert("state_types", {"state": "denied"}, ignore=True)
        self.insert("state_types", {"state": "active"}, ignore=True)
        self.insert("state_types", {"state": "cancelled"}, ignore=True)
        self.insert("state_types", {"state": "completed"}, ignore=True)
        self.insert("state_types", {"state": "completed early"}, ignore=True)
        self.insert("state_types", {"state": "repealed"}, ignore=True)

        self.insert("entry_types", {"type": "election"}, ignore=True)
        self.insert("entry_types", {"type": "resolution"}, ignore=True)
        self.insert("entry_types", {"type": "application"}, ignore=True)
        self.insert("entry_types", {"type": "repeal"}, ignore=True)

        self.insert("roles", {"role": "everyone"}, ignore=True)
        self.insert("roles", {"role": "member"}, ignore=True)
        self.insert("roles", {"role": "administrator"}, ignore=True)

        cursor.close()
        self.commit()

    def close(self):
        self.connection.close()

    def execute(self, sql_command: str, *args):
        return self.connection.execute(sql_command, args)

    def insert(self, table: str, data: Union[dict[str, any], tuple[any]], *, ignore=False):
        ph_string = ", ".join(["?"] * len(data))
        extra = "OR IGNORE" if ignore else ""
        if type(data) == dict:
            columns = ", ".join(data.keys())
            return self.execute(f"INSERT {extra} INTO {table} ({columns}) VALUES ({ph_string})", *data.values())
        return self.execute(f"INSERT {extra} INTO {table} VALUES({ph_string})", data) 

    def simple_query(self, table: str, values: Union[tuple[str], Literal['*']], *, where=None):
        pass

    def query(self, query_statement: str, *params):
        result = self.execute(query_statement, *params)
        return result.fetchall()
    
    def query_once(self, query_statement: str, *params):
        result = self.execute(query_statement, *params)
        return result.fetchone()
    
    #doesnt work!!!
    def update(self, table: str, update_dict: dict[str, any], where_string: str):
        set_list = ["? = ?"] * len(update_dict)
        set_string = ", ".join(set_list)
        args_list = []
        for field, value in update_dict.items():
            args_list.append(field, value)
        self.execute(f"UPDATE {table} SET {set_string} WHERE {where_string}", args_list)
        
    def commit(self):
        self.connection.commit()   


