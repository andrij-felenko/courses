#include <string.h>
#include "mbedtls/ssl.h"
#include "mbedtls/net_sockets.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/entropy.h"

// Виконання рукостискання TLS у неблокуючому режимі
int execute_tls_handshake(mbedtls_ssl_context *ssl) {
    int ret;
    
    // Цикл виконання кроків кінцевого автомата рукостискання
    while ((ret = mbedtls_ssl_handshake(ssl)) != 0) {
        if (ret == MBEDTLS_ERR_SSL_WANT_READ || ret == MBEDTLS_ERR_SSL_WANT_WRITE) {
            // Мережевий буфер ще не готовий, повертаємо контроль системному циклу
            return ret;
        }
        if (ret != 0) {
            // Фатальна помилка рукостискання (наприклад, збій валідації сертифіката)
            return ret;
        }
    }
    
    // Рукостискання успішно завершено (стан MBEDTLS_SSL_HANDSHAKE_OVER)
    return 0;
}
