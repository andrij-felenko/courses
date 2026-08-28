/* C: Вихідний шлюз з підтримкою Idempotency-Key та автоматичним повтором при таймаутах */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

typedef struct {
    int status_code;
    char body[512];
    int is_network_error;
} http_response_t;

/* Симуляція вихідного HTTP POST запиту до зовнішнього API */
static http_response_t mock_http_post(const char *url, const char *idempotency_key, const char *payload, int attempt) {
    http_response_t res;
    memset(&res, 0, sizeof(res));

    /* Симуляція таймауту мережі на 1-й спробі, 409 Conflict на 2-й і 200 OK на 3-й */
    if (attempt == 1) {
        res.is_network_error = 1; /* Таймаут / ECONNRESET */
        res.status_code = 0;
    } else if (attempt == 2) {
        res.status_code = 409;   /* In-flight conflict */
        snprintf(res.body, sizeof(res.body), "{\"error\": \"in_flight\"}");
    } else {
        res.status_code = 200;
        snprintf(res.body, sizeof(res.body), "{\"status\": \"charged\", \"id\": \"ch_1092\"}");
    }
    return res;
}

int send_outbound_charge(const char *order_id, double amount, int max_retries) {
    char idempotency_key[128];
    snprintf(idempotency_key, sizeof(idempotency_key), "charge_order_%s_v1", order_id);

    char payload[256];
    snprintf(payload, sizeof(payload), "{\"order_id\":\"%s\",\"amount\":%.2f}", order_id, amount);

    int backoff_sec = 1;
    for (int attempt = 1; attempt <= max_retries; attempt++) {
        printf("[OUTBOUND C] Спроба %d/%d з Idempotency-Key: %s\n", attempt, max_retries, idempotency_key);
        
        http_response_t res = mock_http_post("https://api.stripe.com/v1/charges", idempotency_key, payload, attempt);

        if (res.is_network_error || res.status_code >= 500) {
            printf("[WARN C] Мережева помилка або 5xx (%d). Чекаємо %d с...\n", res.status_code, backoff_sec);
            sleep(backoff_sec);
            backoff_sec *= 2;
            continue;
        }

        if (res.status_code == 409) {
            printf("[WARN C] 409 Conflict (операція виконується). Чекаємо %d с...\n", backoff_sec);
            sleep(backoff_sec);
            continue;
        }

        if (res.status_code == 200 || res.status_code == 201) {
            printf("[SUCCESS C] Успішно виконано: %s\n", res.body);
            return 0; /* Успіх */
        }

        printf("[FATAL C] Незворотна помилка %d: %s\n", res.status_code, res.body);
        return -1;
    }

    printf("[ERROR C] Вичерпано ліміт спроб для замовлення %s\n", order_id);
    return -2;
}
