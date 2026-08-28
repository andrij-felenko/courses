shopt -s extglob
input="server_node_01.prod"

case "$input" in
    server_+(node|worker)_+([0-9]).@(prod|stage))
        echo "Валідний сервер кластера"
        ;;
    *)
        echo "Невідомий тип хоста"
        ;;
esac
