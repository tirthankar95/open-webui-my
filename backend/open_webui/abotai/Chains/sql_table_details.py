
def fetch_table_details(MAIN_TABLE, PROP_TABLE, IMSI_TABLE):
    deepX_schema = f"""
There are three tables {MAIN_TABLE}, {PROP_TABLE}, {IMSI_TABLE} you have to use. 
1. {MAIN_TABLE} : Each row in this table represents an error that occurred between two nodes in a mobile network.   
2. {PROP_TABLE} : This table contains the error that was propagated from dst_node of {MAIN_TABLE} to the next network node.
3. {IMSI_TABLE} : This table contains the IMSI information where error corresponding to {MAIN_TABLE} occured.
Each entry in the row is an error.

#1. TABLE {MAIN_TABLE}
    id = A unique identifier for the record, a UUID or hash string.
    src_node = The name of the source node in a mobile network(e.g. UDR, UDM, GNODEB, AMF, SMF) where the error occurred.
    src_ip = The IP address of the source node.
    src_port = The port number of the source (could be numeric or named like http).
    dst_node = The name of the destination node (e.g. UDR, UDM, GNODEB, AMF, SMF).
    dst_ip = The IP address of the destination node.
    dst_port = The port number of the destination node.
    inference = The type of error that occurred b/w src_node and dst_node. 
    src_interface =  Refers to the source interface from which a message or procedure originates. (e.g. N1 Interface between UE and AMF)
    dst_interface = Refers to the destination interface from which a message or procedure originates. (e.g. N2 Interface between AMF and gNB)
    protocol = The type of network protocol that was used for communication between src_node and dst_node (e.g. NGAP, HTTP, SCTP).
    procedure = What the UE or network is trying to do (e.g., establish a PDU session).
    procedure_type = How that procedure was handled (e.g., success, reject, handover, etc.)
    procedure_onset_timestamp = 
    timestamp =
    pcap_insight =  This is a detailed human readable description of the error that occurred b/w src_node and dst_node.
    message =
    ie =
    value = 


#2. TABLE {PROP_TABLE}
    id = A unique identifier for the record, a UUID or hash string.
    source_issue = This is a foreign key that links to the id column in the {MAIN_TABLE}.
    protocol = The type of network protocol used to propagate the error. 
    src_node = The name of the source node of the next network node where the error was propagated to from the dst_node of {MAIN_TABLE}.
    status = status code if the protocol is HTTP. 
    src_interface =  Refers to the source interface from which a message or procedure originates. (e.g. N1 Interface between UE and AMF)
    dst_node = The name of the destination node of the next network node where the error was propagated to from the dst_node of {MAIN_TABLE}.
    dst_interface = Refers to the destination interface from which a message or procedure originates. (e.g. N2 Interface between AMF and gNB)
    pcap_insight = This is a detailed human readable description of the propagated error.
    response_code_description = 
    nf_service = 
    service_operation =
    operation_id = 
    callback_type = 
    url_route = 
    method = 

#3. TABLE {IMSI_TABLE}
    id = A unique identifier for the record, a UUID or hash string.
    source_issue = This is a foreign key that links to the id column in the {MAIN_TABLE}.
    imsi =  The International Mobile Subscriber Identity(IMSI) where the error occured.
    timestamp = The timestamp when the error occured for the IMSI. 

"""
    return deepX_schema


if __name__ == "__main__":
    # Example usage
    MAIN_TABLE = "main_x"
    PROP_TABLE = "propagated_x"
    IMSI_TABLE = "imsi_x"
    
    details = fetch_table_details(MAIN_TABLE, PROP_TABLE, IMSI_TABLE)
    print(details)