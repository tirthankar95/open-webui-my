'''
Make a SQL table from Mongo Collection.
'''
import logging 
from sqlalchemy import (
    Column, 
    DateTime, 
    String,
    create_engine,
    MetaData
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import os 
from pathlib import Path 

logger = logging.getLogger(__name__)
Base = declarative_base()

OPEN_WEBUI_DIR = Path(__file__).parent.parent
DATA = Path(OPEN_WEBUI_DIR) / "data"
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DATA}/webui.db")

class CorrelatedNode(Base):
    __tablename__ = 'correlated_node'
    # window_start = Column(DateTime(timezone=True))
    # window_end = Column(DateTime(timezone=True))
    src = Column(String, primary_key=True)

class CorrelatedNodeModel(BaseModel):
    src: str

# Setup a database engine
engine = create_engine(DATABASE_URL)
# Create a session
SessionLocal = sessionmaker(bind = engine)
session = SessionLocal()


class InsertLog:
    def __init__(self):
        pass 

    def start(self, artifacts):
        for artifact in artifacts:
            correlated_node = CorrelatedNodeModel(
                **{
                    "src": artifact['src']
                }
            )
            result = CorrelatedNode(**correlated_node.model_dump())
            # Add to DB.
            session.add(result)
            session.commit()









    # '''
    # Creates all tables if not already there
    # '''
    # create_all()