#include <stdio.h>
#include <string.h>
#include <stdbool.h>

/* Імітація інтерфейсу сховища та віддаленого Redis */
typedef struct {
    TinyLfuSketch admission_filter;
    /* покажчик на з'єднання з Redis / локальний кеш */
} SmartCacheClient;

void smart_cache_init(SmartCacheClient *client) {
    tiny_lfu_init(&client->admission_filter);
}

/* Отримання значення з бази або кешу з фільтрацією допуску */
bool smart_cache_get_or_load(SmartCacheClient *client,
                             const char *key, size_t key_len,
                             char *out_buf, size_t out_max,
                             bool (*db_fetch_fn)(const char*, char*, size_t)) {
    // 1. Фіксуємо факт звернення в ескізі TinyLFU (дешева операція в RAM)
    tiny_lfu_record_access(&client->admission_filter, key, key_len);

    // 2. Спроба читання з кешу (наприклад, Redis GET)
    bool in_cache = false; /* імітація промаху */
    if (in_cache) {
        return true;
    }

    // 3. Промах повз кеш: читаємо з первинної бази даних
    if (!db_fetch_fn(key, out_buf, out_max)) {
        return false; // Запис у базі відсутній
    }

    // 4. Оцінка допуску перед записом у Redis
    uint8_t freq = tiny_lfu_estimate_frequency(&client->admission_filter, key, key_len);

    /* Якщо частота звернень перевищує поріг (наприклад, freq >= 2), зберігаємо в Redis */
    if (freq >= 2) {
        // redis_set(key, out_buf, TTL);
        // Запис допущено до кешу
    } else {
        // Кешування відхилено: повертаємо клієнту напряму з БД без забруднення Redis
    }

    return true;
}
