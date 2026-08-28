#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/prctl.h>
#include <sys/wait.h>
#include <grp.h>

#define UNPRIV_UID 65534 /* nobody */
#define UNPRIV_GID 65534 /* nogroup */

enum IpcCommand {
    CMD_LOG_MESSAGE = 1,
    CMD_AUTH_CHECK  = 2,
    CMD_EXIT        = 3
};

struct IpcMessage {
    int command;
    int payload_len;
    char buffer[256];
};

/* Скидання прав процесу до абсолютного мінімуму */
static int drop_worker_privileges(void) {
    /* 1. Очищення списку додаткових груп */
    if (setgroups(0, NULL) == -1) {
        perror("setgroups");
        return -1;
    }

    /* 2. Скидання реального, ефективного та збереженого GID */
    if (setresgid(UNPRIV_GID, UNPRIV_GID, UNPRIV_GID) == -1) {
        perror("setresgid");
        return -1;
    }

    /* 3. Скидання реального, ефективного та збереженого UID */
    if (setresuid(UNPRIV_UID, UNPRIV_UID, UNPRIV_UID) == -1) {
        perror("setresuid");
        return -1;
    }

    /* 4. Заборона отримання будь-яких нових привілеїв у майбутньому */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
        perror("prctl(PR_SET_NO_NEW_PRIVS)");
        return -1;
    }

    return 0;
}

/* Логіка ізольованого воркера */
static void run_sandboxed_worker(int ipc_fd) {
    if (drop_worker_privileges() != 0) {
        fprintf(stderr, "Помилка деескалації прав воркера\n");
        close(ipc_fd);
        _exit(1);
    }

    /* Воркер парсить вхідні дані та формує IPC-запит до монітора */
    struct IpcMessage msg;
    memset(&msg, 0, sizeof(msg));
    msg.command = CMD_LOG_MESSAGE;
    
    const char *event_text = "З'єднання оброблено в ізольованому воркері";
    msg.payload_len = (int)strlen(event_text);
    strncpy(msg.buffer, event_text, sizeof(msg.buffer) - 1);

    if (write(ipc_fd, &msg, sizeof(msg)) != sizeof(msg)) {
        perror("worker write to ipc");
        close(ipc_fd);
        _exit(1);
    }

    close(ipc_fd);
    _exit(0);
}

/* Логіка привілейованого монітора */
static void run_privileged_monitor(int ipc_fd, pid_t worker_pid) {
    struct IpcMessage msg;
    ssize_t bytes_read = read(ipc_fd, &msg, sizeof(msg));

    if (bytes_read == sizeof(msg)) {
        if (msg.command == CMD_LOG_MESSAGE) {
            msg.buffer[sizeof(msg.buffer) - 1] = '\0';
            printf("[MONITOR LOG] Отримано подію від PID %d: %s\n",
                   worker_pid, msg.buffer);
        }
    } else {
        fprintf(stderr, "Помилка читання IPC повідомлення\n");
    }

    close(ipc_fd);

    int status = 0;
    waitpid(worker_pid, &status, 0);
}

int main(void) {
    int sv[2];
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, sv) == -1) {
        perror("socketpair");
        return 1;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        close(sv[0]);
        close(sv[1]);
        return 1;
    }

    if (pid == 0) {
        /* Дочірній процес: закриваємо кінцівку монітора */
        close(sv[0]);
        run_sandboxed_worker(sv[1]);
    } else {
        /* Батьківський процес: закриваємо кінцівку воркера */
        close(sv[1]);
        run_privileged_monitor(sv[0], pid);
    }

    return 0;
}
