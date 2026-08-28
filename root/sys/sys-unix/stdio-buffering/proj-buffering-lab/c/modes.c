/* modes.c — куди веде дескриптор 1, такий і режим */
#include <stdio.h>
#include <unistd.h>

int main(void)
{
    fprintf(stderr, "isatty(1) = %d\n", isatty(STDOUT_FILENO));
    for (int i = 1; i <= 400; i++)
        printf("progress %3d of 400\n", i);
    return 0;
}
