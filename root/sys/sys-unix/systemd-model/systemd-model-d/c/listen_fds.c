// Отримання слухаючого сокета: перша половина контракту сокетної активації.
// Менеджер уже викликав socket()/bind()/listen() до нашого запуску й передав
// готовий дескриптор через execve(); нам лишається його впізнати й перевірити.
#define _GNU_SOURCE

#include "listen_fds.h"

#include <systemd/sd-daemon.h>

#include <errno.h>
#include <fcntl.h>
#include <stddef.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <unistd.h>

static int set_nonblocking(int fd)
{
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags < 0)
        return -errno;
    if ((flags & O_NONBLOCK) == 0 && fcntl(fd, F_SETFL, flags | O_NONBLOCK) < 0)
        return -errno;
    return 0;
}

// Запуск без менеджера (з рук розробника чи в контейнері без systemd):
// піднімаємо точно такий самий сокет самі, щоб решта коду не знала різниці.
static int bind_own_socket(const char *path, struct listen_socket *out)
{
    struct sockaddr_un addr;
    size_t len = strlen(path);
    int fd, saved;

    if (len == 0 || len >= sizeof addr.sun_path)
        return -ENAMETOOLONG;

    // Після падіння служби у файловій системі лишається мертвий вузол сокета:
    // bind() на нього дає EADDRINUSE, хоч слухати вже нікому.
    if (unlink(path) < 0 && errno != ENOENT)
        return -errno;

    fd = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC | SOCK_NONBLOCK, 0);
    if (fd < 0)
        return -errno;

    memset(&addr, 0, sizeof addr);
    addr.sun_family = AF_UNIX;
    memcpy(addr.sun_path, path, len);

    if (bind(fd, (const struct sockaddr *)&addr, sizeof addr) < 0)
        goto fail;

    // Права менеджер задав би директивою SocketMode=; робимо те саме руками.
    if (chmod(path, 0660) < 0)
        goto fail;

    if (listen(fd, SOMAXCONN) < 0)
        goto fail;

    out->fd = fd;
    out->source = LISTEN_FROM_SELF;
    memcpy(out->path, path, len);
    out->path[len] = '\0';
    return 0;

fail:
    saved = errno;
    close(fd);
    unlink(path);
    return -saved;
}

int listen_socket_acquire(const char *fallback_path, struct listen_socket *out)
{
    int n, fd, r;

    out->fd = -1;
    out->path[0] = '\0';

    // Нуль у аргументі: після читання прибрати LISTEN_FDS і LISTEN_PID зі
    // середовища, щоб наші власні нащадки не сприйняли дескриптори як свої.
    n = sd_listen_fds(0);
    if (n < 0)
        return n;

    if (n == 0)
        return bind_own_socket(fallback_path, out);

    if (n > 1)
        // Юніт описує рівно один Listen*=. Кілька дескрипторів означають, що
        // сокет-юніт і бінарник розійшлися; мовчки взяти перший — приховати ваду.
        return -E2BIG;

    // Перший переданий дескриптор завжди має номер 3: нулем, одиницею й двійкою
    // лишаються стандартні потоки.
    fd = SD_LISTEN_FDS_START;

    // Перевіряємо, що це справді слухаючий потоковий сокет AF_UNIX, а не,
    // скажімо, датаграмний Netlink від сусіднього .socket-юніта.
    r = sd_is_socket_unix(fd, SOCK_STREAM, 1, NULL, 0);
    if (r < 0)
        return r;
    if (r == 0)
        return -EPROTOTYPE;

    // Менеджер віддає дескриптор блокуючим — цикл на epoll вимагає O_NONBLOCK,
    // інакше accept4() між подією й викликом застрягне на зниклому з'єднанні.
    r = set_nonblocking(fd);
    if (r < 0)
        return r;

    out->fd = fd;
    out->source = LISTEN_FROM_SYSTEMD;
    return 0;
}

const char *listen_source_name(enum listen_source source)
{
    return source == LISTEN_FROM_SYSTEMD ? "від менеджера" : "власний";
}

void listen_socket_release(struct listen_socket *sock)
{
    if (sock->fd < 0)
        return;

    close(sock->fd);
    sock->fd = -1;

    if (sock->source == LISTEN_FROM_SELF && sock->path[0] != '\0')
        unlink(sock->path);
}
