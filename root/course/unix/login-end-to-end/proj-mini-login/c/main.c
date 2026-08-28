#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pwd.h>
#include <grp.h>
#include <termios.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/ioctl.h>
#include <security/pam_appl.h>

/* Функція діалогу PAM: читання пароля з термінала */
static int login_conv(int num_msg, const struct pam_message **msg,
                      struct pam_response **resp, void *appdata_ptr) {
    if (num_msg <= 0 || num_msg > PAM_MAX_NUM_MSG)
        return PAM_CONV_ERR;

    struct pam_response *reply = calloc(num_msg, sizeof(struct pam_response));
    if (!reply)
        return PAM_BUF_ERR;

    for (int i = 0; i < num_msg; ++i) {
        switch (msg[i]->msg_style) {
            case PAM_PROMPT_ECHO_OFF: {
                /* Вимикаємо відлуння символів для вводу пароля */
                struct termios old_t, new_t;
                tcgetattr(STDIN_FILENO, &old_t);
                new_t = old_t;
                new_t.c_lflag &= ~(ECHO | ECHOE | ECHOK | ECHONL);
                tcsetattr(STDIN_FILENO, TCSANOW, &new_t);

                printf("%s", msg[i]->msg);
                fflush(stdout);

                char buf[256];
                if (!fgets(buf, sizeof(buf), stdin)) {
                    tcsetattr(STDIN_FILENO, TCSANOW, &old_t);
                    free(reply);
                    return PAM_CONV_ERR;
                }
                tcsetattr(STDIN_FILENO, TCSANOW, &old_t);
                printf("\n");

                buf[strcspn(buf, "\r\n")] = '\0';
                reply[i].resp = strdup(buf);
                reply[i].resp_retcode = 0;
                break;
            }
            case PAM_PROMPT_ECHO_ON: {
                printf("%s", msg[i]->msg);
                fflush(stdout);
                char buf[256];
                if (!fgets(buf, sizeof(buf), stdin)) {
                    free(reply);
                    return PAM_CONV_ERR;
                }
                buf[strcspn(buf, "\r\n")] = '\0';
                reply[i].resp = strdup(buf);
                reply[i].resp_retcode = 0;
                break;
            }
            case PAM_ERROR_MSG:
                fprintf(stderr, "%s\n", msg[i]->msg);
                break;
            case PAM_TEXT_INFO:
                printf("%s\n", msg[i]->msg);
                break;
            default:
                free(reply);
                return PAM_CONV_ERR;
        }
    }
    *resp = reply;
    return PAM_SUCCESS;
}

int main(int argc, char *argv[]) {
    if (getuid() != 0) {
        fprintf(stderr, "Помилка: mini-login повинен запускатися з правами root (UID 0)\n");
        return EXIT_FAILURE;
    }

    char username[128];
    if (argc > 1) {
        strncpy(username, argv[1], sizeof(username) - 1);
        username[sizeof(username) - 1] = '\0';
    } else {
        printf("login: ");
        fflush(stdout);
        if (!fgets(username, sizeof(username), stdin))
            return EXIT_FAILURE;
        username[strcspn(username, "\r\n")] = '\0';
    }

    struct passwd *pw = getpwnam(username);
    if (!pw) {
        fprintf(stderr, "Невідомий користувач або запис відсутній у NSS\n");
        return EXIT_FAILURE;
    }

    pam_handle_t *pamh = NULL;
    struct pam_conv conv = { .conv = login_conv, .appdata_ptr = NULL };

    int rc = pam_start("login", username, &conv, &pamh);
    if (rc != PAM_SUCCESS) {
        fprintf(stderr, "pam_start збій: %s\n", pam_strerror(pamh, rc));
        return EXIT_FAILURE;
    }

    /* 1. Фаза auth: перевірка пароля */
    rc = pam_authenticate(pamh, 0);
    if (rc != PAM_SUCCESS) {
        fprintf(stderr, "Помилка автентифікації: %s\n", pam_strerror(pamh, rc));
        pam_end(pamh, rc);
        return EXIT_FAILURE;
    }

    /* 2. Фаза account: перевірка терміну дії та блокування */
    rc = pam_acct_mgmt(pamh, 0);
    if (rc != PAM_SUCCESS) {
        fprintf(stderr, "Помилка облікового запису: %s\n", pam_strerror(pamh, rc));
        pam_end(pamh, rc);
        return EXIT_FAILURE;
    }

    /* 3. Фаза session: підготовка облікових даних та сеансу */
    rc = pam_setcred(pamh, PAM_ESTABLISH_CRED);
    if (rc != PAM_SUCCESS) {
        pam_end(pamh, rc);
        return EXIT_FAILURE;
    }

    rc = pam_open_session(pamh, 0);
    if (rc != PAM_SUCCESS) {
        fprintf(stderr, "Збій відкриття сесії PAM: %s\n", pam_strerror(pamh, rc));
        pam_setcred(pamh, PAM_DELETE_CRED);
        pam_end(pamh, rc);
        return EXIT_FAILURE;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        pam_close_session(pamh, 0);
        pam_end(pamh, PAM_ABORT);
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        /* Дочірній процес: підготовка середовища та запуск Login Shell */
        if (setsid() < 0)
            perror("setsid");

        /* Критичний порядок скидання привілеїв: initgroups -> setgid -> setuid */
        if (initgroups(pw->pw_name, pw->pw_gid) < 0) {
            perror("initgroups");
            _exit(EXIT_FAILURE);
        }

        if (setgid(pw->pw_gid) < 0) {
            perror("setgid");
            _exit(EXIT_FAILURE);
        }

        if (setuid(pw->pw_uid) < 0) {
            perror("setuid");
            _exit(EXIT_FAILURE);
        }

        /* Налаштування робочого каталогу та змінних */
        if (chdir(pw->pw_dir) < 0) {
            fprintf(stderr, "Попередження: не вдалося перейти в $HOME, перехід у /\n");
            if (chdir("/") < 0) _exit(EXIT_FAILURE);
        }

        setenv("HOME", pw->pw_dir, 1);
        setenv("USER", pw->pw_name, 1);
        setenv("LOGNAME", pw->pw_name, 1);
        setenv("SHELL", pw->pw_shell, 1);

        /* Експорт змінних, створених модулями PAM (pam_env) */
        char **pam_env = pam_getenvlist(pamh);
        if (pam_env) {
            for (char **e = pam_env; *e != NULL; ++e) {
                putenv(*e);
            }
        }

        /* Запуск login shell з дефісом у нульовому аргументі */
        char *shell = pw->pw_shell[0] ? pw->pw_shell : "/bin/sh";
        char *argv0 = malloc(strlen(shell) + 2);
        sprintf(argv0, "-%s", strrchr(shell, '/') ? strrchr(shell, '/') + 1 : shell);

        char *args[] = { argv0, NULL };
        execve(shell, args, environ);

        perror("execve");
        _exit(EXIT_FAILURE);
    }

    /* Батьківський процес: очікування виходу користувача та закриття PAM */
    int status;
    waitpid(pid, &status, 0);

    pam_close_session(pamh, 0);
    pam_setcred(pamh, PAM_DELETE_CRED);
    pam_end(pamh, PAM_SUCCESS);

    return EXIT_SUCCESS;
}
