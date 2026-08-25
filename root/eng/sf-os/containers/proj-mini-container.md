# ⚙️ Створення мінімалістичного контейнерного рушія на C та C++

Утиліти на кшталт Docker, Podman чи `runc` можуть здаватися складними монолітними системами, проте фундаментально низькорівневий рантайм контейнера — це звичайна програма простору користувача. Вона послідовно конфігурує ресурси ядра Linux за допомогою стандартних системних викликів: створює контрольну групу `cgroups v2`, викликає системний виклик `clone` із прапорцями просторів назв, виконує поворот кореня файлової системи через `pivot_root`, знижує привілеї процесу через скидання Capabilities та передає керування бізнес-коду через виклик `execve`.

У цій практичній роботі ми створимо повністю працездатний мінімалістичний контейнерний рушій `minicontainer`. Рушій ізолює цільовий процес у власних просторах назв (PID, Mount, UTS, IPC, Network), встановлює жорсткі ліміти на оперативну пам'ять і процесор через cgroups v2, створює безпечне кореневе середовище з приватними монтуваннями `/proc` та `/sys`, скидає небезпечні системні привілеї та запускає ізольований командний інтерпретатор.

---

## 1. Архітектура та послідовність життєвого циклу

Запуск ізольованого контейнера вимагає суворої координації між двома процесами:
1. **Батьківський процес (Супервізор / Рантайм):** створює контрольні групи `cgroups v2`, виділяє стековий простір, викликає системний виклик `clone(2)`, реєструє новий PID у підсистемі обліку ресурсів, передає сигнал синхронізації дочірньому процесу та очікує його завершення через `waitpid(2)`.
2. **Дочірній процес (Корисне навантаження / PID 1):** блокується до отримання сигналу готовності від батька, налаштовує мережеве ім'я хоста, ізолює таблицю монтування віртуальної файлової системи (VFS), здійснює підміну кореня через `pivot_root`, монтує псевдофайлові системи `/proc`, `/sys` та `/dev`, скидає критичні привілеї ядра (Capabilities), активує заборону підвищення прав `PR_SET_NO_NEW_PRIVS` і передає керування цільовому бінарному файлу через системний виклик `execvp(2)`.

```
Батьківський процес (Рантайм)               Дочірній процес (Контейнер)
        │                                                │
1. Створення каталогу cgroups v2                         │
   (/sys/fs/cgroup/minicontainer-<pid>)                  │
        │                                                │
2. Запис лімітів cpu.max, memory.max                     │
        │                                                │
3. Створення каналу синхронізації (pipe)                 │
        │                                                │
4. Виклик clone() із прапорцями CLONE_NEW* ─────────────►│
        │                                                │
5. Запис PID дочірнього процесу в cgroup.procs           │ 6. Блокуюче очікування сигналу
        │                                                   від батька через pipe
7. Відправка сигналу готовності через pipe ─────────────►│
        │                                                │
8. Очікування завершення через waitpid()                 │ 8. sethostname("minicontainer")
        │                                                │ 9. mount(MS_REC | MS_PRIVATE)
        │                                                │ 10. pivot_root(rootfs, old_root)
        │                                                │ 11. mount("/proc", "/sys", "/dev")
        │                                                │ 12. prctl(PR_CAPBSET_DROP)
        │                                                │ 13. prctl(PR_SET_NO_NEW_PRIVS)
        │                                                │ 14. execvp("/bin/sh")
        ▼                                                ▼
9. Очищення каталогу cgroup після виходу        (Виконання коду застосунку)
```

### Запобігання стану перегонів під час алокації ресурсів

Найбільш небезпечним крайовим випадком на етапі створення контейнера є **стан перегонів ініціалізації cgroups (Cgroup Attachment Race)**.

Коли системний виклик `clone(2)` створює новий процес, новостворений процес негайно починає виконуватися планувальником ядра. Якщо цей процес встигне виконати важкі операції виділення пам'яті (`malloc`, `mmap`) або зайняти всі доступні ядра процесора до того, як батьківський процес запише його ідентифікатор у файл `/sys/fs/cgroup/.../cgroup.procs`, виникають такі ризики:
- Процес контейнера споживає пам'ять хоста понад встановлений ліміт без спрацьовування механізму OOM-кілера групи;
- Процес використовує 100% потужності всіх процесорних ядер, спричиняючи деградацію продуктивності сусідніх сервісів на хості;
- Якщо батьківський процес упаде через аварійний сигнал до моменту реєстрації дочірнього процесу в cgroup, контейнер перетвориться на некерований ізольований процес без жодних ресурсних обмежень.

Для гарантованого усунення цих перегонів ми використовуємо односпрямований системний канал (POSIX Pipe) або пару сокетів (`socketpair`). Дочірній процес першим рядком викликає блокуюче читання `read(sync_pipe[0], &byte, 1)`. Ядро переводить дочірній потік у стан очікування події (`TASK_INTERRUPTIBLE`), виключаючи його з черги активного планування. Лише після того, як батьківський процес успішно запише ліміти в `memory.max`, `cpu.max` та додасть PID у `cgroup.procs`, він відправляє синхронізаційний байт у канал, дозволяючи дочірньому процесу продовжити ініціалізацію.

---

## 2. Реалізація мінімалістичного рантайму

Нижче наведено повні та готові до компіляції реалізації контейнерного рушія двома мовами: класичною C із прямими системними викликами POSIX та сучасною ідіоматичною C++20 із застосуванням ідіоми RAII (Resource Acquisition Is Initialization), автоматичних деструкторів для закриття дескрипторів і демонтування файлових систем, обгортки `std::span` та строгих типів помилок.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <sched.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <linux/capability.h>

#define STACK_SIZE (1024 * 1024) /* 1 МБ стек для дочірнього процесу */
#define CGROUP_BASE "/sys/fs/cgroup/minicontainer"

