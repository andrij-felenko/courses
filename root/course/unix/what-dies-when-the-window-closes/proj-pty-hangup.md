# ⚙️ Демонстрація розриву PTY та перехоплення SIGHUP

Цей практичний проект демонструє програмне створення псевдотермінала (PTY), запуск дочірнього процесу у виділеному сеансі та моделювання закриття вікна емулятора шляхом закриття дескриптора майстра. Без практичного відтворення важко наочно побачити асинхронний ланцюг: у який момент ядро генерує сигнал `SIGHUP`, як поводиться стандартне введення-виведення при переході термінала в стан *hung up* та чому звичайне ігнорування сигналу не рятує від системної помилки `EIO`.

## Задача та архітектура симулятора

Програма повинна вирішити такі системні інженерні завдання:
1. Відкрити мастер-дескриптор псевдотермінала через мультиплексор `/dev/ptmx` (виклик `posix_openpt`), налаштувати права доступу (`grantpt`), розблокувати слейв (`unlockpt`) та отримати шлях до пристрою `/dev/pts/N` у файловій системі (`ptsname`).
2. Породити дочірній процес через системний виклик `fork()`.
3. У дочірньому процесі створити новий сеанс (`setsid()`), відкрити слейв-дескриптор, призначити його керівним терміналом (`TIOCSCTTY`) і перенаправити стандартні потоки `0, 1, 2` на цей термінал через `dup2()`.
4. Встановити сигнальний обробник сигналу `SIGHUP` через структуру `struct sigaction` з атомарним прапорцем типу `sig_atomic_t` (або `std::sig_atomic_t`).
5. У батьківському процесі імітувати роботу емулятора термінала, почекати 1 секунду та закрити мастер-дескриптор `close(master_fd)`, емулюючи закриття графічного вікна користувачем або розрив мережевої сесії SSH.
6. Зафіксувати поведінку дочірнього процесу: надходження сигналу `SIGHUP`, поведінку виклику `read()` (повернення 0, тобто `EOF`) та виклику `write()` (повернення `-1` з `errno == EIO`).

## Реалізація симулятора

Нижче наведено повністю робочий код симулятора мовами C та C++. Обидва варіанти реалізують повний протокол створення термінального сеансу, обробки сигналів та діагностики помилок введення-виведення.

