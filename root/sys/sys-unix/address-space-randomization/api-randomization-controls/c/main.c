#define _GNU_SOURCE
#include <stdio.h>
#include <sys/personality.h>
#include <unistd.h>

int main(int argc, char *argv[])
{
    if (argc < 2) {
        fprintf(stderr, "usage: %s program [args...]\n", argv[0]);
        return 2;
    }

    /* 1. Прочитати чинну особистість, нічого не змінюючи. */
    int cur = personality(0xffffffff);
    if (cur == -1) {
        perror("personality (read)");
        return 1;
    }

    /* 2. Додати один біт, зберігши все інше — і домен у молодшому байті. */
    if (personality((unsigned long)cur | ADDR_NO_RANDOMIZE) == -1) {
        perror("personality (set)");
        return 1;
    }

    /* 3. Карту будує саме execve — і тепер він будуватиме її без жереба. */
    execvp(argv[1], &argv[1]);
    perror("execvp");
    return 1;
}
