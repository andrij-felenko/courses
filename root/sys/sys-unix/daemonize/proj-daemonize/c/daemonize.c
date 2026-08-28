/* daemonize.c — повний обряд.
   cc -std=c11 -D_GNU_SOURCE -Wall -Wextra -c daemonize.c            */

#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>

static int close_inherited_fds(int keep);   /* тіла — нижче, порядок викладу */
static int attach_dev_null(void);
static int reset_signals(void);
static int claim_pidfile(const char *path);

/* Повідомлення пускачеві. Обидва кінці — той самий бінарник,
   тож питання вирівнювання полів тут не виникає.               */
struct ready_msg {
    char tag;         /* 'R' — піднялися, 'E' — не змогли */
    int  err;         /* errno, коли tag == 'E'            */
    char stage[24];   /* назва кроку, що не вдався         */
};

static int ready_fd  = -1;   /* кінець запису; живе до сигналу готовності */
static int pidfile_fd = -1;  /* НЕ закривати: замок тримається дескриптором */

/* Єдине місце, звідки говорять у трубу. Після відповіді кінець
   закривається: пускач має побачити або повідомлення, або кінець файлу. */
static void report(char tag, int err, const char *stage)
{
    if (ready_fd < 0) return;

    struct ready_msg m;
    memset(&m, 0, sizeof m);
    m.tag = tag;
    m.err = err;
    snprintf(m.stage, sizeof m.stage, "%s", stage ? stage : "");

    (void)!write(ready_fd, &m, sizeof m);   /* ≤ PIPE_BUF — запис атомарний */
    close(ready_fd);
    ready_fd = -1;
}

void daemon_ready(void)              { report('R', 0, ""); }
void daemon_fail(const char *stage)  { report('E', errno, stage); }
