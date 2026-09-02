#include "terminfo_caps.h"

#include <curses.h>
#include <term.h>

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

static int g_out_fd = 1;
static int g_ready;

/* tputs хоче функцію на один байт — вона й пише в потрібний дескриптор. */
static int put_byte(int c)
{
    unsigned char b = (unsigned char)c;

    for (;;) {
        ssize_t n = write(g_out_fd, &b, 1);
        if (n == 1)
            return c;
        if (n < 0 && errno == EINTR)
            continue;
        return EOF;
    }
}

static int ensure_setup(int fd)
{
    int err = 0;

    if (g_ready)
        return 0;
    if (setupterm(NULL, fd, &err) != OK) {
        /* err: 1 — термінал знайдено, але він «дурний»; 0 — назви немає
           в базі; -1 — самої бази terminfo в системі немає. */
        const char *term = getenv("TERM");
        fprintf(stderr, "setupterm: код %d (TERM=%s)\n", err, term ? term : "");
        return -1;
    }
    g_ready = 1;
    return 0;
}

/* Друкує послідовність читабельно: ESC → \E, решта керівних → ^X. */
static void print_seq(const char *cap, const char *value)
{
    printf("  %-8s ", cap);
    if (value == NULL || value == (const char *)-1) {
        puts("(нема)");
        return;
    }
    for (const unsigned char *p = (const unsigned char *)value; *p != '\0'; ++p) {
        if (*p == 033)
            fputs("\\E", stdout);
        else if (*p < 32)
            printf("^%c", (char)(*p + 64));
        else
            putchar(*p);
    }
    putchar('\n');
}

int terminfo_dump(int fd)
{
    const char *term = getenv("TERM");

    if (ensure_setup(fd) < 0)
        return -1;

    printf("TERM = %s\n", term ? term : "(не задано)");
    printf("  %-8s %s\n", "am", tigetflag("am") == 1 ? "так" : "ні");
    printf("  %-8s %s\n", "bce", tigetflag("bce") == 1 ? "так" : "ні");
    printf("  %-8s %d\n", "colors", tigetnum("colors"));
    printf("  %-8s %d x %d\n", "розмір", tigetnum("cols"), tigetnum("lines"));

    print_seq("smcup", tigetstr("smcup"));   /* вхід в альтернативний екран */
    print_seq("rmcup", tigetstr("rmcup"));   /* вихід із нього              */
    print_seq("civis", tigetstr("civis"));   /* сховати курсор              */
    print_seq("cnorm", tigetstr("cnorm"));   /* показати курсор             */
    print_seq("sgr0",  tigetstr("sgr0"));    /* скинути атрибути            */
    print_seq("cup",   tigetstr("cup"));     /* шаблон переміщення курсора  */

    return 0;
}

int terminfo_move_cursor(int fd, int row, int col)
{
    char *cup;
    char *seq;

    if (ensure_setup(fd) < 0)
        return -1;

    cup = tigetstr("cup");
    if (cup == NULL || cup == (char *)-1)
        return -1;

    /* tparm розгортає шаблон \033[%i%p1%d;%p2%dH: %i додає одиницю до
       перших двох параметрів — з 0-індексованих координат C виходять
       1-індексовані координати ANSI. */
    seq = tparm(cup, row, col);
    if (seq == NULL)
        return -1;

    g_out_fd = fd;
    /* tputs сам домалює символи-заповнювачі, якщо в можливості записано
       затримку виду $<50>: він знає вихідну швидкість лінії. */
    return tputs(seq, 1, put_byte) == OK ? 0 : -1;
}
