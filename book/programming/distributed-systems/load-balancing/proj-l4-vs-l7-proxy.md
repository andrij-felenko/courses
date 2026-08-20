# ⚙️ Реалізація L4 TCP-сплайсера та L7 HTTP-маршрутизатора

Щоб побачити принципову архітектурну різницю між 4-м та 7-м рівнями балансування, порівняємо дві самодостатні реалізації на системному рівні:
1. **L4 TCP-проксі:** працює як симетричний потоковий міст між сокетом клієнта та сокетом бекенда; балансувальник не заглядає у байти корисного навантаження і передає дані за допомогою неблокуючого мультиплексування вводу-виводу (`poll`/`epoll`) без розбору протоколів.
2. **L7 HTTP-маршрутизатор:** термінує вхідне з'єднання, вичитує HTTP-запит, розбирає рядок запиту, URI та заголовки, ухвалює рішення про маршрутизацію на основі шляху (`/api` проти `/static`), модифікує заголовки (`X-Forwarded-For`) і ретранслює запит до відповідного пулу бекендів.

### Архітектура та життєвий цикл L4-сплайсера

L4-проксі оперує двома сокетами на кожну клієнтську сесію: дескриптором клієнта (`client_fd`) та дескриптором висхідного сервера (`backend_fd`). Проксі переводить обидва сокети в неблокуючий режим (`O_NONBLOCK`) і реєструє їх у системному опитувачі подій (`poll` або `epoll`).

Коли на сокеті клієнта з'являються дані (подія `POLLIN`), проксі зчитує масив байтів у проміжний буфер фіксованого розміру і негайно записує його у висхідний сокет. Зворотний потік від сервера до клієнта обслуговується абсолютно симетрично. Балансувальник не знає, де закінчується один логічний запит і починається наступний; він бачить лише безперервний потік октетів.

Для мінімізації затримок на обох сокетах вимикається алгоритм Нейгла за допомогою прапорця `TCP_NODELAY`, що запобігає штучній затримці невеликих пакетів у буфері ядра перед відправкою.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>

#define BUF_SIZE 16384

static int configure_socket(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    if (fcntl(fd, F_SETFL, flags | O_NONBLOCK) == -1) return -1;

    int one = 1;
    setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &one, sizeof(one));
    return 0;
}

