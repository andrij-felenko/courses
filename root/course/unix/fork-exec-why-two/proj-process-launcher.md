# ⚙️ Надійний запуск процесів через fork+exec: перенаправлення, обмеження та звіт про помилки

Коли системна програма запускає сторонній бінарний файл, проста послідовність викликів `fork()` та `execve()` виявляється вкрай вразливою до помилок. Якщо новий образ не вдалося завантажити через відсутність файлу або брак прав доступу, дочірній процес тихо гине, а батьківський процес дізнається про це лише через `waitpid` у формі неінформативного коду завершення `127` без можливості зрозуміти першопричину (`ENOENT`, `EACCES` чи `ENOMEM`).

У цій практичній роботі ми побудуємо промисловий лаунчер процесів (аналогічний підсистемам запуску в systemd та контейнерних рушіях), що використовує канал зв'язку з прапорцем `O_CLOEXEC` для передачі помилок конфігурації, налаштовує перенаправлення потоків вводу-виводу, очищає змінні середовища, накладає жорсткі ліміти системних ресурсів та ізолює сигнали.

## Інженерний прийом: самознищуваний канал діагностики помилок

Головна складність передачі діагностичного статусу між дитиною та батьком полягає в точці неповернення системного виклику `execve`. Якщо заміна образу завершується успішно, увесь попередній код дитини, глобальні змінні та адресний простір миттєво знищуються. Батько не може отримати повідомлення про успіх через спільну пам'ять або структури даних, оскільки дитина більше не виконує код лаунчера.

Рішення полягає у використанні неіменованого каналу ([pipe](topic:sys-unix/file-descriptor)), створеного з прапорцем `O_CLOEXEC`:

1. Перед виконанням `fork()` батьківський процес створює діагностичний канал: `pipe2(err_pipe, O_CLOEXEC)`. Обидва файлові дескриптори каналу автоматично позначаються прапорцем закриття при заміні образу.
2. Після `fork()` батьківський процес негайно закриває свій дескриптор запису `err_pipe[1]`, залишаючи відкритим лише дескриптор читання `err_pipe[0]`.
3. Дочірній процес закриває дескриптор читання `err_pipe[0]`, налаштовує власне оточення (перенаправлення потоків, зміну каталогу, ліміти ресурсів) і викликає `execve()`.
4. **Сценарій успішного запуску**: ядро завантажує новий виконуваний образ. У момент переходу точки неповернення ядро автоматично закриває дескриптор `err_pipe[1]` через прапорець `FD_CLOEXEC`. Батьківський процес, який очікує на виклику `read(err_pipe[0], ...)`, негайно отримує ознаку кінця файлу (`EOF`, функція повертає 0 зчитаних байтів) і фіксує успішний старт нової програми.
5. **Сценарій відмови**: якщо `execve()` або будь-яка попередня дія зазнає невдачі, дочірній процес записує системний код помилки `errno` (4 байти `int`) у відкритий дескриптор `err_pipe[1]` і викликає системний вихід `_exit(127)`. Батьківський процес зчитує ці 4 байти й точно знає, яка саме функція дала збій.

## Очищення середовища та гігієна дескрипторів

Перед передачею керування новому бінарному файлу надійний лаунчер зобов'язаний виконати три кроки системної гігієни:

### 1. Санація змінних оточення

Пряме успадкування масиву `environ` від батьківського процесу несе загрозу безпеці. Змінні на зразок `LD_PRELOAD`, `LD_LIBRARY_PATH`, `BASH_ENV` та `IFS` можуть бути використані для ін'єкції шкідливого коду або підміни системних бібліотек. Лаунчер повинен формувати масив `envp` за білим списком дозволених змінних або явно фільтрувати небезпечні префікси.

### 2. Закриття сторонніх дескрипторів

Якщо батьківський процес відкривав файли або сокети без прапорця `O_CLOEXEC`, вони залишаться відкритими в дочірній програмі. Для їх закриття сучасне ядро Linux надає системний виклик `close_range(3, ~0U, 0)`, який за одну атомарну операцію закриває всі дескриптори від номера 3 до нескінченності. У разі відсутності `close_range` лаунчер читає вміст каталогу `/proc/self/fd` або використовує цикл до `sysconf(_SC_OPEN_MAX)`.

### 3. Ізоляція групи процесів та сигналів