struct container_config {
    const char *rootfs;
    const char *hostname;
    long memory_limit_bytes;
    long cpu_quota_usec;
    long cpu_period_usec;
    int sync_pipe[2];
    char **argv;
};

/* Обгортка над системним викликом pivot_root */
static int sys_pivot_root(const char *new_root, const char *put_old) {
    return syscall(SYS_pivot_root, new_root, put_old);
}

/* Скидання небезпечних Capabilities */
static int drop_capabilities(void) {
    const int caps_to_drop[] = {
        CAP_SYS_ADMIN,
        CAP_SYS_MODULE,
        CAP_SYS_RAWIO,
        CAP_SYS_PTRACE,
        CAP_NET_ADMIN,
        CAP_DAC_OVERRIDE
    };
    size_t count = sizeof(caps_to_drop) / sizeof(caps_to_drop[0]);

    for (size_t i = 0; i < count; i++) {
        if (prctl(PR_CAPBSET_DROP, caps_to_drop[i], 0, 0, 0) != 0) {
            /* Якщо ядро не підтримує якийсь cap або немає прав */
            if (errno != EINVAL) {
                perror("Помилка prctl(PR_CAPBSET_DROP)");
                return -1;
            }
        }
    }
    return 0;
}

/* Налаштування ізольованої файлової системи VFS */
static int setup_rootfs(const char *rootfs_path) {
    char old_root_path[512];

    /* 1. Запобігання витоку монтувань на хостову систему */
    if (mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) != 0) {
        perror("Помилка переведення кореня в MS_PRIVATE");
        return -1;
    }

    /* 2. Bind-монтування кореневого каталогу на самого себе (вимога pivot_root) */
    if (mount(rootfs_path, rootfs_path, "bind", MS_BIND | MS_REC, NULL) != 0) {
        perror("Помилка bind mount rootfs");
        return -1;
    }

    /* 3. Створення каталогу для тимчасового зберігання старого кореня */
    snprintf(old_root_path, sizeof(old_root_path), "%s/.old_root", rootfs_path);
    if (mkdir(old_root_path, 0700) != 0 && errno != EEXIST) {
        perror("Помилка створення .old_root");
        return -1;
    }

    /* 4. Атомарний обмін кореневих точок монтування */
    if (sys_pivot_root(rootfs_path, old_root_path) != 0) {
        perror("Помилка pivot_root");
        return -1;
    }

    /* 5. Перехід у новий корінь */
    if (chdir("/") != 0) {
        perror("Помилка chdir до нового кореня");
        return -1;
    }

    /* 6. Демонтування та видалення старого хостового кореня */
    if (umount2("/.old_root", MNT_DETACH) != 0) {
        perror("Помилка umount2 .old_root");
        return -1;
    }
    rmdir("/.old_root");

    /* 7. Монтування обов'язкових віртуальних файлових систем */
    if (mount("proc", "/proc", "proc", MS_NOSUID | MS_NOEXEC | MS_NODEV, NULL) != 0) {
        perror("Помилка монтування /proc");
        return -1;
    }
    if (mount("sysfs", "/sys", "sysfs", MS_NOSUID | MS_NOEXEC | MS_NODEV | MS_RDONLY, NULL) != 0) {
        perror("Помилка монтування /sys");
        return -1;
    }
    if (mount("tmpfs", "/dev", "tmpfs", MS_NOSUID | MS_STRICTATIME, "mode=755") != 0) {
        perror("Помилка монтування /dev");
        return -1;
    }

    return 0;
}

/* Функція, що виконується в новому просторі процесів PID 1 */
static int container_entrypoint(void *arg) {
    struct container_config *cfg = (struct container_config *)arg;
    char sync_byte;

    /* Закриваємо записуючий кінець каналу */
    close(cfg->sync_pipe[1]);

    /* Блокуюче очікування завершення налаштування cgroups батьківським процесом */
    if (read(cfg->sync_pipe[0], &sync_byte, 1) != 1) {
        fprintf(stderr, "Помилка отримання сигналу синхронізації від батька\n");
        close(cfg->sync_pipe[0]);
        return 1;
    }
    close(cfg->sync_pipe[0]);

    /* Встановлення власного імені хоста */
    if (sethostname(cfg->hostname, strlen(cfg->hostname)) != 0) {
        perror("Помилка sethostname");
        return 1;
    }

    /* Налаштування ізольованого файлового дерева */
    if (setup_rootfs(cfg->rootfs) != 0) {
        fprintf(stderr, "Не вдалося ініціалізувати кореневу файлову систему\n");
        return 1;
    }

    /* Скидання небезпечних привілеїв */
    if (drop_capabilities() != 0) {
        fprintf(stderr, "Не вдалося скинути Linux Capabilities\n");
        return 1;
    }

    /* Заборона підвищення привілеїв через SUID */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        perror("Помилка активації PR_SET_NO_NEW_PRIVS");
        return 1;
    }

    /* Запуск цільової програми */
    printf("[minicontainer] Контейнер успішно запущено. Передача керування PID 1...\n");
    execvp(cfg->argv[0], cfg->argv);

    /* Якщо execvp повернув керування — сталася помилка */
    perror("Помилка виконання execvp");
    return 127;
}

