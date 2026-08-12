# ⚙️ Практичний аналізатор процесів на основі pidfs

У цьому проєкті реалізовано консольну утиліту перевірки тотожності двох процесів через інспектування номерів inode в `pidfs`, витягування дескриптора Network Namespace через `ioctl` та читанні бінарних метаданих процесу без звернення до Віртуальної файлової системи `/proc`.

## Опис задачі та архітектура рішення

Системним демонам та контейнерним супервізорам (системам на кшталт `containerd`, `runc` чи `systemd`) часто необхідно перевірити, чи посилаються дві процедури або два дескриптори на один і той самий процес у системі. Застосування традиційних системних викликів над чисельним PID не дає жодних гарантій через можливість перевикористання ідентифікаторів (англ. *PID recycling*).

Коли один процес помирає, ядро Linux вивільняє його чисельний PID і через деякий час може віддати його новому процесу. Якщо наглядач намагається надіслати сигнал або перевірити стан процесу за чисельним PID, виникає гонка між перевіркою та використанням (англ. *Time-of-Check to Time-of-Use*, TOCTOU).

Для усунення цієї гонки та забезпечення абсолютної надійності утиліта реалізує таку послідовність дій:
1. Відкриває дескриптори `pidfd` для двох заданих чисельних PID за допомогою системного виклику `pidfd_open(2)`.
2. Запитує атрибути файлової системи через виклик `statx()` для кожного `pidfd` і порівнює атрибути `stx_dev` та `stx_ino`. Збіг цих двох полів гарантує тотожність двох процесів на рівні об'єкта ядра `struct pid`.
3. Запитує дескриптор Network Namespace цільового процесу безпосередньо з його `pidfd` через `ioctl(pidfd, PIDFD_GET_NET_NAMESPACE, 0)`. Це дозволяє отримати доступ до мережевого простору процесу без читання шляхів `/proc/<pid>/ns/net`.
4. Викликає `ioctl(pidfd, PIDFD_GET_INFO, &info)` для швидкого бінарного зчитування ефективного UID, батьківського PPID та часу запуску процесу без накладних витрат на форматування й парсинг текстових файлів.

## Механізми системних викликів та перевірка прав

Системний виклик `pidfd_open(pid, flags)` є основною точкою входу для отримання дескриптора процесу. На архітектурі x86_64 цей системний виклик має номер 434. Першим аргументом передається чисельний PID цільового процесу у контексті поточного PID namespace викликача. Другим аргументом передаються прапорці (наразі зарезервовано `0`). При успіху виклик повертає новий файловий дескриптор, що посилається на об'єкт у псевдофайловій системі `pidfs`.

Для отримання атрибутів файлової системи утиліта використовує розширений системний виклик `statx(fd, "", AT_EMPTY_PATH, STATX_INO, &stx)`. Прапорець `AT_EMPTY_PATH` наказує ядрові працювати безпосередньо з відкритим файловим дескриптором `fd`, ігноруючи аргумент шляху. Маска `STATX_INO` запитує номер індексу `inode`. Файлова система `pidfs` гарантує, що `stx_ino` є унікальним 64-бітним цілим числом, яке залишається незмінним упродовж усього життєвого циклу об'єкта `struct pid`.

Отримання дескриптора простору імен через `ioctl(pidfd, PIDFD_GET_NET_NAMESPACE, 0)` перевіряє права доступу викликача. Ядро звертається до внутрішньої функції `ptrace_may_access(task, PTRACE_MODE_READ_REALCREDS)`. Якщо процес-викликач намагається отримати простір імен процесу з іншими ідентифікаторами UID/GID або з іншого простору користувачів (User Namespace), він мусить мати привілей `CAP_SYS_PTRACE`. Якщо привілеїв недостатньо, `ioctl` повертає помилку `EPERM`.

Для отримання метаданих через `PIDFD_GET_INFO` структура `struct pidfd_info` заповнюється маскою бажаних полів (`PIDFD_INFO_PID`, `PIDFD_INFO_PPID`, `PIDFD_INFO_CREDENT`). Виклик заповнює поля `pid`, `ppid`, `euid`, `egid` та 64-бітний ідентифікатор контрольної групи `cgroupid` v2. Це дозволяє утиліті миттєво з'ясувати статус процесу в cgroup v2 без читання файлу `/proc/<pid>/cgroup`.

## Реалізація аналізатора

Програму наведено у двох ідіоматичних варіантах — мовою C з прямим системним API та мовою C++ з використанням концепції RAII, автоматичного управління ресурсами, системних категорій помилок та сучасної обробки виняткових ситуацій.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <linux/types.h>

#ifndef SYS_pidfd_open
#define SYS_pidfd_open 434
#endif

#ifndef PIDFS_IOCTL_MAGIC
#define PIDFS_IOCTL_MAGIC 0x70
#endif