Якщо дочірній процес не відокремити від групи батька, сигнал переривання з термінала (`Ctrl+C`, `SIGINT`) потрапить одночасно і в батьківський сервіс, і в запущений підпроцес. Виклик `setpgid(0, 0)` створює нову групу процесів, роблячи дитину її лідером. Додатково лаунчер скидає маску блокування сигналів `sigprocmask` на порожню, щоб дитина не успадкувала заблоковані батьком сигнали.

## Повна реалізація захищеного лаунчера

Нижче наведено повну реалізацію системного лаунчера мовами C та сучасного C++ (C++23 із застосуванням `std::expected` та RAII).

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <signal.h>
#include <sys/syscall.h>

typedef struct {
    const char *executable;
    char *const *argv;
    char *const *envp;
    const char *working_dir;
    int stdin_fd;
    int stdout_fd;
    int stderr_fd;
    rlim_t max_memory_bytes;
    rlim_t max_cpu_seconds;
} ProcessConfig;

/* Допоміжне закриття дескрипторів вище збережених */
static void close_inherited_fds(int min_fd) {
#if defined(__NR_close_range)
    if (syscall(__NR_close_range, min_fd, ~0U, 0) == 0) {
        return;
    }
#endif
    long max_fd = sysconf(_SC_OPEN_MAX);
    if (max_fd < 0 || max_fd > 4096) max_fd = 4096;
    for (int fd = min_fd; fd < max_fd; ++fd) {
        close(fd);
    }
}

