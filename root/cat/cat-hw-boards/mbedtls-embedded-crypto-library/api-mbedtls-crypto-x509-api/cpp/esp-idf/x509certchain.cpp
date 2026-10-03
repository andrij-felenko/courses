#include "mbedtls/x509_crt.h"
#include <cstring>

class X509CertChain {
private:
    mbedtls_x509_crt chain_;
    bool loaded_;

public:
    X509CertChain() : loaded_(false) {
        mbedtls_x509_crt_init(&chain_);
    }

    ~X509CertChain() {
        mbedtls_x509_crt_free(&chain_);
    }

    bool parsePem(const char *pemCert) {
        size_t len = std::strlen(pemCert) + 1;
        int ret = mbedtls_x509_crt_parse(&chain_, reinterpret_cast<const unsigned char*>(pemCert), len);
        if (ret == 0) {
            loaded_ = true;
        }
        return loaded_;
    }

    mbedtls_x509_crt* getChain() { return &chain_; }
};
