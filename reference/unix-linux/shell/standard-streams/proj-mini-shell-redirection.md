# ⚙️ Практична реалізація перенаправлення потоків та конвеєрів

Ця практична вставка детально розбирає побудову системного механізму перенаправлення стандартних потоків `0`, `1`, `2` та реалізацію двохкомпонентного міжпроцесного каналу (`cmd1 | cmd2`) мовами C та C++.

Наведений проект демонструє, як командна оболонка (Shell) керує дескрипторами процесів на рівні системних викликів POSIX, запобігає витіканню ресурсів, обробляє сигнали переривання та гарантує коректне очищення буферів користувацького простору.

## 1. Архітектурні принципи та підводні камені

Реалізація перенаправлення потоків вимагає строгого дотримання фундаментальних правил системного програмування в Unix:

### Очищення буферів перед розгалуженням (`fork()`)
Бібліотека `libc` утримує власні буфери пам'яті у просторі користувача для вихідних потоків `stdout` та `stderr`. Якщо програма записує дані через `printf()` або `std::cout`, ці дані залишаються в буфері до тих пір, поки потік не буде скинуто. 

Коли програма викликає `fork()`, ядро створює повну копію адресного простору процесу, включно з незавершеними буферами `libc`. Якщо не очистити буфери примусово через `fflush(NULL)` або `std::cout.flush()` **до виклику `fork()`**, і батьківський, і дочірній процеси згодом скинуть один і той самий буфер на диск, що призведе до задубльованих записів у файлах.

### Закриття дублюючих файлових дескрипторів
Коли процес відкриває файл за допомогою `open()` або створює канал за допомогою `pipe()`, він отримує нові дескриптори (наприклад, `3` та `4`). Після того як виклик `dup2(3, 1)` перенаправляє дескриптор `1` на той самий файл, **оригінальний дескриптор `3` повинен бути негайно закритий викликом `close(3)`**. 

Якщо цього не зробити, процес буде тримати зайве посилання на файл. У випадку з міжпроцесним каналом (`pipe`), якщо дочірній процес-читач залишить відкритим свій кінець каналу для запису (`pipefd[1]`), виклик `read()` на каналі **ніколи не поверне `0` (EOF)**, оскільки ядро бачитиме принаймні одного потенційного письменника. У результаті програма зависне в очікуванні даних назавжди.

### Атомарність `dup2()` проти стану гонитви
У старих Unix-системах перенаправлення іноді записували як послідовність викликів `close(1); dup(fd);`. Однак ця послідовність містить небезпечний стан гонитви (race condition): якщо між викликами `close(1)` та `dup(fd)` у багатопотоковій програмі інший потік виконає системний виклик `open()` або `socket()`, ядро віддасть вивільнений дескриптор `1` цьому новому файлу, зруйнувавши логіку перенаправлення.

Виклик `dup2(oldfd, newfd)` позбавлений цього недоліку: він закриває `newfd` і призначає йому новий файл **атомарно всередині ядра під захистом внутрішніх блокувань**.

### Використання `_exit()` у дочірньому процесі
Якщо у дочірньому процесі виклик `execvp()` зазнає невдачі (наприклад, вказаний виконуваний файл не знайдено), дочірній процес **не повинен викликати звичайну функцію `exit()`**. Звичайна `exit()` запускає обробники `atexit()` та скидає буфери `libc`, які були успадковані від батьківського процесу, що може призвести до повторного запису даних. Дочірній процес у разі помилки виклику `exec` зобов'язаний негайно завершувати роботу через системний виклик `_exit(code)`.

## 2. Відстеження системних викликів за допомогою `strace`

Щоб побачити, як ядро обробляє маніпуляції з дескрипторами під час виконання перенаправлення, виконаємо утиліту під керуванням `strace`:

```text
execve("./mini_shell", ["./mini_shell"], 0x7ffc...) = 0
write(1, "[C] Тестування перенаправлення\n", 56) = 56
pipe2([3, 4], 0)                        = 0
clone(child_stack=NULL, flags=CLONE_CHILD_CLEARTID|...) = 4102
clone(child_stack=NULL, flags=CLONE_CHILD_CLEARTID|...) = 4103
[pid 4102] close(3)                     = 0
[pid 4102] dup2(4, 1)                   = 1
[pid 4102] close(4)                     = 0
[pid 4102] execve("/bin/ls", ["ls", "-la", "/"], ...) = 0
[pid 4103] close(4)                     = 0
[pid 4103] dup2(3, 0)                   = 0
[pid 4103] close(3)                     = 0
[pid 4103] execve("/bin/grep", ["grep", "etc"], ...) = 0
close(3)                                = 0
close(4)                                = 0
wait4(4102, [{WIFEXITED(s) && WEXITSTATUS(s) == 0}], 0, NULL) = 4102
wait4(4103, [{WIFEXITED(s) && WEXITSTATUS(s) == 0}], 0, NULL) = 4103
```

