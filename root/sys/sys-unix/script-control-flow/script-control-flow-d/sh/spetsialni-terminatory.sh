# Демонстрація ;;& для послідовного накопичення властивостей
feature="PROD_LOG_DEBUG"

case "$feature" in
    *PROD*)
        echo "Середовище: Production"
        ;;&
    *LOG*)
        echo "Увімкнено логування"
        ;;&
    *DEBUG*)
        echo "Увімкнено детальний режим"
        ;;
esac
