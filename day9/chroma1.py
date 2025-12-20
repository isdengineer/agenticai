import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# --- 1. INDEXING PHASE: Setup ChromaDB ---
# Define the data
documents = [
    Document(page_content="The new project codename is 'Atlas'. It focuses on cloud infrastructure."),
    Document(page_content="Atlas development started in Q3 2024. The budget is $5 million."),
    Document(page_content="All internal documentation can be found on the SharePoint portal."),
]

# 1a. Initialize local Ollama Embeddings
ollama_embeddings = OllamaEmbeddings(model="nomic-embed-text") 

# 1b. Create or Load the ChromaDB Vectorstore
# We create a new collection in a local directory
vectordb = Chroma.from_documents(
    documents=documents, 
    embedding=ollama_embeddings, 
    collection_name="basic_rag_collection",
    persist_directory="./chroma_db_basic"
)
# Create a retriever for searching the database
retriever = vectordb.as_retriever(search_kwargs={"k": 2})

# --- 2. QUERY PHASE: Define the RAG Chain with LCEL ---

# 2a. Initialize the local Ollama LLM
llm = ChatOllama(model="llama3", temperature=0)

# 2b. Define the RAG Prompt Template
RAG_PROMPT = """
You are a project assistant. Answer the user's question only based on the following context. 
If the information is not available in the context, state that clearly.

CONTEXT:
{context}

QUESTION: {question}
"""
rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT)

# 2c. Define the RAG Chain using LCEL (The pipe syntax)
rag_chain = (
    # Step 1: Prepare the inputs for the next stage (RunnablePassthrough)
    {
        # 'context': This key runs the retriever, which searches ChromaDB
        "context": retriever, 
        # 'question': This key passes the original user input through
        "question": RunnablePassthrough() 
    }
    # Step 2: Pass structured input to the prompt template
    | rag_prompt
    # Step 3: Pass the compiled prompt to the LLM (Ollama)
    | llm
    # Step 4: Convert the LLM's response object into a simple string
    | StrOutputParser()
)

# --- 3. EXECUTION ---
query = "When did development for the Atlas project begin and what is its budget?"

print(f"--- Querying Simple RAG Chain ---")
print(f"User Query: {query}")
print("-" * 30)

final_answer = rag_chain.invoke(query)

print(f"\n✅ LLM (Ollama) Answer:")
print(final_answer)

# Clean up the files created for the demo
# os.system("rm -rf ./chroma_db_basic")