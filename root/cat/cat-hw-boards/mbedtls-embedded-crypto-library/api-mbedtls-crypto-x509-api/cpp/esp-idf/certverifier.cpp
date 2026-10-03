#include "mbedtls/x509_crt.h"
#include <iostream>

class CertVerifier {
public:
    static bool verify(mbedtls_x509_crt *crt, mbedtls_x509_crt *trustCa, const char *domain) {
        uint32_t flags = 0;
        int ret = mbedtls_x509_crt_verify(crt, trustCa, nullptr, domain, &flags, nullptr, nullptr);

        if (ret != 0 || flags != 0) {
            char buffer[512];
            mbedtls_x509_crt_verify_info(buffer, sizeof(buffer), "  ! ", flags);
            std::cerr << "Validation failed: " << buffer << std::endl;
            return false;
        }
        return true;
    }
};
