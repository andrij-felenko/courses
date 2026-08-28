#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CRYPTO_KEY_SIZE      32
#define CRYPTO_NONCE_SIZE    12
#define CRYPTO_TAG_SIZE      16
#define MAX_SSID_LEN         32
#define MAX_PASSPHRASE_LEN   64

typedef enum {
    PROV_STATUS_SUCCESS = 0,
    PROV_STATUS_INVALID_LEN,
    PROV_STATUS_CRYPTO_FAIL,
    PROV_STATUS_AUTH_FAIL,
    PROV_STATUS_STATION_TIMEOUT
} prov_status_t;

typedef struct {
    char ssid[MAX_SSID_LEN + 1];
    char password[MAX_PASSPHRASE_LEN + 1];
} wifi_credentials_t;

typedef struct {
    uint8_t priv_key[CRYPTO_KEY_SIZE];
    uint8_t pub_key[CRYPTO_KEY_SIZE];
    uint8_t session_key[CRYPTO_KEY_SIZE];
    bool    session_established;
} prov_crypto_context_t;

/* Платформні криптографічні функції */
extern void crypto_generate_x25519_keypair(uint8_t *pub, uint8_t *priv);
extern bool crypto_x25519_shared_secret(const uint8_t *peer_pub, const uint8_t *our_priv, uint8_t *shared);
extern void crypto_hkdf_sha256(const uint8_t *salt, size_t salt_len,
                               const uint8_t *ikm, size_t ikm_len,
                               const uint8_t *pop, size_t pop_len,
                               uint8_t *okm, size_t okm_len);
extern bool crypto_aes_gcm_decrypt(const uint8_t *key, const uint8_t *nonce,
                                   const uint8_t *tag, const uint8_t *ciphertext,
                                   size_t len, uint8_t *plaintext);

/* Безпечне очищення чутливих даних без оптимізації компілятором */
static void secure_wipe(void *v, size_t n) {
    volatile uint8_t *p = (volatile uint8_t *)v;
    while (n--) *p++ = 0;
}

/* Санітизація відкритого ключа клієнта */
static bool is_valid_curve_point(const uint8_t *pub) {
    uint8_t all_zeros = 0;
    for (size_t i = 0; i < CRYPTO_KEY_SIZE; ++i) {
        all_zeros |= pub[i];
    }
    return (all_zeros != 0); // Відкидаємо повністю нульові точки
}

/* Обробка рукостискання на характеристиці prov-session */
prov_status_t prov_handle_session_write(prov_crypto_context_t *ctx,
                                        const uint8_t *client_pub, size_t client_pub_len,
                                        const uint8_t *pop_token, size_t pop_len,
                                        uint8_t *device_pub_out, uint8_t *nonce_salt_out)
{
    if (client_pub_len != CRYPTO_KEY_SIZE || !is_valid_curve_point(client_pub)) {
        return PROV_STATUS_INVALID_LEN;
    }

    /* 1. Генеруємо власну ефемерну пару ключів X25519 */
    crypto_generate_x25519_keypair(ctx->pub_key, ctx->priv_key);
    memcpy(device_pub_out, ctx->pub_key, CRYPTO_KEY_SIZE);

    /* 2. Обчислюємо спільний секрет Diffie-Hellman */
    uint8_t shared_secret[CRYPTO_KEY_SIZE];
    if (!crypto_x25519_shared_secret(client_pub, ctx->priv_key, shared_secret)) {
        return PROV_STATUS_CRYPTO_FAIL;
    }

    /* 3. Заповнюємо псевдовипадкову сіль (Nonce) */
    memset(nonce_salt_out, 0xA5, CRYPTO_NONCE_SIZE);

    /* 4. Виводимо симетричний сесійний ключ AES-256 через HKDF-SHA256 разом із PoP */
    crypto_hkdf_sha256(nonce_salt_out, CRYPTO_NONCE_SIZE,
                       shared_secret, CRYPTO_KEY_SIZE,
                       pop_token, pop_len,
                       ctx->session_key, CRYPTO_KEY_SIZE);

    /* Безпечне очищення проміжного спільного секрету зі стека */
    secure_wipe(shared_secret, sizeof(shared_secret));
    ctx->session_established = true;
    return PROV_STATUS_SUCCESS;
}

/* Розшифрування корисного навантаження SSID та Password на характеристиці prov-config */
prov_status_t prov_handle_config_write(prov_crypto_context_t *ctx,
                                       const uint8_t *encrypted_payload, size_t payload_len,
                                       wifi_credentials_t *out_creds)
{
    if (!ctx->session_established) {
        return PROV_STATUS_AUTH_FAIL;
    }

    if (payload_len <= (CRYPTO_NONCE_SIZE + CRYPTO_TAG_SIZE)) {
        return PROV_STATUS_INVALID_LEN;
    }

    const uint8_t *nonce = encrypted_payload;
    const uint8_t *tag = encrypted_payload + CRYPTO_NONCE_SIZE;
    const uint8_t *ciphertext = encrypted_payload + CRYPTO_NONCE_SIZE + CRYPTO_TAG_SIZE;
    size_t cipher_len = payload_len - CRYPTO_NONCE_SIZE - CRYPTO_TAG_SIZE;

    uint8_t plaintext[MAX_SSID_LEN + MAX_PASSPHRASE_LEN + 4];
    if (cipher_len >= sizeof(plaintext)) {
        return PROV_STATUS_INVALID_LEN;
    }

    /* Автентифіковане розшифрування AES-GCM */
    if (!crypto_aes_gcm_decrypt(ctx->session_key, nonce, tag, ciphertext, cipher_len, plaintext)) {
        return PROV_STATUS_CRYPTO_FAIL;
    }

    /* Формат TLV: [SSID_Len:1B][SSID][Pass_Len:1B][Password] */
    uint8_t ssid_len = plaintext[0];
    if (ssid_len > MAX_SSID_LEN || (1 + ssid_len) >= cipher_len) {
        return PROV_STATUS_INVALID_LEN;
    }
    memcpy(out_creds->ssid, &plaintext[1], ssid_len);
    out_creds->ssid[ssid_len] = '\0';

    uint8_t pass_len = plaintext[1 + ssid_len];
    if (pass_len > MAX_PASSPHRASE_LEN || (2 + ssid_len + pass_len) > cipher_len) {
        return PROV_STATUS_INVALID_LEN;
    }
    memcpy(out_creds->password, &plaintext[2 + ssid_len], pass_len);
    out_creds->password[pass_len] = '\0';

    /* Безпечне затирання буфера відкритого тексту */
    secure_wipe(plaintext, sizeof(plaintext));
    return PROV_STATUS_SUCCESS;
}
