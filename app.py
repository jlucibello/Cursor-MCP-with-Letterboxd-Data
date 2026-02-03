from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import duckdb
import os
from datetime import datetime, date
from nl_to_sql import natural_language_to_sql

app = Flask(__name__)
CORS(app)

# Get the path to ratings.csv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "ratings.csv")

def execute_query(query: str, is_natural_language: bool = True):
    """Execute a query - converts natural language to SQL if needed"""
    try:
        # Convert natural language to SQL if needed
        if is_natural_language:
            sql_query = natural_language_to_sql(query, CSV_PATH)
            if sql_query is None:
                return {
                    "success": False,
                    "error": f"Could not understand your query. Try phrases like:\n- 'Show me 10 movies'\n- 'Movies rated 5 stars'\n- 'Movies from 2024'\n- 'Movies per year'"
                }
        else:
            sql_query = query
        
        # Replace 'ratings.csv' in the query with the full path if present
        processed_query = sql_query.replace("'ratings.csv'", f"'{CSV_PATH}'").replace('"ratings.csv"', f"'{CSV_PATH}'")
        
        # Execute the query
        result = duckdb.sql(processed_query).df()
        
        # Convert Timestamp and date objects to strings for JSON serialization
        def convert_to_serializable(obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            elif hasattr(obj, 'isoformat'):  # Handle pandas Timestamp
                return obj.isoformat()
            return obj
        
        # Convert dataframe to records and serialize dates
        records = result.to_dict('records')
        for record in records:
            for key, value in record.items():
                record[key] = convert_to_serializable(value)
        
        # Convert to dictionary for JSON response
        return {
            "success": True,
            "data": records,
            "columns": list(result.columns),
            "row_count": len(result)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def query():
    """API endpoint to execute natural language queries"""
    try:
        if not request.is_json:
            return jsonify({"success": False, "error": "Request must be JSON"}), 400
        
        data = request.get_json()
        if data is None:
            return jsonify({"success": False, "error": "Invalid JSON in request"}), 400
        
        query_text = data.get('query', '')
        is_natural_language = data.get('natural_language', True)
        
        if not query_text:
            return jsonify({"success": False, "error": "No query provided"}), 400
        
        result = execute_query(query_text, is_natural_language)
        return jsonify(result)
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error in /api/query: {error_msg}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": f"Server error: {error_msg}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='127.0.0.1')
