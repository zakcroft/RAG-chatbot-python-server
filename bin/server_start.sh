uvicorn api:app --host 0.0.0.0 --port 80 --reload

alias prettyjson='python -m json.tool'

prettyjson_s() {
    echo "$1" | python -m json.tool
}

prettyjson_f() {
    python -m json.tool "$1"
}

prettyjson_w() {
    curl "$1" | python -m json.tool
}