У трасуванні чітко видно послідовність кроків ядра:
1. `pipe2([3, 4], 0)` створює дескриптори `3` (читання) та `4` (запис).
2. Процес `4102` (письменник) закриває читальний дескриптор `3`, виконує `dup2(4, 1)`, замінюючи `1` на дескриптор каналу, і закриває оригінал `4`.
3. Процес `4103` (читач) закриває писальний дескриптор `4`, виконує `dup2(3, 0)`, замінюючи `0` на читальний дескриптор каналу, і закриває `3`.
4. Батьківський процес закриває дескриптори `3` і `4` у своєму просторі й очікує дочірніх процесів через `wait4()`.

## 3. Обробка сигналу SIGPIPE та передчасний вихід читача

Коли дві програми об'єднуються у конвеєр `cmd1 | cmd2`, може виникнути ситуація, коли друга програма (`cmd2`) завершує роботу раніше, ніж перша (`cmd1`). Наприклад, у конвеєрі `cat huge_log.txt | head -n 5` утиліта `head` прочитає перші 5 рядків і відразу закриє свій стандартний вхід (`STDIN_FILENO`), закриваючи читальний кінець каналу.

Коли утиліта `cat` спробує виконати наступний системний виклик `write(1, buf, len)` у писальний кінець закритого каналу, ядро виконає наступні дії:
1. Системний виклик `write()` негайно завершиться з помилкою, а `errno` буде встановлено у значення `EPIPE` (Broken pipe).
2. Ядро надішле процесу `cat` сигнал `SIGPIPE`.
3. За замовчуванням обробник сигналу `SIGPIPE` негайно завершує процес `cat`.

Якщо ваша програма розробляє власну систему перенаправлення, вона повинна або коректно обробляти сигнал `SIGPIPE` (встановлюючи `signal(SIGPIPE, SIG_IGN)`), або бути готовою отримати помилку `EPIPE` від виклику `write()`.

## 4. Запобігання витіканню дескрипторів за допомогою `O_CLOEXEC`

У багатопотокових серверах створення каналу за допомогою звичайного `pipe()` створює загрозу витікання ресурсів. Якщо потік A виконує `pipe()`, а в цей же мілісекундний проміжок потік B виконує `fork()` і `execve()` для запуску стороннього процесу, цей сторонній процес успадкує відкриті дескриптори каналу потоку A.

Для усунення цієї проблеми в Linux реалізовано системний виклик `pipe2()`, який дозволяє передати прапорець `O_CLOEXEC`:

:::tabs
```c
int pipefd[2];
if (pipe2(pipefd, O_CLOEXEC) < 0) {
    perror("pipe2 failed");
}
```
```cpp
int pipefd[2];
if (::pipe2(pipefd, O_CLOEXEC) < 0) {
    throw std::system_error(errno, std::generic_category(), "pipe2 failed");
}
```
:::

Прапорець `O_CLOEXEC` гарантує, що дескриптори каналу будуть атомарно позначені для автоматичного закриття при будь-якому виклику `execve()`, усуваючи загрозу витікання дескрипторів у паралельних потоках.

## 5. Повна реалізація перенаправлення та конвеєрів

Нижче наведено ідіоматичні реалізації перенаправлення потоків та міжпроцесного конвеєра мовами C та C++.

Версія C використовує прямі системні виклики та низькорівневе керування дескрипторами. Версія C++ застосовує ідіому **RAII** (`sys::FileDescriptor`), автоматичне управління ресурсами та стандартні винятки.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <errno.h>

