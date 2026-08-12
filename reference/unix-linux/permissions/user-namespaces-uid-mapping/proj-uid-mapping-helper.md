# ⚙️ Практичний проєкт: низькорівневе створення User Namespace із мапінгом у C та C++

У цьому проєкті реалізовано низькорівневу системну програму, яка створює новий простір імен користувачів (User Namespace) та налаштовує двонапрямне відображення ідентифікаторів UID та GID без використання сторонніх бібліотек чи високорівневих демонів контейнеризації.

## Архітектура та послідовність міжпроцесної синхронізації

Створення ізольованого середовища з точки зору системного програмування вимагає дотримання чіткої послідовності дій та синхронізації двох процесів: батьківського та дочірнього. 

Справа в тому, що після системного виклику `clone(2)` із прапорцем `CLONE_NEWUSER` дочірній процес відразу починає виконуватися у новому просторі імен. Проте в цей момент правила відображення `/proc/[child_pid]/uid_map` ще відсутні! У результаті дочірній процес має тимчасовий ідентифікатор `65534` (`nobody`) і не має жодних дійсних привілеїв для створення інших просторів імен чи монтування файлових систем.

Для розв'язання цієї проблеми застосовується міжпроцесний канал синхронізації `pipe`:

```text
Батьківський процес (Parent)                  Дочірній процес (Child)
   |                                             |
   |-- 1. pipe()                                 |
   |-- 2. clone(CLONE_NEWUSER) ----------------->| (Створено новий user_ns)
   |                                             |-- 3. read(pipe_fd) [БЛОКУВАННЯ]
   |-- 4. write("/proc/child/setgroups", "deny")  |    (Очікує налаштування мапінгу)
   |-- 5. write("/proc/child/uid_map", "0 1000 1")|
   |-- 6. write("/proc/child/gid_map", "0 1000 1")|
   |-- 7. close(pipe_fd) ----------------------->| (Отримує EOF, відновлює рух)
   |                                             |-- 8. execvp("/bin/sh")
   |-- 9. waitpid()                              |    (Працює як root UID 0)
   v                                             v
```

Покроковий алгоритм міжпроцесної синхронізації розгортається наступним чином:
1. Батьківський процес створює анонімний однонапрямний канал каналізації через виклик `pipe(2)`. Канал повертає два файлові дескриптори: `pipe_fd[0]` для читання та `pipe_fd[1]` для запису.
2. Батьківський процес викликає `clone(2)` з прапорцем `CLONE_NEWUSER`, передаючи вказувач на функцію дочірнього процесу `child_entry` та структуру аргументів, яка містить файлові дескриптори каналу `pipe`.
3. Дочірній процес узагалі не виконує дій із високими привілеями, а відразу закриває дескриптор запису `pipe_fd[1]` і робить блокуюче читання `read(pipe_fd[0], &ch, 1)`. Оскільки у канал нічого не записується, ядро переводить дочірній процес у стан очікування (sleeping/blocked).
4. Батьківський процес у своєму контексті (який володіє необхідним хостовим UID та привілеями) відкриває псевдофайл `/proc/[child_pid]/setgroups` дочірнього процесу і записує рядок `"deny"`. Це є обов'язковою умовою безпеки ядра для непривілейованого налаштування GID.
5. Батьківський процес відкриває `/proc/[child_pid]/uid_map` та записує рядок відображення (наприклад, `0 1000 1`).
6. Батьківський процес відкриває `/proc/[child_pid]/gid_map` та записує рядок відображення групи (наприклад, `0 1000 1`).
7. Після успішного запису всіх три файлів `procfs` батьківський процес закриває свій дескриптор запису `close(pipe_fd[1])`.
8. Закриття останнього дескриптора запису каналу надсилає сигнал EOF (end-of-file) у канал `pipe`. Блокуючий виклик `read()` у дочірньому процесі миттєво повертає `0` байтів.
9. Дочірній процес переконується, що синхронізацію завершено, закриває дескриптор читання `pipe_fd[0]` та виконує `execvp()`, переходячи до роботи з новими ідентифікаторами.

