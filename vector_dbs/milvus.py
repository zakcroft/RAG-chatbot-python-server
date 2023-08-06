import os
from pymilvus import Collection, utility, connections
from langchain.vectorstores import Milvus

from dotenv import load_dotenv
from .embed import get_embedding_model

load_dotenv()

COLLECTION_NAME = os.getenv("ZILLIZ_COLLECTION")
ALIAS = "default"
DIMENSION = 1536
connection_args = {
    "uri": os.getenv("ZILLIZ_CLUSTER"),
    # "user": os.getenv("ZILLIZ_CLOUD_USERNAME"),
    # "password": os.getenv("ZILLIZ_CLOUD_PASSWORD"),
    "token": os.getenv("ZILLIZ_API_KEY"),
    "port": os.getenv("ZILLIZ_PORT"),
    "secure": True,
}

connections.connect("default", **connection_args)


def get_vector_db():
    embeddings = get_embedding_model()
    vector_db: Milvus = Milvus(
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
        connection_args=connection_args,
    )
    return vector_db


def has_collection():
    return utility.has_collection(COLLECTION_NAME, using=ALIAS)


def insert_into_collection(docs):
    embeddings = get_embedding_model()
    # print(docs)
    get_vector_db().from_documents(
        docs,
        embeddings,
        collection_name=COLLECTION_NAME,
        connection_args=connection_args,
    )
    collection = Collection(COLLECTION_NAME)
    print("has_index", collection.has_index(index_name="_default_idx_104"))


def save_docs_to_vector_store(docs):
    insert_into_collection(docs)
