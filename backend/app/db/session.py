from sqlmodel import SQLModel, create_engine, Session
from backend.app.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,           # Set True to see SQL logs
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Initialize tables
def init_db():
    SQLModel.metadata.create_all(engine)

# Dependency for FastAPI (we will import this in routes)
def get_session():
    with Session(engine) as session:
        yield session
