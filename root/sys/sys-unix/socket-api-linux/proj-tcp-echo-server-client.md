# ⚙️ Практикум: повноцінний TCP-сервер та клієнт мовами C та C++

Створення промислового мережевого сервера вимагає від розробника глибинного розуміння механіки системних викликів, обробки виняткових ситуацій та керування ресурсами операційної системи. На відміну від навчальних прикладів, реальний сервер мусить коректно обробляти переривання системними сигналами, не втрачати файлові дескриптори при створенні дочірніх процесів, підтримувати миттєвий перезапуск після зупинки та запобігати витокам пам'яті у системі.

У цьому практичному матеріалі наведено повну, працездатну реалізацію високонавантаженого TCP Echo-сервера та відповідного TCP-клієнта мовами C та C++. Реалізація демонструє правильне налаштування опцій сокета `SO_REUSEADDR`, атомарне створення дескрипторів через системний виклик `accept4()`, надійні цикли читання й запису з обробкою помилок `EINTR` та `EAGAIN`, а також ідіоматичний C++20 підхід на основі концепції RAII (Resource Acquisition Is Initialization).

---

## 1. Архітектурні виклики та принципи побудови системних серверів

Перед розбором вихідного коду необхідно сформулювати ключові вимоги до архітектури мережевого сервера у системі Linux. Кожна з цих вимог диктується конкретним механізмом ядра та поведінкою файлових дескрипторів VFS.

### Безпечне керування файловими дескрипторами (RAII та прапорець `SOCK_CLOEXEC`)

У системі Linux кожен новий сокет, створений викликом `socket()` або витягнутий з черги `accept()`, отримує цілочисельний індекс у таблиці файлових дескрипторів процесу (`struct files_struct`). Якщо сервер обробляє тисячі підключень на секунду й не закриває дескриптори у разі виникнення помилок (наприклад, при розриві мережевого кабелю віддаленим клієнтом), процес швидко вичерпає ліміт `RLIMIT_NOFILE`. Це призведе до того, що всі наступні виклики `socket()` чи `accept()` повертатимуть помилку `EMFILE` (Too many open files), повністю паралізувавши роботу сервера.

У мові C розробник змушений вручну контролювати кожен шлях виконання, викликаючи `close(fd)` на кожній гілці обробки помилок. У мові C++ це завдання розв'язується через концепцію RAII: об'єкт `Socket` утримує дескриптор у приватному полі, а його деструктор `~Socket()` автоматично викликає `::close(fd_)` при виході з області видимості, незалежно від того, чи завершилася функція звичайно, чи вичерпалася через повернення помилки або генерацію винятку.

Додатковим ризиком є успадкування файлових дескрипторів при викликах `fork()` та `execve()`. Якщо серверний процес створює дочірній процес (наприклад, для виконання сторонньої утиліти через `execve()`), дочірній процес успадковує всі відкриті дескриптори батька. Якщо слухаючий сокет залишається відкритим у дочірньому процесі, порт буде заблоковано навіть після зупинки головного сервера. Прапорець `SOCK_CLOEXEC`, переданий безпосередньо у `socket()` та `accept4()`, змушує ядро атомарно закривати дескриптор при зміні образу процесу через `execve()`.

### Усунення затримки перезапуску та опція `SO_REUSEADDR`

За замовчуванням при закритті TCP-з'єднання сокет сервера переходить у стан `TIME_WAIT`, який триває у ядрі 60 секунд (два інтервали MSL). Якщо розробник зупинить сервер (наприклад, під час оновлення конфігурації) і спробує негайно перезапустити його на тому самому порту, системний виклик `bind()` поверне помилку `EADDRINUSE` (Address already in use).

Налаштування сокетної опції `SO_REUSEADDR` через `setsockopt()` дозволяє ядру прив'язувати слухаючий сокет до порту, навіть якщо на ньому перебувають сокети у стані `TIME_WAIT`. Це критично важливо для забезпечення безперервної доступності служб при автоматичних перезапусках.

### Обробка асинхронних сигналів та помилка `EINTR`

