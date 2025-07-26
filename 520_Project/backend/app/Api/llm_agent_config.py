# constants
PANDAS_AGENT_PROMPT = "Give me the pandas code to get answer to the query: {query}"
SQL_AGENT_PROMPT = "Give me the SQL code to get answer to the following query. Do not select specific columns unless I ask you to do so. If I do not specify the number of rows, then assume that I want all such rows i.e. DO NOT USE LIMIT UNLESS I SPECIFY A NUMBER: {query}"

FULL_PYTHON_STARTER_CODE = """import pandas as pd

df = pd.read_csv("filename.csv")"""

PANDAS_LLM_MODEL = "gpt-3.5-turbo-instruct"
SQL_LLM_MODEL = "gpt-4o-mini"