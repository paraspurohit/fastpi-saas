from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config.config import setting


DATABASE_URL = f"postgresql://{setting.database_username}:{setting.database_password}@{setting.database_hostname}:{setting.database_port}/{setting.database_name}"
engine = create_engine(DATABASE_URL, echo=True)

def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
