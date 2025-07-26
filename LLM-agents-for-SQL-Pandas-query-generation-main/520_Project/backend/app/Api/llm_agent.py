import os
import sqlite3
import pandas as pd
import json

# Langchain imports
from langchain_openai import OpenAI
from sqlalchemy import create_engine
from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.chains import create_sql_query_chain
from sqlalchemy.sql import text
# query validators
from app.Api.query_validators import *
# Exceptions
from app.Api.exceptions import *

# Loading variables from .env file
from dotenv import load_dotenv
load_dotenv()

# LLM config variables
from app.Api.llm_agent_config import *

# Logger
from app.logger import logger

# pandas agent related functions
def query_pandas_agent(df, query):
    """
    Processes a string query on a pandas DataFrame using a language model agent.

    Validates the input DataFrame and query, invokes the agent to process the query, 
    and returns the result. The function raises exceptions for invalid input types 
    and an invalid query format.
    """
    if not isinstance(df, pd.core.frame.DataFrame):
        raise Exception("Invalid input. Please provide a pandas DataFrame")
    if not isinstance(query, str):
        raise Exception("Invalid input. Please provide a string query")
    
    # validate the given user query
    valid_query = pandas_input_query_validator(query)
    if not valid_query:
        raise InvalidInputQueryException()
    
    agent = create_pandas_dataframe_agent(OpenAI(model=PANDAS_LLM_MODEL, temperature=0), df, verbose=False,  allow_dangerous_code= True,
                                     return_intermediate_steps=True)
    prompt = PANDAS_AGENT_PROMPT.format(query=query)
    logger.info(prompt)
    res = agent.invoke(prompt)
    logger.info(res)
    return res

def process_pandas_result_to_json(res):
    """
    Converts the result of a pandas query into a JSON format.

    Extracts and formats the query result from the agent's response, determining 
    whether the result is a DataFrame or another type, and returns the result 
    as a JSON object with relevant metadata.
    """
    code = FULL_PYTHON_STARTER_CODE.strip() + '\n'+f"print({res['intermediate_steps'][0][0].dict()['tool_input']})"
    data = {
        "query": code
    }
    logger.info(res)
    data["is_table"] = True
    if(isinstance(res['intermediate_steps'][0][-1],pd.core.frame.DataFrame)):
        data["result"] = res['intermediate_steps'][0][-1].to_json()
    else:
        data["result"] = pd.DataFrame([{"Output": res['intermediate_steps'][0][-1]}]).to_json()
    return data

## SQL agent related functions
def csv_to_sqlite(df, db_file, table_name):
    """Converts a CSV file to an SQLite database table."""
    conn = sqlite3.connect(db_file)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

def query_sql_agent(df, query):
    """
    Executes an SQL query on a pandas DataFrame and returns the result in JSON format.

    Validates the input DataFrame and query, converts the DataFrame to an SQLite 
    database, runs the query using a language model, and formats the result as 
    a JSON object. The result includes whether the output is a table or a single value.
    """
    if not isinstance(df, pd.core.frame.DataFrame):
        raise Exception("Invalid input. Please provide a pandas DataFrame")
    if not isinstance(query, str):
        raise Exception("Invalid input. Please provide a string query")

    # validate the given user query
    valid_query = sql_input_query_validator(query)
    if not valid_query:
        raise InvalidInputQueryException()
    
    # convert to sqlite
    db_file = "temp_table.db"
    table_name = "temp_table"
    csv_to_sqlite(df, db_file, table_name)
    engine = create_engine(f"sqlite:///{db_file}")
    temp_db = SQLDatabase(engine)

    # run the query via langchain
    chain = create_sql_query_chain(ChatOpenAI(model=SQL_LLM_MODEL), temp_db)
    prompt = SQL_AGENT_PROMPT.format(query=query)
    logger.info(prompt)
    sql_res = chain.invoke({"question": prompt}).split('SQLQuery: ')[1]
    # output_str = temp_db.run(sql_res)

    # for converting database result in string format to json format
    sql_query = text(sql_res)
    with engine.connect() as connection:
        result = connection.execute(sql_query) 
        rows = result.fetchall()               # Fetch all rows
        columns = result.keys()                # Get the column names

    json_output = {}    
    json_output['is_table'] = True
    if len(rows) == 1 and len(columns) == 1:
        table_json = pd.DataFrame([{"Output": str(rows[0][0])}]).to_json()
        print(table_json)
    else:
        
        table_json = [dict(zip(columns, row)) for row in rows]
        table_df = pd.DataFrame(table_json)
        table_json = table_df.to_json()

    json_output['query'] = sql_res
    json_output['result'] = table_json
    os.remove(db_file)    

    return json_output
    