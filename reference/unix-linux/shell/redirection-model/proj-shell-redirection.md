# ⚙️ Реалізація перенаправлення дескрипторів у міні-оболонці

Цей практичний проєкт розкриває повну реалізацію механізму перенаправлення файлових дескрипторів (`<`, `>`, `>>`, `2>&1`) та запуску дочірніх процесів мовами C та C++. Кодуванню передує детальний аналіз архітектурного шаблону, опис обробки сигналів та розбір потенційних пасток під час роботи з низькорівневими системними викликами POSIX.

---

## 1. Архітектурний шаблон виконання команди з перенаправленням

Коли командна оболонка (shell) отримує рядкову команду із перенаправленням (наприклад, `grep "error" < input.log > result.txt 2>&1`), вона виконує послідовну серію кроків для підготовки середовища виконання дочірньої програми.

Основні етапи виконання:

1.  **Парсинг аргументів та лексичний аналіз**: Розділення вхідного рядка на масив числових та текстових аргументів (вектор `argv`) та виділення операторів перенаправлення потоків. Оболонка сканує масив слів, виокремлюючи файлові шляхи для джерел та приймачів.
2.  **Створення дочірнього процесу (`fork`)**: Оболонка створює точну копію поточного процесу. Батьківський процес очікує завершення дочірнього через системний виклик `waitpid`.
3.  **Виконання перенаправлень у дочірньому процесі**:
    *   Відкриття файлів джерел та приймачів даних за допомогою системного виклику `open` із відповідними прапорцями (`O_RDONLY`, `O_WRONLY`, `O_CREAT`, `O_TRUNC`, `O_APPEND`).
    *   Перевизначення стандартних файлових дескрипторів 0, 1 або 2 системним викликом `dup2`.
    *   Обов'язкове закриття тимчасових дескрипторів, отриманих від виклику `open`, для запобігання витоку дескрипторів.
4.  **Заміна образу процесу (`execvp`)**: Викликається цільова утиліта. Оскільки таблиця дескрипторів повністю зберігається при виконанні `exec`, нова програма прозоро пише та читає з призначених файлів.

```
Батьківський процес (Shell)
   │
   ├── fork() ──> Дочірній процес
   │                 │
   │                 ├── open("input.log", O_RDONLY) ──> FD 3
   │                 ├── dup2(3, 0)                  ──> FD 0 (stdin = input.log)
   │                 ├── close(3)
   │                 │
   │                 ├── open("result.txt", O_WRONLY)──> FD 4
   │                 ├── dup2(4, 1)                  ──> FD 1 (stdout = result.txt)
   │                 ├── close(4)
   │                 │
   │                 ├── dup2(1, 2)                  ──> FD 2 (stderr = FD 1)
   │                 │
   │                 └── execvp("grep", ["grep", "error", NULL])
   │
   └── waitpid() ──> Очікування завершення дочірнього процесу
```

---

## 2. Типові пастки та крайові випадки при програмуванні

Під час реалізації перенаправлень у реальних проєктах важливо враховувати такі потенційні проблеми та пастки:

### 2.1 Закриття тимчасових дескрипторів
Якщо після виклику `dup2(3, 1)` процес не виконує `close(3)`, дескриптор 3 залишатиметься відкритим у цільовій програмі. Для дискових файлів це призводить до витоку ресурсів, а для анонімних каналів (`pipe`) це унеможливлює відправку сигналу `EOF` (End of File), через що читач каналу зависне назавжди.

### 2.2 Правильні прапорці відкриття файлів
Створення файлу виведення (`>`) завжди вимагає маски прапорців `O_WRONLY | O_CREAT | O_TRUNC`. Для оператора дописування (`>>`) замість `O_TRUNC` використовується прапорець `O_APPEND`.

### 2.3 Права доступу на нові файли
При виклику `open` із прапорцем `O_CREAT` обов'язково передається третій аргумент режимів доступу (наприклад, `0644` або `S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH`). Пропуск цього аргументу призводить до створення файлу з довільними сміттєвими правами доступу зі стека. Реальні права доступу також модифікуються маскою `umask` процесу.

### 2.4 Обробка системних помилок та кодів повернення
Якщо виклик `open()` повертає від'ємне значення (наприклад, через відсутність прав на читання або запис), дочірній процес повинен негайно вивести повідомлення про помилку у `stderr` та завершити роботу через `exit(EXIT_FAILURE)`. Неприпустимо викликати `execvp()` після невдалої спроби перенаправлення, оскільки команда буде виконана з неправильними або неповними потоками даних.

### 2.5 Аналіз статусів завершення `waitpid`
Батьківський процес повинен коректно аналізувати стан завершення дочірнього процесу за допомогою макросів POSIX:
*   `WIFEXITED(status)`: Повертає істину, якщо дочірній процес завершився нормально (через `exit()` або повернення з `main()`).
*   `WEXITSTATUS(status)`: Повертає код виходу дочірнього процесу (0–255).
*   `WIFSIGNALED(status)`: Повертає істину, якщо дочірній процес було аварійно вбито неперехопленим сигналом (наприклад, `SIGKILL` або `SIGSEGV`).
*   `WTERMSIG(status)`: Повертає номер сигналу, який спричинив загибель процесу.

