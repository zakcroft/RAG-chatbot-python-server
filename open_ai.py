import os
import queue

from langchain import PromptTemplate
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import AsyncCallbackHandler

from vector_dbs.milvus import get_vector_db
from prompts.qa_prompts import qa_prompt_formatted_instructions_template, \
    simple_formatted_instructions_template


class StreamingCallback(AsyncCallbackHandler):
    def __init__(self):
        super().__init__()
        self.stream = queue.Queue()

    def get_stream(self):
        return self.stream

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.stream.put(token)


streaming_callback = StreamingCallback()


async def get_open_ai_assistant():
    llm_chat = ChatOpenAI(model_name="gpt-3.5-turbo-16k-0613", streaming=True,
                          callbacks=[streaming_callback])

    system_prompt_template = PromptTemplate(
        template=simple_formatted_instructions_template,
        input_variables=["context"]
    )
    system_message_template = SystemMessagePromptTemplate(prompt=system_prompt_template)

    async def assistant(query: dict, current_messages: any):
        semantic_search_results = get_vector_db().as_retriever(
            search_type=os.getenv("VECTOR_SEARCH_TYPE"),
            search_kwargs={"k": int(os.environ.get("VECTOR_SEARCH_K"))},
        ).get_relevant_documents(query=query["question"])

        # system_message = system_message_template.format(context=semantic_search_results)
        # chat_message = [system_message] + current_messages
        # answer = llm_chat(chat_message)

        chat_prompt_template = ChatPromptTemplate.from_messages([system_message_template, *current_messages])
        chat_prompt_message = chat_prompt_template.format_prompt(context=semantic_search_results).to_messages()
        answer = await llm_chat.agenerate([chat_prompt_message])
        # print('chat_prompt_message======', chat_prompt_message)

        return answer

    return assistant
