/* fast_tools.c — динамічне розширення gawk: два нативні виклики для AWK.
 *
 *   monotonic_time_ns()  — монотонний годинник ОС у наносекундах;
 *   fnv1a_64(str)        — 64-бітний хеш рядка у вигляді "0x................".
 *
 * Збірка:
 *   gcc -fPIC -shared -O3 -Wall -I/usr/include/gawk \
 *       -o fast_tools.so fast_tools.c fnv1a.c
 * Виклик:
 *   gawk '@load "fast_tools"; BEGIN { print fnv1a_64("ключ") }'
 */
#define _POSIX_C_SOURCE 200809L    /* clock_gettime(2), CLOCK_MONOTONIC */

#include <errno.h>
#include <stdio.h>
#include <stddef.h>
#include <time.h>

#include <gawkapi.h>

#include "fnv1a.h"

/* Ці два імені обов'язкові саме такі: усі зручні макроси <gawkapi.h> —
   get_argument(), make_number(), update_ERRNO_*(), add_ext_func() —
   розгортаються у звернення до `api` та `ext_id`. */
static const gawk_api_t *api;
static awk_ext_id_t ext_id;

static const char *ext_version = "fast_tools: 1.0.0";

/* Без цього символу gawk відмовиться завантажувати бібліотеку взагалі. */
int plugin_is_GPL_compatible;

static awk_value_t *do_monotonic_time_ns(int nargs, awk_value_t *result,
                                         struct awk_ext_func *finfo)
{
    struct timespec ts;

    (void) nargs;
    (void) finfo;

    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) {
        /* Помилку віддаємо через ERRNO, а не через fatal(): скрипт має
           право сам вирішити, чи це для нього фатально. */
        update_ERRNO_int(errno);
        return make_number(-1.0, result);
    }

    /* AWK бачить лише double, а це 53 біти мантиси: наносекунди від старту
       машини лишаються точними приблизно 104 доби, далі крок росте. Для
       вимірювання ІНТЕРВАЛІВ цього досить, для абсолютних міток — ні. */
    return make_number((double) ts.tv_sec * 1e9 + (double) ts.tv_nsec, result);
}

static awk_value_t *do_fnv1a_64(int nargs, awk_value_t *result,
                                struct awk_ext_func *finfo)
{
    awk_value_t arg;
    uint64_t hash;
    char *buf;
    int written;

    (void) finfo;

    if (nargs < 1 || !get_argument(0, AWK_STRING, &arg)) {
        update_ERRNO_string("fnv1a_64: очікується один рядковий аргумент");
        return make_null_string(result);
    }

    /* Рядок AWK не обов'язково закінчується нулем — беремо саме .len. */
    hash = fnv1a_64(arg.str_value.str, arg.str_value.len);

    /* Буфер мусить бути виділений САМЕ аллокатором gawk: рядок переходить
       у власність інтерпретатора, і звільнятиме його він, своїм free(). */
    buf = (char *) gawk_malloc(FNV1A_HEX_SIZE);
    if (buf == NULL) {
        update_ERRNO_int(ENOMEM);
        return make_null_string(result);
    }

    written = fnv1a_64_hex(hash, buf, FNV1A_HEX_SIZE);
    if (written < 0) {
        gawk_free(buf);
        update_ERRNO_string("fnv1a_64: не вдалося відформатувати хеш");
        return make_null_string(result);
    }

    return make_malloced_string(buf, (size_t) written, result);
}

/* Порядок полів: ім'я в AWK, реалізація, максимум аргументів, мінімум,
   придушення lint, контекстні дані модуля. */
static awk_ext_func_t func_table[] = {
    { "monotonic_time_ns", do_monotonic_time_ns, 0, 0, awk_false, NULL },
    { "fnv1a_64",          do_fnv1a_64,          1, 1, awk_false, NULL },
};

int dl_load(const gawk_api_t *const api_p, awk_ext_id_t id)
{
    size_t i;
    int errors = 0;

    api = api_p;
    ext_id = id;

    /* Старша версія мусить збігатися точно — від неї залежить розкладка
       структур; молодша має бути не меншою за ту, під яку зібрано модуль,
       інакше потрібних точок входу в таблиці просто немає. */
    if (api->major_version != GAWK_API_MAJOR_VERSION
        || api->minor_version < GAWK_API_MINOR_VERSION) {
        fprintf(stderr,
                "fast_tools: gawk дає API %d.%d, а модуль зібрано під %d.%d\n",
                api->major_version, api->minor_version,
                GAWK_API_MAJOR_VERSION, GAWK_API_MINOR_VERSION);
        return 0;
    }

    for (i = 0; i < sizeof(func_table) / sizeof(func_table[0]); i++) {
        if (!add_ext_func("", &func_table[i])) {
            warning(ext_id, "fast_tools: не зареєстрована функція %s",
                    func_table[i].name);
            errors++;
        }
    }

    register_ext_version(ext_version);
    return (errors == 0);
}
