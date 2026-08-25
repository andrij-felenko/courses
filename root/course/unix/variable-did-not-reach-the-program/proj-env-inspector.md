# ⚙️ Інспектор та маніпулятор середовища процесів: відтворення execve та аналіз /proc

Коли процес запускає дочірню програму, системний виклик `execve` вимагає явного передавання масиву покажчиків на рядки середовища `char *const envp[]`. Якщо передати туди некоректно сформовану структуру або випадково пропустити змінну, дочірній процес запуститься у викривленому контексті без жодного системного попередження чи сповіщення про помилку.

У цій практичній роботі ми побудуємо повноцінний системний лаунчер та інспектор середовища двома мовами — класичною C (POSIX.1-2008) та сучасним C++ (стандарт C++23). Програма розв'язує комплекс прикладних інженерних задач: формує ізольований масив середовища з білим списком дозволених ключів, запускає дочірній процес через низькорівневий системний виклик `execve`, діагностує можливі помилки запуску та зчитує сирий вміст віртуального файлу `/proc/[pid]/environ` для безпосередньої верифікації байтів, завантажених ядром на вершину стека дочірнього процесу.

## Архітектура масиву envp та читання через procfs

Системний виклик `execve(const char *pathname, char *const argv[], char *const envp[])` приймає масив покажчиків на віртуальну пам'ять, останнім елементом якого обов'язково має бути нульовий покажчик `NULL`. Кожен дійсний елемент масиву вказує на нуль-термінований рядок формату `КЛЮЧ=ЗНАЧЕННЯ`.

```
envp[0] ──> "PATH=/usr/bin:/bin\0"
envp[1] ──> "APP_ENV=production\0"
envp[2] ──> "PORT=8080\0"
envp[3] ──> NULL
```

Після виконання системного виклику `execve` ядро Linux самостійно розміщує ці рядки на вершині стека новоствореної програми, а підсистема віртуальної файлової системи `procfs` робить їх доступними для стороннього спостереження через псевдофайл `/proc/<pid>/environ`.

Усередині файлу `/proc/<pid>/environ` байти середовища зберігаються поспіль, розділені символами нульового байта `\0` (ASCII 0x00), без жодних додаткових символів перенесення рядків `\n`. Зчитування цього файлу дає змогу побачити первинний зліпок пам'яті, який отримав процес у момент старту від ядра, незалежно від будь-яких подальших модифікацій через бібліотечну функцію `setenv()` у просторі користувача.

## Санація змінних оточення перед виконанням

Передавання успадкованого масиву `environ` сторонньому або менш привілейованому бінарному файлу несе прямі загрози інформаційній безпеці. До списку небезпечних змінних, які можуть призвести до підміни поведінки або виконання довільного коду, належать:

- `LD_PRELOAD` та `LD_LIBRARY_PATH` — дозволяють ін'єктувати сторонні динамічні бібліотеки у процес та перехоплювати виклики системних функцій;
- `IFS` (Internal Field Separator) — класичний вектор атак на скрипти командної оболонки, які розбивають аргументи за нестандартними роздільниками;
- `BASH_ENV` та `ENV` — змушують інтерпретатори оболонок завантажувати й виконувати довільні скрипти під час кожної ініціалізації;
- `PYTHONPATH`, `PERL5LIB` та `RUBYLIB` — спричиняють завантаження неперевірених модулів інтерпретованих мов із поточного робочого каталогу.

Надійний системний лаунчер повинен реалізовувати політику безпеки на основі білого списку (allowlist): створювати повністю новий масив покажчиків, явно копіюючи лише дозволені змінні та додаючи необхідні системні параметри конфігурації.

## Повна реалізація лаунчера та інспектора

Нижче наведено робочі реалізації інспектора середовища мовами C (POSIX) та C++23 (із застосуванням концепції RAII для автоматичного закриття дескрипторів, типізованих контейнерів `std::vector`, представлень `std::string_view` та обробки помилок через `std::expected`).

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/wait.h>
#include <sys/types.h>

#define PROC_BUF_SIZE 4096

/* Функція інспекції середовища процесу через /proc/[pid]/environ */
static void inspect_process_environ(pid_t target_pid) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/environ", target_pid);

    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "[Помилка] Не вдалося відкрити %s: %s\n", path, strerror(errno));
        return;
    }

    printf("\n=== Зліпок /proc/%d/environ (роздільник null-byte) ===\n", target_pid);

    char buffer[PROC_BUF_SIZE];
    ssize_t bytes_read;
    size_t var_count = 0;

    while ((bytes_read = read(fd, buffer, sizeof(buffer))) > 0) {
        ssize_t start = 0;
        for (ssize_t i = 0; i < bytes_read; ++i) {
            if (buffer[i] == '\0') {
                if (i > start) {
                    var_count++;
                    printf("  [%02zu] %.*s\n", var_count, (int)(i - start), &buffer[start]);
                }
                start = i + 1;
            }
        }
    }

    if (bytes_read < 0) {
        fprintf(stderr, "[Помилка] Помилка читання з %s: %s\n", path, strerror(errno));
    }

    close(fd);
    printf("=== Усього виявлено змінних у пам'яті: %zu ===\n\n", var_count);
}

