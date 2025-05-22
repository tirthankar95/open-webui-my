from Chains.chain_base import Chains, MIN_CHAT_HISTORY
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from chroma_db import ChromaDB
from langchain_core.documents import Document
from typing import List, Dict
import logging 
import copy
import os 
from pathlib import Path
from models import LM_Models
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    Column,
    String,
    create_engine,
    text
)
from config import (
    TABLE_PREFIX,
    SQL_PATH
)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

Base = declarative_base()
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{SQL_PATH}/webui.db")
TABLE_NAME = TABLE_PREFIX + "x"

class Chain_Sql(Chains):
    """
The Chain_Sql chain is responsible for translating natural language human queries to
SQLite queries so that when this query is executed, related data is retrieved from the database.
Typical natural language human queries are quantitative questions that involve keywords
such as 'count', 'how many', 'average', or similar phrases.
    """
    def __init__(self, chroma_db_dir: str = "LLM_SQL") -> None:
        super().__init__()
        ## SQL connection
        self.session = create_engine(DATABASE_URL, echo=False).connect()
        self.schema = self.session.execute(text(f"PRAGMA table_info({TABLE_NAME})")).fetchall()
        self.schema = "\n".join([' '.join([str(e) for e in row]) for row in self.schema])
        ## Retriever.
        self.all_lm_models = LM_Models()
        self.vector_store = ChromaDB(chroma_db_dir, self.one_shots()).vector_store
        self.retriver = self.vector_store.as_retriever(search_type="similarity", \
                                                       search_kwargs={"k": 1})
        ## BUILD LangChain 
        self.prompt()
        self.chain_fn = self.__vector_retriver | self.prmpt | self.all_lm_models.lm_model | \
                        StrOutputParser() | self.__sql_exec

    def __vector_retriver(self, input_2llm):
        query, history = input_2llm.get('query', None), input_2llm.get('history', None)
        rdocs = self.retriver.invoke(query)
        fmt_docx = "\n".join([doc.page_content for doc in rdocs])
        # Print LLM input. 
        logging.info(f'one_shot: {fmt_docx}\n')
        logging.info(f'history: {history}\n')
        logging.info(f'query: {query}\n')
        return {"schema": self.schema, \
                "one_shot": fmt_docx, \
                "history": history, \
                "query": query}

    def __sql_exec(self, ai_message):
        try:
            logging.info(f'AI sql query: {ai_message}')
            return f"""Executing AI sql query:\n{ai_message} gives result: {self.session.execute(text(ai_message)).fetchall()}."""
        except Exception as e:
            logging.error(f"Error in executing sql query: {ai_message} | {e}")
            raise Exception(f"{ai_message} | {e}")

    def prompt(self):
        self.prmpt = ChatPromptTemplate.from_messages(
            [
                ("system", """You are an expert AI assistant specializing in generating efficient and accurate SQLite queries.""" + \
                   """The schema of the SQLite table is: {schema}.\nHere is an example of sql query interaction you must follow this assisstant response: {one_shot}.\n""" + \
                   """When returning a query, output only the query itself with no extra words or explanations or punctuations,""" + \
                   """so that an human can directly run the command. Donot put a fullstop at the end of the query."""),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{query}")
            ]
        )
    
    def call_chain(self, query: str, history: List[Dict]) -> str:
        '''
        This function calls the lang chain for a specific child class.
        Args:
            query (str): The human query that will be passed to the LLM chain.
            history List[Dict]: The chat history that will be passed to the LLM chain.
        Return:
            output (str): The output string from the LLM chain.
        '''
        logging.info('-s' * 30 + '\n')
        retry = MIN_CHAT_HISTORY//2
        resp = f"Retry limit exceeded."
        history_static = copy.deepcopy(history)
        original_query = query
        while retry:
            try:
                resp = self.chain_fn.invoke({"query": query, "history": history_static})
                retry = 0
            except Exception as ai_message_error:
                ai_message, error = str(ai_message_error).split('|')
                '''
                Manually adding histories for re-tries. 
                This won't affect the main history which originates at the router. 
                '''
                history_static.append({
                    "role": "ai", 
                    "content": f"{ai_message.strip()}"
                    })
                query =  f"""The SQLite query you generated resulted in the following error when executed: "{error.strip()}".  
Please analyze the error, fix the issue, and regenerate a corrected SQLite query based on the original user request: "{original_query}".
                """
                retry -= 1
            return resp
    
    def one_shots(self):
        '''
        Contains a list of one shot examples.
        '''
        examples = [
            Document(
                page_content = f"""human: Count the number of errors with source as AMF?\nai: SELECT COUNT(*) FROM {TABLE_NAME} WHERE src LIKE 'AMF%';""",
                metadata = {"source": "manual_tmittra"}),
            Document(
                page_content = f"""human: Count the number of errors with destination as gNodeB?\nai: SELECT COUNT(*) FROM {TABLE_NAME} WHERE src LIKE 'gNodeB%';""",
                metadata = {"source": "manual_tmittra"})
            ]
        return examples

    def exec_query(self, query: str) -> str:
        '''
        This function executes a query on the SQLite db.
        Args:
            query (str): The query to be executed.
        Return:
            void
        '''
        try:
            logging.info(self.session.execute(text(query)).fetchall())
        except Exception as e:
            logging.info(str(e))


if __name__ == "__main__":
    sql_chain = Chain_Sql()
    # Query 1: Count the number of errors with destination as GNB?
    # Query 2: Display errors with destination as UDM?
    # Query 3: Count how many errors are there?
    
    # TEST 1 ~ Works 
    # sql_chain.exec_query(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE src LIKE 'AMF%';")

    # TEST 2 ~ Works 
    # Count the number of errors with destination as GNB?
    print(sql_chain.call_chain("Count the number of errors with destination as GNODEB?", []))