#ifndef PIDFD_GET_NET_NAMESPACE
#define PIDFD_GET_NET_NAMESPACE _IO(PIDFS_IOCTL_MAGIC, 4)
#endif

#ifndef PIDFD_GET_INFO
struct pidfd_info {
    __u64 mask;
    __u64 cgroupid;
    __u32 pid;
    __u32 tgid;
    __u32 ppid;
    __u32 euid;
    __u32 egid;
    __u64 start_time;
    __u64 spare[11];
};
#define PIDFD_GET_INFO _IOWR(PIDFS_IOCTL_MAGIC, 9, struct pidfd_info)
#define PIDFD_INFO_PID (1U << 1)
#define PIDFD_INFO_PPID (1U << 3)
#define PIDFD_INFO_CREDENT (1U << 4)
#endif

static int open_pidfd(pid_t pid) {
    int fd = (int)syscall(SYS_pidfd_open, pid, 0U);
    if (fd < 0) {
        perror("pidfd_open failed");
    }
    return fd;
}

static int get_pidfs_stat(int pidfd, struct statx *stx) {
    memset(stx, 0, sizeof(*stx));
    if (statx(pidfd, "", AT_EMPTY_PATH, STATX_INO, stx) < 0) {
        perror("statx on pidfd failed");
        return -1;
    }
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <PID_1> <PID_2>\n", argv[0]);
        return EXIT_FAILURE;
    }

    pid_t pid1 = (pid_t)atoi(argv[1]);
    pid_t pid2 = (pid_t)atoi(argv[2]);

    int fd1 = open_pidfd(pid1);
    int fd2 = open_pidfd(pid2);
    if (fd1 < 0 || fd2 < 0) {
        if (fd1 >= 0) close(fd1);
        if (fd2 >= 0) close(fd2);
        return EXIT_FAILURE;
    }

    struct statx stx1, stx2;
    if (get_pidfs_stat(fd1, &stx1) < 0 || get_pidfs_stat(fd2, &stx2) < 0) {
        close(fd1);
        close(fd2);
        return EXIT_FAILURE;
    }

    printf("PID %d: dev=(%u,%u), ino=%llu\n", pid1,
           stx1.stx_dev_major, stx1.stx_dev_minor, (unsigned long long)stx1.stx_ino);
    printf("PID %d: dev=(%u,%u), ino=%llu\n", pid2,
           stx2.stx_dev_major, stx2.stx_dev_minor, (unsigned long long)stx2.stx_ino);

    if (stx1.stx_dev_major == stx2.stx_dev_major &&
        stx1.stx_dev_minor == stx2.stx_dev_minor &&
        stx1.stx_ino == stx2.stx_ino) {
        printf("РЕЗУЛЬТАТ: Дескриптори вказують на ОДИН І ТОЙ САМИЙ процес!\n");
    } else {
        printf("РЕЗУЛЬТАТ: Це РІЗНІ процеси.\n");
    }

    /* Отримання Network Namespace першого процесу */
    int netns_fd = ioctl(fd1, PIDFD_GET_NET_NAMESPACE, 0);
    if (netns_fd >= 0) {
        printf("Успішно отримано netns fd=%d для PID %d\n", netns_fd, pid1);
        close(netns_fd);
    } else {
        printf("Отримання netns не вдалося: %s\n", strerror(errno));
    }

    /* Отримання метаданих через PIDFD_GET_INFO */
    struct pidfd_info info;
    memset(&info, 0, sizeof(info));
    info.mask = PIDFD_INFO_PID | PIDFD_INFO_PPID | PIDFD_INFO_CREDENT;
    if (ioctl(fd1, PIDFD_GET_INFO, &info) >= 0) {
        printf("Метадані PIDFD_GET_INFO: PID=%u, PPID=%u, EUID=%u, EGID=%u\n",
               info.pid, info.ppid, info.euid, info.egid);
    } else {
        printf("PIDFD_GET_INFO не підтримується або завершився з помилкою: %s\n", strerror(errno));
    }

    close(fd1);
    close(fd2);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <system_error>
#include <utility>
#include <string_view>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <linux/types.h>

