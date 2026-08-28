#include <stdint.h>
#include <string.h>

extern void ble_crypto_aes_cmac(const uint8_t key[16], const uint8_t *msg, size_t msg_len, uint8_t mac_out[16]);

/**
 * @brief Крос-транспортна функція перетворення h6
 */
void ble_crypto_h6(const uint8_t w[16], const uint8_t key_id[4], uint8_t out[16]) {
    ble_crypto_aes_cmac(w, key_id, 4, out);
}

/**
 * @brief Крос-транспортна функція перетворення h7
 */
void ble_crypto_h7(const uint8_t salt[16], const uint8_t w[16], uint8_t out[16]) {
    ble_crypto_aes_cmac(salt, w, 16, out);
}
