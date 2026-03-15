from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# database_url="mysql+mysqlconnector://root:2011@localhost:3306/IIT_Academic_website"
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:mop1117668@localhost/dbms_project" #password and database name check


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