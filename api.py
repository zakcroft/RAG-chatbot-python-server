import os

from langchain.memory import RedisChatMessageHistory

import set_up
import time
import secrets
import json

from queue import Empty
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from vector_dbs.milvus import save_docs_to_vector_store, has_collection
from chat_store.db import db_get_conversation, db_create_conversation

from documents.document_loader import store_and_split_file
from open_ai import streaming_callback, get_open_ai_assistant
from fastapi.responses import StreamingResponse

app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # ['*']
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class KeyParams(BaseModel):
    user_id: str
    conversation_id: str


class Query(KeyParams):
    query: str | None = ""


@app.get("/create-new-user-id")
async def get_new_user_id():
    return {"results": {"user_id": secrets.token_hex(8)}}


@app.get("/conversation-history/{key}")
async def get_conversation_history(key: str):
    conversation_history = await db_get_conversation(key)
    return {"results": {"conversation_history": conversation_history}}


@app.post("/create-new-conversation")
async def create_conversation(params: KeyParams):
    user_id = params.user_id
    conversation_id = params.conversation_id
    conversation_history = await db_create_conversation(user_id, conversation_id)
    return {"results": {"conversation_id": conversation_id, "conversation_history": conversation_history}}


@app.post("/query")
async def query(req: Query):
    assistant = await get_open_ai_assistant()
    if assistant is None:
        raise HTTPException(status_code=503, detail="Failed to get OpenAI assistant")

    conversation_key = req.user_id + ':' + req.conversation_id
    if not has_collection():
        return {"results": {"answer": "Please upload a document first"}}

    if has_collection() and (req.query is None or req.query.strip() == ""):
        return {"results": {"answer": "Please ask a question"}}

    else:
        start_time = time.time()
        print(f"OPEN AI Full response START {start_time:.2f} seconds after request")

        history = RedisChatMessageHistory(key_prefix=req.user_id + ':', session_id=req.conversation_id)
        print(history.key)
        history.add_user_message(req.query)

        try:
            res = await assistant({"question": req.query, "conversation_key": conversation_key}, history.messages)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Failed to get answer from assistant: {e}")

        answer = res.generations[0][0].text
        print('answer=====', answer)
        history.add_ai_message(answer)

        response_time = time.time() - start_time
        print(f"OPEN AI Full response received {response_time:.2f} seconds after request")

        return {"results": {"answer": answer, "conversation_history": history.messages}}


@app.get("/query-stream")
async def query():
    if not has_collection():
        return {"results": {"answer": "Please upload a document first"}}
    else:
        def chat_gpt_streamer():
            stream = streaming_callback.get_stream()
            while True:
                try:
                    data = stream.get(timeout=2)  # adjust timeout as needed (timeout=5)
                    # print("data", type(data), data)
                    if data is None:
                        print("data is None")
                        yield f"data: [END]\n\n"
                        break
                    yield f"data: {json.dumps(data)}\n\n"
                except Empty:
                    print("data is Empty")
                    break
                    # yield b""  # Return empty bytes if no data is available

            # Send a close event to the frontend
            yield f"data: [END]\n\n"

        return StreamingResponse(chat_gpt_streamer(), media_type='text/event-stream')


@app.post("/file/upload")
async def create_upload_file(file: UploadFile):
    if os.environ["ENABLE_UPLOADS"] == "TRUE":
        docs = store_and_split_file(file)
        save_docs_to_vector_store(docs)

        return {"results": {"filename": file.filename}}

    else:
        raise HTTPException(status_code=422, detail="Uploads disabled")


@app.post("/upload/files/")
async def create_upload_files(files: list[UploadFile]):
    # TODO
    if os.environ["ENABLE_UPLOADS"] == "TRUE":
        return {"results": {"filenames": [file.filename for file in files]}}

    else:
        raise HTTPException(status_code=422, detail="Uploads disabled")

if __name__ == "__main__":
    import uvicorn

    # uvicorn.run(app, host="0.0.0.0", port=80, log_level="debug")
