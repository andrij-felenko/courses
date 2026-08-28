/* walk.c — прохід шляхом покомпонентно, зі звітом про кожен крок.
   складання: cc -O2 -o walk walk.c
   вжиток:    ./walk <шлях> [точка-відліку]                        */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>

#define MAX_SUBST 40      /* стільки ж підстановок рахує ядро, далі — ELOOP */

static const char *kind(mode_t m)
{
    if (S_ISDIR(m))  return "каталог";
    if (S_ISLNK(m))  return "посилання";
    if (S_ISREG(m))  return "звичайний файл";
    if (S_ISCHR(m))  return "символьний пристрій";
    if (S_ISBLK(m))  return "блоковий пристрій";
    if (S_ISFIFO(m)) return "іменований канал";
    if (S_ISSOCK(m)) return "сокет";
    return "щось інше";
}

/* Проходить path від start_fd (абсолютний — від root_fd), друкуючи кожен крок.
   Повертає O_PATH-дескриптор кінцевого об'єкта або -1 із виставленим errno.  */
static int walk(int start_fd, int root_fd, const char *path)
{
    char bufs[2][PATH_MAX];        /* пінг-понг: нерозібраний залишок шляху */
    int  cur = 0, dir = -1, substitutions = 0, step = 0;

    if (strlen(path) >= PATH_MAX) { errno = ENAMETOOLONG; return -1; }
    strcpy(bufs[cur], path);
    char *rest = bufs[cur];

    dir = dup(path[0] == '/' ? root_fd : start_fd);
    if (dir < 0) return -1;

    for (;;) {
        while (*rest == '/') rest++;          /* «//» — те саме, що «/» */
        if (*rest == '\0') return dir;        /* складники скінчилися */

        char  *slash = strchr(rest, '/');
        size_t len   = slash ? (size_t)(slash - rest) : strlen(rest);
        char   comp[NAME_MAX + 1];

        if (len > NAME_MAX) { errno = ENAMETOOLONG; goto fail; }
        memcpy(comp, rest, len);
        comp[len] = '\0';
        rest = slash ? slash + 1 : rest + len;      /* нерозібраний хвіст */

        int next = openat(dir, comp, O_PATH | O_NOFOLLOW | O_CLOEXEC);
        if (next < 0) {
            int e = errno;                    /* printf псує errno — рятуємо */
            printf("  ✗ став на складнику «%s»: %s (errno %d)\n",
                   comp, strerror(e), e);
            errno = e;
            goto fail;
        }

        struct stat st;
        if (fstatat(next, "", &st, AT_EMPTY_PATH) < 0) { close(next); goto fail; }

        printf("  %2d. %-20s → %s, dev %u:%u, inode %llu\n",
               ++step, comp, kind(st.st_mode),
               major(st.st_dev), minor(st.st_dev),
               (unsigned long long)st.st_ino);

        if (!S_ISLNK(st.st_mode)) {
            close(dir);
            dir = next;              /* знайдене стає новою точкою відліку */
            continue;
        }

        /* Посилання: залишок відкладаємо, на його місце стає вміст. */
        char    target[PATH_MAX];
        ssize_t n = readlinkat(next, "", target, sizeof target - 1);
        close(next);
        if (n < 0) goto fail;
        if ((size_t)n == sizeof target - 1) {  /* readlink мовчки обрізає */
            errno = ENAMETOOLONG;
            goto fail;
        }
        target[n] = '\0';                      /* і нуля не дописує */
        printf("        вміст «%s»; залишок «%s» відкладено\n", target, rest);

        if (++substitutions > MAX_SUBST) { errno = ELOOP; goto fail; }

        char *nb = bufs[cur ^ 1];
        if (snprintf(nb, PATH_MAX, "%s/%s", target, rest) >= PATH_MAX) {
            errno = ENAMETOOLONG;
            goto fail;
        }
        cur ^= 1;
        rest = nb;

        if (target[0] == '/') {          /* абсолютний вміст — знову від кореня */
            close(dir);
            dir = dup(root_fd);
            if (dir < 0) return -1;
        }
        /* відносний вміст: dir лишається каталогом, де лежить саме посилання */
    }

fail:
    { int e = errno; if (dir >= 0) close(dir); errno = e; }
    return -1;
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "вжиток: %s <шлях> [точка-відліку]\n", argv[0]);
        return 2;
    }
    const char *base = (argc > 2) ? argv[2] : ".";

    int root_fd  = open("/", O_PATH | O_DIRECTORY | O_CLOEXEC);
    int start_fd = open(base, O_PATH | O_DIRECTORY | O_CLOEXEC);
    if (root_fd < 0 || start_fd < 0) { perror("точка відліку"); return 1; }

    printf("шлях «%s», відлік від %s\n", argv[1],
           argv[1][0] == '/' ? "кореня процесу" : base);

    int fd = walk(start_fd, root_fd, argv[1]);
    if (fd < 0) return 1;
    printf("  ✓ дійшли\n");
    close(fd);
    return 0;
}
