#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Коди результатів операцій побудовника ключів */
typedef enum {
    CACHE_KEY_OK = 0,
    CACHE_KEY_ERR_NULL_PARAM,
    CACHE_KEY_ERR_INVALID_CHARS,
    CACHE_KEY_ERR_OVERFLOW,
    CACHE_KEY_ERR_EMPTY_FIELD,
    CACHE_KEY_ERR_INVALID_VERSION,
    CACHE_KEY_ERR_INVALID_TAG,
    CACHE_KEY_ERR_UNSORTED_PARAMS
} CacheKeyStatus;

/* Підтримувані алгоритми згортання фільтрів */
typedef enum {
    DIGEST_NONE = 0,
    DIGEST_MURMUR3_64,
    DIGEST_XXHASH64,
    DIGEST_BLAKE3_128
} KeyDigestAlgorithm;

/* Дескриптор вхідних параметрів для генерації ключа */
typedef struct {
    const char* namespace_name;  /* Ідентифікатор сервісу (наприклад, "orders") */
    const char* tenant_id;       /* Орендар (наприклад, "tenant_42" або "global") */
    const char* entity_name;     /* Назва сутності (наприклад, "shipment") */
    const char* entity_id;       /* Первинний ідентифікатор ("982310") */
    const char* hash_tag;        /* Опціональний хеш-тег слота (без дужок) */
    uint32_t schema_version;     /* Номер версії моделі (>= 1) */
    KeyDigestAlgorithm digest_algo;
    const char* query_params;    /* Рядок фільтрів для хешування */
    int32_t salt_index;          /* -1 якщо без солі, >= 0 для розщеплення */
} KeyDescriptor;

/* Побудувати канонічний рядок ключа у наданий буфер */
CacheKeyStatus cache_key_build(
    const KeyDescriptor* desc,
    char* out_buffer,
    size_t buffer_size,
    size_t* out_written_len
);

/* Вилучити вміст хеш-тега {..} для ручної маршрутизації */
CacheKeyStatus cache_key_extract_tag(
    const char* full_key,
    char* out_tag,
    size_t tag_buffer_size
);

/* Перевірити наявність солі та отримати числовий індекс */
bool cache_key_is_salted(const char* full_key, uint32_t* out_salt_index);
