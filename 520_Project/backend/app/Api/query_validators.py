def sql_input_query_validator(qry):
    """
    Validates a user-provided natural language query for safety and format.

    Parameters:
        qry (str): The input query to validate.

    Returns:
        bool: True if the query is valid, otherwise False.

    Raises:
        ValueError: If the input query is not a string.
    """
    # List of potentially dangerous SQL keywords
    dangerous_keywords = {"DROP", "DELETE", "INSERT", "UPDATE", "TRUNCATE", "ALTER", "EXEC", "MERGE"}

    # Check if the input is a string
    if not isinstance(qry, str):
        raise ValueError("The query must be a string.")

    # Convert query to uppercase for case-insensitive keyword checking
    qry_upper = qry.upper()

    # Check for dangerous keywords
    if any(keyword in qry_upper for keyword in dangerous_keywords):
        return False

    return True

def pandas_input_query_validator(query):
    """
    Validates a user-provided Pandas query string for safety and format.

    Parameters:
        query (str): The Pandas query to validate.

    Returns:
        bool: True if the query is valid, otherwise False.

    Raises:
        ValueError: If the input query is not a string.
    """
    # List of potentially dangerous Pandas or Python expressions
    dangerous_keywords = {
        "exec", "eval", "import", "os", "sys", "__", "subprocess", "open", "shutil",
        "rm", "del", "exit", "globals", "locals"
    }

    # Check if the input is a string
    if not isinstance(query, str):
        raise ValueError("The query must be a string.")

    # Check for dangerous keywords
    query_lower = query.lower()
    if any(keyword in query_lower for keyword in dangerous_keywords):
        return False

    return True

