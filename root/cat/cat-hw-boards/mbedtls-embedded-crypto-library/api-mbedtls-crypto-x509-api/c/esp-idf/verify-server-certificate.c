#include "mbedtls/x509_crt.h"
#include <stdio.h>

// Верифікація ланцюжка сертифікатів та аналіз бітових прапорців
int verify_server_certificate(mbedtls_x509_crt *server_crt,
                              mbedtls_x509_crt *trust_ca,
                              const char *hostname) {
    uint32_t flags = 0;
    int ret;
    char vrify_buf[512];

    ret = mbedtls_x509_crt_verify(server_crt, trust_ca, NULL, hostname, &flags, NULL, NULL);

    if (ret != 0 || flags != 0) {
        // Розшифрування бітової маски помилок валідації
        mbedtls_x509_crt_verify_info(vrify_buf, sizeof(vrify_buf), "  ! ", flags);
        printf("Помилка верифікації сертифіката:\n%s\n", vrify_buf);

        if (flags & MBEDTLS_X509_BADCERT_EXPIRED) {
            printf("Деталі: Термін дії сертифіката вичерпано.\n");
        }
        if (flags & MBEDTLS_X509_BADCERT_NOT_TRUSTED) {
            printf("Деталі: Видавець не належить до довірених CA.\n");
        }
        if (flags & MBEDTLS_X509_BADCERT_CN_MISMATCH) {
            printf("Деталі: Невідповідність доменного імені %s.\n", hostname);
        }
        return -1; // Верифікацію не пройдено
    }

    printf("Сертифікат сервера успішно верифіковано.\n");
    return 0;
}
