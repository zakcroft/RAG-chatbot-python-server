from langchain.embeddings.openai import OpenAIEmbeddings


def get_embedding_model():
    embedding_model = OpenAIEmbeddings()
    return embedding_model
