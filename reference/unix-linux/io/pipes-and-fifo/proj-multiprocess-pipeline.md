# ⚙️ Практика: побудова конвеєра процесів та клієнт-серверного FIFO

Практичні реалізації двох класичних патернів міжпроцесної взаємодії: довільного багатоетапного конвеєра процесів та надійного сервера журналювання на основі іменованого каналу.

## Проект 1: Виконавець довільного багатоетапного конвеєра

Утиліта приймає довільний список команд з аргументами й виконує їх у паралельному конвеєрі:
`cmd[0] | cmd[1] | cmd[2] | ... | cmd[N-1]`.

### Архітектура та інваріанти конвеєра

Для зв'язування `N` процесів у ланцюг системі необхідно створити `N - 1` каналів. Кожен проміжний процес `i` (де `0 < i < N - 1`) має свій стандартний ввід (*stdin*, дескриптор `0`), перенаправлений на кінець читання попереднього каналу `pipes[i - 1][0]`, а свій стандартний вихід (*stdout*, дескриптор `1`), перенаправлений на кінець запису наступного каналу `pipes[i][1]`.

Головний інваріант коректної побудови: кожен створений канал повинен бути закритий у батьківському процесі та в усіх дочірніх процесах, окрім того єдиного процесу, який безпосередньо використовує цей кінець для свого стандартного вводу або виводу. Якщо хоча б один кінець запису залишиться відкритим у батька чи сусіднього дочірнього процесу, читач ніколи не отримає ознаку кінця файлу (`EOF`) і весь конвеєр назавжди зависне в очікуванні даних.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <sys/types.h>

/* Структура для опису однієї команди конвеєра */
typedef struct {
    char *const *argv;
} pipeline_stage;

/* Запуск конвеєра з n команд: stage[0] | stage[1] | ... | stage[n-1] */
int run_pipeline(const pipeline_stage *stages, size_t n) {
    if (n == 0) return 0;
    if (n == 1) {
        pid_t pid = fork();
        if (pid == 0) {
            execvp(stages[0].argv[0], stages[0].argv);
            perror("execvp");
            _exit(127);
        }
        int status;
        waitpid(pid, &status, 0);
        return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
    }

    /* Для n команд потрібно (n - 1) каналів */
    int pipes[n - 1][2];
    for (size_t i = 0; i < n - 1; i++) {
        /* Встановлюємо O_CLOEXEC, щоб дескриптори не витікали при execvp */
        if (pipe2(pipes[i], O_CLOEXEC) < 0) {
            perror("pipe2");
            return -1;
        }
    }

    pid_t pids[n];

    for (size_t i = 0; i < n; i++) {
        pids[i] = fork();
        if (pids[i] < 0) {
            perror("fork");
            return -1;
        }

        if (pids[i] == 0) {
            /* Дочірній процес: налаштовуємо вхідний дескриптор */
            if (i > 0) {
                /* Читаємо з попереднього каналу */
                if (dup2(pipes[i - 1][0], STDIN_FILENO) < 0) {
                    perror("dup2 stdin");
                    _exit(1);
                }
            }

            /* Налаштовуємо вихідний дескриптор */
            if (i < n - 1) {
                /* Пишемо в наступний канал */
                if (dup2(pipes[i][1], STDOUT_FILENO) < 0) {
                    perror("dup2 stdout");
                    _exit(1);
                }
            }

            /* Закриваємо всі успадковані дескриптори каналів у дочірньому процесі */
            for (size_t j = 0; j < n - 1; j++) {
                close(pipes[j][0]);
                close(pipes[j][1]);
            }

            /* Заміщуємо образ процесу цільовою програмою */
            execvp(stages[i].argv[0], stages[i].argv);
            perror("execvp");
            _exit(127);
        }
    }

    /* Батьківський процес: ЗАКРИВАЄМО ВСІ КІНЦІ КАНАЛІВ! */
    for (size_t i = 0; i < n - 1; i++) {
        close(pipes[i][0]);
        close(pipes[i][1]);
    }

    /* Очікуємо завершення всіх дочірніх процесів */
    int last_status = 0;
    for (size_t i = 0; i < n; i++) {
        int status;
        waitpid(pids[i], &status, 0);
        if (i == n - 1 && WIFEXITED(status)) {
            last_status = WEXITSTATUS(status);
        }
    }

    return last_status;
}