/* Безпечний запуск процесу з кастомним масивом envp */
int main(void) {
    printf("[Лаунчер C] Підготовка ізольованого середовища для дочірнього процесу...\n");

    /* Формуємо явний білий список змінних */
    char *custom_env[] = {
        "PATH=/usr/bin:/bin",
        "APP_ENV=production",
        "DATABASE_URL=postgres://app_user:s3cr3t@127.0.0.1:5432/production_db",
        "LOG_LEVEL=info",
        "CUSTOM_INJECTED_VAR=success_reach",
        NULL
    };

    /* Аргументи для запуску sleep, щоб встигнути оглянути /proc */
    char *child_argv[] = {
        "sleep",
        "1",
        NULL
    };

    pid_t pid = fork();
    if (pid < 0) {
        perror("[Помилка] fork");
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        /* Дочірній процес: виконуємо execve з власним масивом envp */
        execve("/bin/sleep", child_argv, custom_env);

        /* Якщо execve повернув керування — сталася помилка */
        perror("[Помилка дочірнього процесу] execve");
        _exit(127);
    }

    /* Батьківський процес: інспектуємо пам'ять дитини через /proc */
    usleep(50000); /* Коротка пауза, щоб дитина встигла виконати execve */
    inspect_process_environ(pid);

    int status;
    if (waitpid(pid, &status, 0) < 0) {
        perror("[Помилка] waitpid");
        return EXIT_FAILURE;
    }

    if (WIFEXITED(status)) {
        printf("[Лаунчер C] Дочірній процес %d завершився з кодом %d.\n", pid, WEXITSTATUS(status));
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <expected>
#include <filesystem>
#include <fstream>
#include <format>
#include <span>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <cstring>

namespace sys {

/* RAII-обгортка для файлового дескриптора */
class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : m_fd(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset();
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
        m_fd = new_fd;
    }

private:
    int m_fd{-1};
};

/* Зчитування та парсинг нуль-термінованого /proc/[pid]/environ */
[[nodiscard]] std::expected<std::vector<std::string>, std::string>
read_proc_environ(pid_t pid) {
    const std::string path = std::format("/proc/{}/environ", pid);
    UniqueFd fd(::open(path.c_str(), O_RDONLY));
    if (!fd.valid()) {
        return std::unexpected(std::format("Не вдалося відкрити {}: {}", path, std::strerror(errno)));
    }

    std::vector<std::string> env_vars;
    std::vector<char> buffer(4096);
    std::string current_entry;

    while (true) {
        const ssize_t bytes = ::read(fd.get(), buffer.data(), buffer.size());
        if (bytes < 0) {
            return std::unexpected(std::format("Помилка читання {}: {}", path, std::strerror(errno)));
        }
        if (bytes == 0) {
            break;
        }

        for (ssize_t i = 0; i < bytes; ++i) {
            if (buffer[static_cast<size_t>(i)] == '\0') {
                if (!current_entry.empty()) {
                    env_vars.push_back(std::move(current_entry));
                    current_entry.clear();
                }
            } else {
                current_entry.push_back(buffer[static_cast<size_t>(i)]);
            }
        }
    }

    if (!current_entry.empty()) {
        env_vars.push_back(std::move(current_entry));
    }

    return env_vars;
}

/* Формування та виконання безпечного запуску */
class ProcessLauncher {
public:
    ProcessLauncher& add_env(std::string key, std::string value) {
        m_env_storage.push_back(std::format("{}={}", key, value));
        return *this;
    }

    [[nodiscard]] std::expected<int, std::string>
    spawn_and_inspect(std::string_view executable, const std::vector<std::string>& args) {
        // Формуємо масив покажчиків argv
        std::vector<char*> raw_argv;
        raw_argv.reserve(args.size() + 2);
        std::string exec_str(executable);
        raw_argv.push_back(exec_str.data());
        for (const auto& arg : args) {
            raw_argv.push_back(const_cast<char*>(arg.c_str()));
        }
        raw_argv.push_back(nullptr);

        // Формуємо масив покажчиків envp
        std::vector<char*> raw_envp;
        raw_envp.reserve(m_env_storage.size() + 1);
        for (auto& entry : m_env_storage) {
            raw_envp.push_back(entry.data());
        }
        raw_envp.push_back(nullptr);

        const pid_t pid = ::fork();
        if (pid < 0) {
            return std::unexpected(std::format("fork() failed: {}", std::strerror(errno)));
        }

        if (pid == 0) {
            ::execve(exec_str.c_str(), raw_argv.data(), raw_envp.data());
            std::cerr << std::format("[Дитина] execve помилка: {}\n", std::strerror(errno));
            ::_exit(127);
        }

        // Батько інспектує стан дочірнього процесу
        ::usleep(50000); // 50 мс для старту execve

        auto inspect_res = read_proc_environ(pid);
        if (inspect_res) {
            std::cout << std::format("\n=== Інспекція C++: /proc/{}/environ ===\n", pid);
            for (size_t i = 0; i < inspect_res->size(); ++i) {
                std::cout << std::format("  [{:02d}] {}\n", i + 1, (*inspect_res)[i]);
            }
            std::cout << std::format("=== Усього перевірено змінних: {} ===\n\n", inspect_res->size());
        } else {
            std::cerr << std::format("[Помилка інспекції] {}\n", inspect_res.error());
        }

        int status = 0;
        if (::waitpid(pid, &status, 0) < 0) {
            return std::unexpected(std::format("waitpid() failed: {}", std::strerror(errno)));
        }

        if (WIFEXITED(status)) {
            return WEXITSTATUS(status);
        }
        return std::unexpected("Дочірній процес завершився аномально");
    }

private:
    std::vector<std::string> m_env_storage;
};

} // namespace sys

int main() {
    std::cout << "[Лаунчер C++] Конфігурація білого списку змінних...\n";

    sys::ProcessLauncher launcher;
    launcher.add_env("PATH", "/usr/bin:/bin")
            .add_env("APP_STAGE", "staging")
            .add_env("STORAGE_BUCKET", "s3://prod-assets-data")
            .add_env("MAX_WORKERS", "16")
            .add_env("SECURITY_TOKEN", "verified_bearer_token");

    auto result = launcher.spawn_and_inspect("/bin/sleep", {"1"});
    if (!result) {
        std::cerr << std::format("[Головна помилка] {}\n", result.error());
        return EXIT_FAILURE;
    }

    std::cout << std::format("[Лаунчер C++] Запуск успішний, код виходу: {}\n", *result);
    return EXIT_SUCCESS;
}
```
:::

## Інженерний розбір деталей реалізації

Під час проектування лаунчера застосовано кілька важливих системних прийомів:

1. **Ізоляція пам'яті від глобального середовища**: Замість непрямого використання покажчика `environ`, що тягне за собою всі змінні середовища сеансу розробника, лаунчер конструює власний вектор рядків (`custom_env` у C або `m_env_storage` у C++). Це гарантує детермінізм запуску незалежно від машини, на якій працює код.
2. **Контракт завершення масиву `NULL`**: В обох мовах масив покажчиків `char* raw_envp[]` завершується обов'язковим маркерним елементом `nullptr`. Якщо пропустити цей маркер, ядро Linux при спробі скопіювати масив на стек дитини почне читати пам'ять за межами виділеного буфера, що негайно спричинить системну помилку `EFAULT`.
3. **Потоковий парсинг нуль-байтів**: Оскільки утиліта `/proc/[pid]/environ` не містить символів переходу рядка, буферизований парсер зчитує дані фіксованими блоками по 4 КБ та фіксує змінні на кожному нульовому байті `\0`. Якщо змінна розділена між двома сусідніми системними блоками читання, рядок `current_entry` безшовно акумулює байти, запобігаючи втраті даних.
4. **Уникнення гонитви за станом зомбі**: Інспекція `/proc/[pid]/environ` виконується до виклику `waitpid()`. Коли дочірній процес завершує виконання функції `main()`, він переходить у стан зомбі (`Z`), і його віртуальний адресний простір негайно знищується ядром. Будь-яка спроба прочитати `/proc/[pid]/environ` після цього повернула б 0 байтів.

## Права доступу та безпека procfs

При спробі зчитати `/proc/[pid]/environ` для чужих процесів ядро Linux застосовує перевірку прав `ptrace` (`PTRACE_MODE_READ_FSCREDS`). Звичайний користувач може інспектувати файл `/proc/[pid]/environ` лише тих процесів, які належать тому самому реальному та ефективному UID, і якщо процес не виконує двійковий файл із бітами `setuid`/`setgid`.

Якщо спробувати зчитати `/proc/1/environ` (середовище процесу init/systemd) від імені звичайного користувача, виклик `open()` поверне помилку `EACCES` (Permission denied). Це критично важливий захист, оскільки змінні середовища системних демонів часто містять паролі до баз даних, приватні токени та внутрішні ключі шифрування.

## Трасування виклику execve через strace

Щоб підтвердити, який саме масив `envp` було передано під час запуску програми на рівні ядра, застосовують системний трасувальник `strace` з прапорцем виводу змінних:

```bash
strace -v -e trace=execve ./my_launcher
```

Прапорець `-v` (verbose) змушує `strace` розгортати всі елементи масиву `envp` повністю, а не обмежувати вивід першими декількома елементами. У виводі ви побачите точний системний виклик:

```
execve("/bin/sleep", ["sleep", "1"], ["PATH=/usr/bin:/bin", "APP_ENV=production", "DATABASE_URL=postgres://...", ...]) = 0
```

Це найнадійніший спосіб верифікувати коректність передачі змінних середовища на стику між простором користувача та ядром операційної системи.
