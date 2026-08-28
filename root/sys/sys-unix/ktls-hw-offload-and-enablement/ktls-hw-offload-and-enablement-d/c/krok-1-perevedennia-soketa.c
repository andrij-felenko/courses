/* Приклад на C */
#include <sys/socket.h>
#include <netinet/tcp.h>

int sock_fd = accept(listen_fd, NULL, NULL);

/* Реєструємо ULP 'tls' для TCP сокета */
if (setsockopt(sock_fd, SOL_TCP, TCP_ULP, "tls", sizeof("tls")) < 0) {
    perror("Помилка активації ULP tls");
}
