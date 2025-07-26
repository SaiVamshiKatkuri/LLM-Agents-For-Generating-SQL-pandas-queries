import json
import pytest
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app/Api')))
from llm_agent import *
import pandas as pd

# creates an sqlite database from a simple pandas dataframe and checks if the data is correct
def test_csv_to_sqlite():
    df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    db_file = "temp_table.db"
    table_name = "temp_table"
    csv_to_sqlite(df, db_file, table_name)
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table_name}")
    rows = c.fetchall()
    assert rows == [(1, 3), (2, 4)]
    conn.close()
    os.remove(db_file)

# test the LLM agent for SQL query generation using queries and answers from the questions.json file
def test_query_sql_agent1():
    df = pd.read_csv("https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv")
    with open('questions.json', 'r') as f:
        queries = json.load(f)
    for query, gt in queries.items():
        sql_data = query_sql_agent(df, query)
        if type(gt) == list:
            ans = json.loads(sql_data['result'])['PassengerId'].values()
            assert set(gt) == set(ans)
        else:
            ans = json.loads(sql_data['result'])['Output']['0']
            assert str(gt).lower() in ans.lower()

# this should return an exception because the dataframe is not a pandas dataframe
def test_query_sql_agent_fail1():
    df = {}
    query = "filter rows where age > 21"
    with pytest.raises(Exception):
        sql_data = query_sql_agent(df, query)

# this should return an exception because the query is not a string
def test_query_sql_agent_fail2():
    df = pd.read_csv("https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv")
    query = 123
    with pytest.raises(Exception):
        sql_data = query_sql_agent(df, query)