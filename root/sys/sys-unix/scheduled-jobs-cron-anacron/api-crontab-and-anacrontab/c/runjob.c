/* _GNU_SOURCE — для initgroups(), pipe2() і dprintf() у glibc. */
#define _GNU_SOURCE

#include "runjob.h"

#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <poll.h>
#include <pwd.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#define OUTPUT_CHUNK 4096

typedef struct {
    char *data;
    size_t len;
    size_t cap;
} buffer_t;

static bool buffer_append(buffer_t *b, const char *src, size_t n)
{
    if (b->len + n + 1 > b->cap) {
        size_t cap = (b->cap == 0) ? OUTPUT_CHUNK : b->cap;
        while (cap < b->len + n + 1) {
            cap *= 2;
        }
        char *grown = realloc(b->data, cap);
        if (grown == NULL) {
            return false;
        }
        b->data = grown;
        b->cap = cap;
    }
    memcpy(b->data + b->len, src, n);
    b->len += n;
    b->data[b->len] = '\0';
    return true;
}

static const char *job_shell(const cron_job_t *job)
{
    return (job->shell != NULL && job->shell[0] != '\0') ? job->shell : "/bin/sh";
}

static void exec_shell(const cron_job_t *job)
{
    const char *shell = job_shell(job);
    const char *slash = strrchr(shell, '/');
    const char *argv0 = (slash != NULL) ? slash + 1 : shell;
    /* execle, а не execl: середовище завдання ми зібрали самі й не хочемо
       нічого успадкувати від демона. */
    execle(shell, argv0, "-c", job->command, (char *)NULL, job->envp);
}

static int drop_privileges(const struct passwd *pw)
{
    /* 1. Додаткові групи користувача з бази NSS. */
    if (initgroups(pw->pw_name, pw->pw_gid) != 0) {
        return -1;
    }
    /* 2. GID знижуємо ОБОВ'ЯЗКОВО перед UID: після setuid() прав на setgid
          уже не лишиться. */
    if (setgid(pw->pw_gid) != 0) {
        return -1;
    }
    /* 3. real, effective і saved UID одразу — повернення до root неможливе. */
    if (setuid(pw->pw_uid) != 0) {
        return -1;
    }
    return 0;
}

static void child_run(const cron_job_t *job, const struct passwd *pw,
                      int in_fd, int out_fd)
{
    /* Ізоляція сесії: завдання не отримує сигналів від термінала демона. */
    if (setsid() < 0) {
        _exit(127);
    }

    /* Обробники сигналів і маска успадковані від демона — повертаємо типові. */
    struct sigaction dfl;
    memset(&dfl, 0, sizeof dfl);
    dfl.sa_handler = SIG_DFL;
    sigaction(SIGINT, &dfl, NULL);
    sigaction(SIGTERM, &dfl, NULL);
    sigaction(SIGPIPE, &dfl, NULL);
    sigset_t empty;
    sigemptyset(&empty);
    sigprocmask(SIG_SETMASK, &empty, NULL);

    if (dup2(in_fd, STDIN_FILENO) < 0 ||
        dup2(out_fd, STDOUT_FILENO) < 0 ||
        dup2(out_fd, STDERR_FILENO) < 0) {
        _exit(127);
    }
    if (in_fd > STDERR_FILENO) {
        close(in_fd);
    }
    if (out_fd > STDERR_FILENO) {
        close(out_fd);
    }

    if (getuid() == 0 && drop_privileges(pw) != 0) {
        dprintf(STDERR_FILENO, "minicron: зниження привілеїв до %s: %s\n",
                pw->pw_name, strerror(errno));
        _exit(127);
    }

    /* Робочий каталог — домівка; якщо недоступна, корінь. */
    if (chdir(pw->pw_dir) != 0 && chdir("/") != 0) {
        dprintf(STDERR_FILENO, "minicron: chdir: %s\n", strerror(errno));
        _exit(127);
    }

    exec_shell(job);
    /* Сюди потрапляємо лише після відмови exec: текст піде у поштовий звіт. */
    dprintf(STDERR_FILENO, "minicron: exec %s: %s\n", job_shell(job), strerror(errno));
    _exit(127);
}

