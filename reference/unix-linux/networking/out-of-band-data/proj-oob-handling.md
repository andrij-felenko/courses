# ⚙️ Практикум: обробка OOB даних за допомогою SIGURG та poll()

Практична реалізація TCP-сервера та клієнта мовами C та C++ для демонстрації обробки позасмугових даних двома методами: асинхронним сигналом `SIGURG` та системним викликом мультиплексування `poll()` із прапорцем `POLLPRI`.

Цей практикум надає вичерпне розібрання розробки мережевого ПЗ, яке підтримує обробку термінових команд без розриву потокового з'єднання. Ми розберемо два підходи: класичний сигнальний метод UNIX (з використанням `sigaction` та `fcntl`) і сучасний подійний підхід (Event Loop) на основі мультиплексування `poll()`.

---

## 1. Архітектурні вимоги та побудова мережевого сервера

При розробці мережевого сервера, що обробляє позасмугові дані, виникає потреба розділити два рівні обробки:
- **Основний потік даних (Data Stream):** Масивний потік байтів, який вичитається додатком послідовно через звичайні виклики `read()` або `recv()`.
- **Терміновий потік команд (Urgent Command):** Поодинокі сигнальні байти, які мають переривати нормальну роботу сервера, обходити чергу очікування й викликати негайну реакцію додатка (наприклад, аварійне скидання стану або скасування поточної транзакції).

Для побудови надійного сервера необхідно забезпечити правильне налаштування сокета на кількох етапах:
1. Створення потокового сокета `SOCK_STREAM` і встановлення опції `SO_REUSEADDR` для швидкого перезапуску сервера без очікування `TIME_WAIT`.
2. Прив'язка сокета до локальної адреси й порту за допомогою `bind()` та переведення в режим прослуховування через `listen()`.
3. Прийняття вхідного підключення клієнта за допомогою `accept()`.
4. Налаштування сигнального обробника `SIGURG` та реєстрація поточного процесу як власника сокета через `fcntl(F_SETOWN, getpid())`.
5. Організація циклу опитування дескриптора за допомогою системного виклику `poll()`, що одночасно контролює прапорці `POLLIN` (звичайні дані) та `POLLPRI` (виняткові термінові дані).

У багатопотокових серверах чи при використанні неблокуючих сокетів `O_NONBLOCK` виникають додаткові крайові випадки. Наприклад, якщо сигнал `SIGURG` надходить у момент, коли сокетний дескриптор опитується викликом `poll()`, обидва механізми (сигнальний обробник і цикл подій) спробують прочитати терміновий байт. Перший виклик `recv(MSG_OOB)` успішно витягне байт з ядра, а другий поверне помилку `EAGAIN` або `EWOULDBLOCK`. Код повинен коректно обробляти цю ситуацію.

---

## 2. Сигнальний підхід: налаштування sigaction та fcntl(F_SETOWN)

Використання сигналу `SIGURG` дозволяє перервати виконання програми незалежно від того, у якій точці коду вона перебуває (наприклад, під час тривалого обчислення або виконання блокуючого системного виклику).

### 2.1. Реєстрація обробника через sigaction

Старий системний виклик `signal()` є застарілим і має невизначену поведінку в різних UNIX-системах. Тому для реєстрації сигнального обробника використовується виклик `sigaction()`.

При налаштуванні структури `struct sigaction` ключовим є встановлення прапорця `SA_RESTART`. Цей прапорець вказує ядру, що якщо сигнал `SIGURG` перервав блокуючий системний виклик (наприклад, `select()` або `poll()`), ядро повинно автоматично відновити його виконання після завершення обробника сигналу, а не повертати помилку `EINTR`.

### 2.2. Правила безпеки в сигнальному обробнику (Async-Signal Safety)

