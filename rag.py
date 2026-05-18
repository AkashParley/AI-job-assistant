from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import os
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

def build_vectorstore(resume_text, jd_text):
    resume_doc = Document(page_content=resume_text, metadata={"source": "resume"})
    jd_doc = Document(page_content=jd_text, metadata={"source": "jd"})

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents([resume_doc, jd_doc])

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    vectorstore = Chroma.from_documents(chunks, embeddings)
    return vectorstore

def retrieve_relevant_chunks(vectorstore, query, k=4):
    results = vectorstore.similarity_search(query, k=k)
    return "\n\n".join([doc.page_content for doc in results])