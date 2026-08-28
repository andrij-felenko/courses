#!/usr/bin/env bash
# node_collector.sh — скрипт збору метрик кластера з типовими архітектурними вадами

CONFIG_FILE="/etc/cluster/nodes.conf"
OUT_DIR="/var/log/cluster_reports"
REPORT_FILE="$OUT_DIR/report_$(date +%Y%m%d).json"

mkdir -p $OUT_DIR

# Зчитування списку вузлів (крихке розбиття на слова)
NODES=$(cat $CONFIG_FILE | grep -v "^#" | awk '{print $1}')

TOTAL_CPU=0
COUNT=0
TMP_DIR="/tmp/node_data_$$"
mkdir -p $TMP_DIR

echo "Запуск паралельного збору метрик..."

# Запуск фонових процесів без контролю пулу
for NODE in $NODES; do
    (
        # Виклик curl та jq з породженням нових процесів
        RESP=$(curl -s --max-time 2 "http://$NODE:9100/metrics.json")
        if [ $? -eq 0 ] && [ -n "$RESP" ]; then
            # Парсинг JSON через jq
            CPU=$(echo "$RESP" | jq -r '.cpu_usage')
            MEM_FREE=$(echo "$RESP" | jq -r '.memory_free_mb')
            STATUS=$(echo "$RESP" | jq -r '.status')
            
            # Запис у тимчасовий файл (ризик гонитви файлової системи)
            echo "$NODE $CPU $MEM_FREE $STATUS" > "$TMP_DIR/$NODE.dat"
        else
            echo "$NODE 0 0 ERROR" > "$TMP_DIR/$NODE.dat"
        fi
    ) &
done

# Очікування завершення всіх фонових процесів
wait

echo "Агрегація результатів..."

# Агрегація з викликами зовнішнього калькулятора bc у циклі
for FILE in $TMP_DIR/*.dat; do
    if [ -f "$FILE" ]; then
        read -r NODE CPU MEM STATUS < "$FILE"
        if [ "$STATUS" = "OK" ]; then
            # Обчислення з плаваючою крапкою через bc (породження fork/exec на кожен крок)
            TOTAL_CPU=$(echo "$TOTAL_CPU + $CPU" | bc -l)
            COUNT=$((COUNT + 1))
        fi
    fi
done

# Розрахунок середнього значення
if [ $COUNT -gt 0 ]; then
    AVG_CPU=$(echo "scale=2; $TOTAL_CPU / $COUNT" | bc -l)
else
    AVG_CPU=0
fi

# Ручна генерація підсумкового JSON без екранування спеціальних символів
cat <<EOF > $REPORT_FILE
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "nodes_polled": $COUNT,
  "average_cpu_usage": $AVG_CPU
}
EOF

# Прибирання тимчасових файлів
rm -rf $TMP_DIR
echo "Звіт сформовано: $REPORT_FILE"
