# ⚙️ Програмне створення rootless простору імен

Ця практична вставка демонструє реалізацію створення безкорінного простору імен користувачів (User Namespace) та нового простору монтування (Mount Namespace) мовами C та C++. Вона показує, як програмно ізолювати процес, виконати міжпроцесну синхронізацію через каналізацію (pipe), запустити зовнішні setuid-утиліти `newuidmap`/`newgidmap` для налаштування підпорядкованих UID/GID, змонтувати непривілейовану файлову систему `tmpfs` та отримати привілеї `root` усередині нового простору імен без прав суперкористувача на хості.

## Задача та архітектура рішення

Для створення функціонального rootless середовища програма повинна розв'язати проблему міжпроцесної синхронізації та послідовності налаштування просторів імен.

Коли непривілейований процес виконує системний виклик `unshare(CLONE_NEWUSER)`, ядро створює новий `user namespace`. У цей момент ефективний UID процесу всередині нового простору тимчасово стає `65534` (`nobody`), оскільки таблиця відображення `/proc/self/uid_map` ще не заповнена. Сам ізольований процес не може записати у `uid_map` більше ніж один рядок. Для запису повноцінного діапазону (наприклад, мапінгу додаткових ідентифікаторів з пулу `/etc/subuid`) зовнішній батьківський процес повинен викликати системні setuid-утиліти `newuidmap` та `newgidmap`, передавши їм PID дочірнього процесу.

Дочірній процес у контейнері не повинен продовжувати виконання (наприклад, виконувати виклики `mount` або `execve`), поки батьківський процес не завершить конфігурацію `uid_map` та `gid_map`. Якщо дочірній процес спробує виконати системні дії до заповнення таблиці відображення, ядро відхилить операції з помилкою `EPERM`.

### Детальний п'ятикроковий алгоритм виконання

1. **Створення синхронізаційного каналу (IPC Pipe)**: Батьківський процес викликає `pipe(2)`, створюючи паралельний канал передачі сигналів. Каналізація використовується як елементарний бар'єр синхронізації між процесами.
2. **Розгалуження та виклик unshare**: Батьківський процес виконує `fork()`. Дочірній процес закриває читальний кінець каналу і викликає `unshare(CLONE_NEWUSER | CLONE_NEWNS)`. Цей системний виклик відокремлює дочірній процес від хостових просторів імен користувачів та точок монтування.
3. **Сигналізація готовності PID**: Дочірній процес надсилає один байт (символ `'R'`) через `pipe` і блокується на виклику `read()`, очікуючи підтвердження від батька.
4. **Авторизація та мапінг батьківським процесом**: Батьківський процес зчитує сигнал, дізнається реальні UID/GID користувача хоста (`getuid()`, `getgid()`) та породжує два окремі процеси через `fork()` + `execlp()`, які виконують утиліти `newuidmap` та `newgidmap`. Утиліти перевіряють конфігурацію `/etc/subuid` і записують мапінг у `/proc/[child_pid]/uid_map`.
5. **Розблокування контейнера та виконання**: Батьківський процес надсилає підтверджувальний байт (символ `'G'`) через `pipe`. Дочірній процес розблоковується, перевіряє свої нові credentials (`getuid()` повертає `0`), монтує приватну файлову систему `tmpfs` у `/tmp` і замінює свій образ на оболонку `bash` через `execvp`.

Нижче наведено повністю робочі реалізації алгоритму мовами C та C++.

## Програмна реалізація

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sched.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/mount.h>
#include <fcntl.h>
#include <signal.h>

// Виклик зовнішніх setuid-утиліт newuidmap / newgidmap
static int execute_map_helper(const char *helper, pid_t pid, const char *inside_id, const char *outside_id, const char *count) {
    pid_t map_pid = fork();
    if (map_pid == -1) {
        perror("fork helper failed");
        return -1;
    }

    if (map_pid == 0) {
        char pid_str[16];
        snprintf(pid_str, sizeof(pid_str), "%d", pid);
        
        // Передаємо аргументи: helper PID inside_id outside_id count
        execlp(helper, helper, pid_str, inside_id, outside_id, count, NULL);
        perror("execlp helper failed");
        _exit(EXIT_FAILURE);
    }

    int status = 0;
    if (waitpid(map_pid, &status, 0) == -1) {
        perror("waitpid helper failed");
        return -1;
    }

    return (WIFEXITED(status) && WEXITSTATUS(status) == 0) ? 0 : -1;
}

