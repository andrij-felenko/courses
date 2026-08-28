# Правильно: масив зберігає кожен елемент як окремий елемент argv[]
CMD_ARGS=(
    curl
    -H "Content-Type: application/json"
    -H "Authorization: Bearer $TOKEN"
    "https://api.example.com/v1/data"
)

# Виклик розгортає масив зі збереженням меж:
"${CMD_ARGS[@]}"
