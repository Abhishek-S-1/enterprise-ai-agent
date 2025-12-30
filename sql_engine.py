import dspy
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- FIX: Use dspy.LM with 'groq/' prefix ---
llama3 = dspy.LM(model='groq/llama-3.3-70b-versatile', api_key=GROQ_API_KEY)
dspy.settings.configure(lm=llama3)

# --- 1. Signature (The Persona) ---
class TextToSQL(dspy.Signature):
    """
    You are a Databricks Solutions Architect. 
    Transform natural language questions about customer consumption into SQLite queries.
    """
    question = dspy.InputField(desc="Question about usage, cost, or customers")
    schema = dspy.InputField(desc="The database schema")
    sql_query = dspy.OutputField(desc="The SQLite query. Output ONLY code.")

# --- 2. Module (The Logic) ---
class SQLGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_sql = dspy.ChainOfThought(TextToSQL)
        
        self.schema = """
        Table: usage_logs
        - account_id (TEXT)
        - customer_name (TEXT) e.g. 'Acme Corp'
        - sku_name (TEXT) e.g. 'Jobs Compute'
        - region (TEXT)
        - dbu_usage (REAL) e.g. 500.5
        - usage_date (TEXT)
        
        Table: pricing_skus
        - sku_name (TEXT)
        - price_per_dbu (REAL)
        
        Hint: To calculate cost, JOIN tables on sku_name and multiply dbu_usage * price_per_dbu.
        """

    def forward(self, question):
        return self.generate_sql(question=question, schema=self.schema)

# --- 3. Execution Tool ---
def execute_sql_query(question: str):
    print(f"\n   🧠 [DSPy Architect] Thinking: '{question}'...")
    
    generator = SQLGenerator()
    result = generator(question=question)
    
    # Clean up output
    raw_sql = result.sql_query
    cleaned_sql = raw_sql.replace("```sql", "").replace("```", "").strip()
    
    print(f"   💻 [Generated SQL] {cleaned_sql}")
    
    conn = sqlite3.connect("databricks_usage.db")
    try:
        cursor = conn.execute(cleaned_sql)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        return f"SQL: {cleaned_sql}\nResult: {rows}\nColumns: {columns}"
    except Exception as e:
        return f"SQL Error: {e}"