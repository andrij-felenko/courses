#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdio.h>

#define LISTEN_FDS_START 3

/* Звичайний код служби, до протоколу передавання не причетний. */
int  open_and_listen(int port);
void serve_forever(int fd);

/* Повертає кількість переданих сокетів; 0 — нам нічого не передавали. */
static int inherited_sockets(void)
{
    const char *pid = getenv("LISTEN_PID");
    const char *cnt = getenv("LISTEN_FDS");
    char self[32];

    if (!pid || !cnt)
        return 0;

    snprintf(self, sizeof self, "%ld", (long) getpid());
    if (strcmp(pid, self) != 0)   /* змінна дісталася нам у спадок від предка */
        return 0;

    return atoi(cnt);
}

int main(void)
{
    int n = inherited_sockets();
    int fd;

    if (n == 1) {
        fd = LISTEN_FDS_START;          /* сокет уже прив'язаний і слухає */
    } else {
        fd = open_and_listen(8080);     /* запустили руками — робимо сокет самі */
    }

    serve_forever(fd);
}
