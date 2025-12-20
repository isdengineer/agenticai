from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableSequence
from langchain_core.output_parsers import StrOutputParser
"""
This example incorporates a crucial step: validation. After retrieving the context and generating the answer, a second LLM call is used to critique and self-correct the initial response, enhancing reliability—a key pattern in advanced RAG pipelines.
"""
# --- A. Setup and Context (The context is slightly ambiguous) ---
docs = [
    Document(page_content="The new Q4 server infrastructure uses a 10Gbps connection speed.", metadata={"source": "IT Manual"}),
    Document(page_content="The official policy requires all staff to use a VPN for external connections.", metadata={"source": "Security Policy"}),
    Document(page_content="The old Q3 server infrastructure used a 1Gbps connection speed.", metadata={"source": "IT Manual"}),
]

ollama_embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = FAISS.from_documents(docs, ollama_embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 1}) # k=1 to force ambiguous retrieval

# 1. Initialize Ollama LLM
ollama_llm = ChatOllama(model="llama3", temperature=0)

# --- B. Define RAG Prompt and Initial Chain ---
RAG_PROMPT = ChatPromptTemplate.from_template("Answer the question based ONLY on the context: {context}\n\nQUESTION: {question}")
initial_rag_chain = RAG_PROMPT | ollama_llm | StrOutputParser()

# --- C. Define the Self-Correction Chain ---
# This prompt asks the LLM to act as a validator.
CRITIQUE_PROMPT = ChatPromptTemplate.from_template(
    """
    You are a critical validator. You are given an original question, the context used to answer it, 
    and the answer generated.
    
    1. Assess if the ANSWER is fully supported by the CONTEXT.
    2. If the answer is NOT supported or is ambiguous, generate a corrected, cautious answer.
    3. If the answer is fully supported, return the original answer verbatim.
    
    QUESTION: {question}
    CONTEXT: {context}
    ANSWER: {answer}
    
    CORRECTED/FINAL ANSWER:
    """
)

def retrieve_and_format_context(question):
    """Retrieves context and formats it for the combined chain."""
    retrieved_docs = retriever.invoke(question)
    return "\n---\n".join([doc.page_content for doc in retrieved_docs])

# The Self-Correcting Chain (The magic is in the structure)
self_correcting_chain = RunnablePassthrough.assign(
    context=RunnableLambda(retrieve_and_format_context)
).assign(
    # First, generate the initial answer
    answer=lambda x: initial_rag_chain.invoke({"context": x['context'], "question": x['question']})
).assign(
    # Second, critique and correct the answer
    final_output=lambda x: CRITIQUE_PROMPT | ollama_llm | StrOutputParser()
).pick("final_output")

# --- D. Execute ---
user_query = "What is the speed of the server infrastructure?"

print(f"\n--- Self-Correcting RAG System ---")
print(f"User Query: {user_query}")
print("-" * 40)

# The initial retrieval might grab the "1Gbps" context, but the correction step should
# note the ambiguity between "old Q3" and "new Q4" if both are present.
final_answer = self_correcting_chain.invoke({"question": user_query})

print(f"\n✅ Final Answer (Self-Corrected):")
print(final_answer)