/* Створення та конфігурація контрольної групи cgroups v2 */
static int setup_cgroups(pid_t child_pid, const struct container_config *cfg, char *cg_path_out, size_t max_len) {
    char file_path[512];
    FILE *f;

    snprintf(cg_path_out, max_len, "%s-%d", CGROUP_BASE, child_pid);

    /* Створення каталогу cgroup для контейнера */
    if (mkdir(cg_path_out, 0755) != 0 && errno != EEXIST) {
        perror("Помилка створення каталогу cgroup v2");
        return -1;
    }

    /* 1. Встановлення ліміту пам'яті (memory.max) */
    snprintf(file_path, sizeof(file_path), "%s/memory.max", cg_path_out);
    f = fopen(file_path, "w");
    if (!f) {
        perror("Помилка відкриття memory.max");
        return -1;
    }
    fprintf(f, "%ld\n", cfg->memory_limit_bytes);
    fclose(f);

    /* 2. Встановлення квоти CPU (cpu.max) */
    snprintf(file_path, sizeof(file_path), "%s/cpu.max", cg_path_out);
    f = fopen(file_path, "w");
    if (!f) {
        perror("Помилка відкриття cpu.max");
        return -1;
    }
    fprintf(f, "%ld %ld\n", cfg->cpu_quota_usec, cfg->cpu_period_usec);
    fclose(f);

    /* 3. Додавання PID дочірнього процесу в групу (cgroup.procs) */
    snprintf(file_path, sizeof(file_path), "%s/cgroup.procs", cg_path_out);
    f = fopen(file_path, "w");
    if (!f) {
        perror("Помилка відкриття cgroup.procs");
        return -1;
    }
    fprintf(f, "%d\n", child_pid);
    fclose(f);

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <шлях_до_rootfs> <команда> [аргументи...]\n", argv[0]);
        return 1;
    }

    /* Перевірка прав суперкористувача (потрібні для створення namespaces та mount) */
    if (geteuid() != 0) {
        fprintf(stderr, "Помилка: запуск контейнера вимагає прав root (sudo)\n");
        return 1;
    }

    struct container_config cfg = {
        .rootfs = argv[1],
        .hostname = "minicontainer",
        .memory_limit_bytes = 256 * 1024 * 1024, /* Ліміт пам'яті: 256 МіБ */
        .cpu_quota_usec = 100000,                /* Квота CPU: 1.0 ядро (100 мс) */
        .cpu_period_usec = 100000,               /* Період CFS: 100 мс */
        .argv = &argv[2]
    };

    /* Створення каналу синхронізації */
    if (pipe(cfg.sync_pipe) != 0) {
        perror("Помилка створення pipe");
        return 1;
    }

    /* Виділення пам'яті під стек дочірнього процесу */
    char *stack = malloc(STACK_SIZE);
    if (!stack) {
        perror("Помилка виділення стеку");
        return 1;
    }
    char *stack_top = stack + STACK_SIZE;

    /* Прапорці ізоляції просторів назв */
    int clone_flags = CLONE_NEWPID |  /* Власне дерево процесів */
                      CLONE_NEWNS  |  /* Власні точки монтування VFS */
                      CLONE_NEWUTS |  /* Власне ім'я хоста */
                      CLONE_NEWIPC |  /* Власні черги IPC */
                      CLONE_NEWNET |  /* Власний мережевий стек */
                      SIGCHLD;        /* Сигнал завершення батькові */

    printf("[minicontainer] Створення дочірнього процесу через clone()...\n");
    pid_t child_pid = clone(container_entrypoint, stack_top, clone_flags, &cfg);
    if (child_pid < 0) {
        perror("Помилка clone()");
        free(stack);
        return 1;
    }

    /* Закриваємо читаючий кінець каналу в батькові */
    close(cfg.sync_pipe[0]);

    /* Конфігурація cgroups v2 для запущеного процесу */
    char cg_path[256];
    printf("[minicontainer] Налаштування лімітів cgroups v2 для PID %d...\n", child_pid);
    if (setup_cgroups(child_pid, &cfg, cg_path, sizeof(cg_path)) != 0) {
        fprintf(stderr, "Аварійна зупинка: не вдалося налаштувати cgroups\n");
        kill(child_pid, SIGKILL);
        waitpid(child_pid, NULL, 0);
        free(stack);
        return 1;
    }

    /* Сповіщення дочірнього процесу про завершення налаштування cgroups */
    char sync_byte = 'G';
    write(cfg.sync_pipe[1], &sync_byte, 1);
    close(cfg.sync_pipe[1]);

    /* Очікування завершення виконання контейнера */
    int status;
    waitpid(child_pid, &status, 0);

    /* Очищення каталогу cgroup після завершення */
    rmdir(cg_path);
    free(stack);

    if (WIFEXITED(status)) {
        printf("[minicontainer] Контейнер завершив роботу з кодом %d\n", WEXITSTATUS(status));
    } else if (WIFSIGNALED(status)) {
        printf("[minicontainer] Контейнер убито сигналом %d\n", WTERMSIG(status));
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <filesystem>
#include <fstream>
#include <system_error>
#include <memory>
#include <cstring>

#include <unistd.h>
#include <sched.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <linux/capability.h>

namespace fs = std::filesystem;

/* Безпечна RAII-обгортка над файловим дескриптором */
class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

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
    [[nodiscard]] bool isValid() const noexcept { return fd_ >= 0; }

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

private:
    int fd_;
};

/* RAII-менеджер створення та очищення контрольної групи cgroups v2 */
class CgroupV2Scope {
public:
    CgroupV2Scope(pid_t pid, long memory_bytes, long cpu_quota_us, long cpu_period_us)
        : path_("/sys/fs/cgroup/minicontainer-" + std::to_string(pid)) {
        
        std::error_code ec;
        fs::create_directories(path_, ec);
        if (ec) {
            throw std::system_error(ec, "Не вдалося створити каталог cgroup");
        }

        // 1. Встановлення ліміту пам'яті
        writeFile("memory.max", std::to_string(memory_bytes));

        // 2. Встановлення квоти CPU
        writeFile("cpu.max", std::to_string(cpu_quota_us) + " " + std::to_string(cpu_period_us));

        // 3. Закріплення процесу за cgroup
        writeFile("cgroup.procs", std::to_string(pid));
    }

    ~CgroupV2Scope() noexcept {
        std::error_code ec;
        fs::remove(path_, ec);
    }

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;

