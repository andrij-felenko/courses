#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    CBF_SUCCESS              =  0, /* Операція виконана успішно */
    CBF_ERR_INVALID_PARAM    = -1, /* Некоректні вхідні параметри (NULL-вказівник, нульова ємність) */
    CBF_ERR_NO_MEMORY        = -2, /* Помилка виділення динамічної пам'яті алокатором */
    CBF_ERR_NOT_FOUND        = -3, /* Елемент гарантовано відсутній при спробі видалення */
    CBF_ERR_BUFFER_TOO_SMALL = -4, /* Наданий користувачем буфер замалий для серіалізації/експорту */
    CBF_ERR_CORRUPT_DATA     = -5, /* Пошкоджені бінарні дані або невідповідність контрольної суми */
    CBF_ERR_INCOMPATIBLE     = -6, /* Невідповідність розмірів або параметрів хешування при злитті */
    CBF_ERR_IO               = -7, /* Помилка дискового введення-виведення або mmap */
    CBF_WARN_SATURATED       =  1  /* Операція успішна, але лічильник досяг максимуму 15 */
} CbfStatus;

typedef struct CountingBloomFilter CountingBloomFilter;

/* Тип функції зворотного виклику для користувацького хешування */
typedef void (*CbfCustomHashFn)(const void *key, size_t len, uint32_t seed, uint32_t *h1, uint32_t *h2);
