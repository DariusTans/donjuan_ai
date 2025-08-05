from typing import List
from xml.dom.minidom import Document
from langchain_community.vectorstores import Chroma
from langchain.schema.embeddings import Embeddings
from langchain.document_loaders import TextLoader,PyMuPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import PERSIS_DIRECTORY
import re

persist_directory = PERSIS_DIRECTORY
collection_name = 'donjuanai'

def post_processing(text):
    # replace \n with space
    text = re.sub(r"\n", " ", text)
    # replace \r with space
    text = re.sub(r"\r", " ", text)

    # remove special characters
    text = re.sub(r"[^a-zA-Z0-9ก-๙\s]", "", text)

    # remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    # remove leading and trailing spaces
    text = text.strip()

    return text


def extract_docs_from_pdf_file(file_path: str) -> List[Document]:
    """
    Extracts documents from a PDF file.
    :param file_path: Path to the PDF file.
    :return: List of Document objects.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50
    )
    file_type = file_path.split('.')[-1]
    print("[+] File type:", file_type)
    if file_type == "txt":
        Loader = TextLoader
    elif file_type == "pdf":
        Loader = PyMuPDFLoader
    else:
        raise ValueError("Unsupported file type. Please provide a .txt or .pdf file.") 
    print(f"[+] Extracting documents from {file_type} file...")

    loader = Loader(file_path)
    docs = loader.load()
    docs = text_splitter.split_documents(docs)
    for i, doc in enumerate(docs):
      doc.metadata['source'] = f"{file_path}_{i}"
      doc.page_content = post_processing(doc.page_content)
    print("[+] Extracted documents from PDF file:")
    print(f"    - {file_path}")
    print("Successfully extracted documents from PDF file.")
    return docs

def create_vector_store_from_docs(
        docs: List[Document], embeddings: Embeddings, 
        collection_name:str = collection_name, 
        persist_directory:str = persist_directory) -> Chroma:
    return Chroma.from_documents(
      documents=docs,
      embedding=embeddings,
      collection_name=collection_name,
      persist_directory=persist_directory
    )

def get_vector_store(embeddings: Embeddings, 
                     collection_name: str = collection_name, 
                     persist_directory: str = persist_directory):
    vector_store = Chroma(
        embedding_function=embeddings,
        collection_name=collection_name,
        persist_directory=persist_directory,
    )
    return vector_store