namespace pidfs_tools {

#ifndef SYS_pidfd_open
constexpr long sys_pidfd_open_nr = 434;
#else
constexpr long sys_pidfd_open_nr = SYS_pidfd_open;
#endif

#ifndef PIDFS_IOCTL_MAGIC
constexpr unsigned int pidfs_magic = 0x70;
#else
constexpr unsigned int pidfs_magic = PIDFS_IOCTL_MAGIC;
#endif

#ifndef PIDFD_GET_NET_NAMESPACE
#define PIDFD_GET_NET_NAMESPACE _IO(0x70, 4)
#endif

struct pidfd_info_layout {
    std::uint64_t mask;
    std::uint64_t cgroupid;
    std::uint32_t pid;
    std::uint32_t tgid;
    std::uint32_t ppid;
    std::uint32_t euid;
    std::uint32_t egid;
    std::uint64_t start_time;
    std::uint64_t spare[11];
};

#ifndef PIDFD_GET_INFO
#define PIDFD_GET_INFO _IOWR(0x70, 9, pidfd_info_layout)
#endif

class process_handle {
public:
    explicit process_handle(pid_t pid) {
        fd_ = static_cast<int>(::syscall(sys_pidfd_open_nr, pid, 0U));
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "pidfd_open failed");
        }
    }

    ~process_handle() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    process_handle(const process_handle&) = delete;
    process_handle& operator=(const process_handle&) = delete;

    process_handle(process_handle&& other) noexcept : fd_(std::exchange(other.fd_, -1)) {}

    process_handle& operator=(process_handle&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = std::exchange(other.fd_, -1);
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

    [[nodiscard]] ::struct statx fetch_statx() const {
        ::struct statx stx{};
        if (::statx(fd_, "", AT_EMPTY_PATH, STATX_INO, &stx) < 0) {
            throw std::system_error(errno, std::generic_category(), "statx on pidfd failed");
        }
        return stx;
    }

    [[nodiscard]] int get_net_namespace() const {
        int netfd = ::ioctl(fd_, PIDFD_GET_NET_NAMESPACE, 0);
        if (netfd < 0) {
            throw std::system_error(errno, std::generic_category(), "PIDFD_GET_NET_NAMESPACE failed");
        }
        return netfd;
    }

    [[nodiscard]] pidfd_info_layout get_info() const {
        pidfd_info_layout info{};
        info.mask = (1U << 1) | (1U << 3) | (1U << 4); // PID | PPID | CREDENT
        if (::ioctl(fd_, PIDFD_GET_INFO, &info) < 0) {
            throw std::system_error(errno, std::generic_category(), "PIDFD_GET_INFO failed");
        }
        return info;
    }

private:
    int fd_{-1};
};

