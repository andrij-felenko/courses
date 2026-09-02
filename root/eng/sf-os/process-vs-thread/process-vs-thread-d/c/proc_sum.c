#define _GNU_SOURCE
#include "proc_sum.h"

#include "chunks.h"

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/wait.h>
#include <unistd.h>

#define MAX_WORKERS 64

/* Та сама глобальна змінна, що й у потоковому варіанті, але тут її чіпають
   діти. Батько своєї копії не побачить зміненою — сторінка роздвоїться. */
static long long g_visits = 0;

/* write(2) має право записати МЕНШЕ, ніж просили, і обірватися на сигналі. */
static int write_all(int fd, const void *buf, size_t len)
{
    const char *p = (const char *)buf;
    while (len > 0) {
        ssize_t k = write(fd, p, len);
        if (k < 0) {
            if (errno == EINTR)
                continue;
            return -1;
        }
        p += k;
        len -= (size_t)k;
    }
    return 0;
}

static int read_all(int fd, void *buf, size_t len)
{
    char *p = (char *)buf;
    while (len > 0) {
        ssize_t k = read(fd, p, len);
        if (k < 0) {
            if (errno == EINTR)
                continue;
            return -1;
        }
        if (k == 0) {           /* кінець файлу раніше часу: дитина вмерла */
            errno = EPIPE;
            return -1;
        }
        p += k;
        len -= (size_t)k;
    }
    return 0;
}

int proc_sum(const int *data, size_t n, size_t workers, long long *out)
{
    if (workers == 0 || workers > MAX_WORKERS)
        return EINVAL;

    chunk_t ranges[MAX_WORKERS];
    int result_fd[MAX_WORKERS];
    pid_t kids[MAX_WORKERS];

    chunk_split(n, workers, ranges);
    g_visits = 0;

    size_t started = 0;
    int err = 0;

    for (size_t i = 0; i < workers; ++i) {
        int fds[2];
        /* O_CLOEXEC ставиться ТИМ САМИМ викликом, атомарно. Якби ми відкрили
           канал і лише потім дописали прапорець через fcntl(), сусідній потік
           устиг би між цими двома викликами зробити fork+execve — і чужа
           програма успадкувала б наш дескриптор. */
        if (pipe2(fds, O_CLOEXEC) < 0) {
            err = errno;
            break;
        }

        pid_t pid = fork();
        if (pid < 0) {
            err = errno;
            close(fds[0]);
            close(fds[1]);
            break;
        }

        if (pid == 0) {
            /* ДИТИНА. Масив дістався їй копією-при-записі: адреси ті самі,
               фізичні сторінки спільні, поки ніхто не пише. Ми лише читаємо,
               тож жодного копіювання 32 МіБ насправді не відбувається. */
            close(fds[0]);
            long long part = sum_range(data, ranges[i]);
            g_visits += 1;   /* запис у .bss — ось ТУТ сторінка роздвоюється */

            /* Після fork у програмі з потоками дозволені лише
               async-signal-safe виклики: write() і _exit(), без printf і
               malloc, бо їхні м'ютекси могли лишитися захопленими навіки. */
            int failed = write_all(fds[1], &part, sizeof part);
            close(fds[1]);
            _exit(failed ? 1 : 0);
        }

        close(fds[1]);          /* батько тримає лише кінець на читання:
                                   інакше read() ніколи не дочекався б EOF */
        result_fd[i] = fds[0];
        kids[i] = pid;
        ++started;
    }

    long long total = 0;
    for (size_t i = 0; i < started; ++i) {
        long long part = 0;
        if (read_all(result_fd[i], &part, sizeof part) < 0) {
            if (err == 0)
                err = errno;
        } else {
            total += part;
            printf("  дитина PID=%d: [%zu..%zu) -> %lld\n",
                   (int)kids[i], ranges[i].start, ranges[i].end, part);
        }
        close(result_fd[i]);
    }

    /* Дитину, яку не поховали через waitpid(), ядро тримає зомбі. */
    for (size_t i = 0; i < started; ++i) {
        int status = 0;
        while (waitpid(kids[i], &status, 0) < 0) {
            if (errno != EINTR)
                break;
        }
        if (!(WIFEXITED(status) && WEXITSTATUS(status) == 0) && err == 0)
            err = ECHILD;
    }

    printf("  g_visits у батька = %lld: записи дітей пішли в їхні власні\n"
           "  копії сторінок і назад не повернулися\n", g_visits);

    if (err != 0)
        return err;

    *out = total;
    return 0;
}