:::tabs
```c
#define _XOPEN_SOURCE 600
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/wait.h>

static volatile sig_atomic_t g_hup_received = 0;

static void hup_handler(int sig) {
    (void)sig;
    g_hup_received = 1;
}

static void run_child(const char *slave_path) {
    /* 1. Створюємо новий сеанс: дочірній процес стає лідером сесії */
    if (setsid() < 0) {
        perror("setsid");
        exit(EXIT_FAILURE);
    }

    /* 2. Відкриваємо слейв PTY */
    int sfd = open(slave_path, O_RDWR);
    if (sfd < 0) {
        perror("open slave");
        exit(EXIT_FAILURE);
    }

    /* 3. Призначаємо відкритий PTY slave керівним терміналом сеансу */
    if (ioctl(sfd, TIOCSCTTY, 0) < 0) {
        perror("ioctl TIOCSCTTY");
        exit(EXIT_FAILURE);
    }

    /* 4. Перенаправляємо стандартні дескриптори на PTY slave */
    dup2(sfd, STDIN_FILENO);
    dup2(sfd, STDOUT_FILENO);
    dup2(sfd, STDERR_FILENO);
    if (sfd > STDERR_FILENO) {
        close(sfd);
    }

    /* 5. Встановлюємо обробник сигналу SIGHUP */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = hup_handler;
    sigemptyset(&sa.sa_mask);
    if (sigaction(SIGHUP, &sa, NULL) < 0) {
        exit(EXIT_FAILURE);
    }

    /* Логування у файл для незалежної фіксації подій */
    FILE *log = fopen("/tmp/pty_child.log", "w");
    if (!log) {
        exit(EXIT_FAILURE);
    }
    setvbuf(log, NULL, _IOLBF, 0);

    fprintf(log, "[CHILD %d] Сеанс створено. Очікування подій...\n", getpid());

    /* Цикл очікування розриву зв'язку */
    for (int i = 0; i < 30; ++i) {
        usleep(100000); /* 100 мс */

        if (g_hup_received) {
            fprintf(log, "[CHILD %d] Отримано сигнал SIGHUP від ядра!\n", getpid());
            
            /* Перевіряємо стан читання з термінала після hangup */
            char buf[64];
            int flags = fcntl(STDIN_FILENO, F_GETFL, 0);
            fcntl(STDIN_FILENO, F_SETFL, flags | O_NONBLOCK);
            ssize_t nr = read(STDIN_FILENO, buf, sizeof(buf));
            fprintf(log, "[CHILD %d] Спроба read(0): повернуто %zd (errno=%d: %s)\n",
                    getpid(), nr, errno, strerror(errno));

            /* Перевіряємо стан запису у завислий термінал */
            ssize_t nw = write(STDOUT_FILENO, "test\n", 5);
            fprintf(log, "[CHILD %d] Спроба write(1): повернуто %zd (errno=%d: %s)\n",
                    getpid(), nw, errno, strerror(errno));

            fprintf(log, "[CHILD %d] Завершення роботи після розриву.\n", getpid());
            fclose(log);
            exit(EXIT_SUCCESS);
        }
    }

    fprintf(log, "[CHILD %d] Таймаут очікування сигналу.\n", getpid());
    fclose(log);
    exit(EXIT_SUCCESS);
}

int main(void) {
    /* 1. Відкриваємо мастер-дескриптор псевдотермінала */
    int mfd = posix_openpt(O_RDWR | O_NOCTTY);
    if (mfd < 0) {
        perror("posix_openpt");
        return EXIT_FAILURE;
    }

    if (grantpt(mfd) < 0 || unlockpt(mfd) < 0) {
        perror("grantpt/unlockpt");
        close(mfd);
        return EXIT_FAILURE;
    }

    char *sname = ptsname(mfd);
    if (!sname) {
        perror("ptsname");
        close(mfd);
        return EXIT_FAILURE;
    }

    printf("[PARENT] PTY Master відкрито (fd=%d). Slave шлях: %s\n", mfd, sname);

    pid_t child_pid = fork();
    if (child_pid < 0) {
        perror("fork");
        close(mfd);
        return EXIT_FAILURE;
    }

    if (child_pid == 0) {
        close(mfd); /* Дитина не повинна утримувати мастер-дескриптор */
        run_child(sname);
    }

    /* Батьківський процес: емулюємо роботу вікна емулятора протягом 1 секунди */
    printf("[PARENT] Дочірній процес запущено (PID=%d). Вікно активне 1 секунду...\n", child_pid);
    sleep(1);

    /* Імітуємо закриття вікна користувачем: закриваємо мастер-дескриптор */
    printf("[PARENT] Закриваємо master_fd (%d), моделюючи клік на [X] вікна...\n", mfd);
    close(mfd);

    /* Очікуємо на завершення дочірнього процесу */
    int status = 0;
    waitpid(child_pid, &status, 0);

    if (WIFEXITED(status)) {
        printf("[PARENT] Дочірній процес завершився зі статусом %d.\n", WEXITSTATUS(status));
    } else if (WIFSIGNALED(status)) {
        printf("[PARENT] Дочірній процес загинув від сигналу %d (%s).\n",
               WTERMSIG(status), strsignal(WTERMSIG(status)));
    }

    /* Виводимо протокол подій дочірнього процесу */
    printf("\n--- Протокол дочірнього процесу (/tmp/pty_child.log) ---\n");
    FILE *log = fopen("/tmp/pty_child.log", "r");
    if (log) {
        char line[256];
        while (fgets(line, sizeof(line), log)) {
            fputs(line, stdout);
        }
        fclose(log);
        unlink("/tmp/pty_child.log");
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <memory>
#include <chrono>
#include <thread>
#include <system_error>
#include <csignal>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/wait.h>

namespace pty_demo {

static volatile std::sig_atomic_t g_hup_flag = 0;

void signal_handler(int sig) noexcept {
    if (sig == SIGHUP) {
        g_hup_flag = 1;
    }
}

class FileDescriptor {
public:
    explicit FileDescriptor(int fd = -1) noexcept : fd_(fd) {}
    ~FileDescriptor() noexcept { reset(); }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    void reset() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = -1;
        }
    }

    int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

private:
    int fd_;
};

void run_child(std::string_view slave_path) {
    if (::setsid() < 0) {
        std::exit(EXIT_FAILURE);
    }

    FileDescriptor sfd(::open(slave_path.data(), O_RDWR));
    if (!sfd.valid()) {
        std::exit(EXIT_FAILURE);
    }

    if (::ioctl(sfd.get(), TIOCSCTTY, 0) < 0) {
        std::exit(EXIT_FAILURE);
    }

    ::dup2(sfd.get(), STDIN_FILENO);
    ::dup2(sfd.get(), STDOUT_FILENO);
    ::dup2(sfd.get(), STDERR_FILENO);

    struct sigaction sa{};
    sa.sa_handler = signal_handler;
    ::sigemptyset(&sa.sa_mask);
    ::sigaction(SIGHUP, &sa, nullptr);

    std::ofstream log_stream("/tmp/pty_child.log", std::ios::out | std::ios::trunc);
    if (!log_stream.is_open()) {
        std::exit(EXIT_FAILURE);
    }

    const pid_t my_pid = ::getpid();
    log_stream << "[CHILD " << my_pid << "] Сеанс створено. Очікування подій...\n" << std::flush;

    for (int i = 0; i < 30; ++i) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));

        if (g_hup_flag) {
            log_stream << "[CHILD " << my_pid << "] Отримано сигнал SIGHUP від ядра!\n";

            int flags = ::fcntl(STDIN_FILENO, F_GETFL, 0);
            ::fcntl(STDIN_FILENO, F_SETFL, flags | O_NONBLOCK);
            std::array<char, 64> buffer{};
            const ssize_t nr = ::read(STDIN_FILENO, buffer.data(), buffer.size());
            log_stream << "[CHILD " << my_pid << "] Спроба read(0): повернуто " << nr
                       << " (errno=" << errno << ": " << std::strerror(errno) << ")\n";

            constexpr std::string_view msg = "test\n";
            const ssize_t nw = ::write(STDOUT_FILENO, msg.data(), msg.size());
            log_stream << "[CHILD " << my_pid << "] Спроба write(1): повернуто " << nw
                       << " (errno=" << errno << ": " << std::strerror(errno) << ")\n";

            log_stream << "[CHILD " << my_pid << "] Завершення роботи після розриву.\n" << std::flush;
            std::exit(EXIT_SUCCESS);
        }
    }

    log_stream << "[CHILD " << my_pid << "] Таймаут очікування.\n" << std::flush;
    std::exit(EXIT_SUCCESS);
}

} // namespace pty_demo

int main() {
    pty_demo::FileDescriptor mfd(::posix_openpt(O_RDWR | O_NOCTTY));
    if (!mfd.valid()) {
        std::cerr << "Помилка відкриття posix_openpt\n";
        return EXIT_FAILURE;
    }

    if (::grantpt(mfd.get()) < 0 || ::unlockpt(mfd.get()) < 0) {
        std::cerr << "Помилка grantpt / unlockpt\n";
        return EXIT_FAILURE;
    }

    const char* pts_name = ::ptsname(mfd.get());
    if (!pts_name) {
        std::cerr << "Помилка отримання імені ptsname\n";
        return EXIT_FAILURE;
    }

    std::cout << "[PARENT] PTY Master відкрито (fd=" << mfd.get() << "). Slave: " << pts_name << '\n';

    const pid_t child_pid = ::fork();
    if (child_pid < 0) {
        std::cerr << "Помилка fork\n";
        return EXIT_FAILURE;
    }

    if (child_pid == 0) {
        mfd.reset();
        pty_demo::run_child(pts_name);
    }

    std::cout << "[PARENT] Дочірній процес запущено (PID=" << child_pid << "). Вікно відкрите...\n";
    std::this_thread::sleep_for(std::chrono::seconds(1));

    std::cout << "[PARENT] Закриваємо master_fd (" << mfd.get() << "), емулюючи закриття вікна...\n";
    mfd.reset();

    int status = 0;
    ::waitpid(child_pid, &status, 0);

    if (WIFEXITED(status)) {
        std::cout << "[PARENT] Дочірній процес завершився із кодом " << WEXITSTATUS(status) << ".\n";
    } else if (WIFSIGNALED(status)) {
        std::cout << "[PARENT] Дочірній процес вбито сигналом " << WTERMSIG(status) << ".\n";
    }

    std::cout << "\n--- Протокол дочірнього процесу (/tmp/pty_child.log) ---\n";
    std::ifstream log_file("/tmp/pty_child.log");
    if (log_file.is_open()) {
        std::string line;
        while (std::getline(log_file, line)) {
            std::cout << line << '\n';
        }
        log_file.close();
        ::unlink("/tmp/pty_child.log");
    }

    return EXIT_SUCCESS;
}
```
:::

