import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain import hub

# --- CORRECT IMPORTS FOR STABLE STACK (v0.1.20) ---
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool

# Import our custom DSPy tool
from sql_engine import execute_sql_query

load_dotenv()

def init_agent():
    print("Initializing Databricks Customer Success Agent...")
    
    # --- 1. Load Technical Documentation ---
    print("Indexing Databricks Documentation...")
    # Use utf-8 to avoid encoding errors on Windows
    loader = TextLoader("tech_docs.txt", encoding="utf-8")
    documents = loader.load()
    
    # Standard text splitter
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever()
    
    def technical_support(query: str):
        print(f" [Doc Search] Looking up feature details: '{query}'...")
        docs = retriever.invoke(query)
        return "\n".join([d.page_content for d in docs])

    # --- 2. Define Tools ---
    tools = [
        Tool(
            name="Consumption_Analyst",
            func=execute_sql_query,
            description="Use this for quantitative questions about DBUs, cost, pricing, or customer usage."
        ),
        Tool(
            name="Technical_Support",
            func=technical_support,
            description="Use this for qualitative questions about Unity Catalog, DLT, features, or best practices."
        )
    ]

    # --- 3. Initialize LLM (Groq) ---
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    # --- 4. Create Agent (ReAct) ---
    # Pull the standard ReAct prompt from LangSmith Hub
    prompt = hub.pull("hwchase17/react")
    
    # Use create_react_agent instead of create_tool_calling_agent
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_parsing_errors=True
    )
    
    return agent_executor

if __name__ == "__main__":
    # Check if data exists
    if not os.path.exists("databricks_usage.db"):
        print("  Data not found. Running setup first...")
        import data_setup
        data_setup.setup_data()
        
    agent_executor = init_agent()
    
    print("\n Agent Ready. (Context: Databricks Usage & Features)")
    print("------------------------------------------------------")
    
    # --- DEMO QUESTION 1: SQL (DSPy) ---
    q1 = "Which customer spent the most money on Compute?"
    print(f"\n>> Manager: {q1}")
    result1 = agent_executor.invoke({"input": q1})
    
    # --- DEMO QUESTION 2: RAG (Docs) ---
    q2 = "What is the best practice for data governance?"
    print(f"\n>> Manager: {q2}")
    result2 = agent_executor.invoke({"input": q2})
