# ⚙️ Мінімальний оркестратор процесів: реалізація ядра REPL мовами C та C++

У цій практичній вставці продемонстровано базова реалізація ядра командної оболонки (mini-shell orchestrator). Код ілюструє повний процес перетворення введеного текстового рядка на граф процесів простору користувача: розбиття на токени, обробка вбудованих команд (`cd`, `exit`), організація асинхронного конвеєра з двох команд (`cmd1 | cmd2`) за допомогою системних викликів `pipe()`, `fork()`, `dup2()` та `execvp()`, а також збір статусів завершення через `waitpid()`.

Реалізація подана паралельно двома мовами: чистим POSIX C та сучасним ідіоматичним C++ з використанням RAII-обгорток для захисту від витоків файлових дескрипторів.

## 1. Архітектура та структура міні-оболонки

Ядро інтерактивної оболонки працює у нескінченному циклі REPL (Read-Eval-Print Loop). Цей цикл є серцем будь-якого інтерпретатора і складається з трьох критичних системних кроків:
1. **Read (Читання та токенізація):** Оболонка виводить запрошення `mini-shell> ` і читає рядок через `fgets()` або `std::getline()`. Після цього рядок розбивається на окремі елементи (токени) за допомогою роздільників (пробіли, табуляції). На цьому ж етапі виконується пошук операторів керування, зокрема символу конвеєра `|`.
2. **Eval (Виконання та оркестрація):**
   - Якщо введено порожній рядок, цикл відразу повертається до запрошення.
   - Якщо це вбудована команда (`cd`, `exit`), вона виконується безпосередньо у контексті батьківського процесу оболонки via системний виклик `chdir()`. Це необхідно тому, що дочірній процес після завершення не може змінити поточний робочий каталог батька.
   - Якщо конвеєр відсутній, оболонка створює один дочірній процес через `fork()`, у якому викликає `execvp()`.
   - Якщо виявлено конвеєр з двох команд (`cmd1 | cmd2`), оболонка спочатку викликає системний виклик `pipe()` для створення неіменованого каналу ядра, після чого здійснює два послідовних виклики `fork()` для створення двох дочірніх процесів. Перший дочірній процес дублює дескриптор запису каналу на місце свого `stdout` (FD 1), а другий — дескриптор читання каналу на місце свого `stdin` (FD 0).
3. **Wait (Очікування та збір статусів):** Батьківська оболонка обов'язково закриває обидві власні копії дескрипторів каналу, щоб не залишити відкритими посилання на кінці каналу, після чого призупиняє своє виконання через системні виклики `waitpid()`, чекаючи на завершення обох дочірніх процесів та збираючи їхні коди виходу.

## 2. Двомовний приклад реалізації ядра оболонки

