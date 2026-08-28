#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Базовий примітив шифрування одного 128-бітного блоку AES */
extern void aes128_ecb_encrypt(const uint8_t key[16], const uint8_t input[16], uint8_t output[16]);
extern int ble_crypto_constant_time_memcmp(const void *a, const void *b, size_t len);

/**
 * @brief Криптографічна функція ah для генерації та резолвінгу RPA
 * @param irk 128-бітний ключ ідентичності IRK (16 байтів)
 * @param prand 24-бітне випадкове число (3 байти, Little-Endian)
 * @param hash_out 24-бітний вихідний хеш (3 байти, Little-Endian)
 */
void ble_crypto_ah(const uint8_t irk[16], const uint8_t prand[3], uint8_t hash_out[3]) {
    uint8_t plaintext[16];
    uint8_t ciphertext[16];

    /* Доповнення prand нулями до 16 байтів */
    memset(plaintext, 0, sizeof(plaintext));
    plaintext[0] = prand[0];
    plaintext[1] = prand[1];
    plaintext[2] = prand[2];

    /* Одноблочне шифрування AES-128 */
    aes128_ecb_encrypt(irk, plaintext, ciphertext);

    /* hash = молодші 24 біти результату (перші 3 байти) */
    hash_out[0] = ciphertext[0];
    hash_out[1] = ciphertext[1];
    hash_out[2] = ciphertext[2];
}

/**
 * @brief Перевірка належності адреси RPA конкретному пристрою за його IRK
 * @param rpa 48-бітна приватна адреса BLE (6 байтів, Little-Endian: [0..2]=hash, [3..5]=prand)
 * @param irk 128-бітний ключ ідентичності
 * @return true, якщо адреса успішно підтверджена ключем IRK
 */
bool ble_resolve_rpa(const uint8_t rpa[6], const uint8_t irk[16]) {
    /* Перевірка бітів ознаки RPA: два старших біти prand повинні бути 01b (0x40..0x7F) */
    if ((rpa[5] & 0xC0) != 0x40) {
        return false;
    }

    const uint8_t *hash = &rpa[0];
    const uint8_t *prand = &rpa[3];
    uint8_t expected_hash[3];

    ble_crypto_ah(irk, prand, expected_hash);

    /* Константне за часом порівняння обчисленого хешу з хешем у пакеті */
    return (ble_crypto_constant_time_memcmp(hash, expected_hash, 3) == 0);
}
