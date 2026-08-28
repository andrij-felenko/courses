/* Приклад на C: Встановлення ключів TX */
#include <linux/tls.h>
#include <string.h>

struct tls12_crypto_info_aes_gcm_128 crypto_info;
memset(&crypto_info, 0, sizeof(crypto_info));

crypto_info.info.version = TLS_1_2_VERSION; /* Або TLS_1_3_VERSION */
crypto_info.info.cipher_type = TLS_CIPHER_AES_GCM_128;

/* Копіюємо ключі, вилучені з OpenSSL після Handshake */
memcpy(crypto_info.key, aes_key, TLS_CIPHER_AES_GCM_128_KEY_SIZE);
memcpy(crypto_info.iv, gcm_iv, TLS_CIPHER_AES_GCM_128_IV_SIZE);
memcpy(crypto_info.salt, gcm_salt, TLS_CIPHER_AES_GCM_128_SALT_SIZE);
memcpy(crypto_info.rec_seq, seq_number, TLS_CIPHER_AES_GCM_128_REC_SEQ_SIZE);

/* Активуємо шифрування вихідного потоку */
if (setsockopt(sock_fd, SOL_TLS, TLS_TX, &crypto_info, sizeof(crypto_info)) < 0) {
    perror("Помилка setsockopt TLS_TX");
}
