import os
from pymilvus import (
    connections,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    utility,
)

from langchain.vectorstores import Milvus
from dotenv import load_dotenv
from .embed import get_embedding_model


load_dotenv()

COLLECTION_NAME = "TalkativeDocs"
DIMENSION = 1536
connection_args = {
    "uri": os.getenv("ZILLIZ_CLUSTER"),
    "token": os.getenv("ZILLIZ_API_KEY"),
    "port": "9091",
    "secure": True,
}

connections.connect(
    "default",
    uri=os.getenv("ZILLIZ_CLUSTER"),
    port="9091",
    token=os.getenv("ZILLIZ_API_KEY"),
    secure=True,
)


def get_vector_db():
    embeddings = get_embedding_model()
    vector_db: Milvus = Milvus(
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
        connection_args=connection_args,
    )
    return vector_db


def similarity_search(query):
    docs = get_vector_db().similarity_search(query)
    # print(docs)
    return docs


def insert_into_collection(docs):
    embeddings = get_embedding_model()
    get_vector_db().from_documents(
        docs,
        embeddings,
        collection_name=COLLECTION_NAME,
        connection_args=connection_args,
    )
    collection = Collection(COLLECTION_NAME)
    print("has_index", collection.has_index(index_name="_default_idx_104"))


def create_index(field_name):
    index_params = {"index_type": "AUTOINDEX", "metric_type": "L2", "params": {}}

    collection = Collection(COLLECTION_NAME)
    collection.create_index(field_name=field_name, index_params=index_params)
    get_vector_db()._create_index()
    utility.index_building_progress(COLLECTION_NAME)
    # Output: {'total_rows': 0, 'indexed_rows': 0}


def create_partition(collection, partition_name):
    if not utility.has_partition(collection, partition_name):
        collection.create_partition(partition_name, description="")


def create_collection(collection_name):
    if not utility.has_collection(COLLECTION_NAME):
        collection = utility.list_collections()
        # Create collection which includes the id, title, and embedding.
        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.INT64,
                description="Ids",
                is_primary=True,
                auto_id=False,
            ),
            FieldSchema(
                name="title",
                dtype=DataType.VARCHAR,
                description="Title texts",
                max_length=200,
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                description="Embedding vectors",
                dim=DIMENSION,
            ),
        ]
        schema = CollectionSchema(fields=fields, description="Title collection")
        collection = Collection(
            name=COLLECTION_NAME, schema=schema, using="default", shards_num=2
        )

        collection = Collection(COLLECTION_NAME)
        collection_list = utility.list_collections()
        print(collection)
        print(collection_list)
        create_index("embedding")
        # return collection


def save_docs_to_zilliz(docs, partition_name="folder_1"):
    # create_collection(COLLECTION_NAME)
    # TODO - partition for folders
    # create_partition(collection, partition_name)
    # using langchain for now but no partitioning available?
    insert_into_collection(docs)


def save_docs_to_vector_store(docs):
    save_docs_to_zilliz(docs)
