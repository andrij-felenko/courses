/* node_layout.h — комірка значення AWK: як інтерпретатор тримає рядок і
 * число в ОДНІЙ структурі й коли він їх синхронізує.
 *
 * Це зменшена, але робоча модель того, що в gawk зветься NODE, а в nawk та
 * mawk — Cell. Імена прапорців і їхній сенс узяті з awk.h gawk 5.x; конкретні
 * числові значення бітів між версіями рухаються, тому тут вони задані
 * порядком. Реальний NODE додає ще широкий рядок (wchar_t), лічильник
 * посилань і поля MPFR/GMP — на семантику двоїстого стану вони не впливають.
 */
#ifndef AWK_NODE_LAYOUT_H
#define AWK_NODE_LAYOUT_H

#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Уся арифметика AWK — це IEEE 754 double: 53 біти мантиси, і крапка. */
typedef double AWKNUM;

enum awk_node_flags {
    AWK_MALLOC     = 1u << 0,  /* буфер sp у купі — звільняти при мутації */
    AWK_STRING     = 1u << 1,  /* значення ПРИСВОЄНО як рядок */
    AWK_STRCUR     = 1u << 2,  /* рядкова форма актуальна */
    AWK_NUMCUR     = 1u << 3,  /* числова форма актуальна (кеш strtod) */
    AWK_NUMBER     = 1u << 4,  /* значення ПРИСВОЄНО як число */
    AWK_USER_INPUT = 1u << 5   /* прийшло з вводу: кандидат у strnum */
};

typedef struct awk_node {
    unsigned int flags;
    AWKNUM       numbr;   /* чинне лише за AWK_NUMCUR */
    char        *sp;      /* текст; НЕ зобов'язаний закінчуватися нулем */
    size_t       slen;
} awk_node;

#define AWK_NUM_SCRATCH 64    /* довше за будь-яке представлення double */

/* Копія рядка з термінальним нулем: sp у AWK його не має, а strtod() без
   нього не обійдеться. Довгі значення числом бути не можуть за означенням. */
static inline int awk_node_cstr(const awk_node *n, char *buf, size_t size)
{
    if (n->sp == NULL || n->slen >= size)
        return 0;
    memcpy(buf, n->sp, n->slen);
    buf[n->slen] = '\0';
    return 1;
}

/* Синтаксис числа за POSIX: провідні й кінцеві пробіли дозволені, а от
   "100MB", "0x1F" та "inf" числовим РЯДКОМ не є — це вже просто рядки. */
static inline int awk_node_looks_numeric(const awk_node *n)
{
    char buf[AWK_NUM_SCRATCH];
    char *end;
    size_t i;

    if (!awk_node_cstr(n, buf, sizeof buf))
        return 0;
    for (i = 0; buf[i] != '\0'; i++)
        if (isalpha((unsigned char) buf[i]) && buf[i] != 'e' && buf[i] != 'E')
            return 0;             /* відсікає inf, nan і "12MB" */

    i = 0;
    while (isspace((unsigned char) buf[i]))
        i++;
    if (buf[i] == '\0')
        return 0;

    strtod(buf + i, &end);
    if (end == buf + i)
        return 0;
    while (isspace((unsigned char) *end))
        end++;
    return *end == '\0';          /* хвіст з'їдено весь — це число */
}

/* strnum: значення прийшло з вводу І виглядає числом. Саме ця пара робить
   порівняння $1 == $2 числовим, а порівняння "010" == "10" — рядковим. */
static inline int awk_node_is_strnum(const awk_node *n)
{
    return (n->flags & AWK_USER_INPUT) != 0 && awk_node_looks_numeric(n);
}

/* Крок 1: поле щойно зчитане з потоку. strtod() НЕ викликається. */
static inline void awk_node_from_input(awk_node *n, char *text, size_t len)
{
    n->flags = AWK_STRCUR | AWK_USER_INPUT;
    n->sp = text;
    n->slen = len;
    n->numbr = 0.0;
}

static inline void awk_node_from_number(awk_node *n, AWKNUM v)
{
    n->flags = AWK_NUMBER | AWK_NUMCUR;
    n->numbr = v;
    n->sp = NULL;
    n->slen = 0;
}

static inline void awk_node_free(awk_node *n)
{
    if ((n->flags & AWK_MALLOC) != 0)
        free(n->sp);
    n->sp = NULL;
    n->slen = 0;
    n->flags = 0;
}

/* Крок 2 і 3: перше звертання в арифметиці платить за strtod(), решта
   беруть готове з numbr. Префіксна семантика: "100MB" -> 100, "err" -> 0. */
static inline AWKNUM awk_node_force_number(awk_node *n)
{
    char buf[AWK_NUM_SCRATCH];

    if ((n->flags & AWK_NUMCUR) != 0)
        return n->numbr;

    n->numbr = awk_node_cstr(n, buf, sizeof buf) ? strtod(buf, NULL) : 0.0;
    n->flags |= AWK_NUMCUR;
    return n->numbr;
}

/* Число -> рядок за CONVFMT. Цілі значення POSIX вимагає друкувати як цілі
   незалежно від CONVFMT: інакше arr[1000000] став би ключем "1e+06". */
static inline const char *awk_node_force_string(awk_node *n, const char *convfmt)
{
    char buf[AWK_NUM_SCRATCH];
    int len;

    if ((n->flags & AWK_STRCUR) != 0)
        return n->sp;

    if (n->numbr == floor(n->numbr) && fabs(n->numbr) < 1e16)
        len = snprintf(buf, sizeof buf, "%.0f", n->numbr);
    else
        len = snprintf(buf, sizeof buf, convfmt, n->numbr);
    if (len < 0)
        len = 0;

    n->sp = (char *) malloc((size_t) len + 1);
    if (n->sp == NULL)
        return "";
    memcpy(n->sp, buf, (size_t) len + 1);
    n->slen = (size_t) len;
    n->flags |= AWK_STRCUR | AWK_MALLOC;
    return n->sp;
}

/* Крок 4: рядкова мутація. Кеш числа й ознака «прийшло з вводу» гинуть —
   після $1 = $1 "_x" поле більше не strnum і порівнюється як рядок. */
static inline void awk_node_assign_string(awk_node *n, char *text, size_t len)
{
    awk_node_free(n);
    n->flags = AWK_STRING | AWK_STRCUR | AWK_MALLOC;
    n->sp = text;
    n->slen = len;
    n->numbr = 0.0;
}

/* Матриця POSIX одним рядком: числове порівняння тоді й лише тоді, коли
   ЖОДЕН операнд не є справжнім рядком. Число проти рядка — рядкове. */
static inline int awk_node_compare_is_numeric(const awk_node *a, const awk_node *b)
{
    int a_num = (a->flags & AWK_NUMBER) != 0 || awk_node_is_strnum(a)
                || (a->flags & (AWK_STRING | AWK_STRCUR)) == 0;
    int b_num = (b->flags & AWK_NUMBER) != 0 || awk_node_is_strnum(b)
                || (b->flags & (AWK_STRING | AWK_STRCUR)) == 0;
    return a_num && b_num;
}

static inline int awk_node_compare(awk_node *a, awk_node *b, const char *convfmt)
{
    if (awk_node_compare_is_numeric(a, b)) {
        AWKNUM x = awk_node_force_number(a);
        AWKNUM y = awk_node_force_number(b);
        return (x < y) ? -1 : (x > y) ? 1 : 0;
    }
    return strcmp(awk_node_force_string(a, convfmt),
                  awk_node_force_string(b, convfmt));
}

#endif /* AWK_NODE_LAYOUT_H */