/* L4 перекачування потоку байтів без інспекції вмісту */
void l4_bridge_loop(int client_fd, int backend_fd) {
    configure_socket(client_fd);
    configure_socket(backend_fd);

    struct pollfd fds[2];
    fds[0].fd = client_fd;
    fds[0].events = POLLIN;
    fds[1].fd = backend_fd;
    fds[1].events = POLLIN;

    char buf[BUF_SIZE];
    int active = 1;

    while (active) {
        int ret = poll(fds, 2, 5000);
        if (ret < 0) {
            if (errno == EINTR) continue;
            break;
        }
        if (ret == 0) continue; /* Таймаут активності */

        /* Дані від клієнта -> направляємо в бекенд */
        if (fds[0].revents & POLLIN) {
            ssize_t n = read(client_fd, buf, sizeof(buf));
            if (n > 0) {
                ssize_t written = 0;
                while (written < n) {
                    ssize_t w = write(backend_fd, buf + written, n - written);
                    if (w <= 0) {
                        if (errno == EAGAIN || errno == EWOULDBLOCK) continue;
                        active = 0;
                        break;
                    }
                    written += w;
                }
            } else if (n == 0 || (n < 0 && errno != EAGAIN)) {
                shutdown(backend_fd, SHUT_WR);
                fds[0].events = 0;
            }
        }

        /* Дані від бекенда -> направляємо клієнту */
        if (fds[1].revents & POLLIN) {
            ssize_t n = read(backend_fd, buf, sizeof(buf));
            if (n > 0) {
                ssize_t written = 0;
                while (written < n) {
                    ssize_t w = write(client_fd, buf + written, n - written);
                    if (w <= 0) {
                        if (errno == EAGAIN || errno == EWOULDBLOCK) continue;
                        active = 0;
                        break;
                    }
                    written += w;
                }
            } else if (n == 0 || (n < 0 && errno != EAGAIN)) {
                shutdown(client_fd, SHUT_WR);
                fds[1].events = 0;
            }
        }

        if ((fds[0].revents & (POLLERR | POLLHUP | POLLNVAL)) ||
            (fds[1].revents & (POLLERR | POLLHUP | POLLNVAL)) ||
            (fds[0].events == 0 && fds[1].events == 0)) {
            break;
        }
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <string_view>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <poll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

class SocketHandle {
    int fd_ = -1;
public:
    explicit SocketHandle(int fd = -1) : fd_(fd) {}
    ~SocketHandle() {
        if (fd_ >= 0) ::close(fd_);
    }
    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;
    SocketHandle(SocketHandle&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    SocketHandle& operator=(SocketHandle&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    void configure() const {
        int flags = ::fcntl(fd_, F_GETFL, 0);
        if (flags >= 0) ::fcntl(fd_, F_SETFL, flags | O_NONBLOCK);
        int one = 1;
        ::setsockopt(fd_, IPPROTO_TCP, TCP_NODELAY, &one, sizeof(one));
    }
    void shutdownWrite() const noexcept {
        if (fd_ >= 0) ::shutdown(fd_, SHUT_WR);
    }
};

/* Ідіоматичний L4-міст на базі C++ RAII та std::span */
void l4BridgeLoopCpp(const SocketHandle& client, const SocketHandle& backend) {
    client.configure();
    backend.configure();

    std::array<pollfd, 2> fds{{
        {client.get(), POLLIN, 0},
        {backend.get(), POLLIN, 0}
    }};

    std::array<char, 16384> buffer{};

    auto forwardData = [](int src, int dst, std::span<char> buf) -> bool {
        ssize_t n = ::read(src, buf.data(), buf.size());
        if (n > 0) {
            ssize_t written = 0;
            while (written < n) {
                ssize_t w = ::write(dst, buf.data() + written, n - written);
                if (w <= 0) {
                    if (errno == EAGAIN || errno == EWOULDBLOCK) continue;
                    return false;
                }
                written += w;
            }
            return true;
        }
        return n == 0 ? false : (errno == EAGAIN);
    };

    while (true) {
        int ret = ::poll(fds.data(), fds.size(), 5000);
        if (ret < 0) {
            if (errno == EINTR) continue;
            break;
        }
        if (ret == 0) continue;

        if (fds[0].revents & POLLIN) {
            if (!forwardData(client.get(), backend.get(), buffer)) {
                backend.shutdownWrite();
                fds[0].events = 0;
            }
        }
        if (fds[1].revents & POLLIN) {
            if (!forwardData(backend.get(), client.get(), buffer)) {
                client.shutdownWrite();
                fds[1].events = 0;
            }
        }

        if ((fds[0].revents & (POLLERR | POLLHUP)) ||
            (fds[1].revents & (POLLERR | POLLHUP)) ||
            (fds[0].events == 0 && fds[1].events == 0)) {
            break;
        }
    }
}
```
:::

---

### Архітектура та розбір запитів у L7-маршрутизаторі

На відміну від L4, прикладний проксі зобов'язаний вичитати початковий блок байтів у пам'ять і запустити кінцевий автомат синтаксичного аналізу (HTTP Parser).

Маршрутизатор розбирає стартовий рядок протоколу, щоб визначити HTTP-метод (`GET`, `POST`, `PUT`), запитаний шлях (`Path`) та версію протоколу. На основі префіксу шляху ухвалюється логічне рішення:
* Запити з префіксом `/api` відправляються на виділений кластер серверів бізнес-логіки (`127.0.0.1:8081`).
* Усі інші запити (наприклад, файли стилів, скрипти або HTML-документи) відправляються на сервери роздачі статики (`127.0.0.1:8082`).

Крім маршрутизації, L7-проксі модифікує потік: він додає службовий заголовок `X-Forwarded-For`, щоб кінцевий бекенд знав реальну IP-адресу клієнта, незважаючи на розрив транспортного з'єднання.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define API_BACKEND_PORT 8081
#define STATIC_BACKEND_PORT 8082

static int connect_backend(int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

    if (connect(fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        close(fd);
        return -1;
    }
    return fd;
}

/* L7 розбір HTTP-запиту та маршрутизація за префіксом шляху */
void l7_handle_http_request(int client_fd, const char* client_ip) {
    char req_buf[8192];
    ssize_t bytes_read = read(client_fd, req_buf, sizeof(req_buf) - 1);
    if (bytes_read <= 0) {
        close(client_fd);
        return;
    }
    req_buf[bytes_read] = '\0';

    char method[16], path[256], proto[16];
    if (sscanf(req_buf, "%15s %255s %15s", method, path, proto) != 3) {
        const char* bad_req = "HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\n\r\n";
        write(client_fd, bad_req, strlen(bad_req));
        close(client_fd);
        return;
    }

    /* Семантичне рішення L7: вибір цільового бекенда за URI */
    int target_port = (strncmp(path, "/api", 4) == 0) ? API_BACKEND_PORT : STATIC_BACKEND_PORT;
    int backend_fd = connect_backend(target_port);
    if (backend_fd < 0) {
        const char* err_503 = "HTTP/1.1 503 Service Unavailable\r\nContent-Length: 0\r\n\r\n";
        write(client_fd, err_503, strlen(err_503));
        close(client_fd);
        return;
    }

    /* Модифікація заголовків: додавання X-Forwarded-For */
    char forward_header[128];
    snprintf(forward_header, sizeof(forward_header), "X-Forwarded-For: %s\r\n", client_ip);

    /* Знаходимо кінець рядка запиту та вставляємо заголовок */
    char* header_insert_pt = strstr(req_buf, "\r\n");
    if (header_insert_pt) {
        header_insert_pt += 2;
        write(backend_fd, req_buf, header_insert_pt - req_buf);
        write(backend_fd, forward_header, strlen(forward_header));
        write(backend_fd, header_insert_pt, strlen(header_insert_pt));
    } else {
        write(backend_fd, req_buf, bytes_read);
    }

    /* Читання відповіді бекенда та повернення клієнту */
    char res_buf[8192];
    ssize_t n;
    while ((n = read(backend_fd, res_buf, sizeof(res_buf))) > 0) {
        write(client_fd, res_buf, n);
    }

    close(backend_fd);
    close(client_fd);
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <array>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

class L7HttpProxy {
    static constexpr uint16_t API_PORT = 8081;
    static constexpr uint16_t STATIC_PORT = 8082;

    static int connectToBackend(uint16_t port) {
        int fd = ::socket(AF_INET, SOCK_STREAM, 0);
        if (fd < 0) return -1;

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port);
        ::inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

        if (::connect(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            ::close(fd);
            return -1;
        }
        return fd;
    }

public:
    static void handleConnection(int rawClientFd, std::string_view clientIp) {
        auto clientFd = std::unique_ptr<int, void(*)(int*)>(
            new int(rawClientFd), [](int* fd) { if (fd) { ::close(*fd); delete fd; } }
        );

        std::array<char, 8192> reqBuffer{};
        ssize_t bytesRead = ::read(*clientFd, reqBuffer.data(), reqBuffer.size() - 1);
        if (bytesRead <= 0) return;
        reqBuffer[bytesRead] = '\0';

        std::string_view request(reqBuffer.data(), bytesRead);
        auto lineEnd = request.find("\r\n");
        if (lineEnd == std::string_view::npos) return;

        std::string_view startLine = request.substr(0, lineEnd);
        auto firstSpace = startLine.find(' ');
        auto secondSpace = startLine.rfind(' ');
        if (firstSpace == std::string_view::npos || secondSpace == firstSpace) return;

        std::string_view path = startLine.substr(firstSpace + 1, secondSpace - firstSpace - 1);

        /* Вибір цільового бекенда за шляхом */
        uint16_t targetPort = path.starts_with("/api") ? API_PORT : STATIC_PORT;
        int rawBackendFd = connectToBackend(targetPort);
        if (rawBackendFd < 0) return;

        auto backendFd = std::unique_ptr<int, void(*)(int*)>(
            new int(rawBackendFd), [](int* fd) { if (fd) { ::close(*fd); delete fd; } }
        );

        /* Ін'єкція заголовка X-Forwarded-For без зайвих алокацій пам'яті */
        std::string mutatedRequest;
        mutatedRequest.reserve(request.size() + 64);
        mutatedRequest.append(request.substr(0, lineEnd + 2));
        mutatedRequest.append("X-Forwarded-For: ");
        mutatedRequest.append(clientIp);
        mutatedRequest.append("\r\n");
        mutatedRequest.append(request.substr(lineEnd + 2));

        ::write(*backendFd, mutatedRequest.data(), mutatedRequest.size());

        std::array<char, 8192> resBuffer{};
        ssize_t n = 0;
        while ((n = ::read(*backendFd, resBuffer.data(), resBuffer.size())) > 0) {
            ::write(*clientFd, resBuffer.data(), n);
        }
    }
};
```
:::

---

### Обробка сигналів та захист від падіння процесу

У розробці мережевих демонів на C та C++ критично важливо враховувати поведінку сигналів операційної системи. Коли клієнт раптово обриває зв'язок (наприклад, закриває вкладку браузера), а проксі намагається записати байти у закритий сокет за допомогою системного виклику `write()`, ядро надсилає процесу сигнал `SIGPIPE`.

За замовчуванням дія сигналу `SIGPIPE` — негайне аварійне завершення процесу. Якщо програма не заблокує або не проігнорує цей сигнал, один обірваний сокет покладе весь багатопотоковий сервер. Тому будь-який мережевий балансувальник під час старту зобов'язаний виконати виклик `signal(SIGPIPE, SIG_IGN)` або передавати прапорець `MSG_NOSIGNAL` у викликах `send()`.

---

### Моделі потоків та масштабування на ядра процесора

Для досягнення максимальної швидкості сучасні L4 та L7 сервери застосовують модель Worker-per-core:
* На кожне апаратне процесорне ядро створюється окремий незалежний потік із власним екземпляром циклу опитування подій `epoll`.
* Використовується прапорець `SO_REUSEPORT`, який дозволяє кільком незалежним сокетам слухати той самий порт. Ядро Linux самостійно розподіляє вхідні з'єднання `SYN` між ядрами за допомогою 4-tuple хешу, усуваючи конкуренцію за блокування між потоками (Thundering Herd Problem).
* Потоки жорстко прив'язуються до ядер процесора (CPU Affinity / Pinning) за допомогою системного виклику `pthread_setaffinity_np()`, що зберігає гарячість кешів L1/L2 та мінімізує перемикання контексту ядра.

---

### Порівняльний аналіз системних ресурсів

1. **Виділення пам'яті та стан сесії:** L4-сплайсеру достатньо одного спільного буфера на робочий потік або кількох кілобайтів пам'яті на активне з'єднання. Натомість L7-проксі потребує від 32 до 128 КБ на сокет для підтримки структур парсера, таблиць заголовків (HPACK/QPACK), буферів потоків та стану TLS-сесії.
2. **Нуль-копіювання (Zero-Copy):** У середовищі Linux балансувальник L4 може замінити виклики `read`/`write` системним викликом `splice()`. Функція `splice()` перенаправляє сторінки пам'яті між дескрипторами на рівні ядра операційної системи без копіювання байтів у простір користувача, досягаючи максимальної пропускної здатності шини PCI Express. Для L7 нуль-копіювання неможливе, оскільки байти мають бути розшифровані та прочитані процесором для парсингу заголовків.
3. **Обробка зворотного тиску (Backpressure):** Якщо бекенд надсилає дані швидше, ніж клієнт встигає їх вичитувати, L4-проксі зупиняє читання з сокета бекенда (`events &= ~POLLIN`). TCP-стек ядра автоматично заповнює вікно прийому (`TCP Receive Window`) і змушує відправника знизити темп передачі без ризику переповнення пам'яті балансувальника.
4. **Обробка таймаутів та витоку ресурсів:** У реальних системах L4-проксі зобов'язаний відслідковувати час бездіяльності з'єднання (Idle Timeout) через таймери `timerfd` або таймвіли, щоб запобігти вичерпанню дескрипторів файлів сокетами-«мерцями». У L7 додається ще й окремий таймаут на очікування відповіді від бекенда (Request Timeout), що дозволяє повертати клієнту коректний статус `504 Gateway Timeout`.
5. **Профілювання продуктивності:** На тестах синтетичного навантаження з 100 000 одночасних з'єднань L4-міст демонструє у 8–15 разів вищу пропускну здатність (RPS) та у 10 разів меншу затримку (p99 latency) порівняно з L7-маршрутизатором. Проте ця швидкість досягається ціною повної втрати контролю над окремими HTTP-запитами всередині мультиплексованих потоків.
