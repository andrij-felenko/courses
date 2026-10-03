#include "mbedtls/ssl.h"
#include "lwip/sockets.h"
#include <errno.h>

class SocketTransport {
public:
    static int sendCallback(void *ctx, const unsigned char *buf, size_t len) {
        int fd = *static_cast<int *>(ctx);
        int ret = send(fd, buf, len, 0);
        if (ret < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                return MBEDTLS_ERR_SSL_WANT_WRITE;
            }
            return -1;
        }
        return ret;
    }

    static int recvCallback(void *ctx, unsigned char *buf, size_t len) {
        int fd = *static_cast<int *>(ctx);
        int ret = recv(fd, buf, len, 0);
        if (ret < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                return MBEDTLS_ERR_SSL_WANT_READ;
            }
            return -1;
        }
        return ret;
    }
};
