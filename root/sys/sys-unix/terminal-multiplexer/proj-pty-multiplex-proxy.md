# ⚙️ Спрощений мультиплексор-детачер: передача PTY через UNIX-сокет

Щоб зрозуміти внутрішню механіку мультиплексора термінала, корисно зняти високорівневі шари складності (парсинг ANSI-графіки, поділ вікон на панелі, конфігураційні файли) і подивитися на фундаментальний інженерний кістяк: як запустити процес у псевдотерміналі всередині фонового демона і пересилати його ввід та вивід через локальний сокет домену UNIX клієнту, дозволяючи клієнту будь-коли від'єднатися без зупинки дочірнього процесу.

Нижче наведено повноцінний робочий приклад мінімального проксі-детачера на мовах C та C++.

## Системна архітектура мінімального детачера

Програма реалізує два взаємодоповнюючі режими роботи:

1. **Режим сервера (`--server`):**
   - Відкриває нову пару псевдотерміналів (`master`/`slave`) за допомогою системної функції `forkpty()`.
   - Створює дочірній процес через виклик `fork()`.
   - Дочірній процес створює новий сеанс (`setsid()`), призначає підлеглий кінець PTY своїми дескрипторами `0` (`stdin`), `1` (`stdout`), `2` (`stderr`) та запускає командну оболонку `/bin/sh`.
   - Батьківський процес створює сокет домену UNIX (`AF_UNIX`) у файлі `/tmp/miniplex.sock`, переходить у фоновий режим і в циклі опитування дескрипторів `poll()` ретранслює дані між підключеним клієнтом та дескриптором `master_fd` псевдотермінала.
   - Якщо клієнт відключається (через натискання комбінації клавіш або обрив з'єднання), сервер закриває клієнтський дескриптор, але не чіпає дочірній процес і терпляче чекає на наступне клієнтське з'єднання через виклик `accept()`.

2. **Режим клієнта (`--client`):**
   - Переводить поточний термінал користувача у сирий режим (*raw mode*), вимикаючи канонічну буферизацію рядків (`ICANON`), локальне відлуння (`ECHO`) та обробку сигнальних комбінацій (`ISIG`).
   - Підключається до локального сокета `/tmp/miniplex.sock`.
   - У неблокуючому циклі передає байти з дескриптора `STDIN_FILENO` у сокет, а байти з сокета — у `STDOUT_FILENO`.
   - Перехоплює керівний байт від'єднання (байт `0x1d`, що відповідає комбінації `Ctrl+]`). Отримавши цей байт, клієнт повертає початкові налаштування термінала за допомогою `tcsetattr()` та виходить, залишаючи сервер і оболонку працювати у фоні.

## Реалізація на C та ідіоматичному C++

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <pty.h>
#include <termios.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/wait.h>
#include <poll.h>

#define SOCKET_PATH "/tmp/miniplex.sock"
#define DETACH_KEY 0x1d /* Ctrl+] */
#define BUFFER_SIZE 4096

static struct termios orig_termios;
static int raw_mode_active = 0;

static void restore_terminal(void) {
    if (raw_mode_active) {
        tcsetattr(STDIN_FILENO, TCSAFLUSH, &orig_termios);
        raw_mode_active = 0;
    }
}

static int enable_raw_mode(void) {
    if (tcgetattr(STDIN_FILENO, &orig_termios) < 0) {
        return -1;
    }
    struct termios raw = orig_termios;
    raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
    raw.c_oflag &= ~(OPOST);
    raw.c_cflag |= (CS8);
    raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
    raw.c_cc[VMIN] = 1;
    raw.c_cc[VTIME] = 0;
    if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) < 0) {
        return -1;
    }
    raw_mode_active = 1;
    atexit(restore_terminal);
    return 0;
}

