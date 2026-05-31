import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# Retrieve database URL from environment/env, default to a local SQLite database
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Use SQLite inside metadata directory as fallback
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "metadata"), exist_ok=True)
    sqlite_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "metadata", "vedamate.db"))
    DATABASE_URL = f"sqlite:///{sqlite_db_path}"
else:
    # SQLAlchemy requires postgresql:// instead of postgres://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite fallback needs connect_args={'check_same_thread': False}
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserProfileModel(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    education_level = Column(String, nullable=False, default="College Undergraduate")
    interests = Column(String, nullable=False, default="General")

class TextbookMetadataModel(Base):
    __tablename__ = "textbooks"
    pdf_name = Column(String, primary_key=True, index=True)
    metadata_json = Column(Text, nullable=False) # JSON-serialized dict

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        # Note: caller will close the session
        pass
