#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_KEY_LEN 256

/* Генерація версіонованого ключа кешу для запобігання Poisoning */
bool format_versioned_cache_key(uint32_t schema_major,
                                const char *entity_name,
                                uint64_t entity_id,
                                char *out_key_buf,
                                size_t buf_size) {
    if (!entity_name || !out_key_buf || buf_size == 0) return false;

    int written = snprintf(out_key_buf, buf_size, "cache:v%u:%s:%llu",
                           schema_major, entity_name, (unsigned long long)entity_id);

    return (written > 0 && (size_t)written < buf_size);
}

/* Перевірка сумісності запису кешу з поточною версією процесу */
bool is_cache_entry_compatible(uint32_t entry_schema_major, uint32_t node_schema_major) {
    /* Сувора ізоляція: читання дозволено лише в межах однакового мажора */
    return (entry_schema_major == node_schema_major);
}