Оскільки сигнальний обробник викликається асинхронно, він не повинен використовувати стандартні бібліотечні функції, які не є асинхронно-безпечними. Зокрема:
- Не можна використовувати `printf()`, `scanf()`, `malloc()`, `free()`.
- Не можна використовувати об'єкти виводу C++ `std::cout`, `std::cerr` або створювати об'єкти в кучі.
- Вивід повідомлень повинен здійснюватися виключно через низькорівневий системний виклик `write(STDOUT_FILENO, ...)`.
- Читання OOB-байта має здійснюватися безпосередньо викликом `recv(fd, &byte, 1, MSG_OOB)`.
- Необхідно зберігати та відновлювати глобальну змінну `errno` (`int saved_errno = errno;`), оскільки виклик `recv()` всередині обробника сигналу може змінити `errno` основного потоку виконання.

---

## 3. Режим мультиплексування: опитування через poll() та POLLPRI

Хоча сигнал `SIGURG` забезпечує миттєву реакцію, у багатопотокових програмах асинхронні сигнали ускладнюють синхронізацію. Альтернативним і більш контрольованим методом є використання системного виклику `poll()`.

### 3.1. Семантика прапорця POLLPRI

При підготовці масиву `struct pollfd` для сокета встановлюються дві події у полі `events`:
- `POLLIN`: Наявність звичайних даних для читання.
- `POLLPRI`: Наявність термінових даних (Out-of-Band / High-Priority Data).

Коли ядро отримує TCP-пакет з увімкненим прапорцем `URG=1`, воно встановлює прапорець `POLLPRI` у полі `revents`. Цикл `poll()` негайно розблоковується, і програма може прочитати OOB-байт викликом `recv(fd, &c, 1, MSG_OOB)`.

### 3.2. Виявлення меж термінового байта через ioctl(SIOCATMARK)

Під час читання звичайних даних із вхідного буфера процес повинен перевіряти, чи не дістався він маркера терміновості. Виклик `ioctl(fd, SIOCATMARK, &atmark)` повертає `1` у змінну `atmark`, якщо наступний байт є терміновим. Це дозволяє додатку зупинити вичитання звичайного потоку та обробити маркер розмежування.

Якщо увімкнено опцію `SO_OOBINLINE`, маркер `SIOCATMARK` вказує на байт безпосередньо у загальному потоці. Якщо `SO_OOBINLINE = 0`, маркер `SIOCATMARK` вказує на точний кордон у потоці sequence numbers, де терміновий байт було витягнуто з потоку.

---

## 4. Повний вихідний код TCP-сервера (C та C++)

Нижче наведено паралельні реалізації повноцінного TCP-сервера мовами C та C++. Реалізація на C++ використовує ідіоматичний підхід RAII для автоматичного управління ресурсами сокетів, обгортки системних викликів із винятками `std::system_error` та контейнери `std::array`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <poll.h>

static int g_client_fd = -1;

// Сигнальний обробник SIGURG
static void handle_sigurg(int sig) {
    (void)sig;
    char oob_byte;
    int saved_errno = errno;

    // Читаємо терміновий байт із прапорцем MSG_OOB
    ssize_t n = recv(g_client_fd, &oob_byte, 1, MSG_OOB);
    if (n > 0) {
        // Використовуємо async-signal-safe системний виклик write
        const char msg[] = "\n[SIGURG Handler] OOB byte received: ";
        write(STDOUT_FILENO, msg, sizeof(msg) - 1);
        write(STDOUT_FILENO, &oob_byte, 1);
        write(STDOUT_FILENO, "\n", 1);
    } else if (n < 0) {
        if (errno == EWOULDBLOCK || errno == EAGAIN) {
            // Байт ще в дорозі або вже прочитаний
        }
    }

    errno = saved_errno;
}

