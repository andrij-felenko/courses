/* c_ktls_raw.c - Низькорівнева активація kTLS на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <linux/tls.h>
#include <sys/sendfile.h>
#include <fcntl.h>

/*
 * Функція enable_ktls_tx виконує переведення звичайного TCP сокета
 * під управління підсистеми kTLS для вихідного напрямку даних (TX).
 */
int enable_ktls_tx(int sock_fd, const unsigned char *key, const unsigned char *iv,
                   const unsigned char *salt, uint64_t seq_num) {
    /* 1. Активація ULP модуля "tls" у мережевому стеку ядра */
    if (setsockopt(sock_fd, SOL_TCP, TCP_ULP, "tls", sizeof("tls")) < 0) {
        fprintf(stderr, "Помилка: Не вдалося зареєструвати ULP 'tls'. Перевірте modprobe tls. Code: %d\n", errno);
        return -1;
    }

    /* 2. Заповнення специфічної структури AES-GCM 128 біт */
    struct tls12_crypto_info_aes_gcm_128 crypto_info;
    memset(&crypto_info, 0, sizeof(crypto_info));

    crypto_info.info.version = TLS_1_2_VERSION;
    crypto_info.info.cipher_type = TLS_CIPHER_AES_GCM_128;

    memcpy(crypto_info.key, key, TLS_CIPHER_AES_GCM_128_KEY_SIZE);
    memcpy(crypto_info.iv, iv, TLS_CIPHER_AES_GCM_128_IV_SIZE);
    memcpy(crypto_info.salt, salt, TLS_CIPHER_AES_GCM_128_SALT_SIZE);
    memcpy(crypto_info.rec_seq, &seq_num, sizeof(seq_num));

    /* 3. Передача криптографічних ключів у рівень SOL_TLS */
    if (setsockopt(sock_fd, SOL_TLS, TLS_TX, &crypto_info, sizeof(crypto_info)) < 0) {
        fprintf(stderr, "Помилка: Не вдалося передати ключі SOL_TLS TLS_TX. Code: %d\n", errno);
        return -1;
    }

    printf("[kTLSEngine] kTLS ULP успішно активовано для TX на сокеті %d.\n", sock_fd);
    return 0;
}

/*
 * Передача файлу за допомогою Zero-Copy виклику sendfile() над kTLS сокетом.
 */
ssize_t send_file_ktls(int sock_fd, int file_fd, off_t *offset, size_t count) {
    ssize_t sent_bytes = sendfile(sock_fd, file_fd, offset, count);
    if (sent_bytes < 0) {
        fprintf(stderr, "Помилка виклику sendfile над kTLS сокетом: %d\n", errno);
    }
    return sent_bytes;
}
