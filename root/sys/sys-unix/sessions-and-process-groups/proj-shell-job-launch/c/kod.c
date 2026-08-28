#define _GNU_SOURCE
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <termios.h>
#include <unistd.h>

#define MAXP 8

struct job {
    pid_t pgid;                 /* ім'я групи = номер першої ланки */
    int   n;
    pid_t pid[MAXP];
    char  st[MAXP];             /* 'r' — живий · 's' — зупинений · 'x' — помер */
    struct termios tmodes;      /* режим термінала, знятий у мить зупинення */
    char  cmd[128];
};

static int   tty;               /* дескриптор керівного термінала */
static pid_t shell_pgid;
static struct termios shell_tmodes;
