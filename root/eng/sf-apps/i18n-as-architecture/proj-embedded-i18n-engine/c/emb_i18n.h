/* ============================================================================
 * emb_i18n.h — Промисловий рушій інтернаціоналізації на C99 для вбудованих систем
 * ============================================================================ */
#ifndef EMB_I18N_H
#define EMB_I18N_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define EMB_I18N_MAGIC 0x45493138 /* ASCII 'EI18' */
#define EMB_I18N_VERSION 1

/* Категорії множини Unicode CLDR */
typedef enum {
    EMB_PLURAL_ZERO  = 0,
    EMB_PLURAL_ONE   = 1,
    EMB_PLURAL_TWO   = 2,
    EMB_PLURAL_FEW   = 3,
    EMB_PLURAL_MANY  = 4,
    EMB_PLURAL_OTHER = 5,
    EMB_PLURAL_COUNT = 6
} emb_plural_category_t;

/* Тип повідомлення */
typedef enum {
    EMB_MSG_SIMPLE = 0,
    EMB_MSG_PLURAL = 1
} emb_msg_type_t;

/* Заголовок двійкового образу */
#pragma pack(push, 4)
typedef struct {
    uint32_t magic;
    uint16_t version;
    uint16_t flags;
    uint32_t locale_count;
    uint32_t locale_table_offset;
    uint32_t total_size;
    uint32_t crc32;
    uint32_t reserved[2];
} emb_image_header_t;

/* Дескриптор локалі */
typedef struct {
    uint32_t locale_id;          /* MurmurHash3 від тегу локалі, напр. "uk-UA" */
    uint16_t plural_rule_id;     /* Ідентифікатор правила множини CLDR */
    uint16_t flags;              /* Bit 0: RTL напрям тексту */
    uint32_t message_count;
    uint32_t index_table_offset;
    uint32_t string_pool_offset;
} emb_locale_desc_t;

/* Запис таблиці індексу ключів */
typedef struct {
    uint32_t key_hash;           /* MurmurHash3 від текстового ключа */
    uint32_t msg_desc_offset;    /* Зміщення дескриптора повідомлення */
} emb_index_entry_t;

/* Дескриптор повідомлення */
typedef struct {
    uint8_t  type;               /* emb_msg_type_t: 0=Simple, 1=Plural */
    uint8_t  reserved;
    uint16_t form_count;         /* Кількість форм множини */
    uint32_t string_offsets[6];  /* Зміщення рядків у пулі для категорій CLDR */
} emb_msg_desc_t;
#pragma pack(pop)

/* Контекст відкритої локалі */
typedef struct {
    const uint8_t           *image_base;
    size_t                  image_size;
    const emb_locale_desc_t *locale;
    const emb_index_entry_t *index_table;
    const char              *string_pool;
    uint32_t                message_count;
    uint16_t                plural_rule_id;
    bool                    is_rtl;
} emb_i18n_ctx_t;

/* Обчислення 32-бітного хешу MurmurHash3 */
uint32_t emb_i18n_hash(const char *key);

/* Ініціалізація контексту локалі з пам'яті Flash */
bool emb_i18n_init(emb_i18n_ctx_t *ctx, const uint8_t *blob, size_t size, uint32_t locale_id);

/* Пошук простого повідомлення за числовим хешем */
const char *emb_i18n_get_by_hash(const emb_i18n_ctx_t *ctx, uint32_t hash);

/* Пошук простого повідомлення за текстовим ключем */
const char *emb_i18n_get(const emb_i18n_ctx_t *ctx, const char *key);

/* Розрахунок категорії множини за правилами CLDR */
emb_plural_category_t emb_i18n_eval_plural(uint16_t rule_id, int32_t n);

/* Пошук множинного повідомлення за числовим хешем та значенням count */
const char *emb_i18n_get_plural_by_hash(const emb_i18n_ctx_t *ctx, uint32_t hash, int32_t count);

/* Пошук множинного повідомлення за текстовим ключем та значенням count */
const char *emb_i18n_get_plural(const emb_i18n_ctx_t *ctx, const char *key, int32_t count);

/* Форматування рядка з підстановкою цілого числа {0} у стек-буфер */
size_t emb_i18n_format_1i(char *dst, size_t max_len, const char *fmt, int32_t arg0);

/* Форматування рядка з підстановкою числа {0} та рядка {1} у стек-буфер */
size_t emb_i18n_format_1i_1s(char *dst, size_t max_len, const char *fmt, int32_t arg0, const char *arg1);

#ifdef __cplusplus
}
#endif

#endif /* EMB_I18N_H */

/* ============================================================================
 * emb_i18n.c — Реалізація рушія локалізації на C99 (Zero-RAM Heap / Flash XIP)
 * ============================================================================ */
#include <string.h>

