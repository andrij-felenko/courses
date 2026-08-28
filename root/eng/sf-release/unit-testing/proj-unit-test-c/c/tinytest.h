/* tinytest.h — увесь каркас: одна структура, три макроси, один прогін */
#ifndef TINYTEST_H
#define TINYTEST_H

#include <setjmp.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

typedef void (*tt_fn)(void);

typedef struct {
    const char *promise;       /* обіцянка людською мовою — вона піде у звіт */
    tt_fn       body;
} tt_case;

extern jmp_buf     tt_abort;
extern const char *tt_file;
extern int         tt_line;
extern char        tt_msg[192];

_Noreturn void tt_fail(const char *file, int line);

#define CHECK(cond)                                                        \
    do {                                                                   \
        if (!(cond)) {                                                     \
            snprintf(tt_msg, sizeof tt_msg, "CHECK(%s)", #cond);           \
            tt_fail(__FILE__, __LINE__);                                   \
        }                                                                  \
    } while (0)

#define CHECK_EQ_INT(actual, expected)                                     \
    do {                                                                   \
        long tt_a = (long)(actual), tt_e = (long)(expected);               \
        if (tt_a != tt_e) {                                                \
            snprintf(tt_msg, sizeof tt_msg,                                \
                     "%s: маємо %ld, чекали %ld  (%s)",                    \
                     #actual, tt_a, tt_e, #expected);                      \
            tt_fail(__FILE__, __LINE__);                                   \
        }                                                                  \
    } while (0)

int tt_run(const tt_case *cases, size_t n, uint32_t seed);

#endif
