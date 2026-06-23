from sqlalchemy import create_engine,Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://postgres:76452@localhost:5432/student_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal= sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()
class DBStudent(Base):
    __tablename__ = "students"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String, nullable = False)
    grade = Column(String, nullable = False)
Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()