/* Одночасно допомпуємо stdin і вичитуємо вивід. Робити це по черзі не можна:
   команда, що надрукувала більше за буфер каналу, спинилася б на write(),
   поки ми чекаємо, доки вона дочитає свій stdin. */
static int pump_io(int read_fd, int *write_fd, const char *in_data, buffer_t *out)
{
    size_t in_len = (in_data != NULL) ? strlen(in_data) : 0;
    size_t in_off = 0;
    bool reading = true;

    while (reading || *write_fd >= 0) {
        struct pollfd fds[2];
        nfds_t n = 0;
        int ri = -1;
        int wi = -1;
        if (reading) {
            fds[n].fd = read_fd;
            fds[n].events = POLLIN;
            fds[n].revents = 0;
            ri = (int)n++;
        }
        if (*write_fd >= 0) {
            fds[n].fd = *write_fd;
            fds[n].events = POLLOUT;
            fds[n].revents = 0;
            wi = (int)n++;
        }

        if (poll(fds, n, -1) < 0) {
            if (errno == EINTR) {
                continue;
            }
            return -1;
        }

        if (wi >= 0 && fds[wi].revents != 0) {
            if ((fds[wi].revents & (POLLERR | POLLHUP)) != 0) {
                /* Команда закрила свій stdin, не дочитавши, — це не аварія. */
                close(*write_fd);
                *write_fd = -1;
            } else {
                ssize_t k = write(*write_fd, in_data + in_off, in_len - in_off);
                if (k < 0 && errno != EINTR && errno != EAGAIN) {
                    close(*write_fd);
                    *write_fd = -1;
                } else if (k > 0) {
                    in_off += (size_t)k;
                    if (in_off == in_len) {
                        close(*write_fd);
                        *write_fd = -1;
                    }
                }
            }
        }

        if (ri >= 0 && fds[ri].revents != 0) {
            char chunk[OUTPUT_CHUNK];
            ssize_t k = read(read_fd, chunk, sizeof chunk);
            if (k > 0) {
                if (!buffer_append(out, chunk, (size_t)k)) {
                    return -1;
                }
            } else if (k == 0) {
                reading = false; /* дитина закрила записувальний кінець */
            } else if (errno != EINTR && errno != EAGAIN) {
                return -1;
            }
        }
    }
    return 0;
}

static int write_all(int fd, const char *data, size_t len)
{
    size_t done = 0;
    while (done < len) {
        ssize_t n = write(fd, data + done, len - done);
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            return -1;
        }
        done += (size_t)n;
    }
    return 0;
}

/* Контракт MTA: sendmail читає адресата із заголовків повідомлення (-t). */
static void deliver_mail(const cron_job_t *job, const char *body, size_t body_len)
{
    int mail_pipe[2];
    if (pipe2(mail_pipe, O_CLOEXEC) != 0) {
        perror("minicron: pipe для sendmail");
        return;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("minicron: fork для sendmail");
        close(mail_pipe[0]);
        close(mail_pipe[1]);
        return;
    }
    if (pid == 0) {
        close(mail_pipe[1]);
        if (dup2(mail_pipe[0], STDIN_FILENO) < 0) {
            _exit(127);
        }
        close(mail_pipe[0]);
        execl("/usr/sbin/sendmail", "sendmail",
              "-FCronDaemon", "-odi", "-oem", "-oi", "-t", (char *)NULL);
        _exit(127);
    }

    close(mail_pipe[0]);

    char host[256];
    if (gethostname(host, sizeof host) != 0) {
        snprintf(host, sizeof host, "localhost");
    }

    char header[1024];
    int header_len = snprintf(header, sizeof header,
        "From: root (Cron Daemon)\n"
        "To: %s\n"
        "Subject: Cron <%s@%s> %s\n"
        "MIME-Version: 1.0\n"
        "Content-Type: text/plain; charset=UTF-8\n"
        "Content-Transfer-Encoding: 8bit\n"
        "Auto-Submitted: auto-generated\n",
        job->mailto, job->user, host, job->command);
    if (header_len > 0) {
        write_all(mail_pipe[1], header, (size_t)header_len);
    }

    /* Середовище завдання їде окремими заголовками X-Cron-Env. */
    for (char *const *env = job->envp; env != NULL && *env != NULL; env++) {
        char line[512];
        int n = snprintf(line, sizeof line, "X-Cron-Env: <%s>\n", *env);
        if (n > 0) {
            write_all(mail_pipe[1], line, (size_t)n);
        }
    }
    write_all(mail_pipe[1], "\n", 1);
    write_all(mail_pipe[1], body, body_len);
    close(mail_pipe[1]);

    int status = 0;
    while (waitpid(pid, &status, 0) < 0 && errno == EINTR) {
        continue;
    }
    if (WIFEXITED(status) && WEXITSTATUS(status) != 0) {
        fprintf(stderr, "minicron: sendmail завершився кодом %d\n", WEXITSTATUS(status));
    }
}

