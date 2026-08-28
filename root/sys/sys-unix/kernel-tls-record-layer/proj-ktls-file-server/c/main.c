#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/sendfile.h>
#include <sys/stat.h>
#include <netinet/tcp.h>
#include <linux/tls.h>

/* Ініціалізація kTLS TX з ключами AES-128-GCM */
int setup_ktls_tx(int client_fd, const unsigned char *key, const unsigned char *iv, const unsigned char *salt) {
    /* 1. Активація ULP модуля "tls" */
    const char *ulp_name = "tls";
    if (setsockopt(client_fd, IPPROTO_TCP, TCP_ULP, ulp_name, strlen(ulp_name)) < 0) {
        perror("setsockopt TCP_ULP");
        return -1;
    }

    /* 2. Підготовка криптографічних параметрів */
    struct tls12_crypto_info_aes_gcm_128 crypto_info;
    memset(&crypto_info, 0, sizeof(crypto_info));

    crypto_info.info.version = TLS_1_2_VERSION;
    crypto_info.info.cipher_type = TLS_CIPHER_AES_GCM_128;

    memcpy(crypto_info.key, key, TLS_CIPHER_AES_GCM_128_KEY_SIZE);
    memcpy(crypto_info.iv, iv, TLS_CIPHER_AES_GCM_128_IV_SIZE);
    memcpy(crypto_info.salt, salt, TLS_CIPHER_AES_GCM_128_SALT_SIZE);
    /* Початковий послідовний номер запису (8 байт нулів на початку) */
    memset(crypto_info.rec_seq, 0, TLS_CIPHER_AES_GCM_128_REC_SEQ_SIZE);

    /* 3. Передача ключів у ядро для напрямку TX */
    if (setsockopt(client_fd, SOL_TLS, TLS_TX, &crypto_info, sizeof(crypto_info)) < 0) {
        perror("setsockopt SOL_TLS TLS_TX");
        return -1;
    }

    return 0;
}

/* Передача файлу через sendfile безпосередньо у kTLS сокет з обробкою часткової відправки */
ssize_t send_file_ktls(int client_fd, const char *filepath) {
    int file_fd = open(filepath, O_RDONLY);
    if (file_fd < 0) {
        perror("open file");
        return -1;
    }

    struct stat st;
    if (fstat(file_fd, &st) < 0) {
        perror("fstat");
        close(file_fd);
        return -1;
    }

    off_t offset = 0;
    size_t total_to_send = st.st_size;
    ssize_t total_sent = 0;

    /* Цикл для обробки можливої часткової відправки даних */
    while (total_sent < total_to_send) {
        ssize_t sent = sendfile(client_fd, file_fd, &offset, total_to_send - total_sent);
        if (sent < 0) {
            if (errno == EINTR) {
                continue; /* Переривання сигналом, повторюємо спробу */
            }
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                /* Буфер сокета заповнено у неблокуючому режимі */
                break;
            }
            perror("sendfile error");
            close(file_fd);
            return -1;
        }
        if (sent == 0) {
            break; /* Досягнуто кінця файлу або сокет закрито */
        }
        total_sent += sent;
    }

    close(file_fd);
    return total_sent;
}
