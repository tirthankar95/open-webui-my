chain_names = ["Chain_General", 
               "Chain_Mongo"]

def is_match(big_string: str, idx: int) -> str:
    for pattern in chain_names:
        sz, sz_pattern = len(big_string), len(pattern)
        jdx = idx 
        pattern_idx = 0
        while pattern_idx < sz_pattern and idx < sz:
            if big_string[idx] != pattern[pattern_idx]:
                break 
            idx += 1
            pattern_idx += 1
        idx = jdx 
        if pattern_idx == sz_pattern: return pattern 
    return ""

def match(big_string):
    chains = []
    for idx, ch in enumerate(big_string):
        if ch == "C":
            response = is_match(big_string, idx)
            print(idx, response)
            if response != "": chains.append(response)
    if len(chains) == 0: return ["Chain_General"]
    return chains