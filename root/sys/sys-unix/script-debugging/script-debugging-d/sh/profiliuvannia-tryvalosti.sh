# Пошук найповільніших інструкцій у журналі трасування
awk -F'[\\[\\]]' '/^\+/ {
    t = $2;
    if (prev_t > 0) {
        delta = t - prev_t;
        if (delta > 0.05) {  # Відбираємо команди, що тривали понад 50 мс
            printf "%8.4f c | %s\n", delta, prev_cmd;
        }
    }
    prev_t = t;
    prev_cmd = $0;
}' /tmp/trace.log | sort -rn | head -n 10
