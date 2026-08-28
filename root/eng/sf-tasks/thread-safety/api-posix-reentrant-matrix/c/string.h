#include <string.h>

/* ЗАСТАРІЛА ФУНКЦІЯ (Повертає статичний рядок) */
char *strerror(int errnum);

/* ВАРІАНТ 1: POSIX.1-2001 (XSI-Compliant) */
int strerror_r(int errnum, char *buf, size_t buflen);

/* ВАРІАНТ 2: GNU-Specific (glibc за наявності _GNU_SOURCE) */
char *strerror_r(int errnum, char *buf, size_t buflen);
