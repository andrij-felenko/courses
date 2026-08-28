#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CHALLENGE_NONCE_SIZE   32
#define ECDSA_SIG_SIZE          64
#define DEVICE_SERIAL_SIZE      16

typedef struct {
    uint8_t serial[DEVICE_SERIAL_SIZE];
    uint8_t signature[ECDSA_SIG_SIZE];
} device_auth_payload_t;

/* Низькорівневий інтерфейс взаємодії з апаратним крипточипом (I2C/SPI) */
extern bool secure_element_read_serial(uint8_t *out_serial_16b);
extern bool secure_element_sign_challenge(const uint8_t *digest_32b, uint8_t *out_sig_64b);

/**
 * @brief Формування криптографічної відповіді на виклик сервера.
 * @param nonce_32b Одноразовий вектор виклику від бекенду.
 * @param payload_out Вихідна структура для передавання по мережі.
 * @return true у разі успішного підпису апаратним модулем.
 */
bool device_generate_attestation_response(const uint8_t *nonce_32b,
                                          device_auth_payload_t *payload_out) {
    if (!nonce_32b || !payload_out) {
        return false;
    }

    /* Очищення пам'яті для уникнення витоку старих даних */
    memset(payload_out, 0, sizeof(device_auth_payload_t));

    /* Читання фабричного серійного номера */
    if (!secure_element_read_serial(payload_out->serial)) {
        return false;
    }

    /* Апаратне обчислення підпису ECDSA P-256 без вивантаження закритого ключа */
    if (!secure_element_sign_challenge(nonce_32b, payload_out->signature)) {
        memset(payload_out, 0, sizeof(device_auth_payload_t));
        return false;
    }

    return true;
}
