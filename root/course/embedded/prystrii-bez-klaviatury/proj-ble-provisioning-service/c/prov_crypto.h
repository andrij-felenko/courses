#ifndef PROV_CRYPTO_H
#define PROV_CRYPTO_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define PROV_KEY_SIZE    32   /* X25519: і скаляр, і u-координата */
#define PROV_SALT_SIZE   16   /* сіль HKDF, віддається клієнтові у відповіді */
#define PROV_NONCE_SIZE  12   /* вектор ініціалізації AES-GCM */
#define PROV_TAG_SIZE    16   /* тег автентифікації GMAC */
#define PROV_PROOF_SIZE  32   /* HMAC-SHA256 доказу володіння */
#define PROV_POP_MAX_LEN 32

/* Затирання, яке компілятор не має права викинути як «мертвий запис». */
void prov_secure_wipe(void *ptr, size_t len);

/*
 * Порівняння за константний час: жодного раннього виходу.
 * memcmp() зупиняється на першому незбіжному байті, і час відповіді
 * BLE-пакета видає, скільки байтів PIN-коду вгадано.
 */
bool prov_ct_equal(const uint8_t *a, const uint8_t *b, size_t len);

/*
 * Санітизація чужого відкритого ключа: суцільні нулі, суцільні одиниці
 * та точки малого порядку (1, 2, 4, 8) — усе це відкидаємо.
 */
bool prov_pubkey_acceptable(const uint8_t pub[PROV_KEY_SIZE]);

/* Маскування бітів скаляра (clamping) за RFC 7748 §5. */
void prov_clamp_scalar(uint8_t priv[PROV_KEY_SIZE]);

/* Ефемерна пара: випадковий скаляр → clamping → публічний ключ. */
void prov_keypair(uint8_t priv[PROV_KEY_SIZE], uint8_t pub[PROV_KEY_SIZE]);

/*
 * Доказ володіння: клієнт надсилає HMAC-SHA256(pop, client_pub).
 * Знати PoP — означає знати наліпку на корпусі; повтор чужого доказу
 * атакуючому нічого не дає, бо спільний секрет вимагає закритого ключа клієнта.
 */
bool prov_pop_proof_valid(const uint8_t *pop, size_t pop_len,
                          const uint8_t client_pub[PROV_KEY_SIZE],
                          const uint8_t proof[PROV_PROOF_SIZE]);

/* ECDH + HKDF-SHA256: спільний секрет → сесійний ключ AES-256-GCM. */
bool prov_derive_session_key(const uint8_t our_priv[PROV_KEY_SIZE],
                             const uint8_t client_pub[PROV_KEY_SIZE],
                             const uint8_t device_pub[PROV_KEY_SIZE],
                             const uint8_t salt[PROV_SALT_SIZE],
                             const uint8_t *pop, size_t pop_len,
                             uint8_t out_key[PROV_KEY_SIZE]);

#endif /* PROV_CRYPTO_H */
