#!/usr/bin/env bash
# latency_percentiles.sh: Розрахунок P50, P90, P95, P99 часу відповіді
export LC_ALL=C

# 1. Витягуємо лише валідні числові значення часу відповіді ($11)
# 2. Швидко сортуємо числа в числовому порядку
# 3. Обчислюємо перцентилі за індексами за один прохід
awk '$11 ~ /^[0-9]+(\.[0-9]+)?$/ { print $11 }' /var/log/nginx/access.log \
  | sort -n \
  | awk '
    {
        count++
        values[count] = $1
    }
    END {
        if (count == 0) { print "Дані відсутні"; exit }
        p50_idx = int(count * 0.50) + 1
        p90_idx = int(count * 0.90) + 1
        p95_idx = int(count * 0.95) + 1
        p99_idx = int(count * 0.99) + 1

        printf "Вибірка: %d запитів\n", count
        printf "P50 (Медіана): %.3f c\n", values[p50_idx]
        printf "P90:          %.3f c\n", values[p90_idx]
        printf "P95:          %.3f c\n", values[p95_idx]
        printf "P99:          %.3f c\n", values[p99_idx]
    }
'
