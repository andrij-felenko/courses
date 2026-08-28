#include <stdio.h>

/* ЯВНЕ ЗАХОПЛЕННЯ ТА ЗВІЛЬНЕННЯ ВНУТРІШНЬОГО ЗАМКА ПОТОКУ */
void flockfile(FILE *filehandle);
int  ftrylockfile(FILE *filehandle);
void funlockfile(FILE *filehandle);

/* ШВИДКІ НЕБЛОКУВАЛЬНІ ОПЕРАЦІЇ (Викликаються лише всередині flockfile) */
int getc_unlocked(FILE *stream);
int getchar_unlocked(void);
int putc_unlocked(int c, FILE *stream);
int putchar_unlocked(int c);
