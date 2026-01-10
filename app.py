import os
import streamlit as st
from dotenv import load_dotenv

# --- LANGCHAIN IMPORTS ---
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool

# --- CUSTOM TOOLS ---
# Import our custom DSPy tool
from sql_engine import execute_sql_query

# Load Environment Variables
load_dotenv()

# --- 1. CACHED DATA SETUP ---
@st.cache_resource
def ensure_data_setup():
    """
    Checks if the database exists. If not, runs the setup script.
    Cached so it only checks once when the app starts.
    """
    if not os.path.exists("databricks_usage.db"):
        print("Data not found. Running setup first...")
        import data_setup
        data_setup.setup_data()
    return True

# --- 2. CACHED AGENT INITIALIZATION ---
@st.cache_resource
def init_agent():
    """
    Initializes the LLM, Tools, Vector DB, and Agent.
    Cached resource prevents reloading heavy models on every user interaction.
    """
    print("Initializing Databricks Customer Success Agent...")
    
    # --- A. Load Technical Documentation (RAG) ---
    print("Indexing Databricks Documentation...")
    # Use utf-8 to avoid encoding errors on Windows
    loader = TextLoader("tech_docs.txt", encoding="utf-8")
    documents = loader.load()
    
    # Standard text splitter
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)
    
    # Embeddings & Vector Store
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever()
    
    # Define the RAG Tool Function
    def technical_support(query: str):
        print(f" [Doc Search] Looking up feature details: '{query}'...")
        docs = retriever.invoke(query)
        return "\n".join([d.page_content for d in docs])

    # --- B. Define Tools ---
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

    # --- C. Initialize LLM (Groq) ---
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    # --- D. Create Agent (ReAct) ---
    # Pull the standard ReAct prompt from LangSmith Hub
    # --- D. Create Agent (ReAct) ---
    # 1. Pull the standard prompt
    prompt = hub.pull("hwchase17/react")
    
    # 2. INJECT THE "GIVE UP" INSTRUCTION
    # We append a critical instruction to the template telling the agent to stop looping.
    new_instruction = """
    IMPORTANT RULES:
    1. If the 'Observation' from a tool does not contain the answer, do NOT search again.
    2. Do NOT make up an answer.
    3. Instead, strictly return this Final Answer: "I apologize, but I do not have information about that topic in my current knowledge base."
    """
    
    # Append instructions to the beginning of the template
    prompt.template = new_instruction + prompt.template

    # 3. Create the Agent
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_parsing_errors=True,
        max_iterations=3  # Safety Net: Force stop after 3 failed attempts
    )
    
    return agent_executor


    # prompt = hub.pull("hwchase17/react")
    
    # agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    
    # agent_executor = AgentExecutor(
    #     agent=agent, 
    #     tools=tools, 
    #     verbose=True, 
    #     handle_parsing_errors=True  # Fixes the "Action: None" infinite loop
    # )
    
    # return agent_executor

# --- 3. STREAMLIT UI ---
def main():
    st.set_page_config(page_title="Enterprise AI Agent", page_icon="🤖")
    st.title("🤖 Enterprise AI Agent (Databricks)")
    st.markdown("Ask questions about **Databricks Usage (SQL)** or **Technical Docs (RAG)**.")

    # Step A: Ensure Data Exists
    ensure_data_setup()

    # Step B: Load the Agent (Cached)
    try:
        agent_executor = init_agent()
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        return

    # Step C: Chat Interface
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("How much did Acme Corp spend on Compute?"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                with st.spinner("Thinking..."):
                    # Invoke the agent
                    response = agent_executor.invoke({"input": prompt})
                    result_text = response["output"]
                
                message_placeholder.markdown(result_text)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": result_text})
                
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                message_placeholder.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()