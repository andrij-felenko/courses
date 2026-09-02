#ifndef LISTEN_FDS_H
#define LISTEN_FDS_H

#include <sys/un.h>

// Звідки взявся слухаючий сокет. Різниця не косметична: сокет менеджера
// переживає нас (PID 1 тримає його відкритим і між перезапусками служби),
// а свій ми мусимо прибрати за собою.
enum listen_source {
    LISTEN_FROM_SYSTEMD,
    LISTEN_FROM_SELF
};

struct listen_socket {
    int fd;                          // слухаючий дескриптор, завжди неблокуючий
    enum listen_source source;
    char path[sizeof(((struct sockaddr_un *)0)->sun_path)];  // порожній рядок для сокета менеджера
};

// Забирає слухаючий сокет у менеджера, а якщо його не передали — створює власний
// за шляхом fallback_path. Повертає 0 або -errno (libsystemd теж віддає -errno).
int listen_socket_acquire(const char *fallback_path, struct listen_socket *out);

// Людська назва джерела — для журналу.
const char *listen_source_name(enum listen_source source);

// Закриває дескриптор і видаляє файл сокета лише тоді, коли створювали його ми.
void listen_socket_release(struct listen_socket *sock);

#endif /* LISTEN_FDS_H */
