from Chains.chain_base import Chains
from Chains.chain_base import MIN_CHAT_HISTORY
from Chains.chain_sql import Chain_Sql
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
MAX_RESP_BEAUTIFY_LEN = 75000

class ChainRouter(Chains):
    def __init__(self, chat_id: str) -> None:
        super().__init__()
        ## Init LM models & prompt
        self.all_lm_models = LM_Models()
        self.prompt()
        ## Init Chains
        self.sql_chain = Chain_Sql(chat_id)
        self.general_chain = Chain_General()
        self.chain_fn = self.prmpt | self.all_lm_models.lm_model | StrOutputParser()
        self.chain_bn = self.prmpt_beautify | self.all_lm_models.lm_model | StrOutputParser()

    def prompt(self):
        '''
        Prompt for the LLM.
        '''
        self.prmpt = ChatPromptTemplate.from_messages(
            [
                ("system", f"""You are a planner responsible for determining which chains to invoke in order to solve a user's query.
Only print the chain names and the sequence in which they should be invoked.
These are the chains you can use:
1. {Chain_Sql.__doc__}
2. {Chain_General.__doc__}
"""),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{query}")
            ]
        )
        self.prmpt_beautify = ChatPromptTemplate.from_messages([
                    ("system", 
                    """You are a helpful assistant specialized in formatting responses. 
        The original response to the query "{query}" was:
        {response}

        Please improve the readability of the response:
        - If it is JSON, first try to present it in a table or sentence if not possible format it with proper indentation.
        - Use Markdown to structure the response where applicable (e.g., lists, headers).
        - Add relevant emojis to make it more engaging, but keep it professional.
        - Ensure overall clarity and neatness.
        
        Respond only with the formatted output. Avoid any introductory or explanatory statements."""
                    )
                ])
    
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
            if function_call == "Chain_Sql":
                resp += self.sql_chain.call_chain(user_query, history)
            else: # Chain_General(default) no check is needed as it's a fallback
                resp += self.general_chain.call_chain(user_query, history)
        logging.info(f'[RESPONSE] ------------> {resp}')
        # I don't want to send too big of a response data to be beautified.
        # Response from SQLite to an user query can sometimes be very big.
        if len(resp) > MAX_RESP_BEAUTIFY_LEN: return resp
        return self.chain_bn.invoke({
            "query": user_query,
            "response": resp
        })
        
if __name__ == "__main__":
    router = ChainRouter("f0b01200b8ae417087950e0e8150c4e6")
    print(router.call_chain("What is the capital of France?"))
    print(router.call_chain("List out all errors by NGAP protocol?"))