[[nodiscard]] bool are_identical(const process_handle& h1, const process_handle& h2) {
    const auto stx1 = h1.fetch_statx();
    const auto stx2 = h2.fetch_statx();

    return (stx1.stx_dev_major == stx2.stx_dev_major) &&
           (stx1.stx_dev_minor == stx2.stx_dev_minor) &&
           (stx1.stx_ino == stx2.stx_ino);
}

} // namespace pidfs_tools

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <PID_1> <PID_2>\n";
        return EXIT_FAILURE;
    }

    try {
        const pid_t pid1 = static_cast<pid_t>(std::atoi(argv[1]));
        const pid_t pid2 = static_cast<pid_t>(std::atoi(argv[2]));

        pidfs_tools::process_handle proc1{pid1};
        pidfs_tools::process_handle proc2{pid2};

        const auto stx1 = proc1.fetch_statx();
        const auto stx2 = proc2.fetch_statx();

        std::cout << "PID " << pid1 << ": dev=(" << stx1.stx_dev_major << "," << stx1.stx_dev_minor
                  << "), ino=" << stx1.stx_ino << "\n";
        std::cout << "PID " << pid2 << ": dev=(" << stx2.stx_dev_major << "," << stx2.stx_dev_minor
                  << "), ino=" << stx2.stx_ino << "\n";

        if (pidfs_tools::are_identical(proc1, proc2)) {
            std::cout << "РЕЗУЛЬТАТ: Дескриптори вказують на ОДИН І ТОЙ САМИЙ процес!\n";
        } else {
            std::cout << "РЕЗУЛЬТАТ: Це РІЗНІ процеси.\n";
        }

        try {
            int net_fd = proc1.get_net_namespace();
            std::cout << "Отримано Network Namespace descriptor: " << net_fd << "\n";
            ::close(net_fd);
        } catch (const std::system_error& e) {
            std::cout << "Не вдалося отримати netns: " << e.what() << "\n";
        }

        try {
            const auto info = proc1.get_info();
            std::cout << "Метадані PIDFD_GET_INFO: PID=" << info.pid
                      << ", PPID=" << info.ppid << ", EUID=" << info.euid << "\n";
        } catch (const std::system_error& e) {
            std::cout << "PIDFD_GET_INFO не підтримується: " << e.what() << "\n";
        }

    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## Покрокове інспектування утиліти через strace та sysfs

Для глибокого розуміння роботи підсистеми `pidfs` корисно простежити виконання утиліти за допомогою утиліти трасування системних викликів `strace`.

Під час відкриття дескрипторів `pidfd` ядро відображає їх на унікальні індекси у внутрішній файловій системі `pidfs`. Оскільки `pidfs` є анонімною псевдофайловою системою, ядро присвоює їй бекграундний пристрій з мажором `0` (структура `makedev(0, minor)`). При зверненні до файлових дескрипторів у `/proc/<pid>/fd/` VFS будує анонімні символьні посилання виду `pidfs:[<ino>]`, де в дужках зазначається унікальний 64-бітний номер inode. Це дозволяє спостерігати прив'язку дескрипторів до єдиної псевдофайлової системи під час трасування системних викликів.

При запуску команди `strace -e pidfd_open,statx,ioctl ./pidfs_checker 1234 1234` системний трасувальник виведе наступну послідовність викликів ядра:

```text
pidfd_open(1234, 0)                     = 3
pidfd_open(1234, 0)                     = 4
statx(3, "", AT_EMPTY_PATH, STATX_INO, {stx_mask=STATX_INO, stx_dev=makedev(0, 0x33), stx_ino=140737488355328}) = 0
statx(4, "", AT_EMPTY_PATH, STATX_INO, {stx_mask=STATX_INO, stx_dev=makedev(0, 0x33), stx_ino=140737488355328}) = 0
ioctl(3, _IO(0x70, 0x4), 0)             = 5
ioctl(3, _IOWR(0x70, 0x9, 0x7fff...), {mask=PIDFD_INFO_PID|..., pid=1234}) = 0
```

З трасування чітко видно дві важливі архітектурні деталі:
- Обидва виклики `pidfd_open` повернули окремі файлові дескриптори (`3` та `4`), але обидва дескриптори посилаються на анонімний пристрій `makedev(0, 0x33)` файлової системи `pidfs` і мають ідентичний `stx_ino=140737488355328`.
- При огляді каталогу `/proc/self/fd/3` за допомогою символьних посилань операційна система виведе спеціальний шлях виду `anon_inode:[pidfs]` або `pidfs:[140737488355328]`, підтверджуючи, що дескриптор належить внутрішній псевдофайловій системі `pidfs`.

## Поведінка при багатопотоковості та у зомбі-станах

При практичному використанні утиліти слід враховувати поведінку `pidfs` у двох крайових випадках:

1. **Багатопотокові процеси (TID проти TGID).** У ядрі Linux кожен потік виконання має власний `struct task_struct` та власне число TID. Системний виклик `pidfd_open(pid, flags)` за замовчуванням відкриває дескриптор для лідера групи потоків (TGID). Якщо спробувати відкрити `pidfd` для окремого дочірнього потоку, системний виклик `pidfd_open` повертає помилку `EINVAL`, оскільки `pidfs` призначена для ідентифікації повноцінних процесів, а не окремих ниток виконання.
2. **Процеси в стані зомбі (Zombie processes).** Якщо цільовий процес завершив виконання (викликав `exit_group`), але його батько ще не зчитав статус через `waitpid`, процес перебуває в стані зомбі. Виклик `pidfd_open` для такого PID завершується успішно, а `statx()` віддає дійсний `stx_ino`. Проте спроба викликати `ioctl(pidfd, PIDFD_GET_NET_NAMESPACE, 0)` повертає помилку `ESRCH`, оскільки структури просторів імен процесу вже розформовано ядром.

## Очікуваний вивід утиліти

При виклику програми з двома різними PID, які вказують на той самий процес (наприклад, при повторному відкритті `pidfd` для одного й того самого ідентифікатора у системі), вивід демонстраційного аналізатора має наступний вигляд:

```text
PID 1234: dev=(0,51), ino=140737488355328
PID 1234: dev=(0,51), ino=140737488355328
РЕЗУЛЬТАТ: Дескриптори вказують на ОДИН І ТОЙ САМИЙ процес!
Отримано Network Namespace descriptor: 5
Метадані PIDFD_GET_INFO: PID=1234, PPID=1000, EUID=1000
```

Якщо один із процесів помер і його чисельні номери встигли повторно виділитися новому процесу, значення `ino` у файловій системі `pidfs` гарантовано відрізнятимуться. У цьому випадку аналізатор видасть результат "Це РІЗНІ процеси", повністю захищаючи наглядача від помилкових системних дій.

## Пастки реалізації та особливості операційної системи

1. **Права доступу PTRACE.** Спроба витягти дескриптори просторів імен через `PIDFD_GET_NET_NAMESPACE` або інші команди групи вимагає привілею `CAP_SYS_PTRACE` щодо цільового процесу. Якщо програма запускається від звичайного користувача для чужого процесу, `ioctl` поверне помилку `EPERM`.
2. **Поведінка після завершення процесу.** Якщо процес помер, виклики `ioctl` над `pidfd` повертають помилку `ESRCH` (процес відсутній). Проте системний виклик `statx()` продовжує віддавати оригінальні `stx_dev` та `stx_ino`. Це дозволяє перевірити тотожність процесу навіть після його завершення.
