/* array_layout.h — асоціативний масив AWK: хеш-таблиця з ланцюжками колізій,
 * рехешуванням за коефіцієнтом завантаження і двома формами delete.
 *
 * Модель узагальнена: gawk має кілька реалізацій масиву одразу (рядкову,
 * цілочисельну й розріджену цілочисельну) і перемикає їх на льоту, mawk та
 * nawk обходяться однією рядковою. Спільне в них рівно те, що нижче.
 */
#ifndef AWK_ARRAY_LAYOUT_H
#define AWK_ARRAY_LAYOUT_H

#include <stdlib.h>
#include <string.h>

#include "node_layout.h"

#define AWK_ARRAY_MIN_BUCKETS 16      /* степінь двійки: індекс маскою, не % */
#define AWK_ARRAY_MAX_LOAD    1.5     /* поріг рехешування */
#define AWK_SUBSEP_DEFAULT    "\034"  /* ASCII 0x1C: у друкованому тексті не буває */

typedef struct awk_bucket {
    struct awk_bucket *next;   /* ланцюжок колізій — однозв'язний список */
    unsigned long      code;   /* кеш хешу: рехеш обходиться без перерахунку */
    char              *name;   /* ключ завжди рядок, навіть коли він "42" */
    size_t             namelen;
    awk_node           value;
} awk_bucket;

typedef struct awk_array {
    awk_bucket **buckets;
    size_t       size;    /* кількість відер, завжди степінь двійки */
    size_t       count;   /* кількість елементів */
} awk_array;

/* Хеш Пітера Вайнбергера (PJW/ElfHash) — той самий сімейний алгоритм, що й
   у gawk за замовчуванням. Дешевий: зсув, додавання, одна перевірка. */
static inline unsigned long awk_hash_pjw(const char *s, size_t len)
{
    unsigned long h = 0, g;
    size_t i;

    for (i = 0; i < len; i++) {
        h = (h << 4) + (unsigned char) s[i];
        g = h & 0xf0000000UL;
        if (g != 0) {
            h ^= g >> 24;
            h ^= g;
        }
    }
    return h;
}

static inline int awk_array_init(awk_array *a)
{
    a->buckets = (awk_bucket **) calloc(AWK_ARRAY_MIN_BUCKETS, sizeof *a->buckets);
    if (a->buckets == NULL)
        return 0;
    a->size = AWK_ARRAY_MIN_BUCKETS;
    a->count = 0;
    return 1;
}

/* Рехешування: новий масив удвічі більший, вузли ПЕРЕЛІНКОВУЮТЬСЯ. Ні ключі,
   ні структури не копіюються — рухаються лише покажчики, тому вставка
   лишається амортизовано O(1). */
static inline int awk_array_rehash(awk_array *a)
{
    size_t new_size = a->size * 2;
    awk_bucket **fresh = (awk_bucket **) calloc(new_size, sizeof *fresh);
    size_t i;

    if (fresh == NULL)
        return 0;

    for (i = 0; i < a->size; i++) {
        awk_bucket *b = a->buckets[i];
        while (b != NULL) {
            awk_bucket *next = b->next;
            size_t idx = (size_t) (b->code & (new_size - 1));
            b->next = fresh[idx];
            fresh[idx] = b;
            b = next;
        }
    }
    free(a->buckets);           /* старий масив покажчиків — і тільки він */
    a->buckets = fresh;
    a->size = new_size;
    return 1;
}

static inline awk_bucket *awk_array_find(const awk_array *a, const char *key,
                                         size_t len, size_t *idx_out)
{
    unsigned long code = awk_hash_pjw(key, len);
    size_t idx = (size_t) (code & (a->size - 1));
    awk_bucket *b;

    if (idx_out != NULL)
        *idx_out = idx;
    for (b = a->buckets[idx]; b != NULL; b = b->next)
        /* Спершу довжина, потім memcmp: ключ може містити нульові байти. */
        if (b->namelen == len && memcmp(b->name, key, len) == 0)
            return b;
    return NULL;
}

