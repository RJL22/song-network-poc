from sqlalchemy import select

print("Starting the test_orm.py script...")

from app.database import SessionLocal
from app.models import Song

print("Fetching all songs from the database...")
db = SessionLocal()
songs = db.scalars(select(Song)).all()

for song in songs:
    print(f"Song ID: {song.id}, Title: {song.title}, Artist: {song.artist}")

print("Done fetching songs.")
