from Chains.chain_base import Chains, MIN_CHAT_HISTORY
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI 
from langchain_core.output_parsers import StrOutputParser
from typing import List, Dict
import logging 
from models import LM_Models
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
from time import time 
class Chain_General(Chains):
    """Chain_General class is used to answer generic human queries that can't be answered using other chains."""
    def __init__(self) -> None:
        super().__init__()
        ## BUILD LangChain 
        self.prompt()
        self.model = LM_Models().lm_model
        self.chain_fn = self.prmpt | self.model | StrOutputParser() 

    def prompt(self):
        self.prmpt = ChatPromptTemplate.from_messages(
            [
                ("system", """You are an expert AI ai, who answers user's questions."""),
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
        resp = ""
        logging.info('-g' * 30 + '\n')
        logging.info(f'query: {query}\n')
        resp = self.chain_fn.invoke({"query": query, "history": history})
        return resp

    