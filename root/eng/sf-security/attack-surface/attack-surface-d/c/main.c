#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <sys/syscall.h>

#define SECURE_PORT 8443

/* Безпечна ініціалізація та прив'язка до локальної петлі */
int create_restricted_socket(void) {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        return -1;
    }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in address;
    memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    /* Мінімізація: прив'язка ВИКЛЮЧНО до 127.0.0.1 замість 0.0.0.0 */
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    address.sin_port = htons(SECURE_PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind");
        close(server_fd);
        return -1;
    }

    if (listen(server_fd, 5) < 0) {
        perror("listen");
        close(server_fd);
        return -1;
    }

    return server_fd;
}

/* Обмеження прав та захист дочірнього обробника */
void harden_worker_process(void) {
    /* 1. Заборона отримання нових привілеїв */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
        perror("prctl(PR_SET_NO_NEW_PRIVS)");
        _exit(1);
    }

    /* 2. Скидання привілеїв до UID nobody (65534) */
    if (setgid(65534) != 0 || setuid(65534) != 0) {
        perror("setuid/setgid");
        _exit(1);
    }

    /* 3. Активація базового суворого режиму Seccomp */
    /* Дозволяє лише read, write, _exit, sigreturn */
    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_STRICT) == -1) {
        perror("prctl(PR_SET_SECCOMP)");
        _exit(1);
    }
}
