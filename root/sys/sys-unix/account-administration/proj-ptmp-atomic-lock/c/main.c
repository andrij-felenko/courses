#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <signal.h>
#include <sys/stat.h>
#include <sys/types.h>

static const char *PASSWD_FILE = "/etc/passwd";
static const char *LOCK_FILE   = "/etc/ptmp";
static volatile sig_atomic_t g_locked = 0;

static void cleanup_lock(void) {
    if (g_locked) {
        unlink(LOCK_FILE);
        g_locked = 0;
    }
}

static void sig_handler(int sig) {
    (void)sig;
    cleanup_lock();
    _exit(1);
}

static void setup_signals(void) {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = sig_handler;
    sigemptyset(&sa.sa_mask);

    sigaction(SIGINT,  &sa, NULL);
    sigaction(SIGHUP,  &sa, NULL);
    sigaction(SIGQUIT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);
}

int acquire_passwd_lock(void) {
    setup_signals();

    int fd = open(LOCK_FILE, O_CREAT | O_EXCL | O_RDWR, 0600);
    if (fd < 0) {
        if (errno == EEXIST) {
            fprintf(stderr, "Помилка: файл блокування %s вже існує.\n", LOCK_FILE);
        } else {
            perror("open(LOCK_FILE)");
        }
        return -1;
    }

    g_locked = 1;
    atexit(cleanup_lock);

    char pid_str[32];
    int len = snprintf(pid_str, sizeof(pid_str), "%d\n", (int)getpid());
    if (write(fd, pid_str, (size_t)len) != len) {
        perror("write(pid)");
        close(fd);
        cleanup_lock();
        return -1;
    }

    return fd;
}

int update_user_shell(const char *target_user, const char *new_shell) {
    int lock_fd = acquire_passwd_lock();
    if (lock_fd < 0) {
        return -1;
    }

    FILE *in = fopen(PASSWD_FILE, "r");
    if (!in) {
        perror("fopen(PASSWD_FILE)");
        close(lock_fd);
        cleanup_lock();
        return -1;
    }

    FILE *out = fdopen(lock_fd, "w");
    if (!out) {
        perror("fdopen(lock_fd)");
        fclose(in);
        close(lock_fd);
        cleanup_lock();
        return -1;
    }

    char line[1024];
    int user_found = 0;
    size_t target_len = strlen(target_user);

    while (fgets(line, sizeof(line), in)) {
        if (strncmp(line, target_user, target_len) == 0 && line[target_len] == ':') {
            user_found = 1;
            char *tokens[7];
            char *saveptr;
            char *tok = strtok_r(line, ":\n", &saveptr);
            int idx = 0;
            while (tok && idx < 7) {
                tokens[idx++] = tok;
                tok = strtok_r(NULL, ":\n", &saveptr);
            }
            if (idx >= 6) {
                fprintf(out, "%s:%s:%s:%s:%s:%s:%s\n",
                        tokens[0], tokens[1], tokens[2],
                        tokens[3], tokens[4], tokens[5],
                        new_shell);
                continue;
            }
        }
        fputs(line, out);
    }

    fclose(in);

    if (!user_found) {
        fprintf(stderr, "Користувача «%s» не знайдено.\n", target_user);
        fclose(out);
        cleanup_lock();
        return -1;
    }

    if (fflush(out) != 0 || fsync(fileno(out)) != 0) {
        perror("fsync(out)");
        fclose(out);
        cleanup_lock();
        return -1;
    }
    fclose(out);

    if (rename(LOCK_FILE, PASSWD_FILE) != 0) {
        perror("rename(LOCK_FILE, PASSWD_FILE)");
        cleanup_lock();
        return -1;
    }

    g_locked = 0;
    return 0;
}
