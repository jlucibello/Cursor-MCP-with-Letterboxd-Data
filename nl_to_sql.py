import re
from typing import Optional

def natural_language_to_sql(query: str, csv_path: str = "ratings.csv") -> str:
    """
    Convert natural language queries to SQL.
    Handles common patterns for movie queries.
    """
    query_lower = query.lower().strip()
    
    # Pattern: "show me [X] movies" or "find [X] movies"
    match = re.search(r'(show|find|list|get|give me)\s+(me\s+)?(\d+)\s+movies?', query_lower)
    if match:
        limit = match.group(3)
        return f"SELECT * FROM '{csv_path}' ORDER BY Date DESC LIMIT {limit}"
    
    # Pattern: "top [X] movies" or "best [X] movies"
    match = re.search(r'(top|best)\s+(\d+)\s+movies?', query_lower)
    if match:
        limit = match.group(2)
        return f"SELECT * FROM '{csv_path}' ORDER BY Rating DESC, Date DESC LIMIT {limit}"
    
    # Pattern: "movies rated [X] stars" or "X star movies"
    match = re.search(r'(rated|with|of)\s+(\d+(?:\.\d+)?)\s+stars?|(\d+(?:\.\d+)?)\s+star\s+movies?', query_lower)
    if match:
        rating = match.group(2) or match.group(3)
        return f"SELECT * FROM '{csv_path}' WHERE Rating = {rating} ORDER BY Date DESC"
    
    # Pattern: "5 star movies" (number first)
    match = re.search(r'^(\d+(?:\.\d+)?)\s+star\s+movies?', query_lower)
    if match:
        rating = match.group(1)
        return f"SELECT * FROM '{csv_path}' WHERE Rating = {rating} ORDER BY Date DESC"
    
    # Pattern: "movies from [year]" or "movies in [year]"
    match = re.search(r'(from|in|during)\s+(\d{4})', query_lower)
    if match:
        year = match.group(2)
        return f"SELECT * FROM '{csv_path}' WHERE Year = {year} ORDER BY Date DESC"
    
    # Pattern: "movies watched in [year]"
    match = re.search(r'watched\s+(in|during|on)\s+(\d{4})', query_lower)
    if match:
        year = match.group(2)
        return f"SELECT * FROM '{csv_path}' WHERE Year = {year} ORDER BY Date DESC"
    
    # Pattern: "all [year] movies" or "list of [year] movies"
    match = re.search(r'(all|list of)\s+(\d{4})\s+movies?', query_lower)
    if match:
        year = match.group(2)
        return f"SELECT * FROM '{csv_path}' WHERE Year = {year} ORDER BY Date DESC"
    
    # Pattern: "last [X] movies" or "recent [X] movies"
    match = re.search(r'(last|recent|latest)\s+(\d+)\s+movies?', query_lower)
    if match:
        limit = match.group(2)
        return f"SELECT Name, Year, Rating, Date FROM '{csv_path}' ORDER BY Date DESC LIMIT {limit}"
    
    # Pattern: "movies per year" or "watched per year"
    if 'per year' in query_lower or 'by year' in query_lower or 'each year' in query_lower:
        return f"SELECT Year, COUNT(*) as MovieCount FROM '{csv_path}' GROUP BY Year ORDER BY Year"
    
    # Pattern: "rating distribution" or "ratings breakdown"
    if 'rating' in query_lower and ('distribution' in query_lower or 'breakdown' in query_lower):
        return f"SELECT Rating, COUNT(*) as Count FROM '{csv_path}' GROUP BY Rating ORDER BY Rating DESC"
    
    # Pattern: "average rating" or "my average rating"
    if 'average' in query_lower and 'rating' in query_lower:
        return f"SELECT AVG(Rating) as AverageRating FROM '{csv_path}'"
    
    # Pattern: "total movies" or "how many movies"
    if 'total' in query_lower and 'movies' in query_lower or 'how many movies' in query_lower:
        return f"SELECT COUNT(*) as TotalMovies FROM '{csv_path}'"
    
    # Pattern: "movies with [rating] or higher" or "movies rated [X] or above"
    match = re.search(r'(\d+(?:\.\d+)?)\s+or\s+(higher|above|more|up)', query_lower)
    if match:
        rating = match.group(1)
        return f"SELECT * FROM '{csv_path}' WHERE Rating >= {rating} ORDER BY Rating DESC, Date DESC"
    
    # Pattern: "movies with [rating] or lower" or "movies rated [X] or below"
    match = re.search(r'(\d+(?:\.\d+)?)\s+or\s+(lower|below|less|down)', query_lower)
    if match:
        rating = match.group(1)
        return f"SELECT * FROM '{csv_path}' WHERE Rating <= {rating} ORDER BY Rating DESC, Date DESC"
    
    # Pattern: "movies between [X] and [Y] stars"
    match = re.search(r'between\s+(\d+(?:\.\d+)?)\s+and\s+(\d+(?:\.\d+)?)', query_lower)
    if match:
        min_rating = match.group(1)
        max_rating = match.group(2)
        return f"SELECT * FROM '{csv_path}' WHERE Rating >= {min_rating} AND Rating <= {max_rating} ORDER BY Rating DESC, Date DESC"
    
    # Pattern: "movies from [year] to [year]" or "movies between [year] and [year]"
    match = re.search(r'(from|between)\s+(\d{4})\s+(to|and)\s+(\d{4})', query_lower)
    if match:
        year1 = match.group(2)
        year2 = match.group(4)
        return f"SELECT * FROM '{csv_path}' WHERE Year >= {year1} AND Year <= {year2} ORDER BY Year, Date DESC"
    
    # Pattern: "movies with [text] in the name" or "movies called [text]"
    match = re.search(r'(with|called|named|titled)\s+["\']?([^"\']+)["\']?\s+(in\s+)?(the\s+)?name', query_lower)
    if match:
        text = match.group(2).strip()
        return f"SELECT * FROM '{csv_path}' WHERE Name LIKE '%{text}%' ORDER BY Date DESC"
    
    # Pattern: "movies like [text]" or "movies containing [text]"
    match = re.search(r'(like|containing|with)\s+["\']?([^"\']+)["\']?$', query_lower)
    if match:
        text = match.group(2).strip()
        return f"SELECT * FROM '{csv_path}' WHERE Name LIKE '%{text}%' ORDER BY Date DESC"
    
    # Pattern: "highest rated movies" or "best rated movies"
    if 'highest' in query_lower or 'best rated' in query_lower:
        match = re.search(r'(\d+)', query_lower)
        limit = match.group(1) if match else "10"
        return f"SELECT * FROM '{csv_path}' ORDER BY Rating DESC, Date DESC LIMIT {limit}"
    
    # Pattern: "lowest rated movies" or "worst rated movies"
    if 'lowest' in query_lower or 'worst rated' in query_lower:
        match = re.search(r'(\d+)', query_lower)
        limit = match.group(1) if match else "10"
        return f"SELECT * FROM '{csv_path}' WHERE Rating > 0 ORDER BY Rating ASC, Date DESC LIMIT {limit}"
    
    # Pattern: "most recent movies" or "recently watched"
    if 'recent' in query_lower or 'latest' in query_lower:
        match = re.search(r'(\d+)', query_lower)
        limit = match.group(1) if match else "10"
        return f"SELECT Name, Year, Rating, Date FROM '{csv_path}' ORDER BY Date DESC LIMIT {limit}"
    
    # Pattern: "oldest movies" or "earliest movies"
    if 'oldest' in query_lower or 'earliest' in query_lower:
        match = re.search(r'(\d+)', query_lower)
        limit = match.group(1) if match else "10"
        return f"SELECT Name, Year, Rating, Date FROM '{csv_path}' ORDER BY Date ASC LIMIT {limit}"
    
    # Default: try to extract any SQL-like patterns or return a helpful error
    # If the query looks like it might already be SQL, return it as-is
    if any(keyword in query_lower for keyword in ['select', 'from', 'where', 'order by', 'group by']):
        return query  # Assume it's already SQL
    
    # If we can't parse it, return None
    return None