Під час виконання блокувальних системних викликів (`accept()`, `read()`, `write()`) потік сервера перебуває у стані очікування у ядрі. Якщо у цей момент процесу надходить асинхронний сигнал (наприклад, `SIGINT`, `SIGTERM` або `SIGALRM`), ядро перериває виконання системного виклику, викликає обробник сигналу та повертає з системного виклику значення `-1`, встановлюючи `errno` в `EINTR` (Interrupted system call).

Наївна програма при отриманні `-1` сприйме це як критичне падіння сокета й закриє з'єднання. Коректний сервер повинен перевіряти стан `errno == EINTR` і продовжувати виконання виклику у циклі `while`.

### Гарантія повної відправки буфера

Системний виклик `write(fd, buf, len)` не гарантує, що ядро негайно відправить усі `len` байтів. Якщо внутрішньоядерний буфер передачі сокета (`sk_write_queue`) заповнений, ядро запише лише таку кількість байтів, яка вміщається у буфер, і поверне це число. Програма повинна запускати внутрішній цикл запису, зміщуючи вказівник буфера на фактично відправлену кількість байтів до повного спорожнення вихідного буфера.

---

## 2. Реалізація TCP Echo-сервера

Нижче наведено вихідні тексти TCP Echo-сервера мовами C та C++. Сервер слухає порт 8080, приймає підключення клієнтів, зчитує вхідні байти та повертає їх назад відправнику.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <signal.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define PORT 8080
#define BUFFER_SIZE 1024
#define BACKLOG 128

static volatile sig_atomic_t g_running = 1;

static void handle_signal(int sig) {
    (void)sig;
    g_running = 0;
}