### 2.6 Взаємодія із керуванням завданнями (Job Control) та сигналами
При запуску процесів із перенаправленням оболонки підтримують обробку системних сигналів `SIGINT` (Ctrl+C) та `SIGTSTP` (Ctrl+Z). У дочірньому процесі після виклику `fork()` відновлюються стандарні обробники сигналів (`SIG_DFL`), щоб запущена програма адекватно реагувала на сигнали користувача, тоді як батьківська оболонка ігнорує ці сигнали під час очікування дочірнього процесу у `waitpid()`.

---

## 3. Повна реалізація міні-оболонки

Нижче наведено повні програмні реалізації оболонки. Приклади демонструють обробку параметрів командного рядка, створення дочірнього процесу через `fork()`, відкриття файлів, перенаправлення дескрипторів за допомогою `dup2()` та очікування завершення дочірнього процесу за допомогою `waitpid()`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <errno.h>

#define MAX_ARGS 64

struct RedirectionConfig {
    char *infile;
    char *outfile;
    int append_mode;
    int merge_stderr;
};

static void execute_command(char **argv, struct RedirectionConfig *cfg) {
    if (cfg->infile) {
        int fd_in = open(cfg->infile, O_RDONLY);
        if (fd_in < 0) {
            perror("open infile failed");
            exit(EXIT_FAILURE);
        }
        if (dup2(fd_in, STDIN_FILENO) < 0) {
            perror("dup2 stdin failed");
            close(fd_in);
            exit(EXIT_FAILURE);
        }
        close(fd_in);
    }

    if (cfg->outfile) {
        int flags = O_WRONLY | O_CREAT | (cfg->append_mode ? O_APPEND : O_TRUNC);
        int fd_out = open(cfg->outfile, flags, 0644);
        if (fd_out < 0) {
            perror("open outfile failed");
            exit(EXIT_FAILURE);
        }
        if (dup2(fd_out, STDOUT_FILENO) < 0) {
            perror("dup2 stdout failed");
            close(fd_out);
            exit(EXIT_FAILURE);
        }
        close(fd_out);
    }

    if (cfg->merge_stderr) {
        if (dup2(STDOUT_FILENO, STDERR_FILENO) < 0) {
            perror("dup2 merge stderr failed");
            exit(EXIT_FAILURE);
        }
    }

    execvp(argv[0], argv);
    perror("execvp failed");
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <команда> [аргументи] [перенаправлення...]\n", argv[0]);
        fprintf(stderr, "Приклад: %s ls -la > out.txt 2>&1\n", argv[0]);
        return EXIT_FAILURE;
    }

    char *cmd_args[MAX_ARGS];
    int arg_idx = 0;
    struct RedirectionConfig cfg = {NULL, NULL, 0, 0};

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "<") == 0 && i + 1 < argc) {
            cfg.infile = argv[++i];
        } else if (strcmp(argv[i], ">") == 0 && i + 1 < argc) {
            cfg.outfile = argv[++i];
            cfg.append_mode = 0;
        } else if (strcmp(argv[i], ">>") == 0 && i + 1 < argc) {
            cfg.outfile = argv[++i];
            cfg.append_mode = 1;
        } else if (strcmp(argv[i], "2>&1") == 0) {
            cfg.merge_stderr = 1;
        } else {
            if (arg_idx < MAX_ARGS - 1) {
                cmd_args[arg_idx++] = argv[i];
            }
        }
    }
    cmd_args[arg_idx] = NULL;

    if (arg_idx == 0) {
        fprintf(stderr, "Помилка: не вказано команду для виконання\n");
        return EXIT_FAILURE;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork failed");
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        /* Дочірній процес */
        execute_command(cmd_args, &cfg);
    } else {
        /* Батьківський процес */
        int status;
        if (waitpid(pid, &status, 0) < 0) {
            perror("waitpid failed");
            return EXIT_FAILURE;
        }
        if (WIFEXITED(status)) {
            printf("[Процес завершено з кодом: %d]\n", WEXITSTATUS(status));
        }
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <system_error>
#include <memory>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>

class ScopedFd {
    int fd_{-1};
public:
    explicit ScopedFd(int fd) : fd_(fd) {}
    ~ScopedFd() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

struct RedirectionOptions {
    std::string_view infile;
    std::string_view outfile;
    bool append{false};
    bool merge_stderr{false};
};

class MiniRunner {
public:
    static int run(const std::vector<std::string_view>& raw_args) {
        std::vector<char*> exec_args;
        RedirectionOptions opts;

        for (size_t i = 0; i < raw_args.size(); ++i) {
            if (raw_args[i] == "<" && i + 1 < raw_args.size()) {
                opts.infile = raw_args[++i];
            } else if (raw_args[i] == ">" && i + 1 < raw_args.size()) {
                opts.outfile = raw_args[++i];
                opts.append = false;
            } else if (raw_args[i] == ">>" && i + 1 < raw_args.size()) {
                opts.outfile = raw_args[++i];
                opts.append = true;
            } else if (raw_args[i] == "2>&1") {
                opts.merge_stderr = true;
            } else {
                exec_args.push_back(const_cast<char*>(raw_args[i].data()));
            }
        }
        exec_args.push_back(nullptr);

        if (exec_args.size() <= 1) {
            std::cerr << "Помилка: відсутня команда\n";
            return 1;
        }

        pid_t pid = ::fork();
        if (pid < 0) {
            std::perror("fork");
            return 1;
        }

        if (pid == 0) {
            child_execute(exec_args.data(), opts);
        }

        int status{0};
        if (::waitpid(pid, &status, 0) < 0) {
            std::perror("waitpid");
            return 1;
        }

        if (WIFEXITED(status)) {
            std::cout << "[Процес завершено з кодом: " << WEXITSTATUS(status) << "]\n";
        }
        return 0;
    }

private:
    [[noreturn]] static void child_execute(char** argv, const RedirectionOptions& opts) {
        if (!opts.infile.empty()) {
            ScopedFd fd_in(::open(opts.infile.data(), O_RDONLY));
            if (!fd_in.valid()) {
                std::perror("open infile");
                std::exit(EXIT_FAILURE);
            }
            if (::dup2(fd_in.get(), STDIN_FILENO) < 0) {
                std::perror("dup2 stdin");
                std::exit(EXIT_FAILURE);
            }
        }

        if (!opts.outfile.empty()) {
            int flags = O_WRONLY | O_CREAT | (opts.append ? O_APPEND : O_TRUNC);
            ScopedFd fd_out(::open(opts.outfile.data(), flags, 0644));
            if (!fd_out.valid()) {
                std::perror("open outfile");
                std::exit(EXIT_FAILURE);
            }
            if (::dup2(fd_out.get(), STDOUT_FILENO) < 0) {
                std::perror("dup2 stdout");
                std::exit(EXIT_FAILURE);
            }
        }

        if (opts.merge_stderr) {
            if (::dup2(STDOUT_FILENO, STDERR_FILENO) < 0) {
                std::perror("dup2 merge stderr");
                std::exit(EXIT_FAILURE);
            }
        }

        ::execvp(argv[0], argv);
        std::perror("execvp");
        std::exit(EXIT_FAILURE);
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <команда> [перенаправлення...]\n";
        return 1;
    }

    std::vector<std::string_view> args(argv + 1, argv + argc);
    return MiniRunner::run(args);
}
```
:::

---

## 4. Порівняння підходів у C та C++

У реалізації мовою C програміст зобов'язаний самостійно відстежувати кожен створений дескриптор та виконувати `close()` у кожній гілці обробки помилок. При ускладненні коду це часто призводить до витоку дескрипторів.

Натомість у реалізації мовою C++ застосування концепції RAII (Resource Acquisition Is Initialization) через клас `ScopedFd` автоматизує керування ресурсами. Деструктор об'єкта `ScopedFd` викличуть автоматично при виході з області видимості, навіть якщо викличеться виняток або станеться передчасне повернення з функції. Це робить код значно надійнішим та безпечнішим.

---

## 5. Простеження таблиці дескрипторів під час виконання

Під час виконання розібраної програми таблиця дескрипторів дочірнього процесу проходить через такі кванти стану:

1.  **Старт дочірнього процесу**: `FD 0 -> tty`, `FD 1 -> tty`, `FD 2 -> tty`.
2.  **Виклик `open("input.log", O_RDONLY)`**: Повертається `FD 3`. Таблиця: `FD 0..2 -> tty`, `FD 3 -> input.log`.
3.  **Виклик `dup2(3, 0)`**: `FD 0` перевизначається на `input.log`. Таблиця: `FD 0 -> input.log`, `FD 1..2 -> tty`, `FD 3 -> input.log`.
4.  **Виклик `close(3)`**: Тимчасовий дескриптор знищується. Таблиця: `FD 0 -> input.log`, `FD 1..2 -> tty`.
5.  **Виклик `open("result.txt", O_WRONLY|O_CREAT|O_TRUNC, 0644)`**: Повертається `FD 3`. Таблиця: `FD 0 -> input.log`, `FD 1..2 -> tty`, `FD 3 -> result.txt`.
6.  **Виклик `dup2(3, 1)`**: `FD 1` перевизначається на `result.txt`. Таблиця: `FD 0 -> input.log`, `FD 1 -> result.txt`, `FD 2 -> tty`, `FD 3 -> result.txt`.
7.  **Виклик `close(3)`**: Тимчасовий дескриптор знищується. Таблиця: `FD 0 -> input.log`, `FD 1 -> result.txt`, `FD 2 -> tty`.
8.  **Виклик `dup2(1, 2)`**: `FD 2` бере вказівник з `FD 1`. Таблиця: `FD 0 -> input.log`, `FD 1 -> result.txt`, `FD 2 -> result.txt`.
9.  **Виклик `execvp()`**: Таблиця дескрипторів зберігається, а код утиліти приступає до роботи із підготовленими потоками I/O.
