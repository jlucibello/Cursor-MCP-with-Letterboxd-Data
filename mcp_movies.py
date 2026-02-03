# mcp_movies.py
import os
import duckdb
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP("Letterboxd-Local")

# This finds the folder where THIS script is saved
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "ratings.csv")

@mcp.tool()
def query_movies(query: str) -> str:
    """
    Run a SQL query against the Letterboxd dataset.
    Table name is 'ratings.csv'. Columns usually include: Date, Name, Year, Rating.
    You can write full SQL queries. If the query references 'ratings.csv', it will use the correct path.
    """
    try:
        # Replace 'ratings.csv' in the query with the full path if present
        # This allows users to write queries like "SELECT * FROM 'ratings.csv' WHERE Rating = 5"
        processed_query = query.replace("'ratings.csv'", f"'{CSV_PATH}'").replace('"ratings.csv"', f"'{CSV_PATH}'")
        
        # Execute the full SQL query
        result = duckdb.sql(processed_query).df()
        return result.to_string()
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()