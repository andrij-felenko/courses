/* clone-flags.c — один виклик, різні набори бітів.
 *   gcc -O2 -Wall -o clone-flags clone-flags.c
 *   ./clone-flags                             нічого не вмикаємо: це fork()
 *   ./clone-flags vm files fs sighand thread  це pthread_create()
 * Запускати НЕ з кореня: зонд каталогу порівнює поточний каталог із "/".
 */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/futex.h>
#include <sched.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>

#define STACK_SIZE (256 * 1024)

static volatile int probe_var;   /* зонд пам'яті: значення міняє інша задача */
static int probe_fd;             /* зонд дескрипторів: відкриває батько      */
static int report[2];            /* канал: ним дитина звітує в усіх випадках */
static int join_word;            /* futex-слово: ядро занулить його на смерті */
static int flags;

struct note { pid_t pid, tid; };

static void on_usr1(int s) { (void)s; }
static pid_t sys_gettid(void) { return (pid_t)syscall(SYS_gettid); }

/* Тіло дитини. Свідомо тримаємося найтонших обгорток libc: у цієї задачі
   немає власної пам'яті потоку, тож усе складніше за них тут ламається. */
static int child(void *arg)
{
    struct sigaction sa;
    struct note n;
    (void)arg;

    probe_var = 42;                        /* 1. пам'ять                  */
    close(probe_fd);                       /* 2. таблиця дескрипторів     */
    if (chdir("/") != 0) return 71;        /* 3. корінь і каталог         */

    memset(&sa, 0, sizeof sa);             /* 4. диспозиції сигналів      */
    sa.sa_handler = on_usr1;
    sigaction(SIGUSR1, &sa, NULL);

    if (flags & CLONE_NEWNS) {             /* окремий дослід: монтування  */
        mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL);
        mount("none", "/mnt", "tmpfs", 0, NULL);
        close(open("/mnt/marker", O_CREAT | O_WRONLY, 0600));
    }

    n.pid = getpid();                      /* 5. ідентичність             */
    n.tid = sys_gettid();
    write(report[1], &n, sizeof n);

    return 0;      /* обгортка glibc зробить SYS_exit — саме задачі, не групи */
}

/* Так само, і майже тим самим кодом, чекає pthread_join. */
static void join_task(void)
{
    int v;
    while ((v = __atomic_load_n(&join_word, __ATOMIC_ACQUIRE)) != 0)
        syscall(SYS_futex, &join_word, FUTEX_WAIT, v, NULL, NULL, 0);
}

static void line(const char *what, const char *seen, int shared)
{
    printf("%-14s %-38s %s\n", what, seen, shared ? "СПІЛЬНЕ" : "своє");
}

int main(int argc, char **argv)
{
    static const struct { const char *name; int bit; } TABLE[] = {
        { "vm",      CLONE_VM      }, { "files",  CLONE_FILES  },
        { "fs",      CLONE_FS      }, { "sighand", CLONE_SIGHAND },
        { "thread",  CLONE_THREAD  }, { "newns",  CLONE_NEWNS  },
        { "newpid",  CLONE_NEWPID  },
    };
    char cwd0[4096], cwd1[4096], b[192], *stack;
    struct sigaction seen;
    struct note n = { 0, 0 };
    int fd_alive, disp_moved;
    pid_t tid;

    for (int i = 1; i < argc; i++)
        for (unsigned j = 0; j < sizeof TABLE / sizeof *TABLE; j++)
            if (strcmp(argv[i], TABLE[j].name) == 0) flags |= TABLE[j].bit;

    getcwd(cwd0, sizeof cwd0);
    probe_fd = open("/dev/null", O_RDONLY);
    pipe(report);
    stack = malloc(STACK_SIZE);

    /* Молодший байт прапорців — сигнал смерті. У групі задач його не буває. */
    if (!(flags & CLONE_THREAD))
        tid = clone(child, stack + STACK_SIZE, flags | SIGCHLD, NULL);
    else
        tid = clone(child, stack + STACK_SIZE,
                    flags | CLONE_PARENT_SETTID | CLONE_CHILD_CLEARTID,
                    NULL, &join_word, NULL, &join_word);

    if (tid == -1) { perror("clone"); return 1; }

    if (flags & CLONE_THREAD) join_task();
    else                      waitpid(tid, NULL, 0);

    read(report[0], &n, sizeof n);
    getcwd(cwd1, sizeof cwd1);
    sigaction(SIGUSR1, NULL, &seen);
    fd_alive   = (fcntl(probe_fd, F_GETFD) != -1);
    disp_moved = (seen.sa_handler == on_usr1);

    snprintf(b, sizeof b, "глобальна змінна = %d", probe_var);
    line("пам'ять", b, probe_var == 42);

    snprintf(b, sizeof b, "fd %d %s", probe_fd,
             fd_alive ? "живий" : "закритий дитиною");
    line("дескриптори", b, !fd_alive);

    snprintf(b, sizeof b, "%s → %s", cwd0, cwd1);
    line("каталог", b, strcmp(cwd0, cwd1) != 0);

    snprintf(b, sizeof b, "SIGUSR1: %s",
             disp_moved ? "обробник дитини" : "типова дія");
    line("диспозиції", b, disp_moved);

    snprintf(b, sizeof b, "батько %d/%d, дитина %d/%d (clone дав %d)",
             getpid(), sys_gettid(), n.pid, n.tid, tid);
    line("ідентичність", b, n.pid == getpid());

    if (flags & CLONE_NEWNS)
        printf("%-14s %s\n", "монтування",
               access("/mnt/marker", F_OK) == 0
                   ? "tmpfs дитини ВИДНО з батька — монтування розповсюдилося"
                   : "tmpfs дитини не видно з батька — простір окремий");

    free(stack);
    return 0;
}
