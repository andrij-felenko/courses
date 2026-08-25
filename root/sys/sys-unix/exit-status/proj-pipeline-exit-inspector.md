# ⚙️ Практичний інспектор статусів виходу та конвеєрів Unix

Практична реалізація системного інспектора процесів та конвеєрів (pipelines) демонструє створення дочірніх процесів, перехоплення викликів `waitpid()`, симуляцію мапування `PIPESTATUS` та підтримку режиму `pipefail`.

Цей проєкт пропонує повний робочий код інспектора процесів мовами C та C++, розбирає системні виклики ядра для побудови конвеєрів та показує способи обходу типових пасток міжпроцесного зв'язку.

---

## 1. Архітектура та задача інспектора статусів

У командній оболонці Unix вертикальний конвеєр з'єднує декілька самостійних системних процесів за допомогою анонімних каналів вводу-виводу (`pipes`):

```bash
cmd1 | cmd2 | cmd3
```

Згідно зі стандартом POSIX, за замовчуванням підсумковим кодом виходу всього конвеєра вважається статус завершення **останньої команди** (`cmd3`). Це створює критичну проблему мовчки пропущених збоїв (silent pipeline failure). Якщо команда `cmd1` впала з помилкою `EX_NOINPUT` (66) або загинула від аварійного сигналу `SIGSEGV` (139), але команда `cmd3` прочитала порожній потік і повернула успішний код `0`, то вся оболонка вважає виконання конвеєра успішним.

Для забезпечення надійності системний інспектор повинен реалізувати наступні задачі:
1. Запустити всі елементи конвеєра як паралельні дочірні процеси через системний виклик `fork()`.
2. З'єднати вихідні файлові дескриптори `STDOUT_FILENO` попередніх процесів із вхідними дескрипторами `STDIN_FILENO` наступних процесів за допомогою системних викликів `pipe()` та `dup2()`.
3. Дочекатися завершення кожного з дочірніх процесів за допомогою системного виклику `waitpid()`.
4. Зібрати та зафіксувати точний масив кодів завершення для кожного елемента (аналог масиву `${PIPESTATUS[@]}` у Bash).
5. Обчислити підсумковий статус виходу за правилом `pipefail` (перший зліва направо ненульовий код виходу або `0`, якщо всі команди завершилися успішно).

### Механізм роботи системних викликів pipe() та dup2()

Анонімний канал (pipe) створюється у ядрі Linux за допомогою системного виклику `pipe(fds)`. Ядро виділяє внутрішній кільцевий буфер пам'яті (розміром за замовчуванням 64 КБ, керований структурою `pipe_inode_info`) та повертає два нових файлових дескриптори:
* `fds[0]` — відкритий для читання з каналу.
* `fds[1]` — відкритий для запису в канал.

Під час виклику `fork()` дочірній процес отримує повну копію таблиці файлових дескрипторів батька. Щоб підключити стандартний вивід процесу `STDOUT_FILENO` (дескриптор 1) до каналу, дочірній процес виконує виклик `dup2(fds[1], STDOUT_FILENO)`. Системний виклик `dup2()` атомарно закриває цільовий дескриптор 1 (якщо він був відкритий) і дублює на його місце дескриптор каналу `fds[1]`.

Після цього дочірній процес зобов'язаний закрити оригінальні дескриптори `fds[0]` та `fds[1]`, щоб не плодити витоків файлових ресурсів.

---

## 2. Реалізація інспектора мовами C та C++

Нижче наведено повні робочі реалізації системного інспектора конвеєрів. Версія на C оперує низькорівневими масивами, явно керує закриттям файлових дескрипторів та використовує системні макроси розпакування `wstatus`. Версія на C++20 застосовує концепцію RAII для автоматичного управління дескрипторами, шаблон `std::expected` для безпечної обробки помилок та сучасні контейнери `std::span`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#define MAX_COMMANDS 8

typedef struct {
    char *argv[16];
} Command;

typedef struct {
    int pid;
    int raw_wstatus;
    int exit_code;
} ProcessResult;

