#include "mbedtls/x509_crt.h"
#include <string.h>

// Текстовий PEM-сертифікат кореневого CA (із нульовим термінатором)
const char ca_pem_cert[] =
"-----BEGIN CERTIFICATE-----\n"
"MIIBvzCCAWagAwIBAgIJAO6nZ5k4mJ... (скорочено)\n"
"-----END CERTIFICATE-----\n";

// Завантаження та парсинг сертифіката X.509
int load_ca_certificate(mbedtls_x509_crt *ca_chain) {
    int ret;

    // Ініціалізація структури порожніми значеннями
    mbedtls_x509_crt_init(ca_chain);

    // Довжина включає нульовий термінатор для PEM
    size_t cert_len = strlen(ca_pem_cert) + 1;

    ret = mbedtls_x509_crt_parse(ca_chain, (const unsigned char *)ca_pem_cert, cert_len);
    if (ret != 0) {
        mbedtls_x509_crt_free(ca_chain);
        return ret; // Помилка парсингу (наприклад, пошкоджений Base64 або маркери)
    }

    return 0; // Сертифікат успішно розібрано та додано до ca_chain
}
