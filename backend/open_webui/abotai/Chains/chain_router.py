from Chains.chain_base import Chains
from Chains.chain_base import MIN_CHAT_HISTORY
from Chains.chain_mongo import Chain_Mongo
from Chains.chain_general import Chain_General
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from models import LM_Models
import logging 
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
from typing import List, Dict
from abot_utils import match

class ChainRouter(Chains):
    def __init__(self) -> None:
        super().__init__()
        ## Init LM models & prompt
        self.all_lm_models = LM_Models()
        self.prompt()
        ## Init Chains
        self.mongo_chain = Chain_Mongo()
        self.general_chain = Chain_General()
        self.chain_fn = self.prmpt | self.all_lm_models.lm_model | StrOutputParser()

    def prompt(self):
        '''
        Prompt for the LLM.
        '''
        self.prmpt = ChatPromptTemplate.from_messages(
            [
                ("system", f"""You are a planner responsible for determining which chains to invoke in order to solve a user's query.
You are not allowed output anything else other than the chain names and the sequence in which they should be invoked.
These are the chains you can use:
1. {Chain_Mongo.__doc__}
2. {Chain_General.__doc__}
"""),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{query}")
            ]
        )
    
    def call_chain(self, query: str, history_un: List[Dict]) -> str:
        '''
        This function calls the lang chain for a specific child class.
        Args:
            query (str): The human query that will be passed to the LLM chain.
        Return:
            output (str): The output string from the LLM chain.
        '''
        resp = ""
        function_calls = []
        history, user_query = query[-(MIN_CHAT_HISTORY+1):-1], query[-1]['content']
        logging.info('-r' * 30 + '\n')
        logging.info(f'[QUERY] ------------> {user_query}')
        function_calls = self.chain_fn.invoke({"query": user_query, "history": history})
        function_calls = match(function_calls)
        logging.info(f'[PLAN] ------------> {function_calls}')
        for function_call in function_calls:
            if function_call == "Chain_Mongo":
                resp = self.mongo_chain.call_chain(user_query, history)
            else: # Chain_General(default) no check is needed as it's a fallback
                resp = self.general_chain.call_chain(user_query, history)
        logging.info(f'[RESPONSE] ------------> {resp}')
        return resp   
        
if __name__ == "__main__":
    import gradio as gr 
    router = ChainRouter()
    print(router.call_chain("What is the capital of France?"))
    print(router.call_chain("Count the number of errors with destination as GNB?"))