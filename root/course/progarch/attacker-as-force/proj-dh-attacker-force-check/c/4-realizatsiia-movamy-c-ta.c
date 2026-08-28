/* c */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_PAYLOAD_SIZE 256
#define MAX_SENSOR_ID_LEN 32
#define HMAC_LEN 32
#define MAX_ALLOWED_TEMP 85.0f
#define MIN_ALLOWED_TEMP -40.0f
#define MAX_PACKETS_PER_SEC 10

typedef struct {
    uint8_t sensor_id[MAX_SENSOR_ID_LEN];
    uint32_t sensor_id_len;
    uint64_t sequence_num;
    float temperature;
    uint8_t hmac[HMAC_LEN];
} dh_sensor_packet_t;

typedef enum {
    GATEWAY_OK = 0,
    ERR_BUFFER_TOO_SMALL,
    ERR_INVALID_HMAC,
    ERR_REPLAY_ATTACK,
    ERR_OUT_OF_BOUNDS,
    ERR_RATE_LIMITED
} gateway_error_t;

typedef struct {
    uint64_t last_sequence;
    uint32_t packet_count_current_sec;
    uint64_t last_window_sec;
    uint8_t secret_key[32];
} sensor_session_t;

// Безпечне порівняння двох буферів за сталий час для запобігання таймінговим атакам
static bool constant_time_memcmp(const uint8_t *a, const uint8_t *b, size_t len) {
    uint8_t result = 0;
    for (size_t i = 0; i < len; ++i) {
        result |= (a[i] ^ b[i]);
    }
    return result == 0;
}

// Мок криптографічної перевірки HMAC-SHA256
static bool verify_hmac_c(const uint8_t *data, size_t len, const uint8_t *key, const uint8_t *expected_hmac) {
    // В реальній системі тут використовується mbedTLS hmac_sha256
    uint8_t computed_hmac[HMAC_LEN];
    memset(computed_hmac, 0xAB, HMAC_LEN); // Симуляція розрахованого підпису
    (void)data; (void)len; (void)key;
    return constant_time_memcmp(computed_hmac, expected_hmac, HMAC_LEN);
}

gateway_error_t dh_gateway_process_packet(
    const uint8_t *raw_buf, 
    size_t raw_len, 
    sensor_session_t *session,
    uint64_t current_time_sec,
    dh_sensor_packet_t *out_packet
) {
    // 1. Повна медіація: Перевірка мінімального та максимального розміру
    const size_t min_expected = sizeof(uint32_t) + 1 + sizeof(uint64_t) + sizeof(float) + HMAC_LEN;
    if (raw_buf == NULL || session == NULL || out_packet == NULL) {
        return ERR_BUFFER_TOO_SMALL;
    }
    if (raw_len < min_expected || raw_len > MAX_PAYLOAD_SIZE) {
        return ERR_BUFFER_TOO_SMALL;
    }

    // 2. Безпечний розбір ідентифікатора (little-endian безпечне зчитування)
    uint32_t id_len = 0;
    memcpy(&id_len, raw_buf, sizeof(uint32_t));
    if (id_len == 0 || id_len > MAX_SENSOR_ID_LEN) {
        return ERR_BUFFER_TOO_SMALL;
    }
    if ((sizeof(uint32_t) + id_len + sizeof(uint64_t) + sizeof(float) + HMAC_LEN) > raw_len) {
        return ERR_BUFFER_TOO_SMALL;
    }

    out_packet->sensor_id_len = id_len;
    memcpy(out_packet->sensor_id, raw_buf + sizeof(uint32_t), id_len);
    
    size_t offset = sizeof(uint32_t) + id_len;
    memcpy(&out_packet->sequence_num, raw_buf + offset, sizeof(uint64_t));
    offset += sizeof(uint64_t);
    
    memcpy(&out_packet->temperature, raw_buf + offset, sizeof(float));
    offset += sizeof(float);

    memcpy(out_packet->hmac, raw_buf + offset, HMAC_LEN);

    // 3. Захист від повторів (Replay protection)
    if (out_packet->sequence_num <= session->last_sequence) {
        return ERR_REPLAY_ATTACK;
    }

    // 4. Перевірка HMAC підпису за сталий час
    size_t payload_len = sizeof(uint32_t) + id_len + sizeof(uint64_t) + sizeof(float);
    if (!verify_hmac_c(raw_buf, payload_len, session->secret_key, out_packet->hmac)) {
        return ERR_INVALID_HMAC;
    }

    // 5. Rate limiting на рівні шлюзу
    if (current_time_sec == session->last_window_sec) {
        if (session->packet_count_current_sec >= MAX_PACKETS_PER_SEC) {
            return ERR_RATE_LIMITED;
        }
        session->packet_count_current_sec++;
    } else {
        session->last_window_sec = current_time_sec;
        session->packet_count_current_sec = 1;
    }

    // 6. Валідація бізнес-інваріанту фізичних величин
    if (out_packet->temperature < MIN_ALLOWED_TEMP || out_packet->temperature > MAX_ALLOWED_TEMP) {
        return ERR_OUT_OF_BOUNDS;
    }

    // Оновлення стану сесії ТІЛЬКИ після успішного проходження всіх рубежів
    session->last_sequence = out_packet->sequence_num;

    return GATEWAY_OK;
}
