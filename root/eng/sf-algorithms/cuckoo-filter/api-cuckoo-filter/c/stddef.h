#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    CUCKOO_SUCCESS = 0,         /* Операція виконана успішно */
    CUCKOO_NOT_FOUND = 1,       /* Елемент відсутній при спробі видалення */
    CUCKOO_ERR_FULL = -1,       /* Вичерпано ліміт витіснень: таблиця переповнена */
    CUCKOO_ERR_INVALID_ARG = -2,/* Некоректні вхідні аргументи (NULL, capacity = 0) */
    CUCKOO_ERR_NO_MEM = -3      /* Не вдалося виділити пам'ять */
} CuckooStatus;

typedef struct CuckooFilter CuckooFilter;

/* Створення нового фільтра з автоматичним підбором розміру */
CuckooFilter *cuckoo_init(size_t capacity, double target_fpr);

/* Звільнення всіх виділених ресурсів */
void cuckoo_free(CuckooFilter *filter);

/* Вставка ключа довільної довжини */
CuckooStatus cuckoo_insert(CuckooFilter *filter, const void *key, size_t key_len);

/* Перевірка належності ключа множині */
bool cuckoo_contains(const CuckooFilter *filter, const void *key, size_t key_len);

/* Видалення одного екземпляра ключа */
CuckooStatus cuckoo_delete(CuckooFilter *filter, const void *key, size_t key_len);

/* Поточний коефіцієнт заповнення (load factor) */
double cuckoo_get_load_factor(const CuckooFilter *filter);

/* Кількість фактично збережених елементів */
size_t cuckoo_get_count(const CuckooFilter *filter);

/* Загальна місткість фільтра у слотах */
size_t cuckoo_get_capacity(const CuckooFilter *filter);

/* Обсяг виділеної оперативної пам'яті в байтах */
size_t cuckoo_get_memory_bytes(const CuckooFilter *filter);

/* Очищення всіх слотів фільтра без перевиділення пам'яті */
void cuckoo_clear(CuckooFilter *filter);

#ifdef __cplusplus
}
#endif
