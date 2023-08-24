
##### Define you ENV Variables in a .env

    .env.example

##### Then either

    - WIP - not fully working for dev yet.
    docker-compose up

##### or ...

##### Redis
    docker compose up redis
    docker exec -it CONTAINER_ID bash
    redis-cli - when in container

##### Back end
###### Make sure you have installed SSL certificates that are used by Python's SSL library, to ensure secure connections with SSL/TLS-enabled services.
###### To install the SSL certificates, follow these steps:
    cd /Applications/Python\ 3.11/
    ./Install\ Certificates.command (it may require sudo)

###### Then:
    install latest python 3.11.4 
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt
    ./bin/server_start.sh

API: http://0.0.0.0:80

Docs: http://0.0.0.0:80/docs


##### Other stuff WIP

Define segmentation strategy
Chunking strategies
https://www.pinecone.io/learn/chunking-strategies/

Questions:
Page split size
  - speed of retrieval on vector db - what is it? - seems nominal and Zilliz is fast.
  - need to maintain context and as large documents being uploaded the split per page
  - page numbers are able to be cited if you split by page.

Store
 - 

author Zak Croft

