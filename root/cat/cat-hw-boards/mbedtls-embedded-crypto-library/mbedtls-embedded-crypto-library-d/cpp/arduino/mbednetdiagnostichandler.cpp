#include <Arduino.h>
#include "mbedtls/ssl.h"
#include "mbedtls/error.h"

class MbedNetDiagnosticHandler {
public:
    static int readNonBlockingData(mbedtls_ssl_context *ssl, uint8_t *buffer, size_t maxLen) {
        int result = mbedtls_ssl_read(ssl, buffer, maxLen);
        
        if (result > 0) {
            return result; // Успішно прочитано байтів
        }
        
        if (result == MBEDTLS_ERR_SSL_WANT_READ || result == MBEDTLS_ERR_SSL_WANT_WRITE) {
            return 0; // Неблокуючий стан: даних немає, очікуємо наступної ітерації
        }
        
        char errorString[100];
        mbedtls_strerror(result, errorString, sizeof(errorString));
        Serial.printf("Zboy mbedTLS IO: -0x%04X (%s)\n", -result, errorString);
        
        return result; // Повертаємо код збою
    }
};
