#include <stdio.h>

struct rec {
    char  kind;   /* 'I' — інформація, 'W' — попередження, 'E' — помилка */
    int   id;     /* наскрізний номер події */
    long  ts;     /* unix-час */
    short len;    /* довжина тексту, що йде далі у файлі */
};

void write_rec(FILE *f, const struct rec *r) {
    fwrite(r, sizeof *r, 1, f);          /* «просто скидаємо структуру» */
}