    void writeFile(std::string_view filename, std::string_view content) const {
        fs::path target = path_ / filename;
        std::ofstream stream(target);
        if (!stream.is_open()) {
            throw std::runtime_error("Не вдалося відкрити файл cgroup: " + target.string());
        }
        stream << content << "\n";
    }
};

/* Конфігурація середовища контейнера */
struct ContainerOptions {
    fs::path rootfs;
    std::string hostname{"minicontainer"};
    long memory_limit_bytes{256 * 1024 * 1024};
    long cpu_quota_usec{100000};
    long cpu_period_usec{100000};
    std::vector<std::string> command;
};

class MiniContainerRuntime {
public:
    explicit MiniContainerRuntime(ContainerOptions options)
        : options_(std::move(options)) {}

    int run() {
        if (::geteuid() != 0) {
            std::cerr << "Помилка: запуск контейнера вимагає прав root (sudo)\n";
            return 1;
        }

        int pipe_fds[2];
        if (::pipe2(pipe_fds, O_CLOEXEC) != 0) {
            throw std::system_error(errno, std::generic_category(), "pipe2 failed");
        }
        UniqueFd read_pipe(pipe_fds[0]);
        UniqueFd write_pipe(pipe_fds[1]);

        constexpr size_t kStackSize = 1024 * 1024;
        auto stack = std::make_unique<char[]>(kStackSize);
        char* stack_top = stack.get() + kStackSize;

        struct ChildContext {
            MiniContainerRuntime* self;
            int sync_read_fd;
        } context{this, read_pipe.get()};

        const int clone_flags = CLONE_NEWPID | CLONE_NEWNS | CLONE_NEWUTS |
                                CLONE_NEWIPC | CLONE_NEWNET | SIGCHLD;

        std::cout << "[minicontainer-cpp] Виклик clone() з новими просторами назв...\n";
        pid_t child_pid = ::clone(&childEntrypoint, stack_top, clone_flags, &context);
        if (child_pid < 0) {
            throw std::system_error(errno, std::generic_category(), "clone failed");
        }

        // Батьківський процес налаштовує cgroups v2
        read_pipe.reset(); // Закриваємо читаючий кінець у батькові
        {
            std::cout << "[minicontainer-cpp] Створення scope cgroups v2 для PID " << child_pid << "...\n";
            CgroupV2Scope cgroup(child_pid, options_.memory_limit_bytes,
                                 options_.cpu_quota_usec, options_.cpu_period_usec);

            // Розблоковуємо дитину
            char sync_byte = 'K';
            if (::write(write_pipe.get(), &sync_byte, 1) != 1) {
                ::kill(child_pid, SIGKILL);
                throw std::runtime_error("Помилка надсилання сигналу синхронізації");
            }
            write_pipe.reset();

            // Очікування завершення виконання контейнера
            int status = 0;
            ::waitpid(child_pid, &status, 0);

            if (WIFEXITED(status)) {
                std::cout << "[minicontainer-cpp] Контейнер завершився з кодом: "
                          << WEXITSTATUS(status) << "\n";
            } else if (WIFSIGNALED(status)) {
                std::cout << "[minicontainer-cpp] Контейнер перервано сигналом: "
                          << WTERMSIG(status) << "\n";
            }
        } // Автоматичне видалення каталогу cgroup через деструктор CgroupV2Scope

        return 0;
    }

private:
    ContainerOptions options_;

    static int childEntrypoint(void* raw_arg) noexcept {
        auto* ctx = static_cast<ChildContext*>(raw_arg);
        return ctx->self->executeChild(ctx->sync_read_fd);
    }

    int executeChild(int sync_fd) noexcept {
        // Очікування ініціалізації cgroups батьком
        char sync_byte = 0;
        if (::read(sync_fd, &sync_byte, 1) != 1) {
            return 1;
        }
        ::close(sync_fd);

        // 1. Встановлення імені хоста
        if (::sethostname(options_.hostname.data(), options_.hostname.size()) != 0) {
            return 1;
        }

        // 2. Ізоляція VFS та поворот кореня
        if (!setupMounts(options_.rootfs)) {
            return 1;
        }

        // 3. Зниження привілеїв Capabilities
        if (!dropCaps()) {
            return 1;
        }

        // 4. Заборона набуття нових привілеїв
        if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
            return 1;
        }

        // 5. Підготовка аргументів та виклик execvp
        std::vector<char*> raw_args;
        raw_args.reserve(options_.command.size() + 1);
        for (auto& s : options_.command) {
            raw_args.push_back(s.data());
        }
        raw_args.push_back(nullptr);