:::tabs
```c
/* mini_shell.c — POSIX C реалізація ядра оркестрації процесів */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

#define MAX_LINE 1024
#define MAX_ARGS 64

/* Розбиття рядка на аргументи за пробілами */
static int tokenize(char *line, char **args) {
    int count = 0;
    char *token = strtok(line, " \t\n\r");
    while (token != NULL && count < MAX_ARGS - 1) {
        args[count++] = token;
        token = strtok(NULL, " \t\n\r");
    }
    args[count] = NULL;
    return count;
}

/* Обробка вбудованих команд у батьківському процесі */
static int handle_builtin(char **args) {
    if (args[0] == NULL) return 1;
    
    if (strcmp(args[0], "exit") == 0) {
        exit(0);
    }
    if (strcmp(args[0], "cd") == 0) {
        const char *dir = args[1] ? args[1] : getenv("HOME");
        if (!dir) dir = "/";
        if (chdir(dir) != 0) {
            perror("mini-shell: cd");
        }
        return 1; /* Оброблено як builtin */
    }
    return 0; /* Зовнішня команда */
}

/* Виконання одиничної зовнішньої команди */
static void execute_simple_command(char **args) {
    pid_t pid = fork();
    if (pid < 0) {
        perror("mini-shell: fork failed");
        return;
    }
    if (pid == 0) {
        /* Дочірній процес */
        execvp(args[0], args);
        perror("mini-shell: execvp failed");
        exit(127);
    } else {
        /* Батьківський процес чекає завершення */
        int status;
        waitpid(pid, &status, 0);
    }
}

/* Виконання конвеєра з двох команд: cmd1 | cmd2 */
static void execute_pipeline(char **cmd1_args, char **cmd2_args) {
    int pipefd[2];
    if (pipe(pipefd) < 0) {
        perror("mini-shell: pipe failed");
        return;
    }

    /* Створення першого дочірнього процесу (cmd1) */
    pid_t pid1 = fork();
    if (pid1 == 0) {
        /* Перенаправляємо stdout у pipe write end */
        dup2(pipefd[1], STDOUT_FILENO);
        close(pipefd[0]);
        close(pipefd[1]);
        execvp(cmd1_args[0], cmd1_args);
        perror("mini-shell: execvp cmd1 failed");
        exit(127);
    }

    /* Створення другого дочірнього процесу (cmd2) */
    pid_t pid2 = fork();
    if (pid2 == 0) {
        /* Перенаправляємо stdin з pipe read end */
        dup2(pipefd[0], STDIN_FILENO);
        close(pipefd[0]);
        close(pipefd[1]);
        execvp(cmd2_args[0], cmd2_args);
        perror("mini-shell: execvp cmd2 failed");
        exit(127);
    }

    /* Батьківський процес обов'язково закриває свої копії дескрипторів каналу */
    close(pipefd[0]);
    close(pipefd[1]);

    /* Очікування завершення обох дочірніх процесів */
    int status;
    waitpid(pid1, &status, 0);
    waitpid(pid2, &status, 0);
}

int main(void) {
    char line[MAX_LINE];

    while (1) {
        printf("mini-shell> ");
        fflush(stdout);

        if (!fgets(line, sizeof(line), stdin)) {
            break; /* EOF (Ctrl+D) */
        }

        /* Пошук символу конвеєра '|' */
        char *pipe_pos = strchr(line, '|');
        if (pipe_pos != NULL) {
            *pipe_pos = '\0';
            char *left_part = line;
            char *right_part = pipe_pos + 1;

            char *cmd1_args[MAX_ARGS];
            char *cmd2_args[MAX_ARGS];

            if (tokenize(left_part, cmd1_args) > 0 && tokenize(right_part, cmd2_args) > 0) {
                execute_pipeline(cmd1_args, cmd2_args);
            }
        } else {
            char *args[MAX_ARGS];
            if (tokenize(line, args) > 0) {
                if (!handle_builtin(args)) {
                    execute_simple_command(args);
                }
            }
        }
    }

    printf("\nGoodbye!\n");
    return 0;
}
```
```cpp
// mini_shell.cpp — Ідіоматична C++20 реалізація з RAII-обгортками дескрипторів
#include <iostream>
#include <string>
#include <vector>
#include <string_view>
#include <sstream>
#include <memory>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

namespace shell {

// RAII обгортка для безпечного керування файловими дескрипторами POSIX
class UniqueFd {
    int fd_{-1};
public:
    constexpr UniqueFd() noexcept = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

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
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

// Розбиття рядка на токени без сирого malloc
static std::vector<std::string> tokenize(std::string_view line) {
    std::vector<std::string> tokens;
    std::istringstream iss{std::string(line)};
    std::string token;
    while (iss >> token) {
        tokens.push_back(token);
    }
    return tokens;
}

// Перетворення std::vector<std::string> у char* array для execvp
class ExecArgs {
    std::vector<char*> ptrs_;
public:
    explicit ExecArgs(const std::vector<std::string>& args) {
        ptrs_.reserve(args.size() + 1);
        for (const auto& arg : args) {
            ptrs_.push_back(const_cast<char*>(arg.c_str()));
        }
        ptrs_.push_back(nullptr);
    }

    [[nodiscard]] char** data() noexcept { return ptrs_.data(); }
};

// Перевірка та виконання вбудованих команд
static bool handle_builtin(const std::vector<std::string>& args) {
    if (args.empty()) return true;

    if (args[0] == "exit") {
        std::exit(0);
    }
    if (args[0] == "cd") {
        std::string dir = (args.size() > 1) ? args[1] : (::getenv("HOME") ? ::getenv("HOME") : "/");
        if (::chdir(dir.c_str()) != 0) {
            std::perror("mini-shell: cd failed");
        }
        return true;
    }
    return false;
}

// Виконання одиночної команди
static void execute_simple(const std::vector<std::string>& args) {
    ExecArgs exec_args{args};
    pid_t pid = ::fork();
    if (pid < 0) {
        std::perror("mini-shell: fork failed");
        return;
    }
    if (pid == 0) {
        ::execvp(exec_args.data()[0], exec_args.data());
        std::perror("mini-shell: execvp failed");
        std::exit(127);
    }

    int status = 0;
    ::waitpid(pid, &status, 0);
}

// Виконання конвеєра з двох команд з автоматичним закриттям RAII дескрипторів
static void execute_pipeline(const std::vector<std::string>& cmd1, const std::vector<std::string>& cmd2) {
    int pipe_raw[2];
    if (::pipe(pipe_raw) < 0) {
        std::perror("mini-shell: pipe failed");
        return;
    }

    UniqueFd read_end{pipe_raw[0]};
    UniqueFd write_end{pipe_raw[1]};

    pid_t pid1 = ::fork();
    if (pid1 == 0) {
        ::dup2(write_end.get(), STDOUT_FILENO);
        read_end.reset();
        write_end.reset();

        ExecArgs exec_args1{cmd1};
        ::execvp(exec_args1.data()[0], exec_args1.data());
        std::perror("mini-shell: execvp cmd1 failed");
        std::exit(127);
    }

    pid_t pid2 = ::fork();
    if (pid2 == 0) {
        ::dup2(read_end.get(), STDIN_FILENO);
        read_end.reset();
        write_end.reset();

        ExecArgs exec_args2{cmd2};
        ::execvp(exec_args2.data()[0], exec_args2.data());
        std::perror("mini-shell: execvp cmd2 failed");
        std::exit(127);
    }

    // Завдяки RAII дескриптори батька закриються автоматично при виході UniqueFd з області видимості
    read_end.reset();
    write_end.reset();

    int status1 = 0, status2 = 0;
    ::waitpid(pid1, &status1, 0);
    ::waitpid(pid2, &status2, 0);
}

} // namespace shell

int main() {
    std::string line;
    while (true) {
        std::cout << "mini-shell> " << std::flush;
        if (!std::getline(std::cin, line)) {
            break;
        }

        auto pipe_pos = line.find('|');
        if (pipe_pos != std::string::npos) {
            auto left = line.substr(0, pipe_pos);
            auto right = line.substr(pipe_pos + 1);

            auto cmd1 = shell::tokenize(left);
            auto cmd2 = shell::tokenize(right);

            if (!cmd1.empty() && !cmd2.empty()) {
                shell::execute_pipeline(cmd1, cmd2);
            }
        } else {
            auto args = shell::tokenize(line);
            if (!args.empty() && !shell::handle_builtin(args)) {
                shell::execute_simple(args);
            }
        }
    }
    std::cout << "\nGoodbye!\n";
    return 0;
}
```
:::

