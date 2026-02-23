from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL format: mysql+mysqlconnector://user:password@host/database_name
# If using XAMPP/Localhost, default user is 'root' and password is empty ''
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:mop1117668@localhost/dbms_project"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to open/close DB session automatically
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()