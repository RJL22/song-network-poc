from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql+psycopg://music_user:password@localhost:5432/music_graph"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()