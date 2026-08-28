#define _XOPEN_SOURCE 600
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(void) {
    int m = posix_openpt(O_RDWR | O_NOCTTY);   /* ведучий кінець */
    grantpt(m);
    unlockpt(m);
    int s = open(ptsname(m), O_RDWR);          /* підлеглий кінець */

    write(m, "ab", 2);                          /* наче натиснули дві клавіші */
    usleep(50000);

    char buf[64];
    ssize_t n = read(m, buf, sizeof buf);
    printf("з ведучого прочитано %zd: %.*s\n", n, (int)n, buf);

    close(s);
    close(m);
    return 0;
}