---

## Детальний розбір реалізації у C та C++

Нижче наведено два варіанти реалізації цієї архітектури:
- **Вкладка C**: Класична реалізація з використанням низькорівневих викликів POSIX, сирих масивів під стек, розбору помилок через `errno` та виведення повідомлень через `perror()`.
- **Вкладка C++**: Сучасна ідіоматична реалізація стандарту C++20 з використанням концепції RAII для автоматичного управління файловими дескрипторами, типом `std::expected` для безпечної обробки системних помилок без винятків та `std::format` для форматування рядків.

:::tabs
```c
#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

#define STACK_SIZE (1024 * 1024)

typedef struct {
    int pipe_fd[2];
    uid_t parent_uid;
    gid_t parent_gid;
} child_args_t;

static int write_proc_file(const char *path, const char *content) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        perror("open proc file failed");
        return -1;
    }
    ssize_t len = strlen(content);
    if (write(fd, content, len) != len) {
        perror("write proc file failed");
        close(fd);
        return -1;
    }
    close(fd);
    return 0;
}

static int child_entry(void *arg) {
    child_args_t *args = (child_args_t *)arg;
    char ch;

    // Закриваємо сторону запису pipe у нащадку
    close(args->pipe_fd[1]);

    // Очікуємо сигнал від батька про завершення мапінгу (блокуюче читання)
    if (read(args->pipe_fd[0], &ch, 1) != 0) {
        fprintf(stderr, "Помилка очікування синхронізації у дочірньому процесі\n");
        return 1;
    }
    close(args->pipe_fd[0]);

    printf("[Child] Перевірка ідентифікаторів усередині User Namespace:\n");
    printf("[Child]   UID = %d (euid = %d)\n", getuid(), geteuid());
    printf("[Child]   GID = %d (egid = %d)\n", getgid(), getegid());

    // Запускаємо тестову shell-оболонку
    char *exec_args[] = { "/bin/sh", "-c", "id && capsh --print 2>/dev/null || true", NULL };
    execvp(exec_args[0], exec_args);

    perror("execvp failed");
    return 1;
}

int main(void) {
    child_args_t args;
    args.parent_uid = getuid();
    args.parent_gid = getgid();

    if (pipe(args.pipe_fd) < 0) {
        perror("pipe creation failed");
        return 1;
    }

    char *child_stack = malloc(STACK_SIZE);
    if (!child_stack) {
        perror("malloc stack failed");
        return 1;
    }

    // Створюємо дочірній процес у новому User Namespace
    pid_t pid = clone(child_entry, child_stack + STACK_SIZE,
                      CLONE_NEWUSER | SIGCHLD, &args);
    if (pid < 0) {
        perror("clone failed");
        free(child_stack);
        return 1;
    }

    printf("[Parent] Створено дочірній процес PID = %d у новому User Namespace\n", pid);

    // 1. Блокуємо setgroups для дочірнього процесу
    char path[256];
    snprintf(path, sizeof(path), "/proc/%d/setgroups", pid);
    if (write_proc_file(path, "deny") < 0) {
        kill(pid, SIGKILL);
        return 1;
    }

    // 2. Налаштовуємо uid_map: 0 -> parent_uid (1 count)
    snprintf(path, sizeof(path), "/proc/%d/uid_map", pid);
    char map_buf[128];
    snprintf(map_buf, sizeof(map_buf), "0 %d 1\n", args.parent_uid);
    if (write_proc_file(path, map_buf) < 0) {
        kill(pid, SIGKILL);
        return 1;
    }

    // 3. Налаштовуємо gid_map: 0 -> parent_gid (1 count)
    snprintf(path, sizeof(path), "/proc/%d/gid_map", pid);
    snprintf(map_buf, sizeof(map_buf), "0 %d 1\n", args.parent_gid);
    if (write_proc_file(path, map_buf) < 0) {
        kill(pid, SIGKILL);
        return 1;
    }

    printf("[Parent] Мапінг UID/GID успішно записано у procfs\n");

    // Сигналізуємо нащадку через закриття pipe
    close(args.pipe_fd[1]);
    close(args.pipe_fd[0]);

    // Очікуємо завершення дочірнього процесу
    int status;
    waitpid(pid, &status, 0);
    free(child_stack);

    printf("[Parent] Дочірній процес завершився з кодом %d\n", WEXITSTATUS(status));
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <system_error>
#include <expected>
#include <memory>
#include <array>
#include <cerrno>
#include <cstring>
#include <sched.h>
#include <sys/wait.h>
#include <unistd.h>
#include <fcntl.h>

namespace userns {

// RAII обгортка для файлового дескриптора
class Pipe {
    std::array<int, 2> fds_{-1, -1};
public:
    Pipe() {
        if (::pipe(fds_.data()) < 0) {
            throw std::system_error(errno, std::generic_category(), "pipe failed");
        }
    }
    ~Pipe() {
        close_read();
        close_write();
    }
    int read_fd() const noexcept { return fds_[0]; }
    int write_fd() const noexcept { return fds_[1]; }

    void close_read() noexcept {
        if (fds_[0] != -1) { ::close(fds_[0]); fds_[0] = -1; }
    }
    void close_write() noexcept {
        if (fds_[1] != -1) { ::close(fds_[1]); fds_[1] = -1; }
    }
};

// Запис рядка у procfs файл із обробкою помилок
std::expected<void, std::error_code> write_proc(std::string_view path, std::string_view content) {
    int fd = ::open(path.data(), O_WRONLY);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    auto cleanup = std::unique_ptr<void, void(*)(void*)>((void*)(intptr_t)fd, [](void* f) {
        ::close((int)(intptr_t)f);
    });

    ssize_t written = ::write(fd, content.data(), content.size());
    if (written != static_cast<ssize_t>(content.size())) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

struct ChildContext {
    Pipe pipe;
    uid_t parent_uid;
    gid_t parent_gid;
};

int child_main(void* arg) {
    auto* ctx = static_cast<ChildContext*>(arg);
    ctx->pipe.close_write();

    char sync_byte;
    // Очікуємо закриття pipe батьківським процесом
    if (::read(ctx->pipe.read_fd(), &sync_byte, 1) != 0) {
        std::cerr << "[Child C++] Sync error\n";
        return 1;
    }
    ctx->pipe.close_read();

    std::cout << "[Child C++] Ізольоване середовище створено:\n"
              << "  UID: " << ::getuid() << " (euid: " << ::geteuid() << ")\n"
              << "  GID: " << ::getgid() << " (egid: " << ::getegid() << ")\n";

    std::array<const char*, 3> args = {"/bin/sh", "-c", "id", nullptr};
    ::execvp(args[0], const_cast<char* const*>(args.data()));
    return 1;
}

} // namespace userns

int main() {
    try {
        userns::ChildContext ctx{
            .pipe = {},
            .parent_uid = ::getuid(),
            .parent_gid = ::getgid()
        };

        constexpr size_t STACK_SIZE = 1024 * 1024;
        auto stack = std::make_unique<char[]>(STACK_SIZE);

        pid_t pid = ::clone(userns::child_main, stack.get() + STACK_SIZE,
                            CLONE_NEWUSER | SIGCHLD, &ctx);
        if (pid < 0) {
            std::cerr << "clone failed: " << std::strerror(errno) << "\n";
            return 1;
        }

        std::cout << "[Parent C++] Створено namespace для PID " << pid << "\n";

        std::string setgroups_path = "/proc/" + std::to_string(pid) + "/setgroups";
        std::string uid_map_path   = "/proc/" + std::to_string(pid) + "/uid_map";
        std::string gid_map_path   = "/proc/" + std::to_string(pid) + "/gid_map";

        if (auto res = userns::write_proc(setgroups_path, "deny"); !res) {
            std::cerr << "Failed setgroups: " << res.error().message() << "\n";
            ::kill(pid, SIGKILL);
            return 1;
        }

        if (auto res = userns::write_proc(uid_map_path, "0 " + std::to_string(ctx.parent_uid) + " 1\n"); !res) {
            std::cerr << "Failed uid_map: " << res.error().message() << "\n";
            ::kill(pid, SIGKILL);
            return 1;
        }

        if (auto res = userns::write_proc(gid_map_path, "0 " + std::to_string(ctx.parent_gid) + " 1\n"); !res) {
            std::cerr << "Failed gid_map: " << res.error().message() << "\n";
            ::kill(pid, SIGKILL);
            return 1;
        }

        std::cout << "[Parent C++] Мапінг успішно записано. Сигналізуємо нащадку...\n";
        ctx.pipe.close_write();

        int status = 0;
        ::waitpid(pid, &status, 0);
        std::cout << "[Parent C++] Дочірній процес завершився.\n";

    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

---

## Детальний розбір кроків коду та системних функцій

Розглянемо ключові моменти написання системного коду для керування User Namespaces:

1. **Виділення пам'яті під стек дочірнього процесу**:
   Виклик `clone(2)` вимагає явного виділення пам'яті під стек нового процесу. У C ми використовуємо `malloc(STACK_SIZE)`, а у C++ — `std::make_unique<char[]>(STACK_SIZE)`. Важливо пам'ятати, що на архітектурах x86/x86_64 стек викликів росте вниз (з високих адрес до низьких), тому в виклик `clone()` передається вказувач `stack + STACK_SIZE`.

2. **Обробка файлових дескрипторів та закриття unused fds**:
   Коли батьківський процес створює `pipe()`, обидва процеси отримують копії файлових дескрипторів. Якщо дочірній процес не закриє свій дескриптор запису `pipe_fd[1]`, лічильник посилань ядра на цей дескриптор ніколи не впаде до нуля! У результаті блокуюче читання `read()` у дочірньому процесі зависне назавжди (deadlock).

3. **Обробка помилок запису в procfs**:
   Файли у `/proc/[pid]/` є віртуальними. Системний виклик `write()` передає буфер безпосередньо в обробник ядра `proc_uid_map_write()`. Якщо форматування рядка містить зайві пробіли або некоректні числа, `write()` миттєво повертає `-1` з `errno = EINVAL`. Якщо батьківський процес не має прав на запис (наприклад, спроба записати чужий UID без `CAP_SETUID`), повертається `EPERM`.

4. **Перевірка привілеїв усередині дочірнього середовища**:
   Після відновлення виконання дочірній процес викликає `getuid()`, який повертає значення `0`. Для перевірки наявних привілеїв capabilities використовується утиліта `capsh --print`, яка зчитує маску з `/proc/self/status` та виводить її у вигляді зрозумілих назв (`cap_sys_admin`, `cap_net_admin`, `cap_setuid` тощо).

---

## Часті помилки та пастки низькорівневої реалізації

- **Забутий `setgroups deny`**: Якщо непривілейований процес спробує записати у `/proc/[pid]/gid_map` без попереднього запису `"deny"` у `/proc/[pid]/setgroups`, виклик `write()` поверне помилку `EPERM` (Permission denied).
- **Переповнення stack верхнього росту**: При використанні системного виклику `clone(2)` під архітектури x86/x86_64 стек росте зверху вниз. Потрібно передавати вказувач на **кінець** виділеного масиву `child_stack + STACK_SIZE`, а не на його початок.
- **Гонка умов (Race Condition)**: Якщо не використати `pipe` або інший механізм синхронізації, дочірній процес розпочне виконання `execvp()` до того, як батько встигне записати мапінг. В результаті процес запуститься з ідентифікатором `nobody` (`65534`).
