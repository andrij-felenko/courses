/* value_layout.h — витяг із <gawkapi.h> gawk 5.x: контейнер, яким розширення
 * обмінюється значеннями з інтерпретатором.
 *
 * Це ЦИТАТА чужого контракту, а не наш код: імена, порядок членів і макроси
 * доступу мусять збігатися з оригіналом, інакше модуль не зібрати. Файл
 * самодостатній для читання, але НЕ підключайте його разом із самим
 * <gawkapi.h> — типи зіткнуться.
 */
#ifndef AWK_VALUE_LAYOUT_H
#define AWK_VALUE_LAYOUT_H

#include <stddef.h>

typedef enum awk_bool { awk_false = 0, awk_true } awk_bool_t;

/* Дискримінатор об'єднання. AWK_UNDEFINED у запиті get_argument() означає
   «віддай як є, без приведення»; AWK_STRNUM — рядок із вводу, який виглядає
   числом; AWK_SCALAR і AWK_VALUE_COOKIE — непрозорі дескриптори для
   багаторазового доступу без пошуку в таблиці символів. */
typedef enum {
    AWK_UNDEFINED,
    AWK_NUMBER,
    AWK_STRING,
    AWK_REGEX,
    AWK_STRNUM,
    AWK_ARRAY,
    AWK_SCALAR,
    AWK_VALUE_COOKIE,
    AWK_BOOL
} awk_valtype_t;

/* Рядок AWK — це пара (байти, довжина). Термінального нуля контракт не
   обіцяє, тому strlen() над .str — класична помилка в розширеннях. */
typedef struct awk_string {
    char  *str;
    size_t len;
} awk_string_t;

typedef enum {
    AWK_NUMBER_TYPE_DOUBLE,
    AWK_NUMBER_TYPE_MPFR,   /* режим -M: значення живе за .ptr */
    AWK_NUMBER_TYPE_MPZ
} awk_number_type_t;

typedef struct awk_number {
    double            d;
    awk_number_type_t type;
    void             *ptr;
} awk_number_t;

/* У самому gawkapi.h це непрозорі покажчики: розширення їх лише переносить. */
typedef struct awk_array        *awk_array_t;
typedef struct awk_scalar       *awk_scalar_t;
typedef struct awk_value_cookie *awk_value_cookie_t;

typedef struct awk_value {
    awk_valtype_t val_type;
    union {
        awk_string_t       s;
        awk_number_t       n;
        awk_array_t        a;
        awk_scalar_t       scl;
        awk_value_cookie_t vc;
    } u;
} awk_value_t;

/* Прийнято звертатися саме через ці макроси, а не через .u напряму. */
#define str_value     u.s
#define strnum_value  str_value
#define regex_value   str_value
#define num_value     u.n.d
#define num_type      u.n.type
#define num_ptr       u.n.ptr
#define array_cookie  u.a
#define scalar_cookie u.scl
#define value_cookie  u.vc

/* Власність на пам'ять — єдине, на чому тут падають:
     make_const_string()    — буфер лишається наш, gawk його копіює;
     make_malloced_string() — буфер переходить gawk, і free() зробить ВІН,
                              тому виділяти треба gawk_malloc(), не malloc();
     get_argument()         — рядок належить gawk, змінювати його не можна. */
static inline const char *awk_valtype_name(awk_valtype_t t)
{
    switch (t) {
    case AWK_UNDEFINED:    return "undefined";
    case AWK_NUMBER:       return "number";
    case AWK_STRING:       return "string";
    case AWK_REGEX:        return "regex";
    case AWK_STRNUM:       return "strnum";
    case AWK_ARRAY:        return "array";
    case AWK_SCALAR:       return "scalar";
    case AWK_VALUE_COOKIE: return "value cookie";
    case AWK_BOOL:         return "bool";
    default:               return "?";
    }
}

#endif /* AWK_VALUE_LAYOUT_H */
