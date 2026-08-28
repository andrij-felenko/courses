#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define SECURE_FRAME_MAGIC     0xA55A
#define TAG_SIZE               16
#define MAX_PAYLOAD_SIZE       128

#pragma pack(push, 1)
typedef struct {
    uint16_t magic;           // Сигнатура протоколу (0xA55A)
    uint32_t sequence_num;    // Монотонний лічильник пакета (захист від повторів)
    uint16_t payload_len;     // Довжина зашифрованого навантаження
} SecureHeader_t;

typedef struct {
    SecureHeader_t header;
    uint8_t payload[MAX_PAYLOAD_SIZE];
    uint8_t tag[TAG_SIZE];
} SecureFrame_t;
#pragma pack(pop)

// Прототипи зовнішніх перевірених функцій шифрування (наприклад, із Monocypher або mbedTLS)
extern void crypto_aead_encrypt(uint8_t *cipher, uint8_t *tag,
                                const uint8_t *key, const uint8_t *nonce,
                                const uint8_t *aad, size_t aad_len,
                                const uint8_t *plain, size_t plain_len);

extern void crypto_aead_decrypt(uint8_t *plain,
                                const uint8_t *key, const uint8_t *nonce,
                                const uint8_t *aad, size_t aad_len,
                                const uint8_t *cipher, size_t cipher_len);

extern int crypto_verify_ct(const uint8_t *a, const uint8_t *b, size_t len);

typedef struct {
    uint8_t session_key[32];
    uint32_t tx_counter;
    uint32_t rx_last_counter;
} CryptoSession_t;

/**
 * @brief Пакування та шифрування вихідного пакета.
 */
bool secure_frame_encode(CryptoSession_t *session,
                         const uint8_t *plain, size_t plain_len,
                         SecureFrame_t *out_frame, size_t *out_frame_len) {
    if (!session || !plain || !out_frame || plain_len > MAX_PAYLOAD_SIZE) {
        return false;
    }

    out_frame->header.magic = SECURE_FRAME_MAGIC;
    out_frame->header.sequence_num = ++(session->tx_counter);
    out_frame->header.payload_len = (uint16_t)plain_len;

    // Формуємо 12-байтовий Nonce з лічильника відправки
    uint8_t nonce[12] = {0};
    memcpy(nonce, &(out_frame->header.sequence_num), sizeof(uint32_t));

    // Шифруємо корисні дані та обчислюємо тег автентифікації над заголовком (AAD) і шифротекстом
    crypto_aead_encrypt(out_frame->payload, out_frame->tag,
                        session->session_key, nonce,
                        (const uint8_t*)&out_frame->header, sizeof(SecureHeader_t),
                        plain, plain_len);

    *out_frame_len = sizeof(SecureHeader_t) + plain_len + TAG_SIZE;
    return true;
}

/**
 * @brief Перевірка автентичності та безпечне розшифрування вхідного пакета.
 */
bool secure_frame_decode(CryptoSession_t *session,
                         const uint8_t *frame_bytes, size_t frame_len,
                         uint8_t *out_plain, size_t *out_plain_len) {
    if (!session || !frame_bytes || !out_plain || frame_len < sizeof(SecureHeader_t) + TAG_SIZE) {
        return false;
    }

    const SecureFrame_t *frame = (const SecureFrame_t*)frame_bytes;

    // 1. Перевірка цілісності структури заголовка
    if (frame->header.magic != SECURE_FRAME_MAGIC) {
        return false;
    }

    size_t expected_payload_len = frame->header.payload_len;
    if (frame_len != sizeof(SecureHeader_t) + expected_payload_len + TAG_SIZE) {
        return false;
    }

    // 2. Суворий захист від повторів (Replay Protection)
    if (frame->header.sequence_num <= session->rx_last_counter) {
        return false; // Старий або повторно відправлений пакет — відхиляємо
    }

    // 3. Формуємо Nonce для перевірки
    uint8_t nonce[12] = {0};
    memcpy(nonce, &(frame->header.sequence_num), sizeof(uint32_t));

    // 4. Обчислюємо очікуваний тег
    uint8_t calculated_tag[TAG_SIZE];
    uint8_t dummy_plain[MAX_PAYLOAD_SIZE];
    
    // Розшифровуємо в тимчасовий буфер для отримання тегу або викликаємо суто перевірку тегу
    crypto_aead_encrypt(dummy_plain, calculated_tag,
                        session->session_key, nonce,
                        (const uint8_t*)&frame->header, sizeof(SecureHeader_t),
                        frame->payload, expected_payload_len);

    // 5. ПЕРЕВІРКА В КОНСТАНТНОМУ ЧАСІ
    if (crypto_verify_ct(calculated_tag, frame->payload + expected_payload_len, TAG_SIZE) != 0) {
        // ТЕГ ХИБНИЙ: Негайно повертаємо відмову!
        // Жоден байт не копіюється у вихідний буфер застосунку!
        return false;
    }

    // 6. Лише після успішної автентифікації розшифровуємо відкритий текст
    crypto_aead_decrypt(out_plain,
                        session->session_key, nonce,
                        (const uint8_t*)&frame->header, sizeof(SecureHeader_t),
                        frame->payload, expected_payload_len);

    *out_plain_len = expected_payload_len;
    session->rx_last_counter = frame->header.sequence_num;
    return true;
}
