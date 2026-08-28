/* C (POSIX API) — Серверний сокет у волотильному каталозі */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/stat.h>
#include <errno.h>

#define SOCKET_PATH "/run/appdaemon/service.sock"

int create_secure_socket(const char *path) {
    int server_fd = -1;
    struct sockaddr_un addr;

    /* Видаляємо застарілий сокет, якщо він лишився після аварійного завершення */
    unlink(path);

    server_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket failed");
        return -1;
    }

    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, path, sizeof(addr.sun_path) - 1);

    /* Прив'язуємо сокет до шляху у волотильному каталозі */
    if (bind(server_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind failed");
        close(server_fd);
        return -1;
    }

    /* Обмежуємо права доступу до сокета лише для власника та групи */
    if (chmod(path, 0660) < 0) {
        perror("chmod failed");
        close(server_fd);
        unlink(path);
        return -1;
    }

    if (listen(server_fd, 5) < 0) {
        perror("listen failed");
        close(server_fd);
        unlink(path);
        return -1;
    }

    return server_fd;
}

int main(void) {
    printf("Starting appdaemon inside /run/appdaemon...\n");
    int listen_fd = create_secure_socket(SOCKET_PATH);
    if (listen_fd < 0) {
        fprintf(stderr, "Failed to initialize server socket\n");
        return EXIT_FAILURE;
    }

    printf("Daemon is listening on %s\n", SOCKET_PATH);

    /* Основний цикл обробки мережевих подій та запитів клієнтів */
    /* ... */

    close(listen_fd);
    unlink(SOCKET_PATH);
    return EXIT_SUCCESS;
}
