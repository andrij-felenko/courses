# 📋 Інтерфейси керування прапорцем FD_CLOEXEC та системні виклики сімейства *_CLOEXEC

Системні виклики операційної системи Linux, що керують поведінкою файлових дескрипторів під час заміни виконуваного образу процесу (`execve`), поділяються на три взаємодоповнюючі групи:
1. **Інтерфейси прямого керування дескрипторними прапорцями:** системний виклик `fcntl()` для зчитування, модифікації та дублювання окремих дескрипторів.
2. **Атомарні виклики виділення ресурсів із суфіксом `_CLOEXEC`:** системні виклики нового покоління (`openat`, `pipe2`, `accept4`, `socket`, `epoll_create1` тощо), які встановлюють біт `close_on_exec` неподільно у момент створення дескриптора в ядрі.
3. **Виклики групового оновлення та масового очищення:** системний виклик `close_range()`, що дозволяє за одну операцію модифікувати або закрити довільний діапазон дескрипторів.

Нижче наведено повний технічний довідник контрактів, параметрів, прапорців та кодів помилок для кожного системного виклику.

---

## 1. Системний виклик fcntl (POSIX.1-1988)

Системний виклик `fcntl()` (англ. *file control*) є базовим універсальним механізмом керування властивостями вже відкритих дескрипторів у стандарті POSIX.

:::tabs
```c
#include <fcntl.h>

/* Сигнатура системного виклику fcntl */
int fcntl(int fd, int cmd, ... /* arg */ );
```
```cpp
#include <fcntl.h>

/* Виклик fcntl у C++ просторі імен */
extern "C" int fcntl(int fd, int cmd, ...);
```
:::

### Команди керування дескрипторними прапорцями

- **`F_GETFD` (аргумент відсутній):** повертає поточну бітову маску прапорців дескриптора `fd`. У разі успіху повертає невід'ємне число, у разі помилки — `-1`.
- **`F_SETFD` (аргумент типу `int`):** встановлює нову бітову маску дескрипторних прапорців для `fd`. Єдиним стандартизованим прапорцем є `FD_CLOEXEC` (значення `1`). Повертає `0` у разі успіху або `-1` при помилці.
- **`F_DUPFD_CLOEXEC` (аргумент типу `int` `minfd`):** створює копію дескриптора `fd`, використовуючи найменший доступний номер дескриптора, що більший або дорівнює `minfd`, і **атомарно встановлює** для нового дескриптора прапорець `FD_CLOEXEC`.

### Коди помилок (errno)
- `EBADF`: переданий аргумент `fd` не є дійсним відкритим файловим дескриптором процесу.
- `EINVAL`: невідоме значення команди `cmd` або некоректне значення `minfd`.
- `EMFILE`: досягнуто ліміту відкритості файлів для поточного процесу (`RLIMIT_NOFILE`).

:::tabs
```c
#include <fcntl.h>
#include <unistd.h>

/* Безпечне встановлення прапорця FD_CLOEXEC через fcntl */
int enable_fd_cloexec(int fd) {
    int flags = fcntl(fd, F_GETFD);
    if (flags == -1)
        return -1;
    return fcntl(fd, F_SETFD, flags | FD_CLOEXEC);
}
```
```cpp
#include <fcntl.h>
#include <unistd.h>
#include <system_error>

void enable_fd_cloexec(int fd) {
    const int flags = ::fcntl(fd, F_GETFD);
    if (flags == -1) {
        throw std::system_error(errno, std::generic_category(), "fcntl(F_GETFD) failed");
    }
    if (::fcntl(fd, F_SETFD, flags | FD_CLOEXEC) == -1) {
        throw std::system_error(errno, std::generic_category(), "fcntl(F_SETFD) failed");
    }
}
```
:::

---

## 2. Атомарні системні виклики створення ресурсів (*_CLOEXEC)

Усі системні виклики цієї групи встановлюють біт у масці `close_on_exec` усередині таблиці `struct fdtable` ядра Linux до того, як числовий номер дескриптора стане видимим для користувацького простору. Це повністю виключає виникнення стану гонитви у багатопотокових програмах.

### Відкриття та дублювання файлів