int main(void) {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_signal;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        perror("socket error");
        return EXIT_FAILURE;
    }

    int optval = 1;
    if (setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(optval)) < 0) {
        perror("setsockopt SO_REUSEADDR");
        close(listen_fd);
        return EXIT_FAILURE;
    }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    if (bind(listen_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("bind error");
        close(listen_fd);
        return EXIT_FAILURE;
    }

    if (listen(listen_fd, BACKLOG) < 0) {
        perror("listen error");
        close(listen_fd);
        return EXIT_FAILURE;
    }

    printf("C TCP Echo Server listening on port %d...\n", PORT);

    while (g_running) {
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);

        int client_fd = accept4(listen_fd, (struct sockaddr *)&client_addr,
                                &client_len, SOCK_CLOEXEC);
        if (client_fd < 0) {
            if (errno == EINTR) {
                continue;
            }
            perror("accept4 error");
            break;
        }

        char ip_str[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client_addr.sin_addr, ip_str, sizeof(ip_str));
        printf("Accepted connection from %s:%d (fd=%d)\n",
               ip_str, ntohs(client_addr.sin_port), client_fd);

        char buffer[BUFFER_SIZE];
        ssize_t bytes_read;
        while ((bytes_read = read(client_fd, buffer, sizeof(buffer))) > 0) {
            ssize_t bytes_written = 0;
            while (bytes_written < bytes_read) {
                ssize_t res = write(client_fd, buffer + bytes_written,
                                    (size_t)(bytes_read - bytes_written));
                if (res <= 0) {
                    if (res < 0 && errno == EINTR) continue;
                    break;
                }
                bytes_written += res;
            }
        }

        printf("Closing connection (fd=%d)\n", client_fd);
        close(client_fd);
    }

    printf("Shutting down server...\n");
    close(listen_fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <vector>
#include <system_error>
#include <memory>
#include <array>
#include <csignal>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

class Socket {
private:
    int fd_{-1};

public:
    explicit Socket(int fd) : fd_(fd) {}
    ~Socket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    Socket(const Socket&) = delete;
    Socket& operator=(const Socket&) = delete;

    Socket(Socket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    Socket& operator=(Socket&& other) noexcept {
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

static volatile std::sig_atomic_t g_running = 1;

void signal_handler(int) {
    g_running = 0;
}

int main() {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    int raw_fd = ::socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (raw_fd < 0) {
        throw std::system_error(errno, std::generic_category(), "socket creation failed");
    }
    Socket server_sock(raw_fd);

    int optval = 1;
    if (::setsockopt(server_sock.get(), SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(optval)) < 0) {
        throw std::system_error(errno, std::generic_category(), "setsockopt SO_REUSEADDR failed");
    }

    sockaddr_in server_addr{};
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(8080);

    if (::bind(server_sock.get(), reinterpret_cast<sockaddr*>(&server_addr), sizeof(server_addr)) < 0) {
        throw std::system_error(errno, std::generic_category(), "bind failed");
    }

    if (::listen(server_sock.get(), 128) < 0) {
        throw std::system_error(errno, std::generic_category(), "listen failed");
    }

    std::cout << "C++ Idiomatic TCP Echo Server listening on port 8080...\n";

    while (g_running) {
        sockaddr_in client_addr{};
        socklen_t client_len = sizeof(client_addr);

        int client_raw_fd = ::accept4(server_sock.get(), reinterpret_cast<sockaddr*>(&client_addr),
                                      &client_len, SOCK_CLOEXEC);
        if (client_raw_fd < 0) {
            if (errno == EINTR) continue;
            break;
        }

        Socket client_sock(client_raw_fd);
        std::array<char, INET_ADDRSTRLEN> ip_str{};
        ::inet_ntop(AF_INET, &client_addr.sin_addr, ip_str.data(), ip_str.size());

        std::cout << "Client connected from " << ip_str.data() << ":" << ntohs(client_addr.sin_port)
                  << " (RAII fd=" << client_sock.get() << ")\n";

        std::array<char, 1024> buffer{};
        ssize_t bytes_read = 0;
        while ((bytes_read = ::read(client_sock.get(), buffer.data(), buffer.size())) > 0) {
            ssize_t bytes_written = 0;
            while (bytes_written < bytes_read) {
                ssize_t res = ::write(client_sock.get(), buffer.data() + bytes_written,
                                      static_cast<size_t>(bytes_read - bytes_written));
                if (res <= 0) {
                    if (res < 0 && errno == EINTR) continue;
                    break;
                }
                bytes_written += res;
            }
        }

        std::cout << "Closing client socket via RAII destructor\n";
    }

    std::cout << "Server graceful shutdown complete.\n";
    return 0;
}
```
:::

---

## 3. Детальний аналіз ключових рішень коду

### Робота із мережевими структурами адрес

У системному виклику `bind()` використовується обнулення структури `sockaddr_in` за допомогою `memset()` або ініціалізації `{}` у C++. Це позбавляє від сміттєвих байтів у вирівнювальних полях `sin_zero`, які можуть призвести до помилок при порівнянні адрес у ядрі.

Макрос `htons(8080)` (host to network short) перетворює порт із порядку байтів хоста (Little-Endian на архітектурах x86_64) у мережевий порядок байтів (Big-Endian). Це необхідно для правильної інтерпретації портів мережевими маршрутизаторами та ядром.

### Застосування `accept4()` із прапорцем `SOCK_CLOEXEC`

Замість застарілого системного виклику `accept()` у коді застосовано виклик `accept4()`. Передача прапорця `SOCK_CLOEXEC` гарантує, що новий файловий дескриптор клієнта створюється у ядрі з вже встановленим прапорцем `FD_CLOEXEC`. Це позбавляє від необхідності викликати `fcntl(fd, F_SETFD, FD_CLOEXEC)`, усуваючи будь-яке вікно для гонитви між потоками.

### RAII-обгортка `Socket` у C++

Клас `Socket` у реалізації C++20 впроваджує семантику виключного володіння дескриптором (Move-only type). Конструктор копіювання `Socket(const Socket&)` та оператор присвоєння копіюванням вилучені через `= delete`. Це унеможливлює випадкове копіювання об'єкта сокета, яке призвело б до подвійного закриття одного й того самого дескриптора через `close()` (Double Free / Double Close vulnerability).

Конструктор переміщення `Socket(Socket&&)` передає володіння дескриптором іншому об'єкту, обнуляючи `fd_` у джерелі (`other.fd_ = -1`). Деструктор `~Socket()` перевіряє `fd_ >= 0` і виконує `::close(fd_)`, звільняючи ресурс ядра при знищенні об'єкта.

---

## 4. Реалізація TCP-клієнта

Нижче наведено вихідний код TCP-клієнта, який підключається до сервера `127.0.0.1:8080`, надсилає текстове повідомлення та зчитує луна-відповідь сервера.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define SERVER_IP "127.0.0.1"
#define PORT 8080
#define MESSAGE "Hello, Linux Socket API!"

int main(void) {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket failed");
        return EXIT_FAILURE;
    }

    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);

    if (inet_pton(AF_INET, SERVER_IP, &serv_addr.sin_addr) <= 0) {
        perror("inet_pton invalid address");
        close(sockfd);
        return EXIT_FAILURE;
    }

    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("connect failed");
        close(sockfd);
        return EXIT_FAILURE;
    }

    printf("Connected to server %s:%d\n", SERVER_IP, PORT);

    ssize_t sent = write(sockfd, MESSAGE, strlen(MESSAGE));
    if (sent < 0) {
        perror("write failed");
        close(sockfd);
        return EXIT_FAILURE;
    }

    char response[1024];
    ssize_t received = read(sockfd, response, sizeof(response) - 1);
    if (received > 0) {
        response[received] = '\0';
        printf("Received echo: %s\n", response);
    }

    close(sockfd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <array>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

class SocketWrapper {
    int fd_{-1};
public:
    explicit SocketWrapper(int fd) : fd_(fd) {}
    ~SocketWrapper() { if (fd_ >= 0) ::close(fd_); }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

int main() {
    int raw_fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (raw_fd < 0) {
        throw std::system_error(errno, std::generic_category(), "socket failed");
    }
    SocketWrapper client_sock(raw_fd);

    sockaddr_in serv_addr{};
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(8080);

    if (::inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0) {
        throw std::system_error(errno, std::generic_category(), "invalid IP address");
    }

    if (::connect(client_sock.get(), reinterpret_cast<sockaddr*>(&serv_addr), sizeof(serv_addr)) < 0) {
        throw std::system_error(errno, std::generic_category(), "connect failed");
    }

    std::cout << "Connected to 127.0.0.1:8080\n";

    constexpr std::string_view msg = "Hello from C++20 Socket Client!";
    if (::write(client_sock.get(), msg.data(), msg.size()) < 0) {
        throw std::system_error(errno, std::generic_category(), "write failed");
    }

    std::array<char, 1024> response{};
    ssize_t bytes_read = ::read(client_sock.get(), response.data(), response.size() - 1);
    if (bytes_read > 0) {
        response[bytes_read] = '\0';
        std::cout << "Received echo: " << response.data() << "\n";
    }

    return 0;
}
```
:::

---

## 5. Збірка, запуск та інспектування утилітами Linux

Для компіляції серверів та клієнтів використовуйте сучасні компілятори `gcc` або `clang` із прапорцями оптимізації та вичерпних попереджень:

```bash
# Компіляція C-версії з суворим контролем стандартів
gcc -Wall -Wextra -Wpedantic -O2 echo_server.c -o echo_server_c
gcc -Wall -Wextra -Wpedantic -O2 echo_client.c -o echo_client_c

# Компіляція C++20-версії
g++ -std=c++20 -Wall -Wextra -Wpedantic -O2 echo_server.cpp -o echo_server_cpp
g++ -std=c++20 -Wall -Wextra -Wpedantic -O2 echo_client.cpp -o echo_client_cpp
```

### Спостереження за допомогою `ss` та `strace`

Запустіть сервер у першому терміналі, а у другому проінспектуйте його стан у ядрі:

```bash
# Перевірка сокета у стані LISTEN
ss -tulpn | grep 8080
# Вивід: LISTEN 0 128 0.0.0.0:8080 0.0.0.0:* users:(("echo_server_c",pid=1234,fd=3))

# Трасування послідовності системних викликів під час підключення клієнта
strace -e trace=socket,bind,listen,accept4,read,write ./echo_server_c
```

Під час роботи `strace` ви чітко побачите, як системний виклик `socket()` повертає `fd=3`, `bind()` прив'язує його до порту 8080, `listen()` встановлює `backlog=128`, а `accept4()` блокується до надходження з'єднання, після чого повертає новий дескриптор `fd=4` із прапорцем `SOCK_CLOEXEC`.