void execute_pipeline(Command cmds[], int cmd_count, int pipefail_enabled) {
    int pipes[MAX_COMMANDS - 1][2];
    ProcessResult results[MAX_COMMANDS];

    // 1. Створення масиву анонімних каналів pipe
    for (int i = 0; i < cmd_count - 1; i++) {
        if (pipe(pipes[i]) < 0) {
            perror("Системна помилка pipe");
            exit(1);
        }
    }

    // 2. Послідовний запуск дочірніх процесів через fork/exec
    for (int i = 0; i < cmd_count; i++) {
        pid_t pid = fork();
        if (pid < 0) {
            perror("Системна помилка fork");
            exit(1);
        }

        if (pid == 0) {
            // Дочірній процес: перенаправлення стандартних потоків вводу-виводу
            if (i > 0) {
                // Перенаправлення STDIN на читання з попереднього каналу
                if (dup2(pipes[i - 1][0], STDIN_FILENO) < 0) {
                    perror("dup2 stdin");
                    _exit(1);
                }
            }
            if (i < cmd_count - 1) {
                // Перенаправлення STDOUT на запис у поточний канал
                if (dup2(pipes[i][1], STDOUT_FILENO) < 0) {
                    perror("dup2 stdout");
                    _exit(1);
                }
            }

            // Закриття всіх копій файлових дескрипторів каналів у дочірньому процесі
            for (int j = 0; j < cmd_count - 1; j++) {
                close(pipes[j][0]);
                close(pipes[j][1]);
            }

            // Заміна образу процесу на цільову програму
            execvp(cmds[i].argv[0], cmds[i].argv);
            perror("Системна помилка execvp");
            _exit(127); // Код виходу POSIX: команду не знайдено
        }

        results[i].pid = pid;
    }

    // Батьківський процес повинен закрити всі копії дескрипторів каналів,
    // інакше дочірні процеси чекатимуть на EOF вічно!
    for (int i = 0; i < cmd_count - 1; i++) {
        close(pipes[i][0]);
        close(pipes[i][1]);
    }

    // 3. Збір та розпакування статусів завершення всіх елементів
    for (int i = 0; i < cmd_count; i++) {
        int wstatus;
        waitpid(results[i].pid, &wstatus, 0);
        results[i].raw_wstatus = wstatus;

        if (WIFEXITED(wstatus)) {
            results[i].exit_code = WEXITSTATUS(wstatus);
        } else if (WIFSIGNALED(wstatus)) {
            results[i].exit_code = 128 + WTERMSIG(wstatus);
        } else {
            results[i].exit_code = 1;
        }
    }

    // 4. Форматований вивід масиву PIPESTATUS
    printf("--- Системний аналіз конвеєра (PIPESTATUS) ---\n");
    for (int i = 0; i < cmd_count; i++) {
        printf("  Елемент [%s] (PID %d) -> Exit Code: %d\n", 
               cmds[i].argv[0], results[i].pid, results[i].exit_code);
    }

    // 5. Обчислення підсумкового статусу $?
    int final_status = 0;
    if (pipefail_enabled) {
        for (int i = 0; i < cmd_count; i++) {
            if (results[i].exit_code != 0) {
                final_status = results[i].exit_code;
                break;
            }
        }
    } else {
        final_status = results[cmd_count - 1].exit_code;
    }

    printf("Підсумковий код виходу оболонки ($?) (pipefail=%s): %d\n", 
           pipefail_enabled ? "ON" : "OFF", final_status);
}