#### open / openat / openat2
- **Прапорець:** `O_CLOEXEC` (доступний починаючи з ядра Linux 2.6.23 та стандартизований у POSIX.1-2008).
- **Опис дії:** відкриває файл і відразу позначає його дескриптор прапорцем `FD_CLOEXEC`.
- **Семантика помилок:** якщо системний виклик зазнає невдачі, дескриптор не виділяється, а глобальна змінна `errno` містить причину помилки (`ENOENT`, `EACCES`, `EMFILE`). Прапорець `O_CLOEXEC` не впливає на права доступу до файлу і не змінює поведінку операцій читання чи запису.

:::tabs
```c
#include <fcntl.h>

int open_readonly_cloexec(const char *path) {
    return open(path, O_RDONLY | O_CLOEXEC);
}
```
```cpp
#include <fcntl.h>
#include <system_error>

int open_readonly_cloexec(const char* path) {
    int fd = ::open(path, O_RDONLY | O_CLOEXEC);
    if (fd == -1) {
        throw std::system_error(errno, std::generic_category(), "open failed");
    }
    return fd;
}
```
:::

#### dup3
- **Прапорці:** `O_CLOEXEC` (Linux 2.6.27, glibc 2.9).
- **Відмінність від dup2:** традиційний виклик `dup2(oldfd, newfd)` завжди примусово скидає `FD_CLOEXEC` на дескрипторі `newfd`. Виклик `dup3` дозволяє атомарно виставити `O_CLOEXEC`. Якщо `oldfd == newfd`, `dup3` повертає помилку `EINVAL` (на відміну від `dup2`, який не виконує жодних дій).

:::tabs
```c
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>

int duplicate_with_cloexec(int src_fd, int target_fd) {
    return dup3(src_fd, target_fd, O_CLOEXEC);
}
```
```cpp
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <system_error>

int duplicate_with_cloexec(int src_fd, int target_fd) {
    int res = ::dup3(src_fd, target_fd, O_CLOEXEC);
    if (res == -1) {
        throw std::system_error(errno, std::generic_category(), "dup3 failed");
    }
    return res;
}
```
:::

---

### Канали та мережеві сокети

#### pipe2
- **Прапорці:** `O_CLOEXEC`, `O_NONBLOCK`, `O_DIRECT` (Linux 2.6.27, glibc 2.9).
- **Опис дії:** створює односпрямований анонімний канал зв'язку, встановлюючи прапорці одразу на обидва кінці (`pipefd[0]` на читання та `pipefd[1]` на запис). Якщо вказано `O_CLOEXEC`, обидва дескриптори будуть автоматично закриті під час виклику `execve`.

:::tabs
```c
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>

int make_cloexec_pipe(int fds[2]) {
    return pipe2(fds, O_CLOEXEC | O_NONBLOCK);
}
```
```cpp
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <array>
#include <system_error>

std::array<int, 2> make_cloexec_pipe() {
    std::array<int, 2> fds{-1, -1};
    if (::pipe2(fds.data(), O_CLOEXEC | O_NONBLOCK) == -1) {
        throw std::system_error(errno, std::generic_category(), "pipe2 failed");
    }
    return fds;
}
```
:::

#### socket та socketpair
- **Прапорці:** `SOCK_CLOEXEC`, `SOCK_NONBLOCK` (Linux 2.6.27, glibc 2.9).
- **Опис дії:** прапорці додаються за допомогою побітового АБО безпосередньо до параметра `type` (наприклад, `SOCK_STREAM | SOCK_CLOEXEC`). Це гарантує, що новостворений сокет не витече в дочірні процеси.

#### accept4
- **Прапорці:** `SOCK_CLOEXEC`, `SOCK_NONBLOCK` (Linux 2.6.28, glibc 2.10).
- **Опис дії:** вилучає перше підключення з черги очікування слухаючого сокета `sockfd` і створює новий підключений сокет з прапорцем `FD_CLOEXEC`. Це критично важливо для уникнення витоку клієнтських сокетів у паралельні процеси під час виклику `fork`.

