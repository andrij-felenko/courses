#include <stdint.h>
#include <stddef.h>

/**
 * @brief Безпечне порівняння двох буферів фіксованої довжини за константний час.
 * @return 0, якщо буфери ідентичні; ненульове значення, якщо є хоча б один відмінний біт.
 */
int crypto_verify_ct(const uint8_t *a, const uint8_t *b, size_t len) {
    // volatile запобігає спробам оптимізатора розгорнути або скоротити обчислення
    volatile uint8_t diff = 0;
    
    for (size_t i = 0; i < len; i++) {
        diff |= (a[i] ^ b[i]);
    }
    
    // diff == 0 тоді й тільки тоді, коли кожен байт a[i] == b[i]
    return (int)diff;
}