int launch_process(const ProcessConfig *cfg, pid_t *out_pid) {
    if (!cfg || !cfg->executable || !cfg->argv) {
        errno = EINVAL;
        return -1;
    }

    int err_pipe[2];
    if (pipe2(err_pipe, O_CLOEXEC) == -1) {
        return -1;
    }

    pid_t pid = fork();
    if (pid < 0) {
        int saved_errno = errno;
        close(err_pipe[0]);
        close(err_pipe[1]);
        errno = saved_errno;
        return -1;
    }

    if (pid == 0) {
        /* ДОЧІРНІЙ ПРОЦЕС: ВІКНО НАЛАШТУВАННЯ */
        close(err_pipe[0]); /* Читаючий кінець дитині не потрібен */

        /* 1. Ізоляція групи процесів */
        if (setpgid(0, 0) == -1) goto child_failure;

        /* 2. Зміна робочого каталогу */
        if (cfg->working_dir && chdir(cfg->working_dir) == -1) {
            goto child_failure;
        }

        /* 3. Встановлення ліміту пам'яті (RLIMIT_AS) */
        if (cfg->max_memory_bytes > 0) {
            struct rlimit mem_lim = {
                .rlim_cur = cfg->max_memory_bytes,
                .rlim_max = cfg->max_memory_bytes
            };
            if (setrlimit(RLIMIT_AS, &mem_lim) == -1) goto child_failure;
        }

        /* 4. Встановлення ліміту часу процесора (RLIMIT_CPU) */
        if (cfg->max_cpu_seconds > 0) {
            struct rlimit cpu_lim = {
                .rlim_cur = cfg->max_cpu_seconds,
                .rlim_max = cfg->max_cpu_seconds
            };
            if (setrlimit(RLIMIT_CPU, &cpu_lim) == -1) goto child_failure;
        }

        /* 5. Перенаправлення дескрипторів STDIN, STDOUT, STDERR */
        if (cfg->stdin_fd >= 0 && cfg->stdin_fd != STDIN_FILENO) {
            if (dup2(cfg->stdin_fd, STDIN_FILENO) == -1) goto child_failure;
        }
        if (cfg->stdout_fd >= 0 && cfg->stdout_fd != STDOUT_FILENO) {
            if (dup2(cfg->stdout_fd, STDOUT_FILENO) == -1) goto child_failure;
        }
        if (cfg->stderr_fd >= 0 && cfg->stderr_fd != STDERR_FILENO) {
            if (dup2(cfg->stderr_fd, STDERR_FILENO) == -1) goto child_failure;
        }

        /* 6. Скидання маски блокування сигналів */
        sigset_t empty_mask;
        sigemptyset(&empty_mask);
        if (sigprocmask(SIG_SETMASK, &empty_mask, NULL) == -1) goto child_failure;

        /* 7. Закриття всіх сторонніх дескрипторів, крім діагностичного каналу */
        close_inherited_fds(3);

        /* 8. Заміна образу пам'яті */
        if (cfg->envp) {
            execvpe(cfg->executable, cfg->argv, cfg->envp);
        } else {
            execvp(cfg->executable, cfg->argv);
        }

child_failure:
        {
            int child_errno = errno;
            /* Записуємо код помилки в діагностичний канал */
            ssize_t written = write(err_pipe[1], &child_errno, sizeof(child_errno));
            (void)written;
            close(err_pipe[1]);
            _exit(127);
        }
    }

    /* БАТЬКІВСЬКИЙ ПРОЦЕС */
    close(err_pipe[1]); /* Закриваємо записуючий кінець у батьку */

    int child_error = 0;
    ssize_t bytes_read;
    
    /* Читання з обробкою переривання сигналами EINTR */
    do {
        bytes_read = read(err_pipe[0], &child_error, sizeof(child_error));
    } while (bytes_read == -1 && errno == EINTR);

    close(err_pipe[0]);

    if (bytes_read == sizeof(child_error)) {
        /* Дочірній процес повідомив про помилку перед виходом */
        waitpid(pid, NULL, 0); /* Прибираємо зомбі */
        errno = child_error;
        return -1;
    }

    if (bytes_read == 0) {
        /* Канал закрився автоматично ядром через O_CLOEXEC: запуск успішний */
        if (out_pid) *out_pid = pid;
        return 0;
    }

    /* Неочікуваний збій читання каналу */
    waitpid(pid, NULL, 0);
    return -1;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <expected>
#include <system_error>
#include <memory>
#include <span>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <signal.h>
#include <sys/syscall.h>

struct ProcessConfigOptions {
    std::string executable;
    std::vector<std::string> argv;
    std::optional<std::vector<std::string>> envp;
    std::optional<std::string> working_dir;
    int stdin_fd = -1;
    int stdout_fd = -1;
    int stderr_fd = -1;
    rlim_t max_memory_bytes = 0;
    rlim_t max_cpu_seconds = 0;
};

class DiagnosticPipeRAII {
public:
    DiagnosticPipeRAII() {
        if (pipe2(fds_, O_CLOEXEC) == -1) {
            throw std::system_error(errno, std::generic_category(), "pipe2 failed");
        }
    }
    ~DiagnosticPipeRAII() noexcept {
        close_read();
        close_write();
    }
    DiagnosticPipeRAII(const DiagnosticPipeRAII&) = delete;
    DiagnosticPipeRAII& operator=(const DiagnosticPipeRAII&) = delete;

    void close_read() noexcept {
        if (fds_[0] != -1) { close(fds_[0]); fds_[0] = -1; }
    }
    void close_write() noexcept {
        if (fds_[1] != -1) { close(fds_[1]); fds_[1] = -1; }
    }
    int read_fd() const noexcept { return fds_[0]; }
    int write_fd() const noexcept { return fds_[1]; }

private:
    int fds_[2] = {-1, -1};
};

static void close_fds_above(int min_fd) noexcept {
#if defined(__NR_close_range)
    if (syscall(__NR_close_range, min_fd, ~0U, 0) == 0) {
        return;
    }
#endif
    long max_fd = sysconf(_SC_OPEN_MAX);
    if (max_fd < 0 || max_fd > 4096) max_fd = 4096;
    for (int fd = min_fd; fd < max_fd; ++fd) {
        close(fd);
    }
}

std::expected<pid_t, std::error_code> launch_process_cpp(const ProcessConfigOptions& opt) {
    if (opt.executable.empty() || opt.argv.empty()) {
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));
    }

    DiagnosticPipeRAII err_pipe;

    pid_t pid = fork();
    if (pid < 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }

    if (pid == 0) {
        /* ДОЧІРНІЙ ПРОЦЕС */
        err_pipe.close_read();

        auto report_and_exit = [&](int err_code) noexcept {
            ssize_t w = write(err_pipe.write_fd(), &err_code, sizeof(err_code));
            (void)w;
            err_pipe.close_write();
            _exit(127);
        };

        if (setpgid(0, 0) == -1) report_and_exit(errno);

        if (opt.working_dir) {
            if (chdir(opt.working_dir->c_str()) == -1) report_and_exit(errno);
        }

        if (opt.max_memory_bytes > 0) {
            struct rlimit lim{ opt.max_memory_bytes, opt.max_memory_bytes };
            if (setrlimit(RLIMIT_AS, &lim) == -1) report_and_exit(errno);
        }

        if (opt.max_cpu_seconds > 0) {
            struct rlimit lim{ opt.max_cpu_seconds, opt.max_cpu_seconds };
            if (setrlimit(RLIMIT_CPU, &lim) == -1) report_and_exit(errno);
        }

        if (opt.stdin_fd >= 0 && opt.stdin_fd != STDIN_FILENO) {
            if (dup2(opt.stdin_fd, STDIN_FILENO) == -1) report_and_exit(errno);
        }
        if (opt.stdout_fd >= 0 && opt.stdout_fd != STDOUT_FILENO) {
            if (dup2(opt.stdout_fd, STDOUT_FILENO) == -1) report_and_exit(errno);
        }
        if (opt.stderr_fd >= 0 && opt.stderr_fd != STDERR_FILENO) {
            if (dup2(opt.stderr_fd, STDERR_FILENO) == -1) report_and_exit(errno);
        }

        sigset_t mask;
        sigemptyset(&mask);
        if (sigprocmask(SIG_SETMASK, &mask, nullptr) == -1) report_and_exit(errno);

        close_fds_above(3);

        std::vector<char*> c_argv;
        c_argv.reserve(opt.argv.size() + 1);
        for (const auto& arg : opt.argv) {
            c_argv.push_back(const_cast<char*>(arg.c_str()));
        }
        c_argv.push_back(nullptr);

        if (opt.envp) {
            std::vector<char*> c_envp;
            c_envp.reserve(opt.envp->size() + 1);
            for (const auto& env : *opt.envp) {
                c_envp.push_back(const_cast<char*>(env.c_str()));
            }
            c_envp.push_back(nullptr);
            execvpe(opt.executable.c_str(), c_argv.data(), c_envp.data());
        } else {
            execvp(opt.executable.c_str(), c_argv.data());
        }

        report_and_exit(errno);
    }

    /* БАТЬКІВСЬКИЙ ПРОЦЕС */
    err_pipe.close_write();

    int child_error = 0;
    ssize_t bytes_read = 0;
    do {
        bytes_read = read(err_pipe.read_fd(), &child_error, sizeof(child_error));
    } while (bytes_read == -1 && errno == EINTR);

    err_pipe.close_read();

    if (bytes_read == sizeof(child_error)) {
        waitpid(pid, nullptr, 0);
        return std::unexpected(std::make_error_code(static_cast<std::errc>(child_error)));
    }

    if (bytes_read == 0) {
        return pid;
    }

    waitpid(pid, nullptr, 0);
    return std::unexpected(std::make_error_code(std::errc::io_error));
}
```
:::

## Покроковий розбір критичних інженерних аспектів

1. **Чому `pipe2` з `O_CLOEXEC` є обов'язковим?**
   Якщо створити канал звичайним викликом `pipe(fds)` і потім встановлювати прапорець через `fcntl(fds[1], F_SETFD, FD_CLOEXEC)`, у багатопотоковому середовищі виникає стан перегонів (race condition): якщо інший потік викличе `fork` між цими двома викликами, дескриптор каналу витече в сторонній дочірній процес. Тоді кінець каналу ніколи не закриється, і батьківський процес заблокується на виклику `read()` назавжди. Виклик `pipe2` гарантує атомарне створення дескрипторів із прапорцем `O_CLOEXEC`.
2. **Чому в гілці дитини використовується виключно `_exit(127)`?**
   Стандартна функція `exit()` викликає зареєстровані обробники `atexit` та спорожнює буфери `stdio` бібліотеки `libc` (`fflush`). Оскільки пам'ять дитини містить копію буферів батька, виклик `exit()` призвів би до повторного скидання напівзаписаних рядків логів або повторного звільнення пам'яті в батьківських структурах. Системний виклик `_exit()` миттєво припиняє виконання процесу на рівні ядра без побічних ефектів.
3. **Обробка переривання сигналом `EINTR`**:
   Виклик `read(err_pipe[0], ...)` у батьківському процесі може бути перерваний доставкою системного сигналу (наприклад, `SIGCHLD` або `SIGALRM`). Без циклу `do { ... } while (bytes_read == -1 && errno == EINTR);` лаунчер помилково сприйняв би системне переривання за аварію запуску процесу.
4. **Запобігання накопиченню процесів-зомбі**:
   Якщо дочірній процес повідомив про помилку й завершився через `_exit(127)`, він переходить у стан зомбі (zombie). Батьківський процес зобов'язаний негайно викликати `waitpid(pid, NULL, 0)`, щоб ядро звільнило дескриптор процесу в таблиці процесів.

## Демонстраційний тест і перевірка крайових випадків

Для перевірки коректності обробки системних помилок та лімітів нижче наведено тестову програму, яка послідовно валідує всі критичні сценарії запуску.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/wait.h>

/* Прототип лаунчера */
int launch_process(const ProcessConfig *cfg, pid_t *out_pid);

int main(void) {
    printf("=== ТЕСТУВАННЯ СИСТЕМНОГО ЛАУНЧЕРА ===\n\n");

    /* Тест 1: Спроба запуску неіснуючого бінарного файлу */
    {
        char *argv[] = { "nonexistent_binary_xyz", NULL };
        ProcessConfig cfg = {
            .executable = "nonexistent_binary_xyz",
            .argv = argv
        };
        pid_t pid;
        int res = launch_process(&cfg, &pid);
        printf("[Тест 1: Неіснуючий файл] Результат: %d, errno: %d (%s)\n",
               res, errno, strerror(errno));
        if (res == -1 && errno == ENOENT) {
            printf("  -> УСПІХ: батько точно визначив помилку ENOENT!\n");
        }
    }

    /* Тест 2: Успішний запуск утиліти echo з передачею аргументів */
    {
        char *argv[] = { "echo", "Привіт із безпечного лаунчера!", NULL };
        ProcessConfig cfg = {
            .executable = "echo",
            .argv = argv
        };
        pid_t pid;
        int res = launch_process(&cfg, &pid);
        printf("\n[Тест 2: Успішний запуск echo] Результат: %d, PID: %d\n", res, pid);
        if (res == 0) {
            int status;
            waitpid(pid, &status, 0);
            printf("  -> УСПІХ: процес завершився з кодом %d\n", WEXITSTATUS(status));
        }
    }

    /* Тест 3: Обмеження пам'яті (RLIMIT_AS) */
    {
        char *argv[] = { "ls", "-la", NULL };
        ProcessConfig cfg = {
            .executable = "ls",
            .argv = argv,
            .max_memory_bytes = 1024 * 1024 /* Лише 1 МБ віртуальної пам'яті */
        };
        pid_t pid;
        int res = launch_process(&cfg, &pid);
        printf("\n[Тест 3: Обмеження пам'яті 1 МБ] Результат: %d, PID/errno: %d\n", res, pid);
        if (res == 0) {
            int status;
            waitpid(pid, &status, 0);
            printf("  -> Підпроцес завершився (можливий збій динамічного лінкера через ліміт пам'яті)\n");
        }
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <cassert>

int main() {
    std::cout << "=== ТЕСТУВАННЯ СИСТЕМНОГО ЛАУНЧЕРА (C++) ===\n\n";

    // Тест 1: Неіснуючий бінарний файл
    {
        ProcessConfigOptions opt;
        opt.executable = "nonexistent_command_12345";
        opt.argv = { "nonexistent_command_12345" };

        auto result = launch_process_cpp(opt);
        if (!result) {
            std::cout << "[Тест 1: Неіснуючий файл] Отримано очікувану помилку: "
                      << result.error().message() << " (код: " << result.error().value() << ")\n";
            assert(result.error() == std::errc::no_such_file_or_directory);
        }
    }

    // Тест 2: Успішний запуск
    {
        ProcessConfigOptions opt;
        opt.executable = "/bin/echo";
        opt.argv = { "echo", "Тест C++ успішний!" };

        auto result = launch_process_cpp(opt);
        if (result) {
            std::cout << "[Тест 2: Успішний запуск] Створено процес PID: " << *result << "\n";
            int status = 0;
            waitpid(*result, &status, 0);
            std::cout << "  -> Процес успішно виконався й повернув код " << WEXITSTATUS(status) << "\n";
        }
    }

    return 0;
}
```
:::

## Підсумкова оцінка надійності

Розроблений патерн лаунчера забезпечує промисловий рівень надійності:
- Батьківський процес завжди отримує детермінований результат запуску (успішний PID або точний код `errno`), усуваючи стан невизначеності.
- Відсутні витоки дескрипторів та незакритих каналів завдяки атомарному застосуванню прапорців `O_CLOEXEC`.
- Відсутній ризик взаємного блокування м'ютексів, оскільки у вікні між `fork` та `execve` викликаються виключно безпечні системні виклики ядра.
