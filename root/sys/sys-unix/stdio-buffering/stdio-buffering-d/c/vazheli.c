#include <stdio.h>
#include <unistd.h>

int main(void)
{
    /* Хочемо бачити поступ навіть у конвеєрі — до будь-якого друку. */
    if (!isatty(STDOUT_FILENO))
        setvbuf(stdout, NULL, _IOLBF, BUFSIZ);
    /* далі звичайна робота з printf */
}
