# ⚙️ Практикум: побудова N-рівневого конвеєра та керування процесами у Unix

У цій практичній вставці показано повну реалізацію конвеєра довільної довжини (від першого процесу P1 через канали pipe1, pipe2 до останнього процесу PN), подібну до тієї, яку виконує командна оболонка (shell) під час виклику ланцюжка команд на кшталт `cat log.txt | grep ERROR | wc -l`.

## 1. Детальний алгоритм побудови та життєвий цикл

Для надійного запуску конвеєра з N команд необхідно суворо дотримуватися послідовності кроків створення ресурсів ядра та керування процесами:

### Крок 1: Виділення та створення каналів

Загальна кількість каналів для передачі даних між N сусідніми процесами становить точно N - 1. Створення каналів виконується у батьківському процесі до виклику функцій розгалуження `fork()`. 

Для запобігання витікання дескрипторів у багатопотоковому середовищі рекомендується використовувати виклик `pipe2()` із прапорцем `O_CLOEXEC`. Це гарантує, що дескриптори закриються автоматично під час системного виклику `execve()`.

### Крок 2: Розгалуження процесів у циклі

У циклі від 0 до N - 1 батьківський процес створює дочірній процес через `fork()`. 

Ідентифікатор створеного дочірнього процесу (PID) зберігається у масиві для подальшого очікування його завершення та перевірки кодів повернення.

### Крок 3: Налаштування файлових дескрипторів у кожній дочірній гілці

У кожному дочірньому процесі з номером i виконуються наступні маніпуляції:

1. **Підключення вхідного потоку:** Якщо i > 0 (це не перший процес конвеєра), процес підключає свій стандартний вхід `stdin` (дескриптор 0) до каналу читання попереднього ступеня `pipes[i - 1][0]` за допомогою виклику `dup2()`.
2. **Підключення вихідного потоку:** Якщо i < N - 1 (це не останній процес конвеєра), процес підключає свій стандартний вивід `stdout` (дескриптор 1) до каналу запису поточного ступеня `pipes[i][1]` за допомогою виклику `dup2()`.
3. **Очищення таблиці дескрипторів:** Процес закриває **абсолютно всі** оригінальні дескриптори каналів з масиву `pipes`. Це фундаментальне правило безпеки системного програмування: залишення хоча б одного незакритого дескриптора на запис призведе до того, що читач наступного ступеня ніколи не отримає символ кінця файлу (`EOF`) і конвеєр висітиме у стані взаємного блокування (deadlock).
4. **Запуск програми:** Процес викликає функцію сімейства `exec()` (наприклад, `execvp()`), яка підміняє поточний процес новим бінарним образом.

### Крок 4: Закриття дескрипторів у батьківському процесі

Одразу після завершення циклу створення дочірніх процесів батьківський процес **зобов'язаний закрити всі кінці всіх каналів у своїй власній таблиці дескрипторів**. 

Батьківський процес не бере участі у зчитуванні чи записі даних каналу; його задача полягає виключно у виклику `waitpid()` та отриманні кодів повернення. Якщо батько забудькувато залишить записувальний кінець каналу відкритим, лічильник посилань ядра не обнулиться навіть після завершення всіх процесів-письменників, і читачі конвеєра заблокуються назавжди.

### Крок 5: Синхронізація та збір кодів повернення

Батьківський процес у циклі викликає `waitpid()` для кожного створеного PID. Бажано очікувати процеси у порядку їх створення або обробляти їх у довільному порядку через `wait()`.

Статусом завершення всього конвеєра за замовчуванням вважається код виходу останнього процесу N - 1.

---

## 2. Реалізація N-ступеневого конвеєра мовами C та C++

Нижче наведено повністю робочу та ідіоматичну реалізацію алгоритму мовами C та C++ з використанням обгортання ресурсів (RAII) та викликів POSIX.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <string.h>
#include <fcntl.h>

// Структура опису окремої команди у конвеєрі
typedef struct {
    char **argv; // Масив аргументів (закінчується NULL)
} command_t;

