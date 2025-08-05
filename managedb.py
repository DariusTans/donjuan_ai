from langchain_openai import OpenAIEmbeddings
from vectordb import create_vector_store_from_docs, extract_docs_from_pdf_file


if __name__ == "__main__":
    # Example usage
    file_path = "Secrets of the Universe about dating for men.pdf"  # Replace with your PDF file path
    docs = extract_docs_from_pdf_file(file_path)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    create_vector_store_from_docs(docs, embeddings)