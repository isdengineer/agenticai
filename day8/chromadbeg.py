import os
import shutil
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
# --- FIX 1: Updated import for create_retrieval_chain ---
from langchain_classic.chains.retrieval import create_retrieval_chain
# --- FIX 2: Updated import for create_stuff_documents_chain ---
from langchain_classic.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

# --- Configuration ---
OLLAMA_LLM_MODEL = "mistral"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text" 
CHROMA_DB_PATH = "./chroma_db"
MOCK_DOCUMENT_PATH = "internal_policy.txt"

# --- 1. Data and DB Setup ---

def create_mock_document(path: str):
    """Creates a sample text file to simulate a document (e.g., a PDF/report)."""
    content = """
    # Company Internal Policy 2025: Remote Work and PTO
    
    ## Remote Work Stipend
    All permanent employees are eligible for a quarterly remote work stipend of $350. 
    This stipend is disbursed on the 15th of the first month of every quarter (Jan, Apr, Jul, Oct).
    New hires become eligible after completing their 90-day probationary period.
    
    ## Paid Time Off (PTO) Policy
    Standard employees accrue 15 days of PTO annually. Managers accrue 20 days.
    All PTO requests must be submitted through the HR portal at least 7 days in advance.
    Unused PTO days, up to a maximum of 5 days, can be rolled over to the next year.
    Any employee using more than 3 consecutive weeks of PTO requires CEO approval.
    """
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"[Setup] Created mock document: {path}")

def setup_chroma_db(documents: list[Document]) -> Chroma:
    """
    Loads documents, splits them, and stores the resulting chunks in ChromaDB.
    """
    # 1. Clean up previous DB runs
    if os.path.exists(CHROMA_DB_PATH):
        shutil.rmtree(CHROMA_DB_PATH)
        print(f"[Setup] Cleared old database at {CHROMA_DB_PATH}")

    # 2. Split documents into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    docs_chunks = text_splitter.split_documents(documents)
    print(f"[Setup] Document split into {len(docs_chunks)} chunks.")
    
    # 3. Define the Ollama Embedding Model
    ollama_embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
    print(f"[Setup] Using Ollama model '{OLLAMA_EMBEDDING_MODEL}' for embeddings.")

    # 4. Create the Vector Store (ChromaDB)
    vectorstore = Chroma.from_documents(
        documents=docs_chunks,
        embedding=ollama_embeddings,
        persist_directory=CHROMA_DB_PATH
    )
    print(f"[Setup] Documents embedded and stored in ChromaDB.")
    return vectorstore

# --- 2. RAG Agent Core Functionality ---

def query_rag_agent(question: str, vectorstore: Chroma):
    """
    Performs the RAG pipeline: Retrieval -> Augmentation -> Generation.
    """
    print(f"\n--- RAG Agent Processing: '{question}' ---")

    # 1. Define the LLM for Generation
    llm = ChatOllama(model=OLLAMA_LLM_MODEL, temperature=0.1)
    print(f"[RAG] Using Ollama model '{OLLAMA_LLM_MODEL}' for generation.")

    # 2. Define the Prompt Template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Use ONLY the following context to answer the question. If the answer is not in the context, state that you cannot find the information.\n\nContext: {context}"),
        ("user", "{input}")
    ])

    # 3. Create the document combining chain
    # This chain takes the retrieved documents and stuffs them into the context variable of the prompt
    document_chain = create_stuff_documents_chain(llm, prompt)

    # 4. Create the Retrieval Chain
    # This chain handles fetching documents from the vectorstore and passes them to the document_chain
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) # Retrieve top 3 chunks
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    # 5. Invoke the chain
    response = retrieval_chain.invoke({"input": question})

    # 6. Extract and display results
    print("\n✅ Final RAG Answer:")
    print(response["answer"])
    
    # Optionally show the source documents the answer was based on
    source_texts = [doc.page_content for doc in response.get("context", [])]
    print("\nSource Context Retrieved (Top 3 Chunks):")
    for i, text in enumerate(source_texts):
        print(f"--- Chunk {i+1} ---\n{text.strip()}")
    print("--------------------")


# --- 3. Execution ---

if __name__ == "__main__":
    
    # Create the data file
    create_mock_document(MOCK_DOCUMENT_PATH)
    
    # Load the document into LangChain Document format
    # Using a simple list of Document objects since we mocked the content
    with open(MOCK_DOCUMENT_PATH, 'r', encoding='utf-8') as f:
        doc_content = f.read()
    
    # Simulate loading as a single document
    documents = [
        Document(
            page_content=doc_content, 
            metadata={"source": MOCK_DOCUMENT_PATH}
        )
    ]

    # Setup the entire vector store
    vector_store = setup_chroma_db(documents)
    
    print("\n" + "="*80)
    print("CHROMA DB & OLLAMA RAG AGENT IS READY.")
    print("="*80)

    # Scenario 1: Question that can be answered by the context
    query_rag_agent(
        question="When is the remote work stipend paid out and what is the amount?",
        vectorstore=vector_store
    )

    # Scenario 2: Question requiring multiple facts
    query_rag_agent(
        question="How many PTO days do standard employees get, and what is the rule for rolling over unused days?",
        vectorstore=vector_store
    )
    
    # Scenario 3: Question the LLM cannot answer from the context (testing RAG grounding)
    query_rag_agent(
        question="What is the CEO's favorite color?",
        vectorstore=vector_store
    )
    
    # Cleanup
    if os.path.exists(MOCK_DOCUMENT_PATH):
        os.remove(MOCK_DOCUMENT_PATH)
        
    print("\nCleanup complete.")