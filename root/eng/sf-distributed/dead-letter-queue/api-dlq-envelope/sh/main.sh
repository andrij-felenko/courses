# Перегляд кількості повідомлень та найстарішого запису
$ dlq-admin inspect --queue orders-dlq --summary

# Експорт перших 10 повідомлень у локальний файл для аналізу
$ dlq-admin export --queue orders-dlq --limit 10 --out ./failed_orders.json

# Запуск безпечного повторного введення зі швидкістю 30 повідомлень/сек
$ dlq-admin redrive --src orders-dlq --dst orders-primary --rate 30 --patch '{"currency":"UAH"}'

# Скидання безнадійних повідомлень у холодний архів S3
$ dlq-admin archive --queue orders-dlq --s3-bucket company-dlq-archive --purge