// Виконання однієї команди з перенаправленням stdout у файл
int run_with_stdout_redirect(const char *cmd, char *const argv[], const char *filepath) {
    // 1. Очищаємо всі користувацькі буфери stdio перед розгалуженням!
    if (fflush(NULL) != 0) {
        perror("fflush failed");
        return -1;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork failed");
        return -1;
    }

    if (pid == 0) {
        // Дочірній процес: відкриваємо файл для запису
        int fd = open(filepath, O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (fd < 0) {
            perror("open output file failed");
            _exit(1);
        }

        // Атомарно перенаправляємо STDOUT_FILENO (1) на відкритий файл
        if (dup2(fd, STDOUT_FILENO) < 0) {
            perror("dup2 failed");
            close(fd);
            _exit(1);
        }

        // Закриваємо оригінальний дескриптор, оскільки 1 тепер вказує на цей файл
        close(fd);

        // Замінюємо образ процесу цільовою програмою
        execvp(cmd, argv);
        
        // Сюди код потрапляє лише у разі помилки execvp
        perror("execvp failed");
        _exit(127);
    }

    // Батьківський процес чекає на завершення дочірнього з обробкою EINTR
    int status = 0;
    while (waitpid(pid, &status, 0) < 0) {
        if (errno != EINTR) {
            return -1;
        }
    }

    return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
}

// Виконання двокомпонентного конвеєра: cmd1_argv | cmd2_argv
int run_pipeline(char *const cmd1_argv[], char *const cmd2_argv[]) {
    // Очищаємо буфери перед створенням процесів
    fflush(NULL);

    int pipefd[2];
    if (pipe(pipefd) < 0) {
        perror("pipe creation failed");
        return -1;
    }

    // Створюємо перший дочірній процес (Письменник)
    pid_t pid1 = fork();
    if (pid1 < 0) {
        perror("fork pid1 failed");
        close(pipefd[0]);
        close(pipefd[1]);
        return -1;
    }

    if (pid1 == 0) {
        // Дочірній процес 1: читальний кінець йому не потрібен
        close(pipefd[0]);

        // Перенаправляємо stdout у писальний кінець каналу (pipefd[1])
        if (dup2(pipefd[1], STDOUT_FILENO) < 0) {
            perror("dup2 pid1 failed");
            _exit(1);
        }
        close(pipefd[1]);

        execvp(cmd1_argv[0], cmd1_argv);
        perror("execvp cmd1 failed");
        _exit(127);
    }

    // Створюємо другий дочірній процес (Читач)
    pid_t pid2 = fork();
    if (pid2 < 0) {
        perror("fork pid2 failed");
        close(pipefd[0]);
        close(pipefd[1]);
        return -1;
    }

    if (pid2 == 0) {
        // Дочірній процес 2: писальний кінець йому не потрібен
        close(pipefd[1]);

        // Перенаправляємо stdin на читальний кінець каналу (pipefd[0])
        if (dup2(pipefd[0], STDIN_FILENO) < 0) {
            perror("dup2 pid2 failed");
            _exit(1);
        }
        close(pipefd[0]);

        execvp(cmd2_argv[0], cmd2_argv);
        perror("execvp cmd2 failed");
        _exit(127);
    }

    // Критичний момент: батьківський процес ПОВИНЕН закрити обидва кінці каналу!
    close(pipefd[0]);
    close(pipefd[1]);

    // Очікуємо на завершення обох дочірніх процесів
    int status1 = 0, status2 = 0;
    while (waitpid(pid1, &status1, 0) < 0) {
        if (errno != EINTR) break;
    }
    while (waitpid(pid2, &status2, 0) < 0) {
        if (errno != EINTR) break;
    }

    return WIFEXITED(status2) ? WEXITSTATUS(status2) : -1;
}

int main(void) {
    printf("[C] Тестування перенаправлення stdout у файл result.txt...\n");
    char *args_ls[] = {"ls", "-l", "/", NULL};
    if (run_with_stdout_redirect("ls", args_ls, "result.txt") == 0) {
        printf("[C] Успішно збережено виведення ls у result.txt\n");
    }

    printf("[C] Тестування конвеєра: ls -la / | grep etc...\n");
    char *cmd1[] = {"ls", "-la", "/", NULL};
    char *cmd2[] = {"grep", "etc", NULL};
    run_pipeline(cmd1, cmd2);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <stdexcept>
#include <system_error>
#include <cerrno>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>

namespace sys {

// RAII-обгортка для безпечного керування файловими дескрипторами ядра
class FileDescriptor {
    int fd_{-1};
public:
    constexpr FileDescriptor() noexcept = default;
    explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
    
    ~FileDescriptor() { reset(); }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.release()) {}
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
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

class PipelineExecutor {
public:
    // Запуск програми з перенаправленням stdout у файл
    static void redirect_stdout_to_file(const std::string& cmd,
                                        const std::vector<std::string>& args,
                                        const std::string& output_filepath) {
        // 1. Очищення буферів C++ streams та C libc перед fork
        std::cout.flush();
        std::cerr.flush();
        ::fflush(nullptr);

        pid_t pid = ::fork();
        if (pid < 0) {
            throw std::system_error(errno, std::generic_category(), "fork failed");
        }

        if (pid == 0) {
            // Дочірній процес
            FileDescriptor file_fd(::open(output_filepath.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0644));
            if (!file_fd.valid()) {
                ::perror("open output file failed");
                ::_exit(1);
            }

            if (::dup2(file_fd.get(), STDOUT_FILENO) < 0) {
                ::perror("dup2 failed");
                ::_exit(1);
            }
            file_fd.reset(); // RAII закриває початковий FD

            // Формуємо масив аргументів C-style для execvp
            std::vector<char*> c_argv;
            c_argv.reserve(args.size() + 2);
            c_argv.push_back(const_cast<char*>(cmd.c_str()));
            for (const auto& arg : args) {
                c_argv.push_back(const_cast<char*>(arg.c_str()));
            }
            c_argv.push_back(nullptr);

            ::execvp(cmd.c_str(), c_argv.data());
            ::perror("execvp failed");
            ::_exit(127);
        }

        int status = 0;
        while (::waitpid(pid, &status, 0) < 0) {
            if (errno != EINTR) {
                throw std::system_error(errno, std::generic_category(), "waitpid failed");
            }
        }

        if (WIFEXITED(status) && WEXITSTATUS(status) != 0) {
            throw std::runtime_error("Process exited with non-zero code: " + 
                                     std::to_string(WEXITSTATUS(status)));
        }
    }

    // Запуск двох програм через міжпроцесний канал (cmd1 | cmd2)
    static void execute_pipeline(const std::string& cmd1, const std::vector<std::string>& args1,
                                 const std::string& cmd2, const std::vector<std::string>& args2) {
        std::cout.flush();
        std::cerr.flush();
        ::fflush(nullptr);

        int raw_pipe[2];
        if (::pipe(raw_pipe) < 0) {
            throw std::system_error(errno, std::generic_category(), "pipe failed");
        }

        FileDescriptor pipe_read(raw_pipe[0]);
        FileDescriptor pipe_write(raw_pipe[1]);

        pid_t pid1 = ::fork();
        if (pid1 < 0) {
            throw std::system_error(errno, std::generic_category(), "fork pid1 failed");
        }

        if (pid1 == 0) {
            pipe_read.reset(); // Закриваємо читальний кінець

            if (::dup2(pipe_write.get(), STDOUT_FILENO) < 0) {
                ::perror("dup2 write failed");
                ::_exit(1);
            }
            pipe_write.reset();

            std::vector<char*> c_argv1;
            c_argv1.push_back(const_cast<char*>(cmd1.c_str()));
            for (const auto& a : args1) c_argv1.push_back(const_cast<char*>(a.c_str()));
            c_argv1.push_back(nullptr);

            ::execvp(cmd1.c_str(), c_argv1.data());
            ::_exit(127);
        }

        pid_t pid2 = ::fork();
        if (pid2 < 0) {
            throw std::system_error(errno, std::generic_category(), "fork pid2 failed");
        }

        if (pid2 == 0) {
            pipe_write.reset(); // Закриваємо писальний кінець

            if (::dup2(pipe_read.get(), STDIN_FILENO) < 0) {
                ::perror("dup2 read failed");
                ::_exit(1);
            }
            pipe_read.reset();

            std::vector<char*> c_argv2;
            c_argv2.push_back(const_cast<char*>(cmd2.c_str()));
            for (const auto& a : args2) c_argv2.push_back(const_cast<char*>(a.c_str()));
            c_argv2.push_back(nullptr);

            ::execvp(cmd2.c_str(), c_argv2.data());
            ::_exit(127);
        }

        // Батьківський процес закриває свої RAII дескриптори каналу
        pipe_read.reset();
        pipe_write.reset();

        int status1 = 0, status2 = 0;
        while (::waitpid(pid1, &status1, 0) < 0) {
            if (errno != EINTR) break;
        }
        while (::waitpid(pid2, &status2, 0) < 0) {
            if (errno != EINTR) break;
        }
    }
};

} // namespace sys

int main() {
    try {
        std::cout << "[C++] Виконання перенаправлення через RAII обгортку...\n";
        sys::PipelineExecutor::redirect_stdout_to_file("uname", {"-a"}, "system_info.txt");
        std::cout << "[C++] Успішно збережено систему в system_info.txt\n";

        std::cout << "[C++] Виконання C++ конвеєра: ls -la / | grep dev...\n";
        sys::PipelineExecutor::execute_pipeline("ls", {"-la", "/"}, "grep", {"dev"});
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::
