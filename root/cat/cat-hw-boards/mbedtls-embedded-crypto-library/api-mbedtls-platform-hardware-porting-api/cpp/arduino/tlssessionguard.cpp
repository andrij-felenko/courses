#include "mbedtls/ssl.h"
#include "mbedtls/error.h"

class TlsSessionGuard {
private:
    mbedtls_ssl_context ssl_;
    mbedtls_ssl_config conf_;
    bool initialized_;

public:
    TlsSessionGuard() : initialized_(false) {
        mbedtls_ssl_init(&ssl_);
        mbedtls_ssl_config_init(&conf_);
    }

    ~TlsSessionGuard() {
        mbedtls_ssl_free(&ssl_);
        mbedtls_ssl_config_free(&conf_);
    }

    bool connectSession() {
        int status = mbedtls_ssl_handshake(&ssl_);
        if (status != 0) {
            char err_msg[128];
            mbedtls_strerror(status, err_msg, sizeof(err_msg));
            // Автоматичне звільнення в деструкторі при виході з області видимості
            return false;
        }
        return true;
    }
};
