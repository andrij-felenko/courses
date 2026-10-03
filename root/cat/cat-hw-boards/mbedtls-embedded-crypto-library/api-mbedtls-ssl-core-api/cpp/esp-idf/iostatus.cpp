#include "mbedtls/ssl.h"

enum class IoStatus {
    Ok,
    WaitRead,
    WaitWrite,
    PeerClosed,
    Error
};

class AsyncSslHandler {
public:
    static IoStatus stepHandshake(mbedtls_ssl_context *ssl) {
        int ret = mbedtls_ssl_handshake(ssl);
        if (ret == 0) return IoStatus::Ok;
        if (ret == MBEDTLS_ERR_SSL_WANT_READ) return IoStatus::WaitRead;
        if (ret == MBEDTLS_ERR_SSL_WANT_WRITE) return IoStatus::WaitWrite;
        return IoStatus::Error;
    }

    static IoStatus readPayload(mbedtls_ssl_context *ssl, unsigned char *buf, size_t len, int &bytesRead) {
        int ret = mbedtls_ssl_read(ssl, buf, len);
        if (ret > 0) {
            bytesRead = ret;
            return IoStatus::Ok;
        }
        if (ret == MBEDTLS_ERR_SSL_WANT_READ) return IoStatus::WaitRead;
        if (ret == MBEDTLS_ERR_SSL_PEER_CLOSE_NOTIFY) return IoStatus::PeerClosed;
        return IoStatus::Error;
    }
};
