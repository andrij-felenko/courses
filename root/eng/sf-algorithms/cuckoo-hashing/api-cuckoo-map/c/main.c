#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Коди результатів виконання операцій */
typedef enum {
    CUCKOO_OK               =  0,  /* Операція завершилася успішно */
    CUCKOO_ERR_NOT_FOUND    = -1,  /* Ключ не знайдено в жодній таблиці чи схованці */
    CUCKOO_ERR_KEY_EXISTS   = -2,  /* Ключ уже присутній у таблиці */
    CUCKOO_ERR_NO_MEMORY    = -3,  /* Збій виділення динамічної пам'яті */
    CUCKOO_ERR_REHASH_FAIL  = -4,  /* Не вдалося перехешувати таблицю після вичерпання спроб */
    CUCKOO_WARN_STASH_USED  =  1   /* Елемент збережено в аварійній схованці */
} CuckooStatus;

/* Статистика внутрішнього стану таблиці */
typedef struct {
    size_t total_elements;        /* Загальна кількість збережених пар */
    size_t table_capacity;         /* Сумарна місткість основних таблиць T1 + T2 */
    size_t stash_count;            /* Поточна кількість елементів у схованці */
    size_t rehash_count;           /* Кількість виконаних перехешувань за час життя */
    double load_factor;            /* Поточний коефіцієнт заповнення (elements / capacity) */
} CuckooStats;

/* Непрозора структура хеш-таблиці */
typedef struct CuckooMap CuckooMap;
