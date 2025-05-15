"""
Make a SQL table from Mongo Collection.
Explicitly using SQLite.
"""

import logging
import os
from pathlib import Path
from sqlalchemy import (
    Column,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define SQLAlchemy Base
Base = declarative_base()

# Paths and DB setup
OPEN_WEBUI_DIR = Path(__file__).parent.parent
DATA = OPEN_WEBUI_DIR / "data"
'''
parents=True: allows creation of nested directories like open_webui/data/.
exist_ok=True: prevents errors if the directory already exists.
'''
DATA.mkdir(parents=True, exist_ok=True)
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DATA}/webui.db")

# ORM Model
class CorrelatedNode(Base):
    __tablename__ = 'correlated_node'
    src = Column(String, primary_key=True)

# Pydantic Model
class CorrelatedNodeModel(BaseModel):
    src: str

# Setup engine and session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

'''
This line creates all tables that have been declared as subclasses of Base 
(i.e., models you've defined using declarative_base()), such as:
'''
Base.metadata.create_all(bind=engine)

class InsertLog:
    def __init__(self):
        self.session = SessionLocal()

    def start(self, artifacts):
        try:
            for artifact in artifacts:
                correlated_node = CorrelatedNodeModel(src=artifact['src'])
                result = CorrelatedNode(**correlated_node.model_dump())
                self.session.add(result)

            self.session.commit()
            logger.info("All records inserted successfully.")

        except Exception as e:
            self.session.rollback()
            logger.exception("Error during insertion: %s", e)
        finally:
            self.session.close()
