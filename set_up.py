import os
import getpass
import openai
from dotenv import load_dotenv

load_dotenv()


def set_environment_variables():
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")

    openai.api_key = os.getenv("OPENAI_API_KEY")

    if os.getenv("OPENAI_ORGANIZATION_API_KEY"):
        openai.organization = os.getenv("OPENAI_ORGANIZATION_API_KEY")

    openai.log = 'info'
    # Defaults for RecursiveCharacterTextSplitter
    #  chunk_size: int = 4000,
    #  chunk_overlap: int = 200,
    os.environ["TEXT_SPLIT_CHUNK_SIZE"] = "1000"
    os.environ["TEXT_SPLIT_OVERLAP"] = "200"
    os.environ["TEXT_SPLIT_BY_PAGE"] = "False"

    # "similarity","similarity_score_threshold","mmr",
    os.environ["VECTOR_SEARCH_TYPE"] = "similarity"
    os.environ["VECTOR_SEARCH_K"] = "10"

    # "stuff","map_reduce","refine","map_rerank"
    os.environ["CHAIN_TYPE"] = "stuff"

    print(
        f"PARAMETERS:\n",
        f'TEXT_SPLIT_BY_PAGE: - {os.getenv("TEXT_SPLIT_BY_PAGE")}\n',
        f'TEXT_SPLIT_CHUNK_SIZE: - {os.getenv("TEXT_SPLIT_CHUNK_SIZE")}\n',
        f'TEXT_SPLIT_OVERLAP: - {os.getenv("TEXT_SPLIT_OVERLAP")}\n',
        f'VECTOR_SEARCH_TYPE: - {os.getenv("VECTOR_SEARCH_TYPE")}\n'
        f'VECTOR_SEARCH_K: - {os.getenv("VECTOR_SEARCH_K")}\n',
        f'CHAIN_TYPE: - {os.getenv("CHAIN_TYPE")}\n',
    )


set_environment_variables()
