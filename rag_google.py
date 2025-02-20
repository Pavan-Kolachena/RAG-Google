# -*- coding: utf-8 -*-
"""RAG Google.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12jnw31R4A946jIgSxVF1wx-_11SGAAAp
"""

#!pip install streamlit
#!pip install sentence_transformers
#!pip install faiss-cpu
#!pip install -U langchain-community
#!pip install transformers
#!pip install pypdf
import streamlit as st
import numpy as np
#from sentence_transformers import SentenceTransformer
import faiss
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from transformers import pipeline
from langchain.embeddings import SentenceTransformerEmbeddings

# Load your PDF
loader = PyPDFLoader("/content/Best Practices of RAG.pdf")
documents = loader.load()

# Split documents into chunks
texts = [doc.page_content for doc in documents]
# Split documents into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, separator='\n')
split_texts = []
for text in texts:
    split_texts.extend(text_splitter.split_text(text))  # Split each document's text



# Create embeddings
#model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')

# Embed a sample query to get the shape
sample_embedding = embeddings.embed_query("This is a sample query")

# Embed the documents and convert to a NumPy array
embedded_docs = embeddings.embed_documents(texts)
embedded_docs_np = np.array(embedded_docs)  # Convert to NumPy array

# Create vector store with the NumPy array
index = faiss.IndexFlatL2(embedded_docs_np.shape[-1])  # Get shape from the embedded docs
index.add(embedded_docs_np)  # Add the embedded documents to the index

# Create a docstore
docstore = FAISS.from_texts(texts, embeddings) # Changed variable name from 'docsearch' to 'docstore'

# Create retriever, provide the mapping between the index and docstore
retriever = FAISS(embeddings.embed_query, index, docstore, {i:i for i in range(len(texts))}) # Use 'docstore' instead of 'docsearch'

# Create a basic LLM (replace with a more suitable one)
nlp = pipeline("text-generation", model="gpt2")

# Streamlit app
def main():
    st.title("RAG Bot")

    user_query = st.text_input("Ask your question:")

    if user_query:
        docs = retriever.get_relevant_documents(user_query)
        context = "\n".join([doc.page_content for doc in docs])
        response = nlp(f"{context}\n{user_query}", max_length=100, num_return_sequences=1)[0]['generated_text']
        st.write(response)

if __name__ == "__main__":
    main()
