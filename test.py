from src.database import Database


db = Database("test.db")
db.create_db()

repo = UserRepository(db)
UserLogic(repo)

cd