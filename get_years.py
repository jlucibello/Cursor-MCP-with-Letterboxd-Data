import duckdb

results = duckdb.sql("SELECT Year, COUNT(*) as MovieCount FROM 'ratings.csv' GROUP BY Year ORDER BY Year").fetchall()

print("Year | Movies Watched")
print("-" * 25)
for year, count in results:
    print(f"{year} | {count}")