## Аналіз системних результатів та механіки ядра

Під час запуску скомпільованої програми формується послідовний протокол подій операційної системи:

1. **Фаза створення сеансу та прив'язки TTY**:
   * Батьківський процес викликає функцію `posix_openpt()`, яка відкриває мастер-сторону псевдотермінала `/dev/ptmx` та повертає файловий дескриптор.
   * Виклики `grantpt()` та `unlockpt()` змінюють права доступу до вузла `/dev/pts/N` у віртуальній системі `devpts` та знімають внутрішній замок блокування ядра.
   * Дочірній процес викликає системний виклик `setsid()`, утворюючи повністю ізольовану сесію. Виклик `ioctl(TIOCSCTTY, 0)` закріплює відкритий слейв як керівний термінал цієї сесії.
2. **Фаза емуляції розриву зв'язку**:
   * Через 1 секунду батьківський процес виконує системний виклик `close(mfd)`.
   * Підсистема ядра `drivers/tty/pty.c` фіксує, що кількість активних дескрипторів майстра зменшилася до нуля. Викликається функція ядра `tty_vhangup()`.
   * Ядро перевіряє сесію, закріплену за цим терміналом, і асинхронно відправляє сигнал `SIGHUP` лідеру сеансу (дочірньому процесу).
3. **Фаза поведінки стандартних потоків введення-виведення**:
   * Обробник сигналу миттєво переводить атомарний прапорець `g_hup_received` у значення `1`.
   * Неблокуючий виклик `read(0, ...)` на читання зі стандартного введення повертає `0` (`EOF`). Будь-який інтерактивний цикл читання (`while (read(...) > 0)`) сприймає це як завершення потоку вхідних даних і виходить.
   * Виклик `write(1, ...)` на запис у стандартне виведення повертає `-1` зі встановленням системної помилки `errno = 5` (`EIO` — Input/output error). Це пряме свідчення того, що кінцевий пристрій термінала перейшов у стан незворотного зависання.

