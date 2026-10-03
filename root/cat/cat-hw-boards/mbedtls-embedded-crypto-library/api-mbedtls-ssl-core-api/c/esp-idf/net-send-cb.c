#include "mbedtls/ssl.h"
#include "lwip/sockets.h"
#include <errno.h>

// Кастомний коллбек відправки даних через неблокуючий сокет lwIP
int net_send_cb(void *ctx, const unsigned char *buf, size_t len) {
    int fd = *((int *)ctx);
    int ret = send(fd, buf, len, 0);

    if (ret < 0) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return MBEDTLS_ERR_SSL_WANT_WRITE;
        }
        return -1;
    }
    return ret;
}

// Кастомний коллбек прийому даних через неблокуючий сокет lwIP
int net_recv_cb(void *ctx, unsigned char *buf, size_t len) {
    int fd = *((int *)ctx);
    int ret = recv(fd, buf, len, 0);

    if (ret < 0) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return MBEDTLS_ERR_SSL_WANT_READ;
        }
        return -1;
    }
    return ret;
}

void setup_bio(mbedtls_ssl_context *ssl, int *socket_fd) {
    // Прив'язка сокета та неблокуючих коллбеків до SSL-контексту
    mbedtls_ssl_set_bio(ssl, socket_fd, net_send_cb, net_recv_cb, NULL);
}
