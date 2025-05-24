from pydantic import BaseModel
from datetime import datetime 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    Column,
    String,
    DateTime,
    create_engine,
    ForeignKey
)
from config import (
    SQL_PATH,
    DPX_MAIN_TABLE,
    DPX_PROP_TABLE,
    DPX_IMSI_TABLE
)
import os 
import copy
from uuid import uuid4 
import logging 
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_chat_table(chat_id: str, artefact_orig):
    # Define SQLAlchemy Base
    Base = declarative_base()
    DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{SQL_PATH}/webui.db")
    # Setup engine and session
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    IMSI_TABLE = DPX_IMSI_TABLE + chat_id
    PROP_TABLE = DPX_PROP_TABLE + chat_id
    MAIN_TABLE = DPX_MAIN_TABLE + chat_id
    # Pydantic Model ~ PropagatedIssues
    class ImsiNodeModel(BaseModel):
        id: str
        source_issue: str
        imsi: str
        timestamp: datetime

    # ORM Model
    class ImsiNode(Base):
        __tablename__ = IMSI_TABLE
        __table_args__ = {'extend_existing': True}
        id = Column(String, primary_key=True)
        source_issue = Column(String, ForeignKey(f'{MAIN_TABLE}.id'))
        imsi = Column(String)
        timestamp = Column(DateTime)

    # Pydantic Model ~ PropagatedIssues
    class PropagatedIssueModel(BaseModel):
        id: str
        source_issue: str
        protocol: str
        src_node: str
        status: str
        src_interface: str
        dst_node: str
        dst_interface: str
        pcap_insight: str
        response_code_description: str
        nf_service: str
        service_operation: str
        operation_id: str
        callback_type: str
        url_route: str
        method: str

    # ORM Model
    class PropagatedIssues(Base):
        __tablename__ = PROP_TABLE
        __table_args__ = {'extend_existing': True}
        id = Column(String, primary_key=True)
        source_issue = Column(String, ForeignKey(f'{MAIN_TABLE}.id'))
        protocol = Column(String)
        src_node = Column(String)
        status = Column(String)
        src_interface = Column(String)
        dst_node = Column(String)
        dst_interface = Column(String)
        pcap_insight = Column(String)
        response_code_description = Column(String)
        nf_service = Column(String)
        service_operation = Column(String)
        operation_id = Column(String)
        callback_type = Column(String)
        url_route = Column(String)
        method = Column(String)

    # Pydantic Model ~ DeepX
    class DeepXNodeModel(BaseModel):
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

    # ORM Model
    class DeepXNode(Base):
        # TBD based on chat-id: PREFIX + chat-id
        __tablename__ = MAIN_TABLE
        __table_args__ = {'extend_existing': True}
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
        timestamp = Column(DateTime)
        pcap_insight = Column(String)
        message = Column(String)
        ie = Column(String)
        value = Column(String)

    '''
    This line creates all tables that have been declared as subclasses of Base 
    (i.e., models you've defined using declarative_base()), such as:
    '''
    Base.metadata.create_all(bind=engine)
    for doc in artefact_orig:
        if "pcap" in doc and "prompt" in doc["pcap"]:
            artefact = copy.deepcopy(doc['pcap']['prompt'])
            artefact_id = doc["job_id"]
            # Process temp_occurence_times
            temp_occurence_times = artefact.get('occurrence_times', [])
            for idx, x in enumerate(temp_occurence_times):
                artefact['occurrence_times'] = datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")

            # Process imsi
            temp_occurence_imsis = artefact.get('occurrence_imsis', [])
            for idx, x in enumerate(temp_occurence_times):
                imsi_node = ImsiNodeModel(**{
                    'id': str(uuid4()),
                    'source_issue': artefact_id,
                    'imsi': temp_occurence_imsis[idx],
                    'timestamp': x
                })
                imsi_result = ImsiNode(**imsi_node.model_dump())
                session.add(imsi_result)
                session.commit()

            # Process propagated_issues
            temp_propagated_issues = []
            for x in artefact.get('propagated_issues', []):
                x['id'] = str(uuid4())
                x['source_issue'] = artefact_id
                propagated_issue_model = PropagatedIssueModel(**x)
                p_result = PropagatedIssues(**propagated_issue_model.model_dump())
                session.add(p_result)
                session.commit()
                temp_propagated_issues.append(x['id'])

            try:
                deepx_node = DeepXNodeModel(**{
                    'id': artefact_id,
                    'src_node': artefact.get('src_node', 'NA'),
                    "src_ip": artefact.get('src_ip', 'NA'),
                    "src_port": artefact.get('src_port', 'NA'),
                    'dst_node': artefact.get('dst_node', 'NA'),
                    'dst_ip': artefact.get('dst_ip', 'NA'),
                    'dst_port': artefact.get('dst_port', 'NA'),
                    'inference': artefact.get('inference', 'NA'),
                    'src_interface': artefact.get('src_interface', 'NA'),
                    'dst_interface': artefact.get('dst_interface', 'NA'),
                    'protocol': artefact.get('protocol', 'NA'),
                    'procedure': artefact.get('procedure', 'NA'),
                    'procedure_type': artefact.get('procedure_type', 'NA'),
                    'procedure_onset_timestamp': datetime.fromtimestamp(int(artefact.get('procedure_onset_timestamp', 0))/1000000),
                    'timestamp': datetime.fromtimestamp(int(artefact.get('timestamp', 0))/1000000),
                    'pcap_insight': artefact.get('pcap_insight', 'NA'),
                    'message': artefact.get('message', 'NA'),
                    'ie': artefact.get('ie', 'NA'),
                    'value': artefact.get('value', 'NA')
                })
                result = DeepXNode(**deepx_node.model_dump())
                session.add(result)
                session.commit()
                logger.info("All records inserted successfully.")
            except Exception as e:
                session.rollback()
                logger.exception("Error during insertion: %s", e)
            finally:
                session.close()