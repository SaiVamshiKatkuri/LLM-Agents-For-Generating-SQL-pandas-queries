import json
import pytest
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app/Api')))
from llm_agent import *
import pandas as pd

# test the LLM agent for pandas query generation using queries and answers from the questions.json file
def test_query_pandas_agent():
    df = pd.read_csv("https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv")
    with open('questions.json', 'r') as f:
        queries = json.load(f)
    for query, gt in queries.items():
        pandas_data = query_pandas_agent(df, query)
        if type(gt) == list:
            ans = pandas_data['intermediate_steps'][0][1]['PassengerId']
            assert set(gt) == set(ans)
        else:
            ans = pandas_data['output']
            assert str(gt).lower() in ans.lower()

# this should return an exception because the dataframe is not a pandas dataframe
def test_query_pandas_agent_fail1():
    df = {}
    query = "filter rows where age > 21"
    with pytest.raises(Exception):
        pandas_data = query_pandas_agent(df, query)

# this should return an exception because the query is not a string
def test_query_pandas_agent_fail2():
    df = pd.read_csv("https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv")
    query = 123
    with pytest.raises(Exception):
        pandas_data = query_pandas_agent(df, query)