int cron_job_run(const cron_job_t *job)
{
    struct passwd *pw = getpwnam(job->user);
    if (pw == NULL) {
        fprintf(stderr, "minicron: невідомий користувач «%s»\n", job->user);
        return -1;
    }

    /* O_CLOEXEC на обох кінцях: у дитини потрібні дескриптори переживуть exec
       лише тому, що dup2() знімає прапорець із копії. */
    int out_pipe[2];
    if (pipe2(out_pipe, O_CLOEXEC) != 0) {
        perror("minicron: pipe");
        return -1;
    }

    int in_pipe[2] = {-1, -1};
    int null_fd = -1;
    const bool has_stdin = (job->stdin_data != NULL && job->stdin_data[0] != '\0');
    if (has_stdin) {
        if (pipe2(in_pipe, O_CLOEXEC) != 0) {
            perror("minicron: pipe");
            close(out_pipe[0]);
            close(out_pipe[1]);
            return -1;
        }
        /* Записувальний кінець неблокуючий — інакше повний канал спинив би
           демона, поки команда не почне читати. */
        int flags = fcntl(in_pipe[1], F_GETFL, 0);
        if (flags >= 0) {
            fcntl(in_pipe[1], F_SETFL, flags | O_NONBLOCK);
        }
    } else {
        /* Без даних після '%' stdin завдання — /dev/null: читання дає EOF. */
        null_fd = open("/dev/null", O_RDWR | O_CLOEXEC);
        if (null_fd < 0) {
            perror("minicron: open /dev/null");
            close(out_pipe[0]);
            close(out_pipe[1]);
            return -1;
        }
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("minicron: fork");
        close(out_pipe[0]);
        close(out_pipe[1]);
        if (null_fd >= 0) {
            close(null_fd);
        }
        if (in_pipe[0] >= 0) {
            close(in_pipe[0]);
            close(in_pipe[1]);
        }
        return -1;
    }
    if (pid == 0) {
        close(out_pipe[0]);
        if (in_pipe[1] >= 0) {
            close(in_pipe[1]);
        }
        child_run(job, pw, has_stdin ? in_pipe[0] : null_fd, out_pipe[1]);
        _exit(127); /* сюди не потрапляємо */
    }

    close(out_pipe[1]);
    if (null_fd >= 0) {
        close(null_fd);
    }
    if (has_stdin) {
        close(in_pipe[0]);
    }

    buffer_t output = {NULL, 0, 0};
    int write_fd = has_stdin ? in_pipe[1] : -1;
    int rc = pump_io(out_pipe[0], &write_fd, job->stdin_data, &output);
    if (rc != 0) {
        fprintf(stderr, "minicron: обмін із завданням: %s\n", strerror(errno));
    }
    if (write_fd >= 0) {
        close(write_fd);
    }
    close(out_pipe[0]);

    int status = 0;
    while (waitpid(pid, &status, 0) < 0) {
        if (errno != EINTR) {
            perror("minicron: waitpid");
            free(output.data);
            return -1;
        }
    }

    int exit_code = WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status);

    /* Пошта йде лише тоді, коли MAILTO непорожній І вивід не порожній —
       мовчазне завдання не турбує адміністратора незалежно від коду виходу. */
    if (job->mailto != NULL && job->mailto[0] != '\0' && output.len > 0) {
        deliver_mail(job, output.data, output.len);
    }
    free(output.data);
    return exit_code;
}