## Особливості реалізації мовами C та C++

Порівняння двох вкладок демонструє ключові відмінності в управлінні системними ресурсами:

* **Керування дескрипторами (RAII)**: у версії C++ дескриптор псевдотермінала обгорнуто в клас `FileDescriptor`. Його деструктор автоматично викликає `::close()` при виході зі scope або виникненні винятку. Це гарантує відсутність витоку дескрипторів майстра навіть у разі аварійного завершення. У версії C закриття `close(mfd)` доводиться викликати вручну в кожній гілці помилки.
* **Асинхронно-сигнальна безпека**: в обох мовах обробник сигналу виконує лише одну атомарну операцію запису в глобальну змінну `sig_atomic_t` (або `std::sig_atomic_t`). Виклик будь-яких функцій виведення (`printf`, `std::cout`, `malloc`) всередині обробника сигналу суворо заборонено через небезпеку взаємних блокувань (*deadlocks*).
* **Потоки введення-виведення**: замість використання буферизованих об'єктів `stdio` дочірній процес записує діагностичний протокол у файл через неблокуючі виклики та прямі системні операції `read`/`write`, що усуває вплив бібліотечної буферизації.

## Інженерні пастки при роботі з PTY

Під час реалізації емуляторів терміналів або демонізації процесів часто припускаються таких критичних помилок:

* **Витік master_fd у дочірньому процесі**: якщо після виклику `fork()` дочірній процес не закриє успадкований `master_fd`, лічильник посилань ядра на мастер PTY не впаде до 0 при закритті батька. У результаті ядро ніколи не згенерує сигнал `SIGHUP`, і термінал не перейде в стан розриву, утримуючи фантомний відкритий пристрій у пам'яті.
* **Нескінченний цикл зі 100% утилізацією CPU**: якщо програма опитує стандартне введення без чіткої обробки повернення значення `0` як ознаки кінця файлу (`EOF`), перехід термінала в стан `hung up` перетворює цикл читання на нескінченний холостий прогін, що завантажує процесорне ядро на повну потужність.
* **Падіння на необробленій помилці EIO**: утиліта `disown` рятує фоновий процес від сигналу `SIGHUP`, проте залишає його стандартні дескриптори прив'язаними до мертвого PTY slave. Перший же виклик `printf()` або `std::cout` після закриття вікна призводить до помилки `EIO`, яка може спричинити фатальне переривання виконання програми через паніку бібліотеки виведення.
* **Зомбі-процеси при відсутності waitpid**: якщо батьківський процес емулятора не збирає статус нащадків через `waitpid()` або не встановлює обробник `SIGCHLD`, завершені дочірні процеси залишаються в системній таблиці у стані `Z` (*Zombie*), блокуючи вивільнення ідентифікаторів PID.