int main(void) {
    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        perror("socket");
        return 1;
    }

    int reuse = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(9099);

    if (bind(listen_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(listen_fd);
        return 1;
    }

    if (listen(listen_fd, 5) < 0) {
        perror("listen");
        close(listen_fd);
        return 1;
    }

    printf("Server listening on port 9099...\n");
    g_client_fd = accept(listen_fd, NULL, NULL);
    if (g_client_fd < 0) {
        perror("accept");
        close(listen_fd);
        return 1;
    }
    printf("Client connected, fd=%d\n", g_client_fd);

    // Налаштовуємо сигнальний обробник SIGURG
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_sigurg;
    sa.sa_flags = SA_RESTART;
    sigaction(SIGURG, &sa, NULL);

    // Призначаємо поточний процес власником сокета
    if (fcntl(g_client_fd, F_SETOWN, getpid()) < 0) {
        perror("fcntl F_SETOWN");
    }

    // Головний цикл з poll()
    struct pollfd fds[1];
    fds[0].fd = g_client_fd;
    fds[0].events = POLLIN | POLLPRI;

    char buf[128];
    while (1) {
        int ret = poll(fds, 1, -1);
        if (ret < 0) {
            if (errno == EINTR) continue;
            perror("poll");
            break;
        }

        // Перевіряємо наявність виняткового стану (OOB data)
        if (fds[0].revents & POLLPRI) {
            printf("[poll] POLLPRI event detected!\n");
            char oob_c;
            ssize_t res = recv(g_client_fd, &oob_c, 1, MSG_OOB);
            if (res > 0) {
                printf("[poll] OOB Byte read via MSG_OOB: '%c'\n", oob_c);
            }
        }

        // Перевіряємо наявність звичайних даних для читання
        if (fds[0].revents & POLLIN) {
            int atmark = 0;
            ioctl(g_client_fd, SIOCATMARK, &atmark);
            if (atmark) {
                printf("[poll] Socket is currently at OOB mark!\n");
            }

            ssize_t n = recv(g_client_fd, buf, sizeof(buf) - 1, 0);
            if (n <= 0) {
                if (n == 0) printf("Client disconnected.\n");
                else perror("recv");
                break;
            }
            buf[n] = '\0';
            printf("Received normal data (%zd bytes): %s", n, buf);
        }
    }

    close(g_client_fd);
    close(listen_fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <array>
#include <string_view>
#include <system_error>
#include <memory>
#include <csignal>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <poll.h>

// RAII обгортка для файлового дескриптора сокета
class SocketFd {
    int fd_{-1};
public:
    explicit SocketFd(int fd = -1) : fd_(fd) {}
    ~SocketFd() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    SocketFd(const SocketFd&) = delete;
    SocketFd& operator=(const SocketFd&) = delete;
    SocketFd(SocketFd&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    SocketFd& operator=(SocketFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

static int g_client_fd = -1;

static void handle_sigurg(int sig) {
    (void)sig;
    char oob_byte = 0;
    int saved_errno = errno;

    ssize_t n = ::recv(g_client_fd, &oob_byte, 1, MSG_OOB);
    if (n > 0) {
        constexpr std::string_view msg{"\n[SIGURG Handler C++] OOB byte received: "};
        ::write(STDOUT_FILENO, msg.data(), msg.size());
        ::write(STDOUT_FILENO, &oob_byte, 1);
        ::write(STDOUT_FILENO, "\n", 1);
    }

    errno = saved_errno;
}

int main() {
    try {
        SocketFd listen_fd{::socket(AF_INET, SOCK_STREAM, 0)};
        if (!listen_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "socket creation failed");
        }

        int reuse = 1;
        if (::setsockopt(listen_fd.get(), SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) < 0) {
            throw std::system_error(errno, std::generic_category(), "setsockopt SO_REUSEADDR failed");
        }

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(9099);

        if (::bind(listen_fd.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            throw std::system_error(errno, std::generic_category(), "bind failed");
        }

        if (::listen(listen_fd.get(), 5) < 0) {
            throw std::system_error(errno, std::generic_category(), "listen failed");
        }

        std::cout << "C++ Server listening on port 9099...\n";

        SocketFd client_fd{::accept(listen_fd.get(), nullptr, nullptr)};
        if (!client_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "accept failed");
        }

        std::cout << "Client connected, fd=" << client_fd.get() << "\n";
        g_client_fd = client_fd.get();

        struct sigaction sa{};
        sa.sa_handler = handle_sigurg;
        sa.sa_flags = SA_RESTART;
        ::sigaction(SIGURG, &sa, nullptr);

        if (::fcntl(client_fd.get(), F_SETOWN, ::getpid()) < 0) {
            throw std::system_error(errno, std::generic_category(), "fcntl F_SETOWN failed");
        }

        std::array<pollfd, 1> fds{};
        fds[0].fd = client_fd.get();
        fds[0].events = POLLIN | POLLPRI;

        std::array<char, 128> buf{};

        while (true) {
            int ret = ::poll(fds.data(), fds.size(), -1);
            if (ret < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "poll failed");
            }

            if (fds[0].revents & POLLPRI) {
                std::cout << "[poll C++] POLLPRI event detected!\n";
                char oob_c = 0;
                ssize_t res = ::recv(client_fd.get(), &oob_c, 1, MSG_OOB);
                if (res > 0) {
                    std::cout << "[poll C++] OOB Byte read: '" << oob_c << "'\n";
                }
            }

            if (fds[0].revents & POLLIN) {
                int atmark = 0;
                if (::ioctl(client_fd.get(), SIOCATMARK, &atmark) == 0 && atmark != 0) {
                    std::cout << "[poll C++] Socket is currently at OOB mark!\n";
                }

                ssize_t n = ::recv(client_fd.get(), buf.data(), buf.size() - 1, 0);
                if (n <= 0) {
                    if (n == 0) std::cout << "Client disconnected.\n";
                    else perror("recv");
                    break;
                }
                buf[n] = '\0';
                std::cout << "Received normal data (" << n << " bytes): " << buf.data();
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Fatal error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

---

## 5. Відправка термінових даних від клієнта

Для тестування роботи сервера розробляється простий клієнт, який спочатку відправляє текстовий рядок `"hello "`, робить коротку затримку, відправляє терміновий байт `'!'` через `send(..., MSG_OOB)` і завершує передачу рядком `"world\n"`.

:::tabs
```c
#include <stdio.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main(void) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(9099);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

    connect(fd, (struct sockaddr*)&addr, sizeof(addr));

    send(fd, "hello ", 6, 0);
    usleep(100000); // 100мс затримка

    // Відправлення позасмугового байта
    send(fd, "!", 1, MSG_OOB);
    usleep(100000);

    send(fd, "world\n", 6, 0);

    close(fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <thread>
#include <chrono>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main() {
    int fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return 1;

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(9099);
    ::inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

    if (::connect(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
        ::close(fd);
        return 1;
    }

    ::send(fd, "hello ", 6, 0);
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    // Відправлення позасмугового байта
    ::send(fd, "!", 1, MSG_OOB);
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    ::send(fd, "world\n", 6, 0);

    ::close(fd);
    return 0;
}
```
:::

---

## 6. Підсумковий аналіз обробки подій

При запуску цього комплексу спостерігається наступна послідовність дій ядра та процесів:

1. Клієнт надсилає `"hello "`. Ядро сервера записує ці байти в `sk_receive_queue`. Серверний виклик `poll()` розблоковується з прапорцем `POLLIN`.
2. Клієнт викликає `send(fd, "!", 1, MSG_OOB)`. Ядро сервера формує сигнал `SIGURG` і одночасно виставляє прапорець `POLLPRI`.
3. Обробник `handle_sigurg()` асинхронно виконує `recv(MSG_OOB)` і друкує повідомлення про отримання байта `'!'`.
4. Якщо виклик `poll()` перебував у стані очікування, він виходить із подіями `POLLPRI` та `POLLIN`.
5. Перевірка `SIOCATMARK` дає змогу точно визначити позицію розмежувача в потоці даних і уникнути злиття керуючих команд із бізнес-даними додатка.

Подібний підхід дає повне розуміння того, як системне програмування на рівні C та C++ управляє винятковими станами сокета в Linux.
