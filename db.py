from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from config import SQLALCHEMY_DATABASE_URL

# Remove this connection string if config.py is working fine.

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base=declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally: 
        db.close()

# def create_tables():
#     Base.metadata.create_all(bind=engine)