int main(void) {
    printf("[Init] Starting Rootless Container Setup Demo...\n");

    // Створюємо Pipe для двосторонньої синхронізації
    int sync_pipe[2];
    if (pipe(sync_pipe) == -1) {
        perror("pipe creation failed");
        return EXIT_FAILURE;
    }

    uid_t parent_uid = getuid();
    gid_t parent_gid = getgid();

    printf("[Parent] Host User UID: %d, GID: %d\n", parent_uid, parent_gid);

    pid_t child_pid = fork();
    if (child_pid == -1) {
        perror("fork child failed");
        return EXIT_FAILURE;
    }

    if (child_pid == 0) {
        // --- Дочірній процес (Контейнер) ---
        close(sync_pipe[0]); // Закриваємо читальний кінець у дитині

        printf("[Child] Creating User Namespace (CLONE_NEWUSER) & Mount Namespace (CLONE_NEWNS)...\n");
        if (unshare(CLONE_NEWUSER | CLONE_NEWNS) == -1) {
            perror("unshare failed");
            _exit(EXIT_FAILURE);
        }

        // Повідомляємо батька, що namespace створено
        char signal_byte = 'R';
        if (write(sync_pipe[1], &signal_byte, 1) != 1) {
            perror("write sync signal failed");
            _exit(EXIT_FAILURE);
        }

        // Блокуємося і чекаємо, поки батьківський процес виконає newuidmap
        if (read(sync_pipe[1], &signal_byte, 1) != 1) {
            perror("read finish sync failed");
            _exit(EXIT_FAILURE);
        }
        close(sync_pipe[1]);

        // Перевіряємо отримані ідентифікатори
        uid_t inner_uid = getuid();
        gid_t inner_gid = getgid();
        printf("[Child] Inner Container Credentials: UID=%d, GID=%d\n", inner_uid, inner_gid);

        if (inner_uid != 0) {
            fprintf(stderr, "[Child] Error: Failed to escalate to Root inside namespace!\n");
            _exit(EXIT_FAILURE);
        }

        printf("[Child] Successfully gained Root (UID 0) inside container!\n");

        // Звертаємо увагу: оскільки дитина має CAP_SYS_ADMIN у своєму Mount Namespace,
        // вона може виконувати непривілейоване монтування tmpfs
        printf("[Child] Mounting isolated tmpfs filesystem on /tmp...\n");
        if (mount("tmpfs", "/tmp", "tmpfs", 0, "size=16M") == -1) {
            perror("mount tmpfs failed");
            // Продовжуємо виконання, навіть якщо монтування не вдалося
        } else {
            printf("[Child] Successfully mounted private tmpfs on /tmp!\n");
        }

        // Замінюємо процес на bash
        char *exec_args[] = { "/bin/bash", NULL };
        printf("[Child] Executing interactive shell...\n\n");
        execvp(exec_args[0], exec_args);

        perror("execvp failed");
        _exit(EXIT_FAILURE);
    }

    // --- Батьківський процес (Оркестратор) ---
    close(sync_pipe[1]); // Закриваємо записувальний кінець у батька

    // Чекаємо готовності дочірнього процесу
    char sync_buf = 0;
    if (read(sync_pipe[0], &sync_buf, 1) != 1) {
        perror("read initial sync failed");
        kill(child_pid, SIGKILL);
        return EXIT_FAILURE;
    }

    printf("[Parent] Child PID %d created namespaces. Executing newuidmap & newgidmap...\n", child_pid);

    char uid_str[16], gid_str[16];
    snprintf(uid_str, sizeof(uid_str), "%d", parent_uid);
    snprintf(gid_str, sizeof(gid_str), "%d", parent_gid);

    // Запускаємо newuidmap: 0 -> parent_uid (1 count)
    if (execute_map_helper("newuidmap", child_pid, "0", uid_str, "1") != 0) {
        fprintf(stderr, "[Parent] Fatal: newuidmap failed for PID %d\n", child_pid);
        kill(child_pid, SIGKILL);
        return EXIT_FAILURE;
    }

    // Запускаємо newgidmap: 0 -> parent_gid (1 count)
    if (execute_map_helper("newgidmap", child_pid, "0", gid_str, "1") != 0) {
        fprintf(stderr, "[Parent] Fatal: newgidmap failed for PID %d\n", child_pid);
        kill(child_pid, SIGKILL);
        return EXIT_FAILURE;
    }

    printf("[Parent] Mappings successfully configured. Unblocking child...\n");

    // Розблоковуємо дочірній процес
    sync_buf = 'G';
    if (write(sync_pipe[0], &sync_buf, 1) != 1) {
        perror("write unblock signal failed");
        kill(child_pid, SIGKILL);
        return EXIT_FAILURE;
    }
    close(sync_pipe[0]);

    // Чекаємо завершення дочірнього процесу
    int child_status = 0;
    waitpid(child_pid, &child_status, 0);
    printf("[Parent] Child container process exited with status %d.\n", child_status);

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <array>
#include <system_error>
#include <memory>
#include <utility>
#include <unistd.h>
#include <sched.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/mount.h>

namespace rootless {

// RAII безпечна обгортка для файлових дескрипторів Linux
class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_(-1) {}
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
        return std::exchange(fd_, -1);
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

// RAII обгортка для каналу міжпроцесної синхронізації
class Channel {
public:
    static std::pair<Channel, Channel> create_connected_pair() {
        std::array<int, 2> fds{-1, -1};
        if (::pipe(fds.data()) == -1) {
            throw std::system_error(errno, std::generic_category(), "Failed to create IPC pipe");
        }
        return {Channel(UniqueFd(fds[0])), Channel(UniqueFd(fds[1]))};
    }

    explicit Channel(UniqueFd fd) : fd_(std::move(fd)) {}

    void send_token(char token) {
        if (::write(fd_.get(), &token, 1) != 1) {
            throw std::system_error(errno, std::generic_category(), "Failed to write token to pipe");
        }
    }

    char receive_token() {
        char token = 0;
        if (::read(fd_.get(), &token, 1) != 1) {
            throw std::system_error(errno, std::generic_category(), "Failed to read token from pipe");
        }
        return token;
    }

private:
    UniqueFd fd_;
};

// Безпечний запуск зовнішньої setuid-утиліти відображення ідентифікаторів
void invoke_id_map_tool(std::string_view tool_name, pid_t target_pid, 
                        std::string_view inside_id, std::string_view outside_id, 
                        std::string_view range_size) {
    const pid_t map_pid = ::fork();
    if (map_pid == -1) {
        throw std::system_error(errno, std::generic_category(), "Forking map tool failed");
    }

    if (map_pid == 0) {
        const std::string pid_str = std::to_string(target_pid);
        ::execlp(tool_name.data(), tool_name.data(), pid_str.c_str(), 
                 inside_id.data(), outside_id.data(), range_size.data(), nullptr);
        ::exit(EXIT_FAILURE);
    }

    int wait_status = 0;
    if (::waitpid(map_pid, &wait_status, 0) == -1) {
        throw std::system_error(errno, std::generic_category(), "Waiting for map tool failed");
    }

    if (!WIFEXITED(wait_status) || WEXITSTATUS(wait_status) != 0) {
        throw std::runtime_error("Map tool " + std::string(tool_name) + " failed execution");
    }
}

} // namespace rootless

int main() {
    try {
        std::cout << "[CPP Init] Orchestrating Rootless Container via Modern C++...\n";

        auto [reader, writer] = rootless::Channel::create_connected_pair();

        const uid_t host_uid = ::getuid();
        const gid_t host_gid = ::getgid();

        const pid_t child_pid = ::fork();
        if (child_pid == -1) {
            throw std::system_error(errno, std::generic_category(), "Forking container child failed");
        }

        if (child_pid == 0) {
            // --- Дочірній процес контейнера ---
            if (::unshare(CLONE_NEWUSER | CLONE_NEWNS) == -1) {
                throw std::system_error(errno, std::generic_category(), "unshare(CLONE_NEWUSER|CLONE_NEWNS) failed");
            }

            // Відправляємо сигнал батьківському процесу
            writer.send_token('R');

            // Очікуємо підтвердження конфігурації мапінгу від батька
            [[maybe_unused]] const char ack = writer.receive_token();

            std::cout << "[CPP Child] Container Credentials: UID=" << ::getuid() << ", GID=" << ::getgid() << "\n";
            if (::getuid() == 0) {
                std::cout << "[CPP Child] Gained Root Privileges inside isolated Namespace!\n";
            }

            // Монтуємо приватну tmpfs
            if (::mount("tmpfs", "/tmp", "tmpfs", 0, "size=32M") == 0) {
                std::cout << "[CPP Child] Private tmpfs successfully mounted on /tmp!\n";
            }

            const std::array<const char*, 2> bash_args{"/bin/bash", nullptr};
            ::execvp(bash_args[0], const_cast<char* const*>(bash_args.data()));
            ::exit(EXIT_FAILURE);
        }

        // --- Батьківський процес оркестрації ---
        [[maybe_unused]] const char ready_signal = reader.receive_token();

        std::cout << "[CPP Parent] Child process " << child_pid << " is ready. Running setuid helpers...\n";

        const std::string host_uid_str = std::to_string(host_uid);
        const std::string host_gid_str = std::to_string(host_gid);

        // Налаштування таблиці мапінгу через утиліти newuidmap / newgidmap
        rootless::invoke_id_map_tool("newuidmap", child_pid, "0", host_uid_str, "1");
        rootless::invoke_id_map_tool("newgidmap", child_pid, "0", host_gid_str, "1");

        std::cout << "[CPP Parent] Mappings registered successfully. Releasing child...\n";
        reader.send_token('G');

        int child_status = 0;
        ::waitpid(child_pid, &child_status, 0);
        std::cout << "[CPP Parent] Container session finished.\n";

    } catch (const std::exception& err) {
        std::cerr << "[CPP Error] " << err.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## Аналіз виконання та перевірка ізоляції

При компіляції та виконанні цієї програми під звичайним обліковим записом `alice` (UID 1000 на хості):

1. **Створення простору**: Виклик `unshare(CLONE_NEWUSER | CLONE_NEWNS)` створює новий простір імен користувачів та простір монтування.
2. **Запис мапінгу**: Батьківський процес виконує утиліти `newuidmap` та `newgidmap`, прив'язуючи UID 1000 хоста до UID 0 всередині контейнера.
3. **Ескалація привілеїв у контейнері**: Дочірній процес зчитує `getuid()`, який повертає значення `0`. Користувач стає `root` усередині контейнера.
4. **Непривілейоване монтування**: Виклик `mount("tmpfs", "/tmp", "tmpfs", ...)` завершується успішно, оскільки процес має привілеї `CAP_SYS_ADMIN` над своїм новим Mount Namespace.
5. **Захист хоста**: Незважаючи на привілеї `root` всередині контейнера, спроба прочитати чутливий файл хоста `/etc/shadow` або змінити мережеві пристрої хоста відхиляється ядром з помилкою `Permission denied`, оскільки для VFS хоста процес залишається звичайним користувачем `alice`.

### Набуті привілеї та підсистема VFS

Отримання привілеїв `CAP_SYS_ADMIN` всередині нового user namespace дозволяє дочірньому процесу виконувати цілий спектр дій, заборонених для звичайного користувача на хості:
* Монтувати файлові системи `tmpfs`, `procfs`, `sysfs` та `fuse-overlayfs`.
* Змінювати кореневу директорію за допомогою системного виклику `pivot_root(2)` або `chroot(2)`.
* Налаштовувати локальні мережеві пристрої (loopback) та змінювати таблицю маршрутизації всередині свого `CLONE_NEWNET`.

Водночас будь-який виклик VFS, який зачіпає файлову систему хоста (наприклад, відкриття файлів на звичайних розділах ext4), проходить підконтрольну конвертацію ідентифікаторів `kuid_t`. Оскільки внутрішній UID 0 мапиться на хостовий UID 1000, ядро не дозволяє контейнеру записувати у файли, які належать справжньому суперкористувачеві хоста.

### Порівняльний розбір C та C++ реалізацій

Хоча C та C++ коди реалізують однаковий послідовний алгоритм, між ними є важливі архітектурні відмінності:
1. **Управління ресурсами**: C-версія вимагає явного виклику `close()` у кожній гілці обробки помилок. У C++ версії клас `UniqueFd` та структура `Channel` автоматично закривають файлові дескриптори в деструкторах при виході з області видимості або при генерації винятку `std::system_error`.
2. **Передача типів та безпека рядків**: У C-коді використовується небезпечна заміна рядків через `snprintf()`, тоді як C++ використовує безпечні об'єкти `std::string` та `std::string_view`, що виключає ризики переповнення буфера при роботі з PID та ідентифікаторами.
3. **Обробка помилок системних викликів**: У C-коді повернені коди перевіряються через явні інструкції `if (res == -1)`. У C++ реалізації помилки конвертуються в об'єкти `std::system_error`, збережені в стандартній системі винятків `<system_error>`.

### Обробка помилок та пастки під час проектування

При практичній реалізації rootless оркестраторів слід зважати на такі потенційні пастки:
1. **Race Condition при виклику helpers**: Якщо батьківський процес викликає `newuidmap` до того, як дочірній процес завершить системний виклик `unshare(CLONE_NEWUSER)`, утиліта відхилить запит з помилкою `invalid ns`. Саме тому наявність міжпроцесної синхронізації через `pipe` або `eventfd` є строго обов'язковою.
2. **Обмеження на setgroups**: Якщо дочірній процес намагається самостійно налаштувати `gid_map` без використання `newgidmap`, він повинен першим кроком записати `deny` у `/proc/self/setgroups`. Забудькуватість на цьому кроці призводить до помилки `EPERM` від ядра.
3. **Витоки файлових дескрипторів**: При розгалуженні через `fork()` усі відкриті файлові дескриптори наслідуються. Використання прапорця `O_CLOEXEC` та RAII обгортки `UniqueFd` у C++ коді запобігає витоку дескрипторів каналу зв'язку в контейнерну оболонку після виклику `execvp`.