static inline int awk_array_exists(const awk_array *a, const char *key, size_t len)
{
    return awk_array_find(a, key, len, NULL) != NULL;   /* оператор in */
}

/* Читання неіснуючого елемента в AWK його СТВОРЮЄ — ось те саме в коді.
   Саме тому перевіряти наявність треба через in, а не через порівняння. */
static inline awk_node *awk_array_lookup(awk_array *a, const char *key, size_t len)
{
    size_t idx;
    awk_bucket *b = awk_array_find(a, key, len, &idx);

    if (b != NULL)
        return &b->value;

    if ((double) (a->count + 1) / (double) a->size > AWK_ARRAY_MAX_LOAD) {
        if (!awk_array_rehash(a))
            return NULL;
        awk_array_find(a, key, len, &idx);      /* індекс після рехешу інший */
    }

    b = (awk_bucket *) malloc(sizeof *b);
    if (b == NULL)
        return NULL;
    b->name = (char *) malloc(len + 1);
    if (b->name == NULL) {
        free(b);
        return NULL;
    }
    memcpy(b->name, key, len);
    b->name[len] = '\0';
    b->namelen = len;
    b->code = awk_hash_pjw(key, len);
    memset(&b->value, 0, sizeof b->value);      /* порожнє значення: "" і 0 */
    b->next = a->buckets[idx];
    a->buckets[idx] = b;
    a->count++;
    return &b->value;
}

/* delete arr[k]: вузол вилучається з ланцюжка, пам'ять ключа й значення
   звільняється, масив відер лишається того ж розміру. */
static inline int awk_array_delete(awk_array *a, const char *key, size_t len)
{
    unsigned long code = awk_hash_pjw(key, len);
    size_t idx = (size_t) (code & (a->size - 1));
    awk_bucket *b = a->buckets[idx], *prev = NULL;

    while (b != NULL) {
        if (b->namelen == len && memcmp(b->name, key, len) == 0) {
            if (prev == NULL)
                a->buckets[idx] = b->next;
            else
                prev->next = b->next;
            awk_node_free(&b->value);
            free(b->name);
            free(b);
            a->count--;
            return 1;
        }
        prev = b;
        b = b->next;
    }
    return 0;
}

/* delete arr: один прохід пам'яттю замість N пошуків, і таблиця стискається
   назад до мінімуму — саме через це циклічна обробка пакетів не тече. */
static inline void awk_array_clear(awk_array *a)
{
    size_t i;

    for (i = 0; i < a->size; i++) {
        awk_bucket *b = a->buckets[i];
        while (b != NULL) {
            awk_bucket *next = b->next;
            awk_node_free(&b->value);
            free(b->name);
            free(b);
            b = next;
        }
        a->buckets[i] = NULL;
    }
    a->count = 0;
    if (a->size > AWK_ARRAY_MIN_BUCKETS) {
        awk_bucket **shrunk = (awk_bucket **) calloc(AWK_ARRAY_MIN_BUCKETS,
                                                     sizeof *shrunk);
        if (shrunk != NULL) {
            free(a->buckets);
            a->buckets = shrunk;
            a->size = AWK_ARRAY_MIN_BUCKETS;
        }
    }
}

static inline void awk_array_destroy(awk_array *a)
{
    awk_array_clear(a);
    free(a->buckets);
    a->buckets = NULL;
    a->size = 0;
}

/* arr[i, j] — не двовимірність, а склейка через SUBSEP в один рядковий ключ. */
static inline size_t awk_subsep_key(char *dst, size_t size,
                                    const char *first, const char *second)
{
    int len = snprintf(dst, size, "%s%s%s", first, AWK_SUBSEP_DEFAULT, second);
    return (len < 0 || (size_t) len >= size) ? 0 : (size_t) len;
}

#endif /* AWK_ARRAY_LAYOUT_H */
