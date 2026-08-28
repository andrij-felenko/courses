/* minibox.c — найменший контейнер: збірка з системних викликів.
   Складання: cc -Wall -O2 -o minibox minibox.c
   Запуск:    ./minibox ./rootfs /bin/sh        (без sudo)          */
#define _GNU_SOURCE
#include <sched.h>
#include <sys/mount.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>

static char stack[1 << 20];        /* clone() стека не виділяє — це наш клопіт */

struct box { int wait_fd; const char *root; char **argv; };

static void die(const char *what) { perror(what); _exit(127); }

/* у glibc немає обгортки — кличемо за номером виклику */
static int pivot_root(const char *new_root, const char *put_old)
{
    return syscall(SYS_pivot_root, new_root, put_old);
}

static int enter(void *arg)
{
    struct box *b = arg;
    char ready;

    /* поки батько не написав мапу, ми — 65534 і не маємо ідентичності */
    if (read(b->wait_fd, &ready, 1) != 1) die("канал: мапу не підтверджено");
    close(b->wait_fd);

    if (sethostname("box", 3) == -1) die("sethostname");

    /* 1. свіжа копія дерева монтувань досі обмінюється подіями з системою */
    if (mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) == -1) die("make-rprivate");

    /* 2. pivot_root вимагає, щоб новий корінь був точкою монтування */
    if (mount(b->root, b->root, NULL, MS_BIND | MS_REC, NULL) == -1) die("bind rootfs");
    if (chdir(b->root) == -1) die("chdir rootfs");

    /* 3. власний примірник procfs — покаже номери НАШОГО простору */
    if (mount("proc", "proc", "proc", MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL) == -1)
        die("mount proc");

    /* 4. підміна кореня: put_old навмисно збігається з new_root */
    if (pivot_root(".", ".") == -1) die("pivot_root");
    if (umount2(".", MNT_DETACH) == -1) die("umount старого кореня");
    if (chdir("/") == -1) die("chdir /");

    execv(b->argv[0], b->argv);
    die("execv");
    return 127;
}

static void put(const char *path, const char *data)
{
    int fd = open(path, O_WRONLY);
    if (fd == -1) die(path);
    if (write(fd, data, strlen(data)) != (ssize_t) strlen(data)) die(path);
    close(fd);
}

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "вжиток: %s <rootfs> <програма> [аргументи…]\n", argv[0]);
        return 2;
    }

    int ch[2];
    if (pipe(ch) == -1) die("pipe");

    struct box b = { .wait_fd = ch[0], .root = argv[1], .argv = &argv[2] };

    int flags = CLONE_NEWUSER | CLONE_NEWNS | CLONE_NEWPID |
                CLONE_NEWUTS  | CLONE_NEWIPC | CLONE_NEWNET | SIGCHLD;

    pid_t pid = clone(enter, stack + sizeof stack, flags, &b);
    if (pid == -1) die("clone");
    close(ch[0]);

    char path[64], line[64];

    snprintf(path, sizeof path, "/proc/%d/setgroups", pid);
    put(path, "deny");                      /* файл є від ядра 3.19 */

    snprintf(path, sizeof path, "/proc/%d/uid_map", pid);
    snprintf(line, sizeof line, "0 %u 1", (unsigned) getuid());
    put(path, line);

    snprintf(path, sizeof path, "/proc/%d/gid_map", pid);
    snprintf(line, sizeof line, "0 %u 1", (unsigned) getgid());
    put(path, line);

    if (write(ch[1], "!", 1) != 1) die("канал");
    close(ch[1]);

    int st;
    if (waitpid(pid, &st, 0) == -1) die("waitpid");
    return WIFEXITED(st) ? WEXITSTATUS(st) : 128 + WTERMSIG(st);
}