int execute_pipeline(command_t *cmds, size_t num_cmds) {
    if (num_cmds == 0) return 0;

    // Створюємо масив каналів (num_cmds - 1 каналів)
    int (*pipes)[2] = NULL;
    if (num_cmds > 1) {
        pipes = malloc(sizeof(int[2]) * (num_cmds - 1));
        if (!pipes) {
            perror("malloc failed");
            return -1;
        }

        for (size_t i = 0; i < num_cmds - 1; ++i) {
            if (pipe2(pipes[i], O_CLOEXEC) == -1) {
                perror("pipe2 failed");
                free(pipes);
                return -1;
            }
        }
    }

    pid_t *pids = malloc(sizeof(pid_t) * num_cmds);
    if (!pids) {
        perror("malloc pids failed");
        if (pipes) free(pipes);
        return -1;
    }

    for (size_t i = 0; i < num_cmds; ++i) {
        pids[i] = fork();
        if (pids[i] == -1) {
            perror("fork failed");
            break;
        }

        if (pids[i] == 0) {
            // --- ДОЧІРНІЙ ПРОЦЕС i ---

            // 1. Вхідний потік (stdin)
            if (i > 0) {
                if (dup2(pipes[i - 1][0], STDIN_FILENO) == -1) {
                    perror("dup2 stdin failed");
                    exit(EXIT_FAILURE);
                }
            }

            // 2. Вихідний потік (stdout)
            if (i < num_cmds - 1) {
                if (dup2(pipes[i][1], STDOUT_FILENO) == -1) {
                    perror("dup2 stdout failed");
                    exit(EXIT_FAILURE);
                }
            }

            // 3. Закриваємо УСІ канали у дочірньому процесі
            if (pipes) {
                for (size_t j = 0; j < num_cmds - 1; ++j) {
                    close(pipes[j][0]);
                    close(pipes[j][1]);
                }
            }

            // 4. Виконуємо команду
            execvp(cmds[i].argv[0], cmds[i].argv);
            perror("execvp failed");
            exit(EXIT_FAILURE);
        }
    }

    // --- БАТЬКІВСЬКИЙ ПРОЦЕС ---
    // Закриваємо всі кінці каналів у батька!
    if (pipes) {
        for (size_t j = 0; j < num_cmds - 1; ++j) {
            close(pipes[j][0]);
            close(pipes[j][1]);
        }
        free(pipes);
    }

    // Чекаємо завершення усіх створених дочірніх процесів
    int last_status = 0;
    for (size_t i = 0; i < num_cmds; ++i) {
        if (pids[i] > 0) {
            int status = 0;
            waitpid(pids[i], &status, 0);
            if (i == num_cmds - 1) {
                last_status = status;
            }
        }
    }

    free(pids);
    return WIFEXITED(last_status) ? WEXITSTATUS(last_status) : -1;
}

