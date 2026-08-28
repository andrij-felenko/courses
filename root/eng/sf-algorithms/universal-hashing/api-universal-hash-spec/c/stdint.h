#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/**
 * @brief Перелік можливих статусових кодів помилок API хешування.
 */
typedef enum {
    UH_SUCCESS              =  0,  /**< Операція виконана успішно */
    UH_ERR_INVALID_PARAM    = -1,  /**< Некоректні параметри (нульові вказівники, m=0) */
    UH_ERR_ENTROPY_FAILURE  = -2,  /**< Помилка зчитування системного джерела ентропії */
    UH_ERR_OUT_OF_RANGE     = -3,  /**< Ключ перевищує допустимий простір U */
    UH_ERR_BAD_ALIGNMENT    = -4   /**< Невирівняна адреса буферу */
} uh_status_t;

/**
 * @brief Перелік доступних типів універсальних сімейств.
 */
typedef enum {
    UH_FAMILY_MODULAR_P61   = 1,   /**< Модульне сімейство над полем GF(2^61 - 1) */
    UH_FAMILY_MULTIPLY_SHIFT = 2,  /**< Множильно-зсувне сімейство Dietzfelbinger (mod 2^64) */
    UH_FAMILY_TABULATION_64  = 3   /**< Табульоване хешування (8x256 таблиці) */
} uh_family_type_t;

/**
 * @brief Структура конфігурації генератора універсальних хеш-функцій.
 */
typedef struct {
    uh_family_type_t family_type;  /**< Тип обраного сімейства */
    uint64_t num_buckets;          /**< Кількість бакетів (m). Для MultiplyShift має бути 2^M */
    uint64_t custom_seed;          /**< Явне зерно ентропії (якщо 0, зчитується з OS CSPRNG) */
    bool use_custom_seed;          /**< Прапор використання кастомного зерна */
} uh_config_t;

/**
 * @brief Непрозорий контекст екземпляра універсальної хеш-функції.
 */
typedef struct uh_context uh_context_t;

/**
 * @brief Створення та ініціалізація нового екземпляра хеш-функції.
 *
 * @param[out] ctx_out Вказівник на створений контекст.
 * @param[in]  config  Структура параметрів ініціалізації.
 * @return uh_status_t Статус виконання операції.
 */
uh_status_t uh_create(uh_context_t **ctx_out, const uh_config_t *config);

/**
 * @brief Обчислення 64-бітного хеш-коду для 64-бітного цілого ключа.
 *
 * @param[in]  ctx   Контекст хеш-функції.
 * @param[in]  key   Вхідне 64-бітне значення ключа.
 * @param[out] hash  Результат хешування у діапазоні [0 .. m-1].
 * @return uh_status_t Статус виконання.
 */
uh_status_t uh_hash_uint64(const uh_context_t *ctx, uint64_t key, uint64_t *hash);

/**
 * @brief Обчислення хеш-коду для послідовності байтів (рядка).
 *
 * @param[in]  ctx   Контекст хеш-функції.
 * @param[in]  data  Вказівник на байтовий масив.
 * @param[in]  len   Довжина масиву в байтах.
 * @param[out] hash  Результат хешування у діапазоні [0 .. m-1].
 * @return uh_status_t Статус виконання.
 */
uh_status_t uh_hash_bytes(const uh_context_t *ctx, const void *data, size_t len, uint64_t *hash);

/**
 * @brief Генерація нової випадкової хеш-функції з того ж сімейства (reseed).
 *
 * @param[in,out] ctx Контекст для оновлення параметрів.
 * @return uh_status_t Статус виконання.
 */
uh_status_t uh_reseed(uh_context_t *ctx);

/**
 * @brief Звільнення ресурсів контексту та безпечне очищення зерен.
 *
 * @param[in] ctx Контекст для знищення.
 */
void uh_destroy(uh_context_t *ctx);