        std::cout << "[minicontainer-cpp] Перехід у простір контейнера (PID 1)...\n";
        ::execvp(raw_args[0], raw_args.data());
        return 127;
    }

    static bool setupMounts(const fs::path& rootfs_path) noexcept {
        if (::mount(nullptr, "/", nullptr, MS_REC | MS_PRIVATE, nullptr) != 0) {
            return false;
        }
        if (::mount(rootfs_path.c_str(), rootfs_path.c_str(), "bind", MS_BIND | MS_REC, nullptr) != 0) {
            return false;
        }

        fs::path old_root = rootfs_path / ".old_root";
        std::error_code ec;
        fs::create_directories(old_root, ec);
        if (ec) return false;

        if (::syscall(SYS_pivot_root, rootfs_path.c_str(), old_root.c_str()) != 0) {
            return false;
        }
        if (::chdir("/") != 0) {
            return false;
        }
        if (::umount2("/.old_root", MNT_DETACH) != 0) {
            return false;
        }
        fs::remove("/.old_root", ec);

        // Монтування системних каталогів
        if (::mount("proc", "/proc", "proc", MS_NOSUID | MS_NOEXEC | MS_NODEV, nullptr) != 0) return false;
        if (::mount("sysfs", "/sys", "sysfs", MS_NOSUID | MS_NOEXEC | MS_NODEV | MS_RDONLY, nullptr) != 0) return false;
        if (::mount("tmpfs", "/dev", "tmpfs", MS_NOSUID | MS_STRICTATIME, "mode=755") != 0) return false;

        return true;
    }

    static bool dropCaps() noexcept {
        constexpr int caps[] = {
            CAP_SYS_ADMIN, CAP_SYS_MODULE, CAP_SYS_RAWIO,
            CAP_SYS_PTRACE, CAP_NET_ADMIN, CAP_DAC_OVERRIDE
        };
        for (int cap : caps) {
            if (::prctl(PR_CAPBSET_DROP, cap, 0, 0, 0) != 0 && errno != EINVAL) {
                return false;
            }
        }
        return true;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_rootfs> <команда> [аргументи...]\n";
        return 1;
    }

    ContainerOptions options;
    options.rootfs = argv[1];
    for (int i = 2; i < argc; ++i) {
        options.command.emplace_back(argv[i]);
    }

    try {
        MiniContainerRuntime runtime(std::move(options));
        return runtime.run();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка рантайму: " << ex.what() << "\n";
        return 1;
    }
}
```
:::

---

## 3. Покроковий розбір кожної ланки ініціалізації

Розглянемо детально, які перетворення відбуваються в ядрі Linux під час виконання кожної фази нашого рантайму.

### Крок 1: Створення адресного простору та прапорці `clone`

У звичайних програмах для створення процесів використовується виклик `fork(2)`, проте він копіює всі простори назв батька. Системний виклик `clone(2)` дозволяє явно задати бітову маску нових просторів назв.

Ми передаємо прапорці:
- `CLONE_NEWPID`: ядро створює нову таблицю ідентифікаторів процесів. Перший процес, створений у цьому просторі, отримує віртуальний ідентифікатор `PID 1`. При цьому на хості цей самий процес має реальний ідентифікатор (наприклад, `PID 48291`). Всі системні виклики `getpid()` всередині контейнера повертатимуть `1`.
- `CLONE_NEWNS`: створює незалежну копію дерева монтування віртуальної файлової системи (VFS). Будь-які наступні виклики `mount` або `umount` всередині контейнера будуть невидимими для операційної системи хоста.
- `CLONE_NEWUTS`: відокремлює ідентифікатори вузла мережі. Виклик `sethostname("minicontainer")` змінює ім'я хоста лише для контейнера, залишаючи системне ім'я сервера хоста незмінним.
- `CLONE_NEWIPC`: ізолює системні черги повідомлень (POSIX Message Queues) та семафори System V. Процеси контейнера не можуть надсилати повідомлення процесам хоста через спільну пам'ять IPC.
- `CLONE_NEWNET`: створює абсолютно чистий мережевий стек. Новостворений контейнер має лише ізольований інтерфейс `lo` (Loopback), що перебуває у вимкненому стані (`DOWN`), і не має доступу до фізичних мережевих карт хоста.
- `SIGCHLD`: стандартний сигнал ядра, який буде надіслано батьківському процесу після завершення виконання дочірнього процесу для коректного збору статусу виходу.

### Крок 2: Налаштування файлової системи через `pivot_root`

Просте використання застарілого виклику `chroot` є серйозною дірою безпеки: якщо процес збереже відкритий файловий дескриптор до каталогу поза межами в'язниці, він зможе викликати `fchdir` і повністю вийти з обмеженого простору.

Тому сучасні контейнери використовують виклик `pivot_root(new_root, put_old)`. Він вимагає виконання суворої послідовності:

:::tabs
```c
/* 1. Переведення кореневого монтування в приватний режим */
mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL);

/* 2. Перетворення цільового каталогу rootfs на самостійну точку монтування */
mount(rootfs_path, rootfs_path, "bind", MS_BIND | MS_REC, NULL);

/* 3. Атомарний поворот кореня */
syscall(SYS_pivot_root, rootfs_path, old_root_path);

/* 4. Від'єднання старого хостового кореня */
chdir("/");
umount2("/.old_root", MNT_DETACH);
rmdir("/.old_root");
```
```cpp
/* 1. Переведення кореневого монтування в приватний режим */
::mount(nullptr, "/", nullptr, MS_REC | MS_PRIVATE, nullptr);

/* 2. Перетворення цільового каталогу rootfs на самостійну точку монтування */
::mount(rootfs_path.c_str(), rootfs_path.c_str(), "bind", MS_BIND | MS_REC, nullptr);

/* 3. Атомарний поворот кореня */
::syscall(SYS_pivot_root, rootfs_path.c_str(), old_root_path.c_str());

/* 4. Від'єднання старого хостового кореня */
::chdir("/");
::umount2("/.old_root", MNT_DETACH);
::fs::remove("/.old_root", ec);
```
:::

Прапорець `MNT_DETACH` (ліниве демонтування) змушує ядро негайно видалити вузол зі структури каталогів VFS, унеможливлюючи відкриття будь-яких нових файлів із хоста, і вивільнити пам'ять старих структур після закриття останнього дескриптора.

### Крок 3: Монтування псевдофайлових систем `/proc` та `/sys`

Після повороту кореня утиліти на кшталт `ps`, `top` або системні монітори не зможуть працювати без псевдофайлової системи `procfs`.

Якщо змонтувати хостовий `/proc`, контейнер побачить процеси всієї операційної системи хоста. Але оскільки ми викликали `clone` із прапорцем `CLONE_NEWPID`, системний виклик:

:::tabs
```c
mount("proc", "/proc", "proc", MS_NOSUID | MS_NOEXEC | MS_NODEV, NULL);
```
```cpp
::mount("proc", "/proc", "proc", MS_NOSUID | MS_NOEXEC | MS_NODEV, nullptr);
```
:::

створює новий екземпляр `procfs`, який фільтрує таблицю процесів і відображає виключно процеси поточного PID namespace.

### Крок 4: Скидання Capabilities та безпека

Навіть якщо контейнер працює під `UID 0`, ми скидаємо критичні системні привілеї через `prctl(PR_CAPBSET_DROP)`. Це гарантує:
- Контейнер не зможе завантажити модуль ядра (`CAP_SYS_MODULE`);
- Контейнер не зможе отримати доступ до сирих дисків чи фізичної пам'яті (`CAP_SYS_RAWIO`);
- Контейнер не зможе змінювати мережеві маршрути хоста (`CAP_NET_ADMIN`).

Додатковий системний виклик:

:::tabs
```c
prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);
```
```cpp
::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);
```
:::

гарантує, що навіть запуск сторонньої утиліти із бітом `setuid root` не зможе повернути скинуті Capabilities.

---

## 4. Підготовка тестового оточення та запуск

Для практичної перевірки нашого контейнерного рушія необхідно підготувати мінімальну кореневу файлову систему `rootfs`.

```bash
# 1. Створення каталогу для rootfs
mkdir -p /tmp/alpine-rootfs