int main(void) {
    // Еквівалент командного рядка: ls -l | grep txt | wc -l
    char *cmd1[] = {"ls", "-l", NULL};
    char *cmd2[] = {"grep", "txt", NULL};
    char *cmd3[] = {"wc", "-l", NULL};

    command_t pipeline[] = {
        {.argv = cmd1},
        {.argv = cmd2},
        {.argv = cmd3}
    };

    printf("Executing pipeline: ls -l | grep txt | wc -l\n");
    int exit_code = execute_pipeline(pipeline, 3);
    printf("Pipeline finished with exit code: %d\n", exit_code);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <array>
#include <memory>
#include <system_error>
#include <unistd.h>
#include <sys/wait.h>
#include <fcntl.h>

class ScopedPipe {
public:
    ScopedPipe() {
        if (::pipe2(fds_.data(), O_CLOEXEC) == -1) {
            throw std::system_error(errno, std::generic_category(), "pipe2 failed");
        }
    }

    ~ScopedPipe() {
        close_read();
        close_write();
    }

    ScopedPipe(const ScopedPipe&) = delete;
    ScopedPipe& operator=(const ScopedPipe&) = delete;

    ScopedPipe(ScopedPipe&& other) noexcept : fds_(other.fds_) {
        other.fds_ = {-1, -1};
    }

    int read_fd() const noexcept { return fds_[0]; }
    int write_fd() const noexcept { return fds_[1]; }

    void close_read() noexcept {
        if (fds_[0] != -1) {
            ::close(fds_[0]);
            fds_[0] = -1;
        }
    }

    void close_write() noexcept {
        if (fds_[1] != -1) {
            ::close(fds_[1]);
            fds_[1] = -1;
        }
    }

private:
    std::array<int, 2> fds_{-1, -1};
};

struct Command {
    std::string program;
    std::vector<std::string> args;

    std::vector<char*> to_argv() const {
        std::vector<char*> argv;
        argv.push_back(const_cast<char*>(program.c_str()));
        for (const auto& arg : args) {
            argv.push_back(const_cast<char*>(arg.c_str()));
        }
        argv.push_back(nullptr);
        return argv;
    }
};

int execute_cpp_pipeline(const std::vector<Command>& commands) {
    if (commands.empty()) return 0;

    const std::size_t n = commands.size();
    std::vector<ScopedPipe> pipes;
    pipes.reserve(n - 1);
    for (std::size_t i = 0; i < n - 1; ++i) {
        pipes.emplace_back();
    }

    std::vector<pid_t> pids;
    pids.reserve(n);

    for (std::size_t i = 0; i < n; ++i) {
        pid_t pid = ::fork();
        if (pid == -1) {
            throw std::system_error(errno, std::generic_category(), "fork failed");
        }

        if (pid == 0) {
            // --- ДОЧІРНІЙ ПРОЦЕС ---
            if (i > 0) {
                if (::dup2(pipes[i - 1].read_fd(), STDIN_FILENO) == -1) {
                    ::perror("dup2 stdin");
                    ::_exit(EXIT_FAILURE);
                }
            }

            if (i < n - 1) {
                if (::dup2(pipes[i].write_fd(), STDOUT_FILENO) == -1) {
                    ::perror("dup2 stdout");
                    ::_exit(EXIT_FAILURE);
                }
            }

            // Закриваємо дескриптори каналів перед execvp
            for (auto& p : pipes) {
                p.close_read();
                p.close_write();
            }

            auto argv = commands[i].to_argv();
            ::execvp(argv[0], argv.data());
            ::perror("execvp failed");
            ::_exit(EXIT_FAILURE);
        }

        pids.push_back(pid);
    }

    // БАТЬКІВСЬКИЙ ПРОЦЕС: Закриваємо всі дескриптори каналів
    for (auto& p : pipes) {
        p.close_read();
        p.close_write();
    }

    int last_status = 0;
    for (std::size_t i = 0; i < pids.size(); ++i) {
        int status = 0;
        ::waitpid(pids[i], &status, 0);
        if (i == pids.size() - 1) {
            last_status = status;
        }
    }

    return WIFEXITED(last_status) ? WEXITSTATUS(last_status) : -1;
}

int main() {
    std::vector<Command> pipeline = {
        {"cat", {"/etc/passwd"}},
        {"grep", {"bash"}},
        {"wc", {"-l"}}
    };

    try {
        std::cout << "Executing C++ pipeline: cat /etc/passwd | grep bash | wc -l\n";
        int rc = execute_cpp_pipeline(pipeline);
        std::cout << "Pipeline finished with exit code: " << rc << "\n";
    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
```
:::

---

## 3. Аналіз підводних каменів та типізованих помилок

Під час практичної реалізації конвеєрів системні програмісти стикаються з трьома основними категоріями проблем:

### 1. Ресурсний витік файлових дескрипторів (File Descriptor Leaks)

Якщо програма створює конвеєри у циклі без прапорця `O_CLOEXEC` або забудькувато залишає дескриптори відкритими, таблиця дескрипторів швидко вичерпує ліміт `RLIMIT_NOFILE`. Наступний системний виклик `pipe()` або `open()` поверне помилку `EMFILE`. У C++ класах рекомендується використовувати принцип RAII (Resource Acquisition Is Initialization), реалізований у класі `ScopedPipe`, щоб автоматично закривати дескриптори у деструкторі при виході з області видимості.

### 2. Сигнал `SIGPIPE` та неочікуване падіння сервера

Якщо конвеєр є частиною довгопрацюючого демона або сервера, передчасне завершення читача (наприклад, скасування підключення клієнтом) призведе до того, що черговий виклик `write()` у канал згенерує сигнал `SIGPIPE`. За замовчуванням `SIGPIPE` вбиває весь серверний процес. Для запобігання цьому сервер зобов'язаний встановлювати обробник `signal(SIGPIPE, SIG_IGN)` та обробляти помилку `EPIPE` вручну.

### 3. Обіг паніки та очищення у разі помилки `fork()`

Якщо під час створення 5-ступеневого конвеєра виклик `fork()` завершився помилкою на 3-му ступені (наприклад, через вичерпання ліміту процесів у системі `EAGAIN`), батьківський процес зобов'язаний надсилати сигнал `SIGTERM` вже створеним першим двом дочірнім процесам та коректно закрити всі канали, а не залишати у системі осиротілі процеси-"зомбі".

### 4. Робота з прапором `O_NONBLOCK` та обробка `EAGAIN`

При використанні неблокуючих каналів розробник повинен коректно обробляти повернення `EAGAIN` або `EWOULDBLOCK` під час викликів `read()` та `write()`. Часткові записи потребують додаткового буферизатора у просторі користувача для повторної відправки залишків даних.
