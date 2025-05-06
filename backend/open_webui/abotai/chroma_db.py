from chromadb import Client
from langchain_chroma import Chroma
from langchain_core.documents import Document
from models import LM_Models
from typing import List
from uuid import uuid4

class ChromaDB:
    _instance = None 
    _collections = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._pre_init()
        return cls._instance
    
    def _pre_init(self):
        self.client = Client()
        self.embed_model = LM_Models().embed_model
    
    def __init__(self, db_name: str = "DEFAULT_DB", document_list: List[Document] = None):
        if db_name not in self._collections:
            self.client.get_or_create_collection(db_name)
            self._collections[db_name] = Chroma(client=self.client, 
                                                collection_name=db_name,
                                                embedding_function=self.embed_model)
            uuids = [str(uuid4()) for _ in range(len(document_list))]
            self._collections[db_name].add_documents(documents = document_list, ids = uuids)
        self.vector_store = self._collections[db_name]