# 2. Експорт розпакованого образу Alpine Linux із Docker Hub
docker export $(docker create alpine:latest) | tar -C /tmp/alpine-rootfs -xf -

# 3. Компіляція програми на C
gcc -O2 -Wall minicontainer.c -o minicontainer

# 4. Компіляція програми на C++20
g++ -O2 -Wall -std=c++20 minicontainer.cpp -o minicontainer-cpp

# 5. Запуск ізольованої оболонки під керуванням нашого рантайму
sudo ./minicontainer /tmp/alpine-rootfs /bin/sh
```

### Простеження ізоляції зсередини контейнера

Після потрапляння в командний рядок контейнера виконаємо діагностичні команди:

```bash
# Перевірка PID: ми бачимо лише наш шелл як PID 1
/ # ps aux
PID   USER     TIME  COMMAND
    1 root      0:00 /bin/sh
    5 root      0:00 ps aux

# Перевірка імені хоста
/ # hostname
minicontainer

# Перевірка обмеження пам'яті через cgroups v2
/ # cat /sys/fs/cgroup/memory.max
268435456

# Спроба виконати заборонену дію (скинутий CAP_SYS_ADMIN)
/ # mount -t tmpfs none /mnt
mount: permission denied (are you root?)
```

---

## 5. Виробничі пастки та крайові випадки реалізації

Під час написання низькорівневих контейнерних рушіїв виникають специфічні проблеми ядра, які рідко зустрічаються у звичайному прикладному програмуванні.

### Пастка 1: Проблема «Зомбі-процесів» та обробка сигналів у PID 1

У Linux процес із `PID 1` має спеціальний системний статус. Якщо дочірній процес контейнера створює власні підпроцеси, а ті завершуються, саме `PID 1` зобов'язаний збирати їхні статуси виходу через виклик `wait()` або `waitpid()`. Якщо цього не робити, таблиця процесів операційної системи заповнюється записами типу `[defunct]` (зомбі-процеси), що врешті-решт блокує створення нових процесів у системі через вичерпання ліміту `pids.max`.

Крім того, ядро Linux **не застосовує стандартні обробники сигналів (Default Signal Actions) для процесу з PID 1**. Якщо застосунок не встановив явний обробник через `sigaction(SIGTERM, ...)` або `sigaction(SIGINT, ...)`, надсилання сигналу `SIGTERM` буде просто проігноровано ядром. Саме тому в промислових контейнерах часто використовують легковагові ініціалізатори (`tini`, `dumb-init`), які перехоплюють сигнали та коректно транслюють їх дочірнім процесам.

### Пастка 2: Витік монтувань та взаємодія з systemd

За замовчуванням у сучасних дистрибутивах Linux (Ubuntu, Debian, Fedora, RHEL) системний менеджер `systemd` монтує кореневу файлову систему з прапорцем спільного поширення `MS_SHARED`. Це означає, що будь-яке монтування, здійснене всередині простору назв дочірнього процесу, автоматично поширюється у вихідний простір назв хоста.

Якщо перед викликом `pivot_root` не виконати переведення кореня в режим `MS_PRIVATE`, подальші операції монтування `/proc`, `/sys` та тимчасових каталогів зіпсують файлову систему хоста, а системний виклик `pivot_root` поверне помилку `EINVAL`.

### Пастка 3: Тротлінг планувальника CFS та затримки p99

При налаштуванні квоти `cpu.max` важливо враховувати період планувальника `cpu_period_usec`. Якщо встановити період занадто великим (наприклад, `1000000` мкс або 1 секунду) при квості `100000` мкс (0.1 ядра), багатонитковий застосунок може використати всю 100-мілісекундну квоту за перші 100 мс на початку секунди. Решту 900 мс процес перебуватиме в стані примусового заморожування (CFS throttling), викликаючи сплеск 99-го процентиля затримки (p99 latency) до майже повної секунди. Рекомендований стандартний період для більшості хмарних застосунків становить `100000` мкс (100 мс).

---

## 6. Мережева сантехніка: підключення veth-пари

Оскільки ми передали у виклик `clone` прапорець `CLONE_NEWNET`, запущений контейнер має повністю ізольований мережевий стек без зовнішнього зв'язку. Щоб надати контейнеру доступ до локальної мережі хоста або інтернету, рантайм налаштовує віртуальну кабельну пару **veth (Virtual Ethernet Pair)**.

Мережеве налаштування здійснюється батьківським процесом (або CNI-плагіном) у проміжку між викликом `clone` та відправкою сигналу готовності:

```bash
# 1. Створення пари віртуальних інтерфейсів на хості
sudo ip link add veth_host type veth peer name veth_guest