int main(void) {
    /* Приклад конвеєра: cat /etc/passwd | grep -v nobody | cut -d: -f1 */
    char *cmd0[] = {"cat", "/etc/passwd", NULL};
    char *cmd1[] = {"grep", "-v", "nobody", NULL};
    char *cmd2[] = {"cut", "-d:", "-f1", NULL};

    pipeline_stage stages[] = {
        {cmd0},
        {cmd1},
        {cmd2}
    };

    return run_pipeline(stages, 3);
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <sys/types.h>

// RAII-обгортка над сирим файловим дескриптором
class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_(-1) {}
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
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

struct Stage {
    std::vector<std::string> args;
};

// Виконання ланцюжка процесів із RAII-керуванням дескрипторами
int execute_pipeline(const std::vector<Stage>& stages) {
    if (stages.empty()) return 0;
    const size_t n = stages.size();

    if (n == 1) {
        pid_t pid = ::fork();
        if (pid < 0) throw std::system_error(errno, std::generic_category(), "fork");
        if (pid == 0) {
            std::vector<char*> raw_args;
            for (const auto& a : stages[0].args) raw_args.push_back(const_cast<char*>(a.c_str()));
            raw_args.push_back(nullptr);
            ::execvp(raw_args[0], raw_args.data());
            ::_exit(127);
        }
        int status = 0;
        ::waitpid(pid, &status, 0);
        return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
    }

    // Створюємо канали із прапорцем O_CLOEXEC
    struct PipeEnds {
        UniqueFd read_end;
        UniqueFd write_end;
    };
    std::vector<PipeEnds> pipes(n - 1);

    for (size_t i = 0; i < n - 1; ++i) {
        int fds[2];
        if (::pipe2(fds, O_CLOEXEC) < 0) {
            throw std::system_error(errno, std::generic_category(), "pipe2 failed");
        }
        pipes[i].read_end.reset(fds[0]);
        pipes[i].write_end.reset(fds[1]);
    }

    std::vector<pid_t> pids;
    pids.reserve(n);

    for (size_t i = 0; i < n; ++i) {
        pid_t pid = ::fork();
        if (pid < 0) {
            throw std::system_error(errno, std::generic_category(), "fork failed");
        }

        if (pid == 0) {
            // Дочірній процес: дублюємо вхід
            if (i > 0) {
                if (::dup2(pipes[i - 1].read_end.get(), STDIN_FILENO) < 0) {
                    ::_exit(1);
                }
            }
            // Дублюємо вихід
            if (i < n - 1) {
                if (::dup2(pipes[i].write_end.get(), STDOUT_FILENO) < 0) {
                    ::_exit(1);
                }
            }

            // Закриваємо всі RAII-дескриптори каналів перед exec
            pipes.clear();

            std::vector<char*> raw_args;
            for (const auto& a : stages[i].args) {
                raw_args.push_back(const_cast<char*>(a.c_str()));
            }
            raw_args.push_back(nullptr);

            ::execvp(raw_args[0], raw_args.data());
            ::_exit(127);
        }

        pids.push_back(pid);
    }

    // Батьківський процес закриває всі свої копії каналів через очищення вектору
    pipes.clear();

    int last_status = 0;
    for (size_t i = 0; i < n; ++i) {
        int status = 0;
        ::waitpid(pids[i], &status, 0);
        if (i == n - 1 && WIFEXITED(status)) {
            last_status = WEXITSTATUS(status);
        }
    }

    return last_status;
}

int main() {
    try {
        std::vector<Stage> pipeline = {
            {{"cat", "/etc/passwd"}},
            {{"grep", "-v", "nobody"}},
            {{"cut", "-d:", "-f1"}}
        };

        return execute_pipeline(pipeline);
    } catch (const std::exception& ex) {
        std::cerr << "Pipeline error: " << ex.what() << '\n';
        return 1;
    }
}
```
:::

### Розбір ключових моментів реалізації

1. **Виклик `dup2(oldfd, newfd)`:** Атомарно закриває дескриптор `newfd` (якщо він був відкритий) і призначає йому копію файлового опису `oldfd`. У дочірньому процесі дескриптор `STDIN_FILENO` (0) стає читацьким кінцем попереднього каналу, а `STDOUT_FILENO` (1) — кінцем запису наступного каналу;
2. **Прапорець `O_CLOEXEC` у `pipe2()`:** Гарантує, що під час виконання `execvp()` усі проміжні дескриптори каналів будуть автоматично закриті ядром. Це запобігає витоку відкритих каналів у сторонні системні програми;
3. **Очищення масиву дескрипторів у батьківському процесі:** Одразу після запуску всіх `N` процесів батько викликає `close()` для кожного створеного каналу (або робить `pipes.clear()` у C++). Це критично: єдиними відкритими кінцями запису мають лишатися відповідні дочірні процеси. Щойно попередній етап конвеєра завершується, ядро скидає лічильник письменників до нуля, і наступний етап бачить `EOF`;
4. **Збір статусів через `waitpid()`:** Батьківський процес чекає завершення всіх нащадків у циклі. За угодою командної оболонки статус завершення всього конвеєра визначається статусом останньої команди `stages[n - 1]`.

---

## Проект 2: Асинхронний сервер-реєстратор подій на FIFO

Іменований канал (FIFO) використовується як централізований шлюз для збору логів і команд від багатьох незалежних клієнтських процесів без відкриття мережевих портів.

### Проблема «нескінченного циклу EOF» та її розв'язання

Якщо сервер відкриває FIFO у звичайному режимі читання `open(FIFO_PATH, O_RDONLY)`, виникає критичний дефект: коли перший клієнт завершує відправку повідомлення й закриває свій дескриптор, у системі лишається 0 відкритих письменників. У цей момент виклик `read()` на сервері повертає `0` (EOF). Якщо сервер просто спробує повторити `read()`, він знову отримає `0`, увійде в нескінченний цикл зі 100% завантаженням процесора і не засне.

Стандартне ідіоматичне розв'язання в Unix полягає у відкритті FIFO сервером у режимі читання й запису: `open(FIFO_PATH, O_RDWR)`. Оскільки сам дескриптор сервера утримує відкритий кінець запису, лічильник письменників `pipe->writers` у ядрі ніколи не падає нижче одиниці. Коли черговий клієнт від'єднується, виклик `read()` не повертає `0`, а спокійно блокується в черзі очікування ядра до появи нового клієнтського повідомлення.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <signal.h>
#include <errno.h>
#include <time.h>

#define FIFO_PATH "/tmp/app_events.fifo"
#define MAX_MSG_SIZE 512 /* Значно менше PIPE_BUF (4096), тому запис строго атомарний */

/* Запуск демона-читача логів */
void run_server(void) {
    /* Створюємо FIFO з правами rw-rw-rw- */
    unlink(FIFO_PATH);
    if (mkfifo(FIFO_PATH, 0666) < 0 && errno != EEXIST) {
        perror("mkfifo");
        exit(EXIT_FAILURE);
    }

    printf("[Сервер] FIFO створено: %s\n", FIFO_PATH);

    /* Трюк O_RDWR: утримуємо лічильник письменників >= 1, щоб read не крутився в 0 (EOF) */
    int fifo_fd = open(FIFO_PATH, O_RDWR);
    if (fifo_fd < 0) {
        perror("open server FIFO");
        exit(EXIT_FAILURE);
    }

    printf("[Сервер] Очікування повідомлень від клієнтів...\n");

    char buffer[MAX_MSG_SIZE];
    while (1) {
        ssize_t bytes_read = read(fifo_fd, buffer, sizeof(buffer) - 1);
        if (bytes_read > 0) {
            buffer[bytes_read] = '\0';
            printf("[Отримано подію] %s", buffer);
            fflush(stdout);
        } else if (bytes_read < 0) {
            if (errno == EINTR) continue;
            perror("read error");
            break;
        }
    }

    close(fifo_fd);
    unlink(FIFO_PATH);
}

/* Відправка події від клієнта */
int send_log_event(const char *service_name, const char *message) {
    /* Відкриваємо з O_NONBLOCK: якщо сервер не слухає, дістанемо ENXIO негайно */
    int fd = open(FIFO_PATH, O_WRONLY | O_NONBLOCK);
    if (fd < 0) {
        if (errno == ENXIO) {
            fprintf(stderr, "[Клієнт %s] Помилка: Сервер логів не запущений (немає читача).\n", service_name);
        } else {
            perror("open client FIFO");
        }
        return -1;
    }

    char record[MAX_MSG_SIZE];
    time_t now = time(NULL);
    struct tm tm_buf;
    localtime_r(&now, &tm_buf);

    char time_str[32];
    strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", &tm_buf);

    int len = snprintf(record, sizeof(record), "[%s] [%s (PID:%d)]: %s\n",
                       time_str, service_name, getpid(), message);

    if (len > 0) {
        /* Ігноруємо SIGPIPE, щоб процес не загинув при раптовому закритті сервера */
        struct sigaction sa;
        memset(&sa, 0, sizeof(sa));
        sa.sa_handler = SIG_IGN;
        sigaction(SIGPIPE, &sa, NULL);

        ssize_t written = write(fd, record, (size_t)len);
        if (written < 0) {
            if (errno == EPIPE) {
                fprintf(stderr, "[Клієнт %s] Помилка: Канал зламано (EPIPE).\n", service_name);
            } else {
                perror("write client");
            }
            close(fd);
            return -1;
        }
    }

    close(fd);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc > 1 && strcmp(argv[1], "server") == 0) {
        run_server();
    } else if (argc > 3 && strcmp(argv[1], "client") == 0) {
        send_log_event(argv[2], argv[3]);
    } else {
        printf("Використання:\n");
        printf("  %s server                  — запустити фоновий збирач логів\n", argv[0]);
        printf("  %s client <сервіс> <текст> — надіслати подію в іменований канал\n", argv[0]);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <format>
#include <memory>
#include <system_error>
#include <array>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <signal.h>

namespace {
constexpr std::string_view FIFO_PATH = "/tmp/app_events.fifo";
constexpr size_t MAX_MSG_SIZE = 512;

class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_(-1) {}
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) reset(other.release());
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
        if (fd_ >= 0) ::close(fd_);
        fd_ = new_fd;
    }

private:
    int fd_;
};

void run_server() {
    ::unlink(FIFO_PATH.data());
    if (::mkfifo(FIFO_PATH.data(), 0666) < 0 && errno != EEXIST) {
        throw std::system_error(errno, std::generic_category(), "mkfifo failed");
    }

    std::cout << "[Сервер C++] FIFO створено: " << FIFO_PATH << '\n';

    // Відкриваємо O_RDWR, щоб read() не завершувався з 0 (EOF) при від'єднанні клієнтів
    UniqueFd server_fd(::open(FIFO_PATH.data(), O_RDWR));
    if (!server_fd.valid()) {
        throw std::system_error(errno, std::generic_category(), "open FIFO failed");
    }

    std::cout << "[Сервер C++] Очікування подій...\n";

    std::array<char, MAX_MSG_SIZE> buffer{};
    while (true) {
        ssize_t bytes_read = ::read(server_fd.get(), buffer.data(), buffer.size() - 1);
        if (bytes_read > 0) {
            buffer[bytes_read] = '\0';
            std::cout << "[Подія] " << buffer.data();
            std::cout.flush();
        } else if (bytes_read < 0) {
            if (errno == EINTR) continue;
            std::cerr << "Помилка читання з FIFO: " << std::strerror(errno) << '\n';
            break;
        }
    }

    ::unlink(FIFO_PATH.data());
}

void send_event(std::string_view service_name, std::string_view message) {
    // Відкриваємо неблокуюче на запис
    UniqueFd client_fd(::open(FIFO_PATH.data(), O_WRONLY | O_NONBLOCK));
    if (!client_fd.valid()) {
        if (errno == ENXIO) {
            std::cerr << "[Клієнт] Помилка: Сервер логів не активний (немає читача).\n";
            return;
        }
        throw std::system_error(errno, std::generic_category(), "open client FIFO");
    }

    // Ігноруємо SIGPIPE локально
    struct sigaction sa{};
    sa.sa_handler = SIG_IGN;
    ::sigaction(SIGPIPE, &sa, nullptr);

    auto now = std::chrono::system_clock::now();
    std::string record = std::format("[{:%Y-%m-%d %H:%M:%S}] [{}] (PID:{}): {}\n",
                                     now, service_name, ::getpid(), message);

    if (record.size() > MAX_MSG_SIZE) {
        record.resize(MAX_MSG_SIZE - 1);
        record += '\n';
    }

    ssize_t written = ::write(client_fd.get(), record.data(), record.size());
    if (written < 0) {
        if (errno == EPIPE) {
            std::cerr << "[Клієнт] Канал зламано (EPIPE).\n";
        } else {
            std::cerr << "Помилка запису в FIFO: " << std::strerror(errno) << '\n';
        }
    }
}
} // namespace

int main(int argc, char* argv[]) {
    try {
        if (argc > 1 && std::string_view(argv[1]) == "server") {
            run_server();
        } else if (argc > 3 && std::string_view(argv[1]) == "client") {
            send_event(argv[2], argv[3]);
        } else {
            std::cout << "Використання:\n"
                      << "  " << argv[0] << " server                  — запустити сервер\n"
                      << "  " << argv[0] << " client <сервіс> <текст> — надіслати подію\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

### Особливості клієнтського відправника

1. **Неблокуюче підключення через `O_WRONLY | O_NONBLOCK`:** Якщо демон-сервер впав або ще не запустився, клієнтський процес не повинен зависати всередині `open()`. Завдяки `O_NONBLOCK` ядро негайно повертає код помилки `ENXIO`, дозволяючи клієнту записати повідомлення у резервний локальний файл або вивести попередження;
2. **Гарантія атомарності через обмеження розміру:** Розмір записуваного рядка жорстко обмежено константою `MAX_MSG_SIZE = 512` байтів. Оскільки це значення значно менше за `PIPE_BUF` (4096 байтів), ядро гарантує атомарний запис: навіть якщо сотні клієнтів одночасно виконують `write()`, їхні повідомлення записуються неподільними блоками;
3. **Захист від сигналу `SIGPIPE`:** Клієнтський код локально вимикає реакцію на `SIGPIPE` через `sigaction(SIGPIPE, &sa, NULL)`. Якщо сервер раптово зупиниться посеред передачі, клієнт не помре від сигналу, а отримає статус `-1` з `errno == EPIPE` і зможе продовжити виконання основної бізнес-логіки.

---

## Тестування та верифікація поведінки в терміналі

Перевірити коректність роботи реалізованих механізмів можна безпосередньо за допомогою стандартних утиліт командного рядка:

### 1. Перевірка паралельного запису багатьох клієнтів у FIFO
Запустимо сервер у фоновому терміналі, після чого згенеруємо одночасний потік від 50 паралельних процесів:
```sh
# Термінал 1: запуск сервера
$ ./fifo_logger server

# Термінал 2: масовий запуск клієнтів
$ for i in $(seq 1 50); do
    ./fifo_logger client "AuthWorker-$i" "Користувач $i успішно авторизувався" &
  done
$ wait
```
Жоден рядок у журналі сервера не буде обрізаним чи перемішаним, оскільки розмір кожного запису (близько 80 байтів) гарантовано менший за системний ліміт атомарності `PIPE_BUF`.

### 2. Діагностика дескрипторів конвеєра через `/proc`
Щоб переконатися, що виконавець конвеєра не залишає витоків дескрипторів (*file descriptor leaks*), запустимо важкий конвеєр і перевіримо вміст каталогу дескрипторів:
```sh
$ ls -l /proc/$(pgrep -f run_pipeline)/fd/
```
У списку дескрипторів мають бути присутні лише `0` (stdin), `1` (stdout), `2` (stderr). Усі проміжні дескриптори `pipes[i]` повинні бути повністю закриті ядром.

### 3. Поведінка планувальника під навантаженням
Під час передачі великих обсягів даних через конвеєр ядро Linux динамічно передає квант часу процесора між читачем і письменником. Щойно письменник заповнює буфер каналу (64 КіБ), планувальник переводить його в стан `TASK_INTERRUPTIBLE` і безпосередньо передає керування читачеві (*yield*), мінімізуючи накладні витрати на чергу планування.
