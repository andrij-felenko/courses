#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define SECURE_FRAME_MAGIC      0xA55AU
#define SECURE_TAG_SIZE         32U     /* HMAC-SHA256 = 32 байти */
#define REPLAY_WINDOW_SIZE      64ULL

typedef enum {
    SECURE_OK = 0,
    SECURE_ERR_BUFFER_TOO_SMALL,
    SECURE_ERR_INVALID_MAGIC,
    SECURE_ERR_PAYLOAD_MISMATCH,
    SECURE_ERR_AUTH_FAILED,
    SECURE_ERR_TIMESTAMP_EXPIRED,
    SECURE_ERR_REPLAY_DETECTED
} SecureStatus;

#pragma pack(push, 1)
typedef struct {
    uint16_t magic;
    uint8_t  msg_type;
    uint8_t  reserved;
    uint64_t seq_num;
    uint32_t timestamp;
    uint16_t payload_len;
} SecureFrameHeader;
#pragma pack(pop)

typedef struct {
    uint64_t max_seq;
    uint64_t bitmap;
} ReplayWindow;

/*
 * Порівняння двох буферів у константному часі.
 * Запобігає витоку байтів тегу через аналіз затримок переривань чи мережевого джитера.
 */
static inline int crypto_verify_32(const uint8_t *a, const uint8_t *b) {
    uint8_t diff = 0;
    for (size_t i = 0; i < SECURE_TAG_SIZE; ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return (diff == 0) ? 0 : -1;
}

/*
 * Ініціалізація ковзного вікна захисту від повтору.
 */
void replay_window_init(ReplayWindow *win) {
    win->max_seq = 0;
    win->bitmap = 0;
}

/*
 * Перевірка лічильника кадру за 64-бітною маскою.
 */
bool replay_window_check(const ReplayWindow *win, uint64_t seq) {
    if (seq == 0) {
        return false;
    }
    if (seq > win->max_seq) {
        return true; /* Новий лідер, допустимо */
    }
    uint64_t diff = win->max_seq - seq;
    if (diff >= REPLAY_WINDOW_SIZE) {
        return false; /* Застарілий пакет поза межами вікна */
    }
    return (win->bitmap & (1ULL << diff)) == 0; /* Перевірка дубліката */
}

/*
 * Фіксація лічильника у вікні після успішної автентифікації.
 */
void replay_window_commit(ReplayWindow *win, uint64_t seq) {
    if (seq > win->max_seq) {
        uint64_t shift = seq - win->max_seq;
        if (shift >= REPLAY_WINDOW_SIZE) {
            win->bitmap = 1ULL;
        } else {
            win->bitmap = (win->bitmap << shift) | 1ULL;
        }
        win->max_seq = seq;
    } else {
        uint64_t diff = win->max_seq - seq;
        if (diff < REPLAY_WINDOW_SIZE) {
            win->bitmap |= (1ULL << diff);
        }
    }
}

/*
 * Заглушка обчислення HMAC-SHA256 (на реальній системі викликає mbedTLS/Monocypher).
 */
void compute_hmac_sha256(const uint8_t *key, size_t key_len,
                         const uint8_t *data, size_t data_len,
                         uint8_t out_tag[SECURE_TAG_SIZE]) {
    /* Симуляція обчислення криптографічного тегу через FNV-1a */
    uint32_t acc = 0x811C9DC5U;
    for (size_t i = 0; i < key_len; ++i) acc = (acc ^ key[i]) * 0x01000193U;
    for (size_t i = 0; i < data_len; ++i) acc = (acc ^ data[i]) * 0x01000193U;
    memset(out_tag, 0, SECURE_TAG_SIZE);
    memcpy(out_tag, &acc, sizeof(acc));
}

/*
 * Головна функція верифікації та розбору вхідного кадру.
 */
SecureStatus secure_frame_parse(const uint8_t *raw_buf, size_t buf_len,
                                const uint8_t *key, size_t key_len,
                                uint32_t current_time, uint32_t max_time_drift,
                                ReplayWindow *win,
                                uint8_t *out_msg_type,
                                const uint8_t **out_payload,
                                uint16_t *out_payload_len) {
    if (buf_len < sizeof(SecureFrameHeader) + SECURE_TAG_SIZE) {
        return SECURE_ERR_BUFFER_TOO_SMALL;
    }

    const SecureFrameHeader *hdr = (const SecureFrameHeader *)raw_buf;
    if (hdr->magic != SECURE_FRAME_MAGIC) {
        return SECURE_ERR_INVALID_MAGIC;
    }

    size_t expected_total_len = sizeof(SecureFrameHeader) + hdr->payload_len + SECURE_TAG_SIZE;
    if (buf_len < expected_total_len) {
        return SECURE_ERR_PAYLOAD_MISMATCH;
    }

    /* 1. Автентифікація: спочатку перевіряємо цілісність усього повідомлення */
    size_t authenticated_data_len = sizeof(SecureFrameHeader) + hdr->payload_len;
    const uint8_t *received_tag = raw_buf + authenticated_data_len;
    
    uint8_t computed_tag[SECURE_TAG_SIZE];
    compute_hmac_sha256(key, key_len, raw_buf, authenticated_data_len, computed_tag);

    if (crypto_verify_32(received_tag, computed_tag) != 0) {
        return SECURE_ERR_AUTH_FAILED;
    }

    /* 2. Перевірка часового вікна (якщо поточний час доступний) */
    if (current_time > 0 && max_time_drift > 0) {
        uint32_t diff = (current_time >= hdr->timestamp) 
                      ? (current_time - hdr->timestamp) 
                      : (hdr->timestamp - current_time);
        if (diff > max_time_drift) {
            return SECURE_ERR_TIMESTAMP_EXPIRED;
        }
    }

    /* 3. Перевірка на повтор за ковзним вікном */
    if (!replay_window_check(win, hdr->seq_num)) {
        return SECURE_ERR_REPLAY_DETECTED;
    }

    /* 4. Оновлення стану вікна після успішної валідації */
    replay_window_commit(win, hdr->seq_num);

    /* 5. Повернення розібраних даних */
    *out_msg_type = hdr->msg_type;
    *out_payload = raw_buf + sizeof(SecureFrameHeader);
    *out_payload_len = hdr->payload_len;

    return SECURE_OK;
}