:::tabs
```c
#include <sys/socket.h>
#include <netinet/in.h>

int create_bound_server_socket(int port) {
    int fd = socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (fd == -1)
        return -1;

    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(port),
        .sin_addr.s_addr = INADDR_ANY
    };

    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) == -1) {
        close(fd);
        return -1;
    }
    return fd;
}
```
```cpp
#include <sys/socket.h>
#include <netinet/in.h>
#include <system_error>
#include <unistd.h>

int create_bound_server_socket(int port) {
    int fd = ::socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (fd == -1) {
        throw std::system_error(errno, std::generic_category(), "socket creation failed");
    }

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (::bind(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == -1) {
        ::close(fd);
        throw std::system_error(errno, std::generic_category(), "bind failed");
    }
    return fd;
}
```
:::

---

### Примітиви ядра Linux для обробки подій

Системні примітиви ядра Linux для асинхронного сповіщення, моніторингу подій та керування процесами також підтримують атомарні прапорці створення:

- **`epoll_create1(int flags)`:** створює новий дескриптор `epoll`. Приймає прапорець `EPOLL_CLOEXEC`. Доступний з ядра Linux 2.6.27. Дозволяє уникнути передачі всього дерева моніторингу подій дочірнім процесам.
- **`signalfd4(int ufd, const sigset_t *mask, int flags)`:** створює дескриптор для читання сигналів процесу через стандартний інтерфейс файлів. Приймає прапорці `SFD_CLOEXEC` та `SFD_NONBLOCK`. Захищає маску сигналів від успадкування.
- **`timerfd_create(int clockid, int flags)`:** створює дескриптор апаратного таймера. Приймає прапорці `TFD_CLOEXEC` та `TFD_NONBLOCK`. Доступний з версії Linux 2.6.25.
- **`eventfd2(unsigned int initval, int flags)`:** створює 64-бітний числовий лічильник подій для передачі повідомлень між потоками. Приймає `EFD_CLOEXEC`, `EFD_NONBLOCK` та `EFD_SEMAPHORE`.
- **`inotify_init1(int flags)`:** створює чергу моніторингу подій файлової системи. Приймає `IN_CLOEXEC` та `IN_NONBLOCK`. Доступний з версії Linux 2.6.27.
- **`memfd_create(const char *name, unsigned int flags)`:** створює анонімний файл у пам'яті (RAM buffer) з можливістю накладання заборон на зміну розміру та запис (sealing). Приймає `MFD_CLOEXEC` та `MFD_ALLOW_SEALING`. Доступний з Linux 3.17.
- **`userfaultfd(int flags)`:** створює дескриптор для перехоплення помилок сторінок пам'яті у просторі користувача. Приймає `O_CLOEXEC` та `O_NONBLOCK`. Доступний з Linux 4.3.
- **`pidfd_open(pid_t pid, unsigned int flags)`:** створює дескриптор відстеження життєвого циклу процесу за його PID. Дескриптор завжди створюється з прапорцем `O_CLOEXEC`. Доступний з Linux 5.3.

:::tabs
```c
#include <sys/epoll.h>
#include <sys/eventfd.h>
#include <unistd.h>

int init_event_subsystem(int *epoll_out, int *event_out) {
    int epfd = epoll_create1(EPOLL_CLOEXEC);
    if (epfd == -1)
        return -1;

    int evfd = eventfd(0, EFD_CLOEXEC | EFD_NONBLOCK);
    if (evfd == -1) {
        close(epfd);
        return -1;
    }

    *epoll_out = epfd;
    *event_out = evfd;
    return 0;
}
```
```cpp
#include <sys/epoll.h>
#include <sys/eventfd.h>
#include <unistd.h>
#include <system_error>
#include <utility>

std::pair<int, int> init_event_subsystem() {
    int epfd = ::epoll_create1(EPOLL_CLOEXEC);
    if (epfd == -1) {
        throw std::system_error(errno, std::generic_category(), "epoll_create1 failed");
    }

    int evfd = ::eventfd(0, EFD_CLOEXEC | EFD_NONBLOCK);
    if (evfd == -1) {
        ::close(epfd);
        throw std::system_error(errno, std::generic_category(), "eventfd failed");
    }

    return {epfd, evfd};
}
```
:::

---

## 3. Масове закриття та налаштування діапазонів: close_range()

Системний виклик `close_range()` (Linux 5.9+, FreeBSD 12.2+) призначений для оптимізованого виконання масових операцій над дескрипторами в просторі ядра без необхідності сканування простору користувача або ітерації по системних лімітах `sysconf(_SC_OPEN_MAX)`.

