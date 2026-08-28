#include <sys/socket.h>
#include <netinet/tcp.h>
#include <linux/tls.h>
#include <string.h>
#include <stdio.h>

int enable_ktls_example(int sockfd, const struct tls12_crypto_info_aes_gcm_128 *crypto_tx) {
    /* 1. Нашарування ULP модуля kTLS поверх TCP */
    const char *ulp_name = "tls";
    if (setsockopt(sockfd, IPPROTO_TCP, TCP_ULP, ulp_name, strlen(ulp_name)) < 0) {
        perror("setsockopt TCP_ULP");
        return -1;
    }

    /* 2. Передача симетричних ключів у ядро для передачі (TX) */
    if (setsockopt(sockfd, SOL_TLS, TLS_TX, crypto_tx, sizeof(*crypto_tx)) < 0) {
        perror("setsockopt SOL_TLS TLS_TX");
        return -1;
    }

    return 0;
}
