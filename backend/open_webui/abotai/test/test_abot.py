import sys 
import os 
parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_path)
from abot_utils import match 

def test_pattern_chain_match():
    sentence1 = "{Chain_General} is a general chain."
    assert match(sentence1) == ['Chain_General']
    
    sentence2 = "Chain_Mongo is a database access Chain."
    assert match(sentence2) == ['Chain_Mongo']
    
    sentence3 = "Call Chain_General, Chain_Mongo then Chain_General.Chain_genera"
    assert match(sentence3) == ['Chain_General', 'Chain_Mongo', 'Chain_General']
    
    senetence4 = "You will not find any chain here."
    assert match(senetence4) == ["Chain_General"]