/* Хеш-функція MurmurHash3_32 */
uint32_t emb_i18n_hash(const char *key) {
    if (!key) return 0;
    
    uint32_t h = 0x9747b28c;
    const uint8_t *data = (const uint8_t *)key;
    size_t len = 0;
    
    while (data[len]) {
        uint32_t k = (uint32_t)data[len++];
        k *= 0xcc9e2d51;
        k = (k << 15) | (k >> 17);
        k *= 0x1b873593;
        
        h ^= k;
        h = (h << 13) | (h >> 19);
        h = h * 5 + 0xe6546b64;
    }
    
    h ^= (uint32_t)len;
    h ^= h >> 16;
    h *= 0x85ebca6b;
    h ^= h >> 13;
    h *= 0xc2b2ae35;
    h ^= h >> 16;
    return h;
}

/* Ініціалізація та валідація образу */
bool emb_i18n_init(emb_i18n_ctx_t *ctx, const uint8_t *blob, size_t size, uint32_t locale_id) {
    if (!ctx || !blob || size < sizeof(emb_image_header_t)) return false;
    
    const emb_image_header_t *hdr = (const emb_image_header_t *)blob;
    if (hdr->magic != EMB_I18N_MAGIC || hdr->version != EMB_I18N_VERSION) {
        return false;
    }
    
    if (hdr->total_size > size || hdr->locale_table_offset >= size) {
        return false;
    }
    
    const emb_locale_desc_t *loc_table = (const emb_locale_desc_t *)(blob + hdr->locale_table_offset);
    const emb_locale_desc_t *target_locale = NULL;
    
    for (uint32_t i = 0; i < hdr->locale_count; ++i) {
        if (loc_table[i].locale_id == locale_id) {
            target_locale = &loc_table[i];
            break;
        }
    }
    
    /* Якщо точний ID не знайдено, беремо першу локаль як fallback */
    if (!target_locale && hdr->locale_count > 0) {
        target_locale = &loc_table[0];
    }
    
    if (!target_locale) return false;
    
    size_t index_bytes = (size_t)target_locale->message_count * sizeof(emb_index_entry_t);
    if (target_locale->index_table_offset + index_bytes > size ||
        target_locale->string_pool_offset >= size) {
        return false;
    }
    
    ctx->image_base     = blob;
    ctx->image_size     = size;
    ctx->locale         = target_locale;
    ctx->message_count  = target_locale->message_count;
    ctx->plural_rule_id = target_locale->plural_rule_id;
    ctx->is_rtl         = (target_locale->flags & 0x0001) != 0;
    ctx->index_table    = (const emb_index_entry_t *)(blob + target_locale->index_table_offset);
    ctx->string_pool    = (const char *)(blob + target_locale->string_pool_offset);
    return true;
}

