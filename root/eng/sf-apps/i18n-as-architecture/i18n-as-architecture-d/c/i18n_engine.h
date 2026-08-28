/* ============================================================================
 * i18n_engine.h — Компактний рушій локалізації на C99 (XIP / Zero-RAM Heap)
 * ============================================================================ */
#ifndef I18N_ENGINE_H
#define I18N_ENGINE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define I18N_MAGIC 0x4931384E /* 'I18N' */

typedef enum {
    PLURAL_ZERO = 0,
    PLURAL_ONE  = 1,
    PLURAL_TWO  = 2,
    PLURAL_FEW  = 3,
    PLURAL_MANY = 4,
    PLURAL_OTHER= 5
} i18n_plural_cat_t;

typedef struct {
    uint32_t key_hash;     /* MurmurHash3 ключа */
    uint32_t string_offset;/* Зміщення рядка в байтах від початку пулу */
} i18n_index_entry_t;

typedef struct {
    uint32_t magic;
    uint16_t version;
    uint16_t locale_id;
    uint32_t entry_count;
    uint32_t index_offset;
    uint32_t string_pool_offset;
    uint32_t plural_rule_id;
} i18n_binary_header_t;

typedef struct {
    const uint8_t *blob;
    size_t size;
    const i18n_index_entry_t *index;
    const char *string_pool;
    uint32_t entry_count;
    uint32_t plural_rule_id;
} i18n_catalog_t;

/* Обчислення MurmurHash3_32 для рядка ключа */
uint32_t i18n_hash_key(const char *key);

/* Ініціалізація каталогу з пам'яті Flash */
bool i18n_catalog_init(i18n_catalog_t *cat, const uint8_t *blob, size_t size);

/* Пошук локалізованого рядка за хешем ключа */
const char *i18n_get_by_hash(const i18n_catalog_t *cat, uint32_t hash);

/* Пошук локалізованого рядка за текстовим ключем */
const char *i18n_get(const i18n_catalog_t *cat, const char *key);

/* Розрахунок категорії множини за числом для заданого правила */
i18n_plural_cat_t i18n_eval_plural(uint32_t rule_id, int32_t n);

/* Форматування рядка з підстановкою цілого числа у буфер на стеку */
size_t i18n_format_i32(char *dst, size_t dst_max, const char *fmt, int32_t val);

#endif /* I18N_ENGINE_H */

/* ============================================================================
 * i18n_engine.c — Реалізація рушія на C99
 * ============================================================================ */
#include <string.h>

uint32_t i18n_hash_key(const char *key) {
    if (!key) return 0;
    uint32_t h = 0x9747b28c;
    const uint8_t *data = (const uint8_t *)key;
    while (*data) {
        uint32_t k = (uint32_t)(*data++);
        k *= 0xcc9e2d51;
        k = (k << 15) | (k >> 17);
        k *= 0x1b873593;
        
        h ^= k;
        h = (h << 13) | (h >> 19);
        h = h * 5 + 0xe6546b64;
    }
    h ^= (uint32_t)strlen(key);
    h ^= h >> 16;
    h *= 0x85ebca6b;
    h ^= h >> 13;
    h *= 0xc2b2ae35;
    h ^= h >> 16;
    return h;
}

bool i18n_catalog_init(i18n_catalog_t *cat, const uint8_t *blob, size_t size) {
    if (!cat || !blob || size < sizeof(i18n_binary_header_t)) return false;
    
    const i18n_binary_header_t *hdr = (const i18n_binary_header_t *)blob;
    if (hdr->magic != I18N_MAGIC) return false;
    
    if (hdr->index_offset + hdr->entry_count * sizeof(i18n_index_entry_t) > size ||
        hdr->string_pool_offset >= size) {
        return false;
    }
    
    cat->blob = blob;
    cat->size = size;
    cat->entry_count = hdr->entry_count;
    cat->plural_rule_id = hdr->plural_rule_id;
    cat->index = (const i18n_index_entry_t *)(blob + hdr->index_offset);
    cat->string_pool = (const char *)(blob + hdr->string_pool_offset);
    return true;
}

const char *i18n_get_by_hash(const i18n_catalog_t *cat, uint32_t hash) {
    if (!cat || !cat->index || cat->entry_count == 0) return NULL;
    
    int32_t low = 0;
    int32_t high = (int32_t)cat->entry_count - 1;
    
    while (low <= high) {
        int32_t mid = low + ((high - low) >> 1);
        uint32_t cur_hash = cat->index[mid].key_hash;
        
        if (cur_hash == hash) {
            uint32_t off = cat->index[mid].string_offset;
            return cat->string_pool + off;
        } else if (hash < cur_hash) {
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }
    return NULL;
}

const char *i18n_get(const i18n_catalog_t *cat, const char *key) {
    if (!key) return "";
    uint32_t hash = i18n_hash_key(key);
    const char *res = i18n_get_by_hash(cat, hash);
    return res ? res : key;
}

i18n_plural_cat_t i18n_eval_plural(uint32_t rule_id, int32_t n) {
    int32_t abs_n = n < 0 ? -n : n;
    
    switch (rule_id) {
        case 1: /* Англійська (en): one/other */
            return (abs_n == 1) ? PLURAL_ONE : PLURAL_OTHER;
            
        case 2: { /* Українська (uk): one/few/many/other */
            int32_t rem10 = abs_n % 10;
            int32_t rem100 = abs_n % 100;
            if (rem10 == 1 && rem100 != 11) {
                return PLURAL_ONE;
            }
            if (rem10 >= 2 && rem10 <= 4 && (rem100 < 10 || rem100 >= 20)) {
                return PLURAL_FEW;
            }
            return PLURAL_MANY;
        }
        
        case 3: /* Японська (ja): завжди other */
        default:
            return PLURAL_OTHER;
    }
}

size_t i18n_format_i32(char *dst, size_t dst_max, const char *fmt, int32_t val) {
    if (!dst || dst_max == 0 || !fmt) return 0;
    
    size_t d_idx = 0;
    const char *p = fmt;
    
    char num_buf[16];
    int num_len = 0;
    
    /* Конвертація числа в рядок */
    int32_t temp = val;
    bool neg = temp < 0;
    if (neg) temp = -temp;
    
    do {
        num_buf[num_len++] = (char)('0' + (temp % 10));
        temp /= 10;
    } while (temp > 0 && num_len < 14);
    
    if (neg) num_buf[num_len++] = '-';
    
    while (*p && d_idx < dst_max - 1) {
        if (p[0] == '{' && p[1] == '0' && p[2] == '}') {
            p += 3;
            /* Вставка числа у зворотному порядку цифр */
            for (int i = num_len - 1; i >= 0 && d_idx < dst_max - 1; --i) {
                dst[d_idx++] = num_buf[i];
            }
        } else {
            dst[d_idx++] = *p++;
        }
    }
    dst[d_idx] = '\0';
    return d_idx;
}
