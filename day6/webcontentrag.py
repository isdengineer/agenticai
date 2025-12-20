import requests
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup # Need to install: pip install beautifulsoup4

# --- A. Data Loading from Web ---
def fetch_web_content(url):
    """Fetches text content from a given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raise exception for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract meaningful text, ignoring scripts and styles
        text = soup.get_text(separator=' ', strip=True)
        return text
    except Exception as e:
        return f"Error fetching web content: {e}"

# Example URL (using a LangChain specific doc for demonstration)
WEB_URL = "https://python.langchain.com/v0.2/docs/concepts/#prompts" 
page_text = fetch_web_content(WEB_URL)

if "Error fetching" in page_text:
    print(page_text)
    exit()

# Convert the entire page text into a single LangChain Document
web_documents = [Document(page_content=page_text, metadata={"source": WEB_URL})]

# --- B. Chunking and Embedding ---
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(web_documents)

ollama_embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = FAISS.from_documents(docs, ollama_embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# --- C. RAG Chain Definition ---
ollama_llm = ChatOllama(model="llama3", temperature=0)

RAG_PROMPT_TEMPLATE = """
You are a documentation analysis assistant. Answer the user's question based ONLY on the provided web content. 

CONTEXT:
{context}

QUESTION: {question}
"""
rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | rag_prompt
    | ollama_llm
    | StrOutputParser()
)

# --- D. Query the RAG System ---
user_query = "What is the primary role of a Prompt Template according to the documentation?"

print(f"\n--- Querying Web Content RAG System ---")
print(f"User Query: {user_query}")
print("-" * 40)

final_answer = rag_chain.invoke(user_query)

print(f"\n✅ LLM (Ollama) Answer:")
print(final_answer)