/* Бінарний пошук дескриптора повідомлення за хешем */
static const emb_msg_desc_t *emb_find_msg(const emb_i18n_ctx_t *ctx, uint32_t hash) {
    if (!ctx || !ctx->index_table || ctx->message_count == 0) return NULL;
    
    int32_t low = 0;
    int32_t high = (int32_t)ctx->message_count - 1;
    
    while (low <= high) {
        int32_t mid = low + ((high - low) >> 1);
        uint32_t cur_hash = ctx->index_table[mid].key_hash;
        
        if (cur_hash == hash) {
            uint32_t desc_off = ctx->index_table[mid].msg_desc_offset;
            if (desc_off + sizeof(emb_msg_desc_t) <= ctx->image_size) {
                return (const emb_msg_desc_t *)(ctx->image_base + desc_off);
            }
            return NULL;
        } else if (hash < cur_hash) {
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }
    return NULL;
}

/* Отримання простого рядка */
const char *emb_i18n_get_by_hash(const emb_i18n_ctx_t *ctx, uint32_t hash) {
    const emb_msg_desc_t *desc = emb_find_msg(ctx, hash);
    if (!desc || desc->type != EMB_MSG_SIMPLE) return NULL;
    
    uint32_t str_off = desc->string_offsets[0];
    if (ctx->locale->string_pool_offset + str_off < ctx->image_size) {
        return ctx->string_pool + str_off;
    }
    return NULL;
}

const char *emb_i18n_get(const emb_i18n_ctx_t *ctx, const char *key) {
    if (!key) return "";
    uint32_t hash = emb_i18n_hash(key);
    const char *res = emb_i18n_get_by_hash(ctx, hash);
    return res ? res : key;
}

/* Обчислення категорії множини CLDR */
emb_plural_category_t emb_i18n_eval_plural(uint16_t rule_id, int32_t n) {
    int32_t abs_n = n < 0 ? -n : n;
    
    switch (rule_id) {
        case 1: /* English (en): 1 -> one, other */
            return (abs_n == 1) ? EMB_PLURAL_ONE : EMB_PLURAL_OTHER;
            
        case 2: { /* Ukrainian / Slavic (uk): 1,21.. -> one; 2..4,22.. -> few; 0,5..20 -> many */
            int32_t rem10 = abs_n % 10;
            int32_t rem100 = abs_n % 100;
            if (rem10 == 1 && rem100 != 11) {
                return EMB_PLURAL_ONE;
            }
            if (rem10 >= 2 && rem10 <= 4 && (rem100 < 10 || rem100 >= 20)) {
                return EMB_PLURAL_FEW;
            }
            return EMB_PLURAL_MANY;
        }
        
        case 3: /* Polish (pl): 1 -> one; 2..4,22.. -> few; other -> many */
            if (abs_n == 1) return EMB_PLURAL_ONE;
            {
                int32_t rem10 = abs_n % 10;
                int32_t rem100 = abs_n % 100;
                if (rem10 >= 2 && rem10 <= 4 && (rem100 < 12 || rem100 > 14)) {
                    return EMB_PLURAL_FEW;
                }
                return EMB_PLURAL_MANY;
            }
            
        case 4: /* Arabic (ar): 0->zero, 1->one, 2->two, 3..10->few, 11..99->many, other */
            if (abs_n == 0) return EMB_PLURAL_ZERO;
            if (abs_n == 1) return EMB_PLURAL_ONE;
            if (abs_n == 2) return EMB_PLURAL_TWO;
            {
                int32_t rem100 = abs_n % 100;
                if (rem100 >= 3 && rem100 <= 10) return EMB_PLURAL_FEW;
                if (rem100 >= 11 && rem100 <= 99) return EMB_PLURAL_MANY;
                return EMB_PLURAL_OTHER;
            }
            
        case 5: /* Japanese / Chinese (ja, zh): завжди other */
        default:
            return EMB_PLURAL_OTHER;
    }
}

/* Отримання множинного рядка */
const char *emb_i18n_get_plural_by_hash(const emb_i18n_ctx_t *ctx, uint32_t hash, int32_t count) {
    const emb_msg_desc_t *desc = emb_find_msg(ctx, hash);
    if (!desc) return NULL;
    
    if (desc->type == EMB_MSG_SIMPLE) {
        uint32_t str_off = desc->string_offsets[0];
        return ctx->string_pool + str_off;
    }
    
    emb_plural_category_t cat = emb_i18n_eval_plural(ctx->plural_rule_id, count);
    uint32_t str_off = desc->string_offsets[cat];
    
    /* Якщо для цієї форми зміщення нульове, беремо форму OTHER */
    if (str_off == 0 && cat != EMB_PLURAL_OTHER) {
        str_off = desc->string_offsets[EMB_PLURAL_OTHER];
    }
    
    if (ctx->locale->string_pool_offset + str_off < ctx->image_size) {
        return ctx->string_pool + str_off;
    }
    return NULL;
}

const char *emb_i18n_get_plural(const emb_i18n_ctx_t *ctx, const char *key, int32_t count) {
    if (!key) return "";
    uint32_t hash = emb_i18n_hash(key);
    const char *res = emb_i18n_get_plural_by_hash(ctx, hash, count);
    return res ? res : key;
}

/* Форматування числа i32 у рядок */
static int emb_i32_to_str(char *buf, int max_buf, int32_t val) {
    char temp_digits[16];
    int len = 0;
    int32_t v = val;
    bool neg = v < 0;
    if (neg) v = -v;
    
    do {
        temp_digits[len++] = (char)('0' + (v % 10));
        v /= 10;
    } while (v > 0 && len < 14);
    
    if (neg) temp_digits[len++] = '-';
    
    int out_len = 0;
    for (int i = len - 1; i >= 0 && out_len < max_buf - 1; --i) {
        buf[out_len++] = temp_digits[i];
    }
    buf[out_len] = '\0';
    return out_len;
}

/* Безпечний форматувальник з одним числовим аргументом */
size_t emb_i18n_format_1i(char *dst, size_t max_len, const char *fmt, int32_t arg0) {
    if (!dst || max_len == 0 || !fmt) return 0;
    
    char num_str[16];
    int num_len = emb_i32_to_str(num_str, sizeof(num_str), arg0);
    
    size_t d = 0;
    const char *s = fmt;
    
    while (*s && d < max_len - 1) {
        if (s[0] == '{' && s[1] == '0' && s[2] == '}') {
            s += 3;
            for (int i = 0; i < num_len && d < max_len - 1; ++i) {
                dst[d++] = num_str[i];
            }
        } else {
            dst[d++] = *s++;
        }
    }
    dst[d] = '\0';
    return d;
}

/* Безпечний форматувальник із числом та рядком */
size_t emb_i18n_format_1i_1s(char *dst, size_t max_len, const char *fmt, int32_t arg0, const char *arg1) {
    if (!dst || max_len == 0 || !fmt) return 0;
    
    char num_str[16];
    int num_len = emb_i32_to_str(num_str, sizeof(num_str), arg0);
    const char *str_val = arg1 ? arg1 : "";
    
    size_t d = 0;
    const char *s = fmt;
    
    while (*s && d < max_len - 1) {
        if (s[0] == '{' && s[1] == '0' && s[2] == '}') {
            s += 3;
            for (int i = 0; i < num_len && d < max_len - 1; ++i) {
                dst[d++] = num_str[i];
            }
        } else if (s[0] == '{' && s[1] == '1' && s[2] == '}') {
            s += 3;
            const char *p = str_val;
            while (*p && d < max_len - 1) {
                dst[d++] = *p++;
            }
        } else {
            dst[d++] = *s++;
        }
    }
    dst[d] = '\0';
    return d;
}