## 3. Критичні системні аспекти оркестрації процесів

При детальному аналізі коду оркестратора важливо звернути увагу на чотири фундаментальні системні аспекти, порушення яких призводить до критичних помилок або зависань у реальних системах:

1. **Необхідність закриття вихідного кінця pipe у батьківському процесі:**
   Якщо батьківський процес оболонки не закриє свою копію `pipefd[1]` (кінець запису) після завершення системних викликів `fork()`, лічильник посилань ядра Linux на цей файловий дескриптор залишатиметься більшим за нуль. У результаті команда `cmd2` (яка читає з іншого кінця каналу `pipefd[0]`) після завершення роботи `cmd1` ніколи не отримає символ кінця файлу EOF (повернення 0 байтів від `read()`). Процес `cmd2` назавжди зависне у стані очікування читання з порожнього каналу.

2. **Виконання вбудованих команд без створення дочірнього процесу:**
   Команди управления станом оболонки (такі як `cd`, `exit`, `export`, `alias`, `umask`) повинні виконуватися безпосередньо у процесі самої оболонки. Наприклад, системний виклик `chdir()` змінює поточний робочий каталог лише для того процесу, який його викликав, та його майбутніх нащадків. Якби оболонка створила дочірній процес для виконання `cd`, каталог було б змінено у тимчасовому нащадку, який відразу ж вивантажився б через `exit()`, залишивши батьківську оболонку у початковому каталозі.

3. **Атомарність заміни дескрипторів через dup2():**
   Системний виклик `dup2(oldfd, newfd)` виконано так, що якщо дескриптор `newfd` уже був відкритий (наприклад, стандартний вивід FD 1, який за умовчанням вказував на термінал `/dev/pts/X`), ядро атомарно закриває його і копіює посилання `oldfd` у комірку `newfd` таблиці файлових дескрипторів процесу. Це гарантує відсутність гонки даних (race conditions) при комутації потоків.

4. **Розподіл обов'язків між execvp() та PATH:**
   Функція системного рівня `execvp()` приймає назву бинарного файлу і масив рядкових аргументів. Вона автоматично обходить усі каталоги, перелічені у системній змінній середовища `PATH`, шукаючи відповідний виконуваний файл з правами на виконання. Якщо файл знайдено і він має ELF-заголовок, ядро замінює образ пам'яті процесу новим кодом. Якщо ж файл виявляється текстовим скриптом без ELF-магічного числа, `execve` повертає помилку `ENOEXEC`, і оболонка пробує передати цей файл на вхід `/bin/sh`.

## 4. Переваги RAII обгортки UniqueFd у C++ порівняно з POSIX C

У стандартному коді мовою C будь-яке аварійне завершення або помилка у системних викликах між `pipe()` та `execvp()` вимагає ручного переходу на мітку очистки ресурсу (`goto cleanup;`), щоб закрити відкриті файлові дескриптори. Невжиття такого закриття призводить до системного витоку дескрипторів у довготривалих процесах.

У C++ реалізації використання спеціального класу `UniqueFd` розв'язує цю проблему на рівні мовних гарантій:
- Деструктор `~UniqueFd()` автоматично викликає `close()` для дескриптора при виході об'єкта з області видимості (даже якщо було згенеровано виняток або виконано ранній `return`).
- Семантика переміщення (`std::move`) забороняє копіювання файлового дескриптора, запобігаючи подвійному закриттю одного й того ж системного ресурсу (`double close`).
- Метод `release()` дозволяє передати володіння дескриптором системним викликам `dup2()`, не викликаючи закриття в деструкторі.

Такий підхід забезпечує абсолютну виняткову безпеку (exception safety) при побудові складних системних оркестраторів простору користувача.
