"""
Make a SQL table from Mongo Collection.
Explicitly using SQLite.
"""

import logging
import os
from pathlib import Path
from datetime import datetime 
from typing import List  
from sqlalchemy import (
    Column,
    String,
    BigInteger,
    DateTime,
    create_engine,
)
from config import (
    SQL_PATH,
    TABLE_PREFIX
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from uuid import uuid4 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define SQLAlchemy Base
Base = declarative_base()
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{SQL_PATH}/webui.db")

# Pydantic Model
class CorrelatedNodeModel(BaseModel):
    id: str
    src_node: str
    src_ip: str 
    src_port: str
    dst_node: str
    dst_ip: str
    dst_port: str
    inference: str
    src_interface: str
    dst_interface: str
    protocol: str
    procedure: str 
    procedure_type: str 
    procedure_onset_timestamp: datetime
    timestamp: datetime
    pcap_insight: str 
    message: str
    ie: str
    value: str 
    occurrence_imsis: List[str]
    occurrence_times : List[datetime]

# ORM Model
class CorrelatedNode(Base):
    # TBD based on chat-id: PREFIX + chat-id
    __tablename__ = 'functional_x'
    id = Column(String, primary_key=True)
    src_node = Column(String)
    src_ip = Column(String)
    src_port = Column(String)
    dst_node = Column(String)
    dst_ip = Column(String)
    dst_port = Column(String)
    inference = Column(String)
    src_interface = Column(String)
    dst_interface = Column(String)
    protocol = Column(String)
    procedure = Column(String)
    procedure_type = Column(String)
    procedure_onset_timestamp = Column(DateTime)
    

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

    def start(self, artifact):
        try:
            correlated_node = CorrelatedNodeModel(**{
                'id': str(uuid4()),
                'src_node': artifact.get('src_node', 'NA'),
                "src_ip": artifact.get('src_ip', 'NA'),
                "src_port": artifact.get('src_port', 'NA'),
                'dst_node': artifact.get('dst_node', 'NA'),
                'dst_ip': artifact.get('dst_ip', 'NA'),
                'dst_port': artifact.get('dst_port', 'NA'),
                'inference': artifact.get('inference', 'NA'),
                'src_interface': artifact.get('src_interface', 'NA'),
                'dst_interface': artifact.get('dst_interface', 'NA'),
                'protocol': artifact.get('protocol', 'NA')
            })
            result = CorrelatedNode(**correlated_node.model_dump())
            self.session.add(result)
            self.session.commit()
            logger.info("All records inserted successfully.")
        except Exception as e:
            self.session.rollback()
            logger.exception("Error during insertion: %s", e)
        finally:
            self.session.close()
