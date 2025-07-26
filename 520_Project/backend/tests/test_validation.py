import pytest
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app/Api')))
from llm_agent import *
from query_validators import *
import pandas as pd

# test SQL query validation for dangerous keywords
def test_sql_validation():
    assert sql_input_query_validator("SELECT * FROM table") == True
    assert sql_input_query_validator("DELETE FROM table") == False
    assert sql_input_query_validator("DROP TABLE table") == False
    assert sql_input_query_validator("INSERT INTO table") == False
    assert sql_input_query_validator("UPDATE table SET column = value") == False
    assert sql_input_query_validator("TRUNCATE TABLE table") == False
    assert sql_input_query_validator("ALTER TABLE table ADD column") == False
    assert sql_input_query_validator("EXEC sp_name") == False
    assert sql_input_query_validator("MERGE INTO table USING table") == False

# test Pandas query validation for dangerous keywords
def test_pandas_validation():
    assert pandas_input_query_validator("df") == True
    assert pandas_input_query_validator("rm -rf /") == False
    assert pandas_input_query_validator("import os") == False
    assert pandas_input_query_validator("import sys") == False
    assert pandas_input_query_validator("os.system('rm -rf /')") == False
    assert pandas_input_query_validator("del df") == False
    assert pandas_input_query_validator("shutil.rmtree('path')") == False
    assert pandas_input_query_validator("with open('file.txt', 'w') as f: f.write('data')") == False
    assert pandas_input_query_validator("exit()") == False
    assert pandas_input_query_validator("globals()") == False
    assert pandas_input_query_validator("locals()") == False
    assert pandas_input_query_validator("subprocess.run('ls')") == False

# test SQL query validation by attempting to run dangerous queries with the LLM agent
def test_sql_validation_real():
    df = pd.read_csv("https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv")
    queries = ["delete rows where age is 21",
               "drop the table",
               "insert new row for a person named John",
               "update John's age to 22",
               "truncate the table",
               "alter the table by adding a new column",
               "execute a stored procedure",
               "merge two tables"]
    for query in queries:
        with pytest.raises(InvalidInputQueryException):
            query_sql_agent(df, query)

# test Pandas query validation by attempting to run dangerous queries with the LLM agent
def test_pandas_validation_real():
    df = pd.read_csv("https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv")
    queries = ["delete rows where age is 21",
               "delete the file named 'file.txt'",
               "import os",
               "import sys",
               "os.system('rm -rf /')",
               "delete the directory named files",
               "open a file and write data",
               "exit the program",
               "run subprocess.run('ls')"]
    for query in queries:
        with pytest.raises(InvalidInputQueryException):
            query_pandas_agent(df, query)