# 2. Переміщення кінця veth_guest у мережевий простір дочірнього процесу
sudo ip link set veth_guest netns <child_pid>

# 3. Налаштування хостового кінця інтерфейсу
sudo ip addr add 10.200.1.1/24 dev veth_host
sudo ip link set veth_host up

# 4. Налаштування інтерфейсу всередині простору назв контейнера
sudo nsenter -t <child_pid> -n ip addr add 10.200.1.2/24 dev veth_guest
sudo nsenter -t <child_pid> -n ip link set dev veth_guest name eth0
sudo nsenter -t <child_pid> -n ip link set eth0 up
sudo nsenter -t <child_pid> -n ip link set lo up
sudo nsenter -t <child_pid> -n ip route add default via 10.200.1.1
```

Після виконання цих команд пакет, надісланий із сокета всередині контейнера на шлюз `10.200.1.1`, проходить крізь віртуальний кабель `veth`, потрапляє в мережевий стек ядра хоста, де маршрутизується через фізичну мережеву карту хоста за допомогою правил маскарадингу NAT (`iptables -t nat -A POSTROUTING -s 10.200.1.0/24 -j MASQUERADE`).

---

## 7. Простеження та діагностика через `strace` та `/proc`

Для глибокого розуміння того, як ядро обробляє створення нашого контейнера, корисно запустити рантайм під наглядом трасувальника системних викликів `strace`.

```bash
sudo strace -f -e trace=clone,pivot_root,mount,umount2,prctl,sethostname,execve ./minicontainer /tmp/alpine-rootfs /bin/sh
```

У вихідному потоці трасування чітко видно хронологію народження контейнера:

```
[pid 48290] clone(child_stack=0x7ffe1000, flags=CLONE_NEWNS|CLONE_NEWUTS|CLONE_NEWIPC|CLONE_NEWPID|CLONE_NEWNET|SIGCHLD) = 48291
[pid 48290] openat(AT_FDCWD, "/sys/fs/cgroup/minicontainer-48291/cgroup.procs", O_WRONLY|O_CREAT|O_TRUNC, 0666) = 4
[pid 48290] write(4, "48291\n", 6)      = 6
[pid 48290] write(3, "G", 1)             = 1
[pid 48291] read(3, "G", 1)              = 1
[pid 48291] sethostname("minicontainer", 13) = 0
[pid 48291] mount(NULL, "/", NULL, MS_REC|MS_PRIVATE, NULL) = 0
[pid 48291] mount("/tmp/alpine-rootfs", "/tmp/alpine-rootfs", "bind", MS_REC|MS_BIND, NULL) = 0
[pid 48291] pivot_root("/tmp/alpine-rootfs", "/tmp/alpine-rootfs/.old_root") = 0
[pid 48291] chdir("/")                   = 0
[pid 48291] umount2("/.old_root", MNT_DETACH) = 0
[pid 48291] mount("proc", "/proc", "proc", MS_NOSUID|MS_NODEV|MS_NOEXEC, NULL) = 0
[pid 48291] mount("sysfs", "/sys", "sysfs", MS_NOSUID|MS_NODEV|MS_NOEXEC|MS_RDONLY, NULL) = 0
[pid 48291] prctl(PR_CAPBSET_DROP, CAP_SYS_ADMIN, 0, 0, 0) = 0
[pid 48291] prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) = 0
[pid 48291] execve("/bin/sh", ["/bin/sh"], 0x7ffd2000) = 0
```

### Аналіз структури `/proc/self/mountinfo`

Щоб перевірити стан дерева монтувань зсередини контейнера, зчитаємо файл `/proc/self/mountinfo`:

```bash
/ # cat /proc/self/mountinfo
120 100 0:42 / / rw,relatime - overlay overlay rw,lowerdir=...,upperdir=...
121 120 0:43 / /proc rw,nosuid,nodev,noexec,relatime - proc proc rw
122 120 0:44 / /sys ro,nosuid,nodev,noexec,relatime - sysfs sysfs ro
123 120 0:45 / /dev rw,nosuid,relatime - tmpfs tmpfs rw,mode=755
```

Кожен рядок містить ідентифікатор точки монтування, батьківський ідентифікатор, мажорний/мінорний номер пристрою та прапорці безпеки. Усі шляхи відносні до нового кореня `/`, а стара хостова файлова система відсутня в списку, що підтверджує надійність ізоляції VFS.

---

## 8. Додавання фільтрації системних викликів Seccomp-BPF

Для підвищення стійкості пісочниці контейнерний рантайм може заблокувати потенційно небезпечні системні виклики ядра за допомогою підсистеми **Seccomp-BPF (Secure Computing Mode)**.

Фільтр конструюється як масив інструкцій класичної віртуальної машини cBPF:

:::tabs
```c
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <sys/syscall.h>

static int apply_seccomp_filter(void) {
    struct sock_filter filter[] = {
        /* 1. Завантаження номера системної архітектури в акумулятор BPF */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
        /* Перевірка архітектури x86_64; якщо не збігається — вбити процес */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        /* 2. Завантаження номера системного виклику в акумулятор */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

        /* 3. Блокування виклику reboot (перезавантаження сервера) */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_reboot, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

        /* 4. Блокування виклику kexec_load (заміна ядра на льоту) */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_kexec_load, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

        /* 5. Блокування виклику init_module (завантаження драйверів) */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_init_module, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

        /* 6. Дозвіл для всіх інших системних викликів */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW)
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) != 0) {
        perror("Помилка завантаження фільтра Seccomp-BPF");
        return -1;
    }
    return 0;
}
```
```cpp
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <sys/syscall.h>
#include <cstddef>
#include <vector>

static bool applySeccompFilter() noexcept {
    const std::vector<sock_filter> filter = {
        // 1. Перевірка архітектури
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(seccomp_data, arch))),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        // 2. Завантаження номера виклику
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(seccomp_data, nr))),

        // 3. Блокування reboot
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_reboot, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

        // 4. Блокування kexec_load
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_kexec_load, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

        // 5. Блокування init_module
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_init_module, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

        // 6. Дозвіл решти викликів
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW)
    };

    const sock_fprog prog = {
        .len = static_cast<unsigned short>(filter.size()),
        .filter = const_cast<sock_filter*>(filter.data())
    };

    return ::prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) == 0;
}
```
:::

Програма BPF компілюється ядром у швидкий машинний код за допомогою JIT-компілятора ядра. Під час кожного звернення до таблиці системних викликів процесор виконує фільтр за кілька наносекунд. Важливо зазначити, що після завантаження Seccomp-фільтр **неможливо видалити чи послабити**: він автоматично успадковується всіма дочірніми процесами та потоками контейнера під час викликів `clone` та `execve`.

---

## 9. Безпривілейовані контейнери (Rootless Containers)

У наведеному вище рушії ми запускали програму з правами `root` на хості через `sudo`. Проте в сучасній інфраструктурі високої безпеки застосовується технологія **Rootless Containers**, яка дозволяє звичайному непривілейованому користувачеві створювати контейнери без виклику `sudo` та без демонів із привілеями суперкористувача.

Це досягається поєднанням простору користувачів **User Namespaces (`CLONE_NEWUSER`)** та утиліт мапінгу `newuidmap`/`newgidmap`.

### Механіка мапінгу ідентифікаторів

У системних файлах `/etc/subuid` та `/etc/subgid` адміністратор виділяє кожному користувачеві діапазон із 65 536 підлеглих ідентифікаторів:

```
# Користувач developer отримує діапазон хостових UID від 100000 до 165535:
developer:100000:65536
```

Під час запуску rootless-рантайму відбуваються такі кроки:
1. Процес викликає `unshare(CLONE_NEWUSER)`. У цей момент процес стає `UID 0 (root)` усередині нового простору користувачів, але залишається звичайним `UID 1000` на хості.
2. Батьківський процес викликає допоміжну SUID-утиліту `newuidmap <pid> 0 100000 65536`. Це записує в ядро відображення: `UID 0` контейнера стає `UID 100000` на хості.
3. Оскільки процес є суперкористувачем у власному User Namespace, ядро дозволяє йому без прав root на хості створити нові простори `CLONE_NEWPID`, `CLONE_NEWNS`, `CLONE_NEWNET`, монтувати приватні файлові системи `tmpfs`, `procfs` та налаштовувати мережу через TAP-інтерфейси простору користувача (`slirp4netns` або `pasta`).
4. Навіть якщо зловмисник повністю скомпрометує застосунок усередині rootless-контейнера та здійснить вихід (Container Breakout) у файлову систему хоста, ядро розглядатиме всі його операції з правами непривілейованого `UID 100000`, не дозволяючи прочитати файли `/etc/shadow`, системні логи чи чужі каталоги користувачів.

---

## 10. Практична верифікація лімітів: OOM Killer та тротлінг CPU

Щоб переконатися, що налаштовані контролери `cgroups v2` дійсно контролюють виділені ресурси, проведемо два практичні стрес-тести зсередини контейнера.

### Тест 1: Спрацьовування Out-Of-Memory Killer

Наш рантайм встановив ліміт оперативної пам'яті `memory.max = 268435456` (256 МіБ). Запустимо всередині контейнера команду, яка виділяє 300 МіБ анонімної пам'яті через виклик `mmap` або утиліту `stress`:

```bash
/ # stress-ng --vm 1 --vm-bytes 300M --timeout 10s
```

У момент, коли сумарне споживання пам'яті процесами контейнера досягає 256 МіБ, підсистема пам'яті ядра виконує такі дії:
1. Ядро ініціює синхронне витіснення сторінок дискового кешу (Page Cache Reclaim).
2. Оскільки пам'ять зайнята анонімними сторінками коду застосунку, які неможливо скинути на диск без файлу підкачки (Swap), алокатор пам'яті ядра опиняється в стані виснаження.
3. Ядро активує алгоритм вибору жертви в межах контрольної групи `cgroups` та надсилає процесу невідворотний сигнал `SIGKILL` (код 9).

Наш батьківський процес перехоплює подію у виклику `waitpid()` та фіксує аварійне завершення:
```
[minicontainer] Контейнер убито сигналом 9 (SIGKILL)
```

Перевіривши лічильник подій на хості через файл `/sys/fs/cgroup/minicontainer-<pid>/memory.events`, ми побачимо збільшення показників `oom` та `oom_kill`:
```bash
$ cat /sys/fs/cgroup/minicontainer-48291/memory.events
oom 1
oom_kill 1
```

### Тест 2: Фіксація тротлінгу процесора

Запустимо нескінченний цикл обчислень на двох паралельних потоках:
```bash
/ # yes > /dev/null & yes > /dev/null &
```

Оскільки квота `cpu.max` встановлена у значення `100000 100000` (еквівалент 1.0 ядра), а процеси намагаються спожити 2.0 ядра (200 000 мкс за кожен 100-мілісекундний період CFS), планувальник ядра після вичерпання перших 100 мс кожного інтервалу примусово призупиняє виконання обох потоків до початку наступного періоду.

Зчитавши файл `cpu.stat` на хості, ми отримаємо пряме підтвердження роботи планувальника:
```bash
$ cat /sys/fs/cgroup/minicontainer-48291/cpu.stat
nr_periods 640
nr_throttled 638
throttled_usec 31892010
```

Ці показники демонструють, що з 640 періодів планування контейнер зазнавав тротлінгу в 638 періодах, а сумарний час примусового простою склав майже 32 секунди. Це наочно доводить абсолютну надійність механізмів ізоляції ресурсів, що лежать в основі промислових контейнерних систем.