:::tabs
```c
#include <unistd.h>
#include <linux/close_range.h>

/* Сигнатура системного виклику close_range */
int close_range(unsigned int first, unsigned int last, unsigned int flags);
```
```cpp
#include <unistd.h>
#include <linux/close_range.h>

/* Оголошення close_range у C++ */
extern "C" int close_range(unsigned int first, unsigned int last, unsigned int flags);
```
:::

### Параметри системного виклику

- `first`: перший номер файлового дескриптора у діапазоні (включно).
- `last`: останній номер файлового дескриптора у діапазоні (включно). Для охоплення всіх можливих дескрипторів передається константа `~0U` (еквівалент `UINT_MAX`).
- `flags`: комбінація прапорців поведінки:
  - `0`: примусово закрити всі відкриті дескриптори у діапазоні `[first, last]`.
  - `CLOSE_RANGE_CLOEXEC` (доступний починаючи з ядра Linux 5.11): замість закриття встановити прапорець `FD_CLOEXEC` на всі відкриті дескриптори діапазону.
  - `CLOSE_RANGE_UNSHARE` (Linux 5.9+): перед закриттям відв'язати таблицю дескрипторів від інших потоків, якщо вона була спільною (`CLONE_FILES`).

### Практичне застосування close_range

:::tabs
```c
#define _GNU_SOURCE
#include <unistd.h>
#include <linux/close_range.h>
#include <sys/syscall.h>

/* Очищення всіх зайвих дескрипторів перед викликом execve */
int sanitize_fds_before_exec(void) {
    /* Закриваємо все, крім stdin (0), stdout (1) та stderr (2) */
    return syscall(SYS_close_range, 3, ~0U, 0);
}

/* Встановлення прапорця CLOEXEC на всі успадковані дескриптори */
int mark_all_fds_cloexec(void) {
    return syscall(SYS_close_range, 3, ~0U, CLOSE_RANGE_CLOEXEC);
}
```
```cpp
#define _GNU_SOURCE
#include <unistd.h>
#include <linux/close_range.h>
#include <sys/syscall.h>
#include <system_error>

void sanitize_fds_before_exec() {
    if (::syscall(SYS_close_range, 3, ~0U, 0) == -1) {
        throw std::system_error(errno, std::generic_category(), "close_range failed");
    }
}

void mark_all_fds_cloexec() {
    if (::syscall(SYS_close_range, 3, ~0U, CLOSE_RANGE_CLOEXEC) == -1) {
        throw std::system_error(errno, std::generic_category(), "close_range(CLOSE_RANGE_CLOEXEC) failed");
    }
}
```
:::

---

## 4. Зведена таблиця: Застарілі неатомарні виклики проти сучасних атомарних

| Тип операції | Застарілий неатомарний підхід (гонитва) | Сучасний атомарний еквівалент (без гонитви) | Стандарт / Версія ядра |
| :--- | :--- | :--- | :--- |
| Відкриття файлу | `open()` + `fcntl(F_SETFD)` | `open(..., O_CLOEXEC)` | POSIX.1-2008 / Linux 2.6.23 |
| Створення каналу | `pipe()` + 2 × `fcntl(F_SETFD)` | `pipe2(..., O_CLOEXEC)` | Linux 2.6.27 / glibc 2.9 |
| Створення сокета | `socket()` + `fcntl(F_SETFD)` | `socket(..., SOCK_CLOEXEC, ...)` | Linux 2.6.27 / glibc 2.9 |
| Прийняття сокета | `accept()` + `fcntl(F_SETFD)` | `accept4(..., SOCK_CLOEXEC)` | Linux 2.6.28 / glibc 2.10 |
| Дублювання дескриптора | `dup2()` + `fcntl(F_SETFD)` | `dup3(..., O_CLOEXEC)` або `F_DUPFD_CLOEXEC` | POSIX.1-2008 / Linux 2.6.27 |
| Моніторинг epoll | `epoll_create()` + `fcntl()` | `epoll_create1(EPOLL_CLOEXEC)` | Linux 2.6.27 / glibc 2.9 |
| Масове закриття | Цикл `close()` на `sysconf(_SC_OPEN_MAX)` | `close_range(3, ~0U, 0)` | Linux 5.9+ / FreeBSD 12.2+ |
