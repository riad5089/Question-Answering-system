import os
from constants import google_api_key
from langchain.vectorstores import FAISS
from langchain.llms import GooglePalm
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings import HuggingFaceInstructEmbeddings

from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import os



import streamlit as st
os.environ["google_api_key"]=google_api_key
llm=GooglePalm(google_api_key=os.environ["google_api_key"],temperature=.6)


# # Initialize instructor embeddings using the Hugging Face model
instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")
vectordb_file_path = "faiss_index"

# def create_vector_db():
#     # Load data from FAQ sheet
#     loader = CSVLoader(file_path='codebasics_faqs.csv', source_column="prompt")
#     data = loader.load()

#     # Create a FAISS instance for vector database from 'data'
#     vectordb = FAISS.from_documents(documents=data,
#                                     embedding=instructor_embeddings)

#     # Save vector database locally
#     vectordb.save_local(vectordb_file_path)

# Inside your create_vector_db() function, modify the CSVLoader instantiation:
def create_vector_db():
    # Load data from FAQ sheet with explicit encoding specification
    loader = CSVLoader(file_path='codebasics_faqs.csv', source_column="prompt", encoding='ISO-8859-1')

    data = loader.load()

    # Create a FAISS instance for the vector database from 'data'
    vectordb = FAISS.from_documents(documents=data, embedding=instructor_embeddings)

    # Save vector database locally
    vectordb.save_local(vectordb_file_path)


def get_qa_chain():
    # Load the vector database from the local folder
    vectordb = FAISS.load_local(vectordb_file_path, instructor_embeddings)

    # Create a retriever for querying the vector database
    retriever = vectordb.as_retriever(score_threshold=0.7)

    prompt_template = """Given the following context and a question, generate an answer based on this context only.
    In the answer try to provide as much text as possible from "response" section in the source document context without making much changes.
    If the answer is not found in the context, kindly state "I don't know." Don't try to make up an answer.

    CONTEXT: {context}

    QUESTION: {question}"""

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    chain = RetrievalQA.from_chain_type(llm=llm,
                                        chain_type="stuff",
                                        retriever=retriever,
                                        input_key="query",
                                        return_source_documents=True,
                                        chain_type_kwargs={"prompt": PROMPT})

    return chain

if __name__ == "__main__":
    create_vector_db()
    chain = get_qa_chain()
    print(chain("Do you have javascript course?"))