int main(void) {
    Command pipeline[] = {
        {.argv = {"cat", "/nonexistent_file_12345", NULL}},
        {.argv = {"grep", "pattern", NULL}},
        {.argv = {"wc", "-l", NULL}}
    };

    printf("=== Сценарій 1: Запуск конвеєра у стандартному режимі POSIX ===\n");
    execute_pipeline(pipeline, 3, 0);

    printf("\n=== Сценарій 2: Запуск конвеєра у режимі pipefail ===\n");
    execute_pipeline(pipeline, 3, 1);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <span >
#include <memory>
#include <expected>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

// RAII-обгортка для безпечного керування файловими дескрипторами каналів
class PipeFD {
    int fd_ = -1;
public:
    explicit PipeFD(int fd = -1) : fd_(fd) {}
    ~PipeFD() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    PipeFD(const PipeFD&) = delete;
    PipeFD& operator=(const PipeFD&) = delete;

    PipeFD(PipeFD&& o) noexcept : fd_(o.fd_) {
        o.fd_ = -1;
    }

    PipeFD& operator=(PipeFD&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const { return fd_; }
    void release() { fd_ = -1; }
};

struct ProcessInfo {
    std::string command_name;
    pid_t pid;
    int exit_code;
};

class PipelineInspector {
public:
    static std::expected<std::vector<ProcessInfo>, std::string> 
    run_pipeline(std::span<const std::vector<std::string>> commands) {
        size_t n = commands.size();
        if (n == 0) return std::unexpected("Отримано порожній конвеєр");

        std::vector<std::pair<PipeFD, PipeFD>> pipes;
        pipes.reserve(n - 1);

        for (size_t i = 0; i < n - 1; ++i) {
            int fds[2];
            if (::pipe(fds) < 0) {
                return std::unexpected("Системна помилка виклику pipe()");
            }
            pipes.emplace_back(PipeFD(fds[0]), PipeFD(fds[1]));
        }

        std::vector<ProcessInfo> results;
        results.reserve(n);

        for (size_t i = 0; i < n; ++i) {
            pid_t pid = ::fork();
            if (pid < 0) {
                return std::unexpected("Системна помилка виклику fork()");
            }

            if (pid == 0) { // Child process
                if (i > 0) {
                    ::dup2(pipes[i - 1].first.get(), STDIN_FILENO);
                }
                if (i < n - 1) {
                    ::dup2(pipes[i].second.get(), STDOUT_FILENO);
                }

                // Деструктори векторів pipes автоматично закриють усі не потрібні дескриптори
                pipes.clear();

                std::vector<char*> raw_argv;
                for (const auto& arg : commands[i]) {
                    raw_argv.push_back(const_cast<char*>(arg.c_str()));
                }
                raw_argv.push_back(nullptr);

                ::execvp(raw_argv[0], raw_argv.data());
                ::_exit(127); // POSIX код помилки запускa
            }

            results.push_back({commands[i][0], pid, 0});
        }

        // Parent process очищує вектор дескрипторів
        pipes.clear();

        // Очікування завершення кожного процесa
        for (auto& proc : results) {
            int wstatus = 0;
            ::waitpid(proc.pid, &wstatus, 0);

            if (WIFEXITED(wstatus)) {
                proc.exit_code = WEXITSTATUS(wstatus);
            } else if (WIFSIGNALED(wstatus)) {
                proc.exit_code = 128 + WTERMSIG(wstatus);
            } else {
                proc.exit_code = 1;
            }
        }

        return results;
    }

    static int compute_exit_status(std::span<const ProcessInfo> results, bool pipefail) {
        if (results.empty()) return 0;

        if (pipefail) {
            for (const auto& proc : results) {
                if (proc.exit_code != 0) {
                    return proc.exit_code;
                }
            }
            return 0;
        }

        return results.back().exit_code;
    }
};

int main() {
    std::vector<std::vector<std::string>> cmds = {
        {"cat", "/dev/nonexistent_file"},
        {"grep", "main"},
        {"head", "-n", "5"}
    };

    auto res = PipelineInspector::run_pipeline(cmds);
    if (!res) {
        std::cerr << "Помилка виконання: " << res.error() << "\n";
        return 1;
    }

    std::cout << "--- Результати трасування C++20 PipelineInspector ---\n";
    for (const auto& proc : *res) {
        std::cout << "  Команда: " << proc.command_name 
                  << " | PID: " << proc.pid 
                  << " | Exit Code: " << proc.exit_code << "\n";
    }

    std::cout << "Підсумковий статус (без pipefail): " 
              << PipelineInspector::compute_exit_status(*res, false) << "\n";
    std::cout << "Підсумковий статус (з pipefail):    " 
              << PipelineInspector::compute_exit_status(*res, true) << "\n";

    return 0;
}
```
:::

---

## 3. Критичні системні пастки та крайові випадки

При розробці системних конвеєрів та обробці статусів виходу необхідно враховувати чотири фундаментальні системні пастки:

### 1. Зависання на читанні EOF при незакритих дескрипторах `pipe`
Якщо батьківський процес після створення дочірніх процесів забуде закрити власні копії вихідного кінця каналу `pipes[i][1]`, дочірній процес-одержувач **ніколи не отримає сигнал кінця файлу (EOF)**. Ядро Linux вважатиме, що у каналі потенційно ще можуть з'явитися нові дані від батька. В результаті читач зависне на системному виклику `read()` навічно, а батьківський процес заблокується на виклику `waitpid()`.

### 2. Сигнал `SIGPIPE` та передчасне завершення процесів
Якщо права частина конвеєра (наприклад, `head -n 1`) прочитала необхідну кількість рядків і завершила роботу, ядро закриває вхідний кінець каналу `pipe`. Коли ліва частина (наприклад, `cat` або `yes`) намагається записати наступну порцію даних у закритий канал, ядро надсилає цьому процесу сигнал `SIGPIPE` (номер 13). Якщо програма не перехоплює `SIGPIPE`, вона негайно гине, а її статус завершення стає `128 + 13 = 141`. У режимі `pipefail` це викликає аварійне зупинення скрипту, навіть якщо програма відпрацювала коректно.

### 3. Небезпека витоку зомбі-процесів при використанні `_exit()`
У дочірньому процесі після виклику `fork()` у разі невдалого виклику `execvp()` необхідно завжди викликати `_exit(127)`, а не `exit(127)`. Звичайний виклик `exit()` скине буфери `stdio` у просторі користувача, що призведе до повторного виводу накопичених даних батьківського процесу у консоль.

### 4. Невизначеність порядку завершення елементів
Ядро Linux запускає всі елементи конвеєра паралельно на різних ядрах процесора. Порядок їхнього завершення є абсолютно непередбачуваним. Батьківський процес повинен опитувати статуси всіх PIDs у циклі, не роблячи припущень про те, що перша команда обов'язково помре раніше за останню.

---

## 4. Порівняльний аналіз стратегій обробки помилок у конвеєрах

Розробники системних скриптів та CLI-інструментів застосовують три основні стратегії контролю статусів:

1. **POSIX Default Strategy**: Перевіряється тільки `$?` останнього елемента. Підходить для простих конвеєрів форматування, де проміжні команди не можуть згенерувати фатальної помилки.
2. **Bash Strict Mode (`set -euo pipefail`)**: Будь-який ненульовий статус на будь-якому етапі негайно зупиняє скрипт. Найкраща практика для системного адміністрування та CI/CD.
3. **Explicit Subshell Parsing (`PIPESTATUS`)**: Скрипт явним чином аналізує кожен елемент масиву `${PIPESTATUS[@]}`, дозволяючи ігнорувати очикувані помилки (наприклад, код `141` від `SIGPIPE`) і реагувати тільки на реальні збої.
