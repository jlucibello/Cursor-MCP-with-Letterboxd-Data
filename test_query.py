from mcp_movies import query_movies

# Test with a full SQL query
result = query_movies("SELECT Name, Year FROM 'ratings.csv' WHERE Rating = 5 ORDER BY Date DESC LIMIT 3")
print(result)
