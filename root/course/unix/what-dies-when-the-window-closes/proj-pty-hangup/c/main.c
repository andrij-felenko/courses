#define _XOPEN_SOURCE 600
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/wait.h>

static volatile sig_atomic_t g_hup_received = 0;

static void hup_handler(int sig) {
    (void)sig;
    g_hup_received = 1;
}

static void run_child(const char *slave_path) {
    /* 1. Створюємо новий сеанс: дочірній процес стає лідером сесії */
    if (setsid() < 0) {
        perror("setsid");
        exit(EXIT_FAILURE);
    }

    /* 2. Відкриваємо слейв PTY */
    int sfd = open(slave_path, O_RDWR);
    if (sfd < 0) {
        perror("open slave");
        exit(EXIT_FAILURE);
    }

    /* 3. Призначаємо відкритий PTY slave керівним терміналом сеансу */
    if (ioctl(sfd, TIOCSCTTY, 0) < 0) {
        perror("ioctl TIOCSCTTY");
        exit(EXIT_FAILURE);
    }

    /* 4. Перенаправляємо стандартні дескриптори на PTY slave */
    dup2(sfd, STDIN_FILENO);
    dup2(sfd, STDOUT_FILENO);
    dup2(sfd, STDERR_FILENO);
    if (sfd > STDERR_FILENO) {
        close(sfd);
    }

    /* 5. Встановлюємо обробник сигналу SIGHUP */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = hup_handler;
    sigemptyset(&sa.sa_mask);
    if (sigaction(SIGHUP, &sa, NULL) < 0) {
        exit(EXIT_FAILURE);
    }

    /* Логування у файл для незалежної фіксації подій */
    FILE *log = fopen("/tmp/pty_child.log", "w");
    if (!log) {
        exit(EXIT_FAILURE);
    }
    setvbuf(log, NULL, _IOLBF, 0);

    fprintf(log, "[CHILD %d] Сеанс створено. Очікування подій...\n", getpid());

    /* Цикл очікування розриву зв'язку */
    for (int i = 0; i < 30; ++i) {
        usleep(100000); /* 100 мс */

        if (g_hup_received) {
            fprintf(log, "[CHILD %d] Отримано сигнал SIGHUP від ядра!\n", getpid());
            
            /* Перевіряємо стан читання з термінала після hangup */
            char buf[64];
            int flags = fcntl(STDIN_FILENO, F_GETFL, 0);
            fcntl(STDIN_FILENO, F_SETFL, flags | O_NONBLOCK);
            ssize_t nr = read(STDIN_FILENO, buf, sizeof(buf));
            fprintf(log, "[CHILD %d] Спроба read(0): повернуто %zd (errno=%d: %s)\n",
                    getpid(), nr, errno, strerror(errno));

            /* Перевіряємо стан запису у завислий термінал */
            ssize_t nw = write(STDOUT_FILENO, "test\n", 5);
            fprintf(log, "[CHILD %d] Спроба write(1): повернуто %zd (errno=%d: %s)\n",
                    getpid(), nw, errno, strerror(errno));

            fprintf(log, "[CHILD %d] Завершення роботи після розриву.\n", getpid());
            fclose(log);
            exit(EXIT_SUCCESS);
        }
    }

    fprintf(log, "[CHILD %d] Таймаут очікування сигналу.\n", getpid());
    fclose(log);
    exit(EXIT_SUCCESS);
}

int main(void) {
    /* 1. Відкриваємо мастер-дескриптор псевдотермінала */
    int mfd = posix_openpt(O_RDWR | O_NOCTTY);
    if (mfd < 0) {
        perror("posix_openpt");
        return EXIT_FAILURE;
    }

    if (grantpt(mfd) < 0 || unlockpt(mfd) < 0) {
        perror("grantpt/unlockpt");
        close(mfd);
        return EXIT_FAILURE;
    }

    char *sname = ptsname(mfd);
    if (!sname) {
        perror("ptsname");
        close(mfd);
        return EXIT_FAILURE;
    }

    printf("[PARENT] PTY Master відкрито (fd=%d). Slave шлях: %s\n", mfd, sname);

    pid_t child_pid = fork();
    if (child_pid < 0) {
        perror("fork");
        close(mfd);
        return EXIT_FAILURE;
    }

    if (child_pid == 0) {
        close(mfd); /* Дитина не повинна утримувати мастер-дескриптор */
        run_child(sname);
    }

    /* Батьківський процес: емулюємо роботу вікна емулятора протягом 1 секунди */
    printf("[PARENT] Дочірній процес запущено (PID=%d). Вікно активне 1 секунду...\n", child_pid);
    sleep(1);

    /* Імітуємо закриття вікна користувачем: закриваємо мастер-дескриптор */
    printf("[PARENT] Закриваємо master_fd (%d), моделюючи клік на [X] вікна...\n", mfd);
    close(mfd);

    /* Очікуємо на завершення дочірнього процесу */
    int status = 0;
    waitpid(child_pid, &status, 0);

    if (WIFEXITED(status)) {
        printf("[PARENT] Дочірній процес завершився зі статусом %d.\n", WEXITSTATUS(status));
    } else if (WIFSIGNALED(status)) {
        printf("[PARENT] Дочірній процес загинув від сигналу %d (%s).\n",
               WTERMSIG(status), strsignal(WTERMSIG(status)));
    }

    /* Виводимо протокол подій дочірнього процесу */
    printf("\n--- Протокол дочірнього процесу (/tmp/pty_child.log) ---\n");
    FILE *log = fopen("/tmp/pty_child.log", "r");
    if (log) {
        char line[256];
        while (fgets(line, sizeof(line), log)) {
            fputs(line, stdout);
        }
        fclose(log);
        unlink("/tmp/pty_child.log");
    }

    return EXIT_SUCCESS;
}
