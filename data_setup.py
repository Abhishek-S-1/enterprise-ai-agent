import sqlite3
import pandas as pd
import os

def setup_data():
    print("⚙️  Setting up Databricks Usage Lakehouse...")
    
    # --- 1. Create SQL Database (Customer Usage Data) ---
    conn = sqlite3.connect("databricks_usage.db")
    
    # Table 1: Customer Usage Logs (Who is using what?)
    # DBU = Databricks Unit (The currency of Databricks)
    usage_data = {
        'account_id': ['ACC-101', 'ACC-102', 'ACC-103', 'ACC-101', 'ACC-104', 'ACC-102'],
        'customer_name': ['Acme Corp', 'TechFlow Inc', 'Global Bank', 'Acme Corp', 'StartUp.ai', 'TechFlow Inc'],
        'sku_name': ['Jobs Compute', 'All-Purpose Compute', 'Serverless SQL', 'Model Serving', 'Jobs Compute', 'DLT Core'],
        'region': ['us-east-1', 'us-west-2', 'eu-central-1', 'us-east-1', 'ap-south-1', 'us-west-2'],
        'dbu_usage': [5000.5, 120.0, 3500.2, 450.0, 150.0, 800.0],
        'usage_date': ['2025-01-01', '2025-01-01', '2025-01-02', '2025-01-03', '2025-01-02', '2025-01-03']
    }
    
    # Table 2: Pricing Reference (Mock Pricing)
    pricing_data = {
        'sku_name': ['Jobs Compute', 'All-Purpose Compute', 'Serverless SQL', 'Model Serving', 'DLT Core'],
        'price_per_dbu': [0.15, 0.55, 0.70, 0.50, 0.20] # Mock pricing in USD
    }
    
    pd.DataFrame(usage_data).to_sql('usage_logs', conn, if_exists='replace', index=False)
    pd.DataFrame(pricing_data).to_sql('pricing_skus', conn, if_exists='replace', index=False)
    
    conn.close()
    print("✅ SQL Database 'databricks_usage.db' ready.")

    # --- 2. Create Technical Docs (Unstructured Data) ---
    # We simulate the official Databricks Documentation
    tech_docs = """
    DATABRICKS PLATFORM DOCUMENTATION (2025)
    
    1. UNITY CATALOG (Governance):
       - Unity Catalog provides centralized access control, auditing, lineage, and data discovery across Databricks workspaces.
       - Key Feature: 'Lakehouse Federation' allows querying external databases (PostgreSQL, Snowflake) without moving data.
       - Best Practice: Use 'Managed Identities' for secure access to storage buckets (S3/ADLS).
       
    2. DELTA LIVE TABLES (ETL):
       - DLT is a declarative framework for building reliable data pipelines.
       - It automatically handles infrastructure scaling and data quality checks (expectations).
       - 'Enforcement' rule: DROP ROW creates a quarantine for bad data rather than failing the pipeline.
       
    3. MODEL SERVING (Mosaic AI):
       - Databricks Model Serving allows you to deploy LLMs and Scikit-learn models as REST APIs.
       - Supports 'Provisioned Throughput' for guaranteed latency on Llama 3 models.
       - Zero-copy model deployment using MLflow Registry.
       
    4. COST OPTIMIZATION:
       - Use 'Jobs Compute' for automated workflows (cheaper than All-Purpose).
       - Enable 'Serverless SQL' to avoid paying for idle cluster time.
    """
    
    with open("tech_docs.txt", "w", encoding="utf-8") as f:
        f.write(tech_docs)
    print("✅ Knowledge Base 'tech_docs.txt' ready.")

if __name__ == "__main__":
    setup_data()