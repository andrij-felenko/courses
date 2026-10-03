#include "mbedtls/ssl.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/entropy.h"

class TlsConnection {
private:
    mbedtls_ssl_config conf_;
    mbedtls_ssl_context ssl_;

public:
    TlsConnection() {
        mbedtls_ssl_config_init(&conf_);
        mbedtls_ssl_init(&ssl_);
    }

    ~TlsConnection() {
        mbedtls_ssl_free(&ssl_);
        mbedtls_ssl_config_free(&conf_);
    }

    bool configure(mbedtls_ctr_drbg_context *ctr_drbg) {
        int ret = mbedtls_ssl_config_defaults(&conf_,
                                              MBEDTLS_SSL_IS_CLIENT,
                                              MBEDTLS_SSL_TRANSPORT_STREAM,
                                              MBEDTLS_SSL_PRESET_DEFAULT);
        if (ret != 0) return false;

        mbedtls_ssl_conf_rng(&conf_, mbedtls_ctr_drbg_random, ctr_drbg);

        ret = mbedtls_ssl_setup(&ssl_, &conf_);
        return (ret == 0);
    }
};
