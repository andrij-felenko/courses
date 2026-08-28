#include <stdint.h>
#include <string.h>
#include <openssl/aes.h>
#include <openssl/hmac.h>
#include <openssl/crypto.h>

/* Побудова 128-бітного вектора IV для AES-CTR */
static void srtp_build_iv(const uint8_t *salt, uint32_t ssrc, uint64_t index, uint8_t *iv) {
    memcpy(iv, salt, 14);
    iv[14] = 0;
    iv[15] = 0;

    /* IV = (Salt << 16) ^ (SSRC << 64) ^ (Index << 16) */
    iv[4] ^= (uint8_t)(ssrc >> 24);
    iv[5] ^= (uint8_t)(ssrc >> 16);
    iv[6] ^= (uint8_t)(ssrc >> 8);
    iv[7] ^= (uint8_t)(ssrc & 0xFF);

    for (int b = 0; b < 6; ++b) {
        iv[8 + b] ^= (uint8_t)((index >> (8 * (5 - b))) & 0xFF);
    }
}

/* Шифрування корисного навантаження та додавання тега автентифікації */
int srtp_protect_packet(const srtp_session_keys_t *keys,
                        uint8_t *rtp_packet, size_len_t header_len, size_t payload_len,
                        uint32_t ssrc, uint64_t index, uint32_t roc,
                        size_t *out_total_len) {
    uint8_t iv[16];
    srtp_build_iv(keys->salt_key, ssrc, index, iv);

    AES_KEY aes_ctx;
    if (AES_set_encrypt_key(keys->enc_key, 128, &aes_ctx) != 0) {
        return -1;
    }

    /* Шифрування Payload у режимі AES-CTR */
    uint8_t ecount_buf[16] = {0};
    unsigned int num = 0;
    AES_ctr128_encrypt(rtp_packet + header_len, rtp_packet + header_len,
                       payload_len, &aes_ctx, iv, ecount_buf, &num);

    /* Обчислення HMAC-SHA1 поверх [Header || Encrypted_Payload || ROC] */
    uint8_t mac_out[32];
    unsigned int mac_len = 0;
    HMAC_CTX *hmac = HMAC_CTX_new();
    if (!hmac) return -1;

    HMAC_Init_ex(hmac, keys->auth_key, 20, EVP_sha1(), NULL);
    HMAC_Update(hmac, rtp_packet, header_len + payload_len);

    uint8_t roc_be[4] = {
        (uint8_t)(roc >> 24), (uint8_t)(roc >> 16),
        (uint8_t)(roc >> 8),  (uint8_t)(roc & 0xFF)
    };
    HMAC_Update(hmac, roc_be, 4);
    HMAC_Final(hmac, mac_out, &mac_len);
    HMAC_CTX_free(hmac);

    /* Додавання усіченого 80-бітного тега (10 байтів) у трейлер */
    memcpy(rtp_packet + header_len + payload_len, mac_out, 10);
    *out_total_len = header_len + payload_len + 10;

    return 0;
}

/* Верифікація підпису та дешифрування вхідного пакета */
int srtp_unprotect_packet(const srtp_session_keys_t *keys,
                          uint8_t *packet, size_t total_len, size_t header_len,
                          uint32_t ssrc, uint64_t index, uint32_t roc_est,
                          size_t *out_payload_len) {
    if (total_len < header_len + 10) {
        return -1;
    }
    size_t payload_len = total_len - header_len - 10;
    const uint8_t *received_tag = packet + header_len + payload_len;

    /* 1. Обчислення контрольного підпису HMAC-SHA1 */
    uint8_t mac_calc[32];
    unsigned int mac_len = 0;
    HMAC_CTX *hmac = HMAC_CTX_new();
    if (!hmac) return -1;

    HMAC_Init_ex(hmac, keys->auth_key, 20, EVP_sha1(), NULL);
    HMAC_Update(hmac, packet, header_len + payload_len);

    uint8_t roc_be[4] = {
        (uint8_t)(roc_est >> 24), (uint8_t)(roc_est >> 16),
        (uint8_t)(roc_est >> 8),  (uint8_t)(roc_est & 0xFF)
    };
    HMAC_Update(hmac, roc_be, 4);
    HMAC_Final(hmac, mac_calc, &mac_len);
    HMAC_CTX_free(hmac);

    /* 2. Константне порівняння тега автентифікації */
    if (CRYPTO_memcmp(received_tag, mac_calc, 10) != 0) {
        return -2; /* Помилка автентифікації */
    }

    /* 3. Дешифрування корисного навантаження */
    uint8_t iv[16];
    srtp_build_iv(keys->salt_key, ssrc, index, iv);

    AES_KEY aes_ctx;
    if (AES_set_encrypt_key(keys->enc_key, 128, &aes_ctx) != 0) {
        return -3;
    }

    uint8_t ecount_buf[16] = {0};
    unsigned int num = 0;
    AES_ctr128_encrypt(packet + header_len, packet + header_len,
                       payload_len, &aes_ctx, iv, ecount_buf, &num);

    *out_payload_len = payload_len;
    return 0;
}