static int forward_data(int src_fd, int dst_fd, int check_detach) {
    char buf[BUFFER_SIZE];
    ssize_t n = read(src_fd, buf, sizeof(buf));
    if (n <= 0) {
        return -1;
    }
    if (check_detach) {
        for (ssize_t i = 0; i < n; ++i) {
            if ((unsigned char)buf[i] == DETACH_KEY) {
                return 1; /* Сигнал від'єднання */
            }
        }
    }
    ssize_t written = 0;
    while (written < n) {
        ssize_t res = write(dst_fd, buf + written, (size_t)(n - written));
        if (res < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        written += res;
    }
    return 0;
}

static void run_server(void) {
    int master_fd;
    pid_t pid = forkpty(&master_fd, NULL, NULL, NULL);
    if (pid < 0) {
        perror("forkpty");
        exit(EXIT_FAILURE);
    }
    if (pid == 0) {
        execl("/bin/sh", "sh", NULL);
        _exit(EXIT_FAILURE);
    }

    unlink(SOCKET_PATH);
    int listen_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path) - 1);

    if (bind(listen_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        exit(EXIT_FAILURE);
    }
    if (listen(listen_fd, 1) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    /* Фоновий цикл сервера */
    while (1) {
        int client_fd = accept(listen_fd, NULL, NULL);
        if (client_fd < 0) {
            if (errno == EINTR) continue;
            break;
        }

        struct pollfd fds[2];
        fds[0].fd = master_fd;
        fds[0].events = POLLIN;
        fds[1].fd = client_fd;
        fds[1].events = POLLIN;

        int active = 1;
        while (active) {
            int ret = poll(fds, 2, -1);
            if (ret < 0) {
                if (errno == EINTR) continue;
                break;
            }

            if (fds[0].revents & (POLLIN | POLLERR | POLLHUP)) {
                if (forward_data(master_fd, client_fd, 0) < 0) {
                    /* Дочірній процес завершився */
                    close(client_fd);
                    close(master_fd);
                    close(listen_fd);
                    unlink(SOCKET_PATH);
                    waitpid(pid, NULL, 0);
                    return;
                }
            }

            if (fds[1].revents & (POLLIN | POLLERR | POLLHUP)) {
                int status = forward_data(client_fd, master_fd, 0);
                if (status < 0) {
                    /* Клієнт від'єднався */
                    active = 0;
                }
            }
        }
        close(client_fd);
    }
    close(master_fd);
    close(listen_fd);
    unlink(SOCKET_PATH);
}

static void run_client(void) {
    int sock_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (sock_fd < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path) - 1);

    if (connect(sock_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("connect to /tmp/miniplex.sock");
        close(sock_fd);
        exit(EXIT_FAILURE);
    }

    if (enable_raw_mode() < 0) {
        perror("enable_raw_mode");
        close(sock_fd);
        exit(EXIT_FAILURE);
    }

    struct pollfd fds[2];
    fds[0].fd = STDIN_FILENO;
    fds[0].events = POLLIN;
    fds[1].fd = sock_fd;
    fds[1].events = POLLIN;

    while (1) {
        int ret = poll(fds, 2, -1);
        if (ret < 0) {
            if (errno == EINTR) continue;
            break;
        }

        if (fds[0].revents & POLLIN) {
            int status = forward_data(STDIN_FILENO, sock_fd, 1);
            if (status == 1) {
                /* Натиснуто комбінацію від'єднання Ctrl+] */
                break;
            }
            if (status < 0) break;
        }

        if (fds[1].revents & (POLLIN | POLLERR | POLLHUP)) {
            if (forward_data(sock_fd, STDOUT_FILENO, 0) < 0) {
                break;
            }
        }
    }

    restore_terminal();
    close(sock_fd);
}

int main(int argc, char *argv[]) {
    if (argc > 1 && strcmp(argv[1], "--server") == 0) {
        run_server();
    } else if (argc > 1 && strcmp(argv[1], "--client") == 0) {
        run_client();
    } else {
        fprintf(stderr, "Ужиток: %s --server | --client\n", argv[0]);
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <pty.h>
#include <termios.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/wait.h>
#include <poll.h>

namespace miniplex {

constexpr std::string_view kSocketPath = "/tmp/miniplex.sock";
constexpr char kDetachKey = 0x1d; // Ctrl+]
constexpr size_t kBufferSize = 4096;

enum class ErrorCode {
    PtyCreationFailed,
    ForkFailed,
    SocketCreationFailed,
    BindFailed,
    ListenFailed,
    ConnectFailed,
    TerminalConfigFailed,
    IoError
};

std::error_code make_error_code(ErrorCode e) {
    return {static_cast<int>(e), std::generic_category()};
}

class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_{-1} {}
    explicit UniqueFd(int fd) noexcept : fd_{fd} {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_{other.release()} {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        reset(other.release());
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_;
};

class RawTerminalGuard {
public:
    static std::expected<RawTerminalGuard, ErrorCode> create() {
        struct termios orig;
        if (::tcgetattr(STDIN_FILENO, &orig) < 0) {
            return std::unexpected(ErrorCode::TerminalConfigFailed);
        }
        struct termios raw = orig;
        raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
        raw.c_oflag &= ~(OPOST);
        raw.c_cflag |= (CS8);
        raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
        raw.c_cc[VMIN] = 1;
        raw.c_cc[VTIME] = 0;

        if (::tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) < 0) {
            return std::unexpected(ErrorCode::TerminalConfigFailed);
        }
        return RawTerminalGuard(orig);
    }

    ~RawTerminalGuard() {
        if (active_) {
            ::tcsetattr(STDIN_FILENO, TCSAFLUSH, &orig_termios_);
        }
    }

    RawTerminalGuard(const RawTerminalGuard&) = delete;
    RawTerminalGuard& operator=(const RawTerminalGuard&) = delete;
    RawTerminalGuard(RawTerminalGuard&& other) noexcept
        : orig_termios_{other.orig_termios_}, active_{other.active_} {
        other.active_ = false;
    }

private:
    explicit RawTerminalGuard(const struct termios& orig)
        : orig_termios_{orig}, active_{true} {}

    struct termios orig_termios_{};
    bool active_{false};
};

enum class TransferStatus {
    Ok,
    Detached,
    Closed,
    Error
};

TransferStatus forward_stream(int src_fd, int dst_fd, bool check_detach) {
    std::vector<char> buffer(kBufferSize);
    ssize_t n = ::read(src_fd, buffer.data(), buffer.size());
    if (n <= 0) {
        return (n == 0) ? TransferStatus::Closed : TransferStatus::Error;
    }

    std::span<const char> bytes(buffer.data(), static_cast<size_t>(n));
    if (check_detach) {
        for (char b : bytes) {
            if (b == kDetachKey) {
                return TransferStatus::Detached;
            }
        }
    }

    size_t written = 0;
    while (written < bytes.size()) {
        ssize_t res = ::write(dst_fd, bytes.data() + written, bytes.size() - written);
        if (res < 0) {
            if (errno == EINTR) continue;
            return TransferStatus::Error;
        }
        written += static_cast<size_t>(res);
    }
    return TransferStatus::Ok;
}

std::expected<void, ErrorCode> run_server() {
    int raw_master_fd = -1;
    pid_t pid = ::forkpty(&raw_master_fd, nullptr, nullptr, nullptr);
    if (pid < 0) {
        return std::unexpected(ErrorCode::ForkFailed);
    }
    if (pid == 0) {
        ::execl("/bin/sh", "sh", nullptr);
        ::_exit(127);
    }

    UniqueFd master_fd(raw_master_fd);
    ::unlink(kSocketPath.data());

    UniqueFd listen_fd(::socket(AF_UNIX, SOCK_STREAM, 0));
    if (!listen_fd.valid()) {
        return std::unexpected(ErrorCode::SocketCreationFailed);
    }

    struct sockaddr_un addr{};
    addr.sun_family = AF_UNIX;
    std::strncpy(addr.sun_path, kSocketPath.data(), sizeof(addr.sun_path) - 1);

    if (::bind(listen_fd.get(), reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
        return std::unexpected(ErrorCode::BindFailed);
    }
    if (::listen(listen_fd.get(), 1) < 0) {
        return std::unexpected(ErrorCode::ListenFailed);
    }

    while (true) {
        UniqueFd client_fd(::accept(listen_fd.get(), nullptr, nullptr));
        if (!client_fd.valid()) {
            if (errno == EINTR) continue;
            break;
        }

        std::vector<struct pollfd> fds(2);
        fds[0].fd = master_fd.get();
        fds[0].events = POLLIN;
        fds[1].fd = client_fd.get();
        fds[1].events = POLLIN;

        bool client_active = true;
        while (client_active) {
            int ret = ::poll(fds.data(), fds.size(), -1);
            if (ret < 0) {
                if (errno == EINTR) continue;
                break;
            }

            if (fds[0].revents & (POLLIN | POLLERR | POLLHUP)) {
                auto status = forward_stream(master_fd.get(), client_fd.get(), false);
                if (status != TransferStatus::Ok) {
                    ::unlink(kSocketPath.data());
                    ::waitpid(pid, nullptr, 0);
                    return {};
                }
            }

            if (fds[1].revents & (POLLIN | POLLERR | POLLHUP)) {
                auto status = forward_stream(client_fd.get(), master_fd.get(), false);
                if (status != TransferStatus::Ok) {
                    client_active = false;
                }
            }
        }
    }
    ::unlink(kSocketPath.data());
    return {};
}

std::expected<void, ErrorCode> run_client() {
    UniqueFd sock_fd(::socket(AF_UNIX, SOCK_STREAM, 0));
    if (!sock_fd.valid()) {
        return std::unexpected(ErrorCode::SocketCreationFailed);
    }

    struct sockaddr_un addr{};
    addr.sun_family = AF_UNIX;
    std::strncpy(addr.sun_path, kSocketPath.data(), sizeof(addr.sun_path) - 1);

    if (::connect(sock_fd.get(), reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
        return std::unexpected(ErrorCode::ConnectFailed);
    }

    auto term_guard = RawTerminalGuard::create();
    if (!term_guard) {
        return std::unexpected(term_guard.error());
    }

    std::vector<struct pollfd> fds(2);
    fds[0].fd = STDIN_FILENO;
    fds[0].events = POLLIN;
    fds[1].fd = sock_fd.get();
    fds[1].events = POLLIN;

    while (true) {
        int ret = ::poll(fds.data(), fds.size(), -1);
        if (ret < 0) {
            if (errno == EINTR) continue;
            break;
        }

        if (fds[0].revents & POLLIN) {
            auto status = forward_stream(STDIN_FILENO, sock_fd.get(), true);
            if (status == TransferStatus::Detached) {
                break;
            }
            if (status != TransferStatus::Ok) break;
        }

        if (fds[1].revents & (POLLIN | POLLERR | POLLHUP)) {
            auto status = forward_stream(sock_fd.get(), STDOUT_FILENO, false);
            if (status != TransferStatus::Ok) break;
        }
    }
    return {};
}

} // namespace miniplex

int main(int argc, char* argv[]) {
    if (argc > 1 && std::string_view(argv[1]) == "--server") {
        if (auto res = miniplex::run_server(); !res) {
            std::cerr << "Помилка сервера miniplex\n";
            return 1;
        }
    } else if (argc > 1 && std::string_view(argv[1]) == "--client") {
        if (auto res = miniplex::run_client(); !res) {
            std::cerr << "Помилка клієнта miniplex\n";
            return 1;
        }
    } else {
        std::cerr << "Ужиток: " << argv[0] << " --server | --client\n";
        return 1;
    }
    return 0;
}
```
:::

## Інженерний розбір та системні підводні камені

Розглянемо детальніше ключові системні механізми, які забезпечують надійну роботу проксі-детачера на рівні ядра Linux:

### 1. Механізм ізоляції сеансу у forkpty

Функція `forkpty()` є системною обгорткою бібліотеки `libutil`, яка інкапсулює п'ять обов'язкових послідовних кроків:
1. Відкриття файлу клонування псевдотерміналів `/dev/ptmx` для отримання `master_fd`;
2. Виклик `grantpt()` та `unlockpt()` для налаштування прав доступу та розблокування підлеглого пристрою `/dev/pts/N`;
3. Виклик `fork()` для створення дочірнього процесу;
4. У дочірньому процесі: виклик `setsid()` для відриву від успадкованого сеансу та створення нового;
5. Відкриття `/dev/pts/N`, прив'язка його як керівного термінала через `ioctl(slave_fd, TIOCSCTTY, 0)` та дублювання дескриптора на `0`, `1`, `2` через `dup2()`.

Оскільки дескриптор `master_fd` залишається постійно відкритим у серверному процесі, закриття клієнтського сокета ніколи не спричиняє надсилання сигналу `SIGHUP` дочірньому процесу на slave-кінці.

### 2. Налаштування термінала: канонічний проти сирого режиму

Якщо запустити клієнт без модифікації структури `termios`, операційна система продовжить застосовувати стандартну лінійну дисципліну термінала:
- Прапорець `ICANON` накопичує байти в буфері ядра до натискання клавіші `Enter`. Клієнт не зможе передавати окремі натискання клавіш (наприклад, стрілки або автодоповнення по `Tab`).
- Прапорець `ECHO` викликає подвійне відображення символів: локальний термінал друкуватиме символ при натисканні, а потім ще раз відображатиме відлуння, отримане від віддаленої оболонки.
- Прапорець `ISIG` змушує ядро перехоплювати натискання `Ctrl+C` (`0x03`) і `Ctrl+Z` (`0x1a`) та надсилати сигнали самому клієнтському процесу, замість того щоб передати ці байти через сокет віддаленій програмі.
- Прапорці `VMIN = 1` та `VTIME = 0` задають блокуюче читання рівно від одного доступного байта без штучних затримок таймера.

Вимкнення цих прапорців у функції `enable_raw_mode()` перетворює клієнт на прозорий байтовий міст між клавіатурою та сокетом.

### 3. Гарантії безпеки дескрипторів та RAII

У версії на C++ життєвий цикл файлових дескрипторів та налаштувань термінала контролюється за принципом RAII (*Resource Acquisition Is Initialization*):
- Клас `UniqueFd` автоматично закриває файловий дескриптор у деструкторі при виході з області видимості, що унеможливлює витік дескрипторів сокетів чи PTY при помилках.
- Клас `RawTerminalGuard` гарантує відновлення структури `termios` за будь-яких умов виходу з функції `run_client()` (включно з обробкою винятків чи передчасним поверненням). Без цього термінал користувача залишився б у «зламаному» стані.

### 4. Неблокуюча передача даних та дренаж буферів

У наведеному навчальному прикладі виклик `poll()` відстежує готовність дескрипторів до читання. У реальних мультиплексорах (наприклад, `tmux`) цикл розширюється буферизацією виводу на базі кільцевих черг (*ring buffers*). Якщо дочірня програма виводить гігабайти тексту швидше, ніж клієнт встигає їх відображати через повільну мережу, сервер призупиняє читання з `master_fd` (backpressure), що автоматично блокує виклик `write()` у дочірньому процесі через заповнення буфера PTY ядра.

Також слід враховувати перехоплення сигналів `EINTR`: системні виклики `read()`, `write()` та `poll()` можуть бути перервані надходженням сигналу операційної системи. Код зобов'язаний перевіряти `errno == EINTR` і повторювати виклик замість аварійного завершення.

### 5. Практична перевірка роботи

Для збірки та тестування програми виконайте такі кроки у двох вікнах термінала:

```sh
# Збірка прикладу C:
gcc -O2 -Wall -Wextra miniplex.c -lutil -o miniplex

# Або збірка прикладу C++:
g++ -std=c++23 -O2 -Wall -Wextra miniplex.cpp -lutil -o miniplex_cpp

# Запуск фонового сервера:
./miniplex --server &

# Підключення клієнта:
./miniplex --client
```

Усередині запущеної оболонки можна ввести команду на кшталт `top` або запустити нескінченний лічильник `while true; do date; sleep 1; done`. Натискання комбінації `Ctrl+]` безпечно повертає користувача в батьківську консоль. Повторний запуск `./miniplex --client` негайно відновлює зв'язок із працюючим лічильником, демонструючи повну персистентність сеансу.
