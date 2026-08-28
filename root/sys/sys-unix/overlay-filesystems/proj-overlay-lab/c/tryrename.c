/* tryrename.c — що саме повертає rename(), а не що з цього робить mv */
#include <errno.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv)
{
    if (argc != 3) { fprintf(stderr, "вжиток: tryrename <з> <на>\n"); return 2; }

    if (rename(argv[1], argv[2]) == 0) { puts("rename() успішний"); return 0; }

    printf("rename() відмовив: %s (errno=%d)\n", strerror(errno), errno);
    return 1;
}
