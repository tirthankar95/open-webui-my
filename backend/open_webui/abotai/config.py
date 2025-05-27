from pathlib import Path

# MONGO RELATED CONFIG
MONGO_HOST = "192.168.40.92"
MONGO_PORT = 27017
MONGO_COLLECTION = "abotai"
MONGO_DOCUMENT = "abot_ai_insights_stage"


# SQL 
SQL_PATH = Path(__file__).parent.parent.parent / "data"
DPX_MAIN_TABLE = "main_"
DPX_PROP_TABLE = "propagated_issues_"
DPX_IMSI_TABLE = "imsi_issues_"