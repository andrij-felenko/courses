# ⚙️ Реалізація міні-контейнера з системних примітивів

Контейнеризація в операційних системах сімейства Linux часто сприймається як складна магія демонів на кшталт Docker, Podman чи containerd. Насправді будь-який контейнерний рушій — це звичайна програма простору користувача, яка послідовно конфігурує примітиви ядра Linux для розмежування глобальних ідентифікаторів, ізоляції файлових шляхів і обмеження споживання фізичних ресурсів.

Нижче наведено повнофункціональну реалізацію мінімального контейнерного рушія (`minibox`), написаного з нуля за допомогою низькорівневих системних викликів ядра Linux без залучення сторонніх бібліотек, високорівневих фреймворків чи зовнішніх утиліт.

---

### Постановка задачі та архітектура

Головна мета проєкту — створити компактну системну утиліту, яка приймає два параметри: шлях до підготовленого кореневого каталогу (*rootfs*, наприклад, розпакованого архіву Alpine Linux або BusyBox) та виконувану команду з аргументами, після чого запускає цю команду в надійно ізольованій пісочниці.

Щоб створити повноцінне ізольоване середовище, утиліта має вирішити чотири фундаментальні інженерні задачі:

1. **Ізоляція просторів імен (Namespaces):** Процес повинен отримати персональні таблиці монтування файлових систем (`CLONE_NEWNS`), окреме дерево номерів процесів (`CLONE_NEWPID`), ізольований мережевий стек (`CLONE_NEWNET`), власні черги міжпроцесної взаємодії (`CLONE_NEWIPC`), персональне ім'я хоста (`CLONE_NEWUTS`) та персоналізований корінь ієрархії контрольних груп (`CLONE_NEWCGROUP`).
2. **Надійна ізоляція файлової системи (VFS):** Старе кореневе дерево операційної системи хоста має бути повністю відрізане від процесу. Використання застарілого виклику `chroot` є небезпечним через відомі методи втечі. Замість цього утиліта реалізує атомарний обмін точок монтування через `pivot_root`, відмонтовує старий корінь із прапорцем `MNT_DETACH` та монтує нові ізольовані примірники псевдофайлових систем `/proc`, `/sys` і `/dev`.
3. **Квотування та облік ресурсів (cgroups v2):** Процес автоматично прив'язується до новоствореної групи в ієрархії `/sys/fs/cgroup`. Рушій встановлює жорсткий ліміт оперативної пам'яті (64 МБ), квоту процесорного часу (20% від потужності одного процесорного ядра) та обмежує максимальну кількість задач (не більше 32 процесів для захисту від атак типу fork-bomb).
4. **Зниження поверхні атаки на ядро (seccomp-BPF):** Процес встановлює незворотний прапорець `PR_SET_NO_NEW_PRIVS` для блокування підвищення привілеїв через біти `setuid` на бінарних файлах, а також завантажує власний BPF-фільтр системних викликів, який забороняє виконання деструктивних операцій (перезавантаження вузла `reboot`, завантаження модулів ядра `init_module`, маніпуляція свопінгом `swapon`).

#### Схема синхронізації батьківського та дочірнього процесів

Створення ізольованого контейнера вимагає суворої координації між батьківським процесом (що виконується в просторі хоста з правами суперкористувача) та дочірнім процесом (який стає першим процесом PID 1 у новому контейнері). 

Якщо дочірній процес почне виконання коду застосунку до того, як батьківський процес запише його PID у контрольні файли cgroups, дочірній процес зможе миттєво спожити всю доступну пам'ять або заблокувати процесор хоста. Для запобігання стану гонитви (*race condition*) використовується неіменований односпрямований канал (*anonymous pipe*):

```
Батьківський процес (Host PID)                  Дочірній процес (Container PID 1)
───────────────────────────────                  ─────────────────────────────────
1. Створює cgroup v2 у /sys/fs/cgroup            
2. Відкриває неіменований канал (pipe)           
3. Викликає clone(CLONE_NEW*) ─────────────────> Починає виконання в новому стеку
4. Записує PID дочірнього процесу                Блокується на читанні з каналу:
   у /sys/fs/cgroup/minibox/cgroup.procs         read(sync_pipe[0])
5. Записує ліміти пам'яті, CPU, PID              
6. Закриває канал (надсилає EOF) ──────────────> Отримує сигнал розблокування (EOF):
7. Очікує завершення через waitpid()             1. Встановлює hostname (sethostname)
                                                 2. Робить монтування MS_PRIVATE
                                                 3. Виконує pivot_root()
                                                 4. Монтує /proc, /sys, /dev
                                                 5. Вмикає PR_SET_NO_NEW_PRIVS
                                                 6. Завантажує seccomp-BPF фільтр
                                                 7. Викликає execve("/bin/sh")
```

---

### Реалізація коду

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
#include <stddef.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/mount.h>
#include <sys/syscall.h>
#include <sys/prctl.h>
#include <sys/sysmacros.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>

#define STACK_SIZE (1024 * 1024)
#define CGROUP_PATH "/sys/fs/cgroup/minibox"

struct container_config {
    const char *rootfs;
    char **argv;
    int sync_pipe[2];
};

static int pivot_root_syscall(const char *new_root, const char *put_old) {
    return syscall(SYS_pivot_root, new_root, put_old);
}

static int write_file(const char *path, const char *value) {
    int fd = open(path, O_WRONLY | O_TRUNC);
    if (fd < 0) return -1;
    size_t len = strlen(value);
    ssize_t written = write(fd, value, len);
    close(fd);
    return (written == (ssize_t)len) ? 0 : -1;
}

static int setup_cgroup(pid_t pid) {
    mkdir(CGROUP_PATH, 0755);

    char pid_str[32];
    snprintf(pid_str, sizeof(pid_str), "%d\n", pid);

    char procs_path[256];
    snprintf(procs_path, sizeof(procs_path), "%s/cgroup.procs", CGROUP_PATH);
    if (write_file(procs_path, pid_str) < 0) {
        perror("cgroup.procs");
        return -1;
    }

    char mem_path[256];
    snprintf(mem_path, sizeof(mem_path), "%s/memory.max", CGROUP_PATH);
    write_file(mem_path, "67108864\n"); /* 64 MB */

    char cpu_path[256];
    snprintf(cpu_path, sizeof(cpu_path), "%s/cpu.max", CGROUP_PATH);
    write_file(cpu_path, "20000 100000\n"); /* 20% одного ядра */

    char pids_path[256];
    snprintf(pids_path, sizeof(pids_path), "%s/pids.max", CGROUP_PATH);
    write_file(pids_path, "32\n"); /* Максимум 32 процеси */

    return 0;
}

static int install_seccomp_filter(void) {
    struct sock_filter filter[] = {
        /* 1. Перевірка архітектури процесора (x86_64) */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        /* 2. Завантаження номера системного виклику */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

        /* 3. Блокування небезпечних для хоста системних викликів */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_reboot, 5, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_kexec_load, 4, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_init_module, 3, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_finit_module, 2, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_swapon, 1, 0),

        /* 4. Дозвіл для всіх інших системних викликів */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        /* 5. Повернення помилки EPERM для заборонених викликів */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & 0xffff))
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
        perror("prctl(NO_NEW_PRIVS)");
        return -1;
    }

    if (syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog) < 0) {
        perror("seccomp");
        return -1;
    }

    return 0;
}

static int setup_rootfs(const char *rootfs) {
    /* 1. Ізоляція дерева монтування від хоста */
    if (mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) < 0) {
        perror("mount MS_PRIVATE");
        return -1;
    }

    /* 2. Bind mount для перетворення каталогу rootfs на точку монтування VFS */
    if (mount(rootfs, rootfs, NULL, MS_BIND | MS_REC, NULL) < 0) {
        perror("mount bind rootfs");
        return -1;
    }

    /* 3. Створення підкаталогу для тимчасового перенесення старого кореня */
    char old_root[512];
    snprintf(old_root, sizeof(old_root), "%s/.old_root", rootfs);
    mkdir(old_root, 0700);

    /* 4. Атомарний обмін кореневих дерев */
    if (pivot_root_syscall(rootfs, old_root) < 0) {
        perror("pivot_root");
        return -1;
    }

    if (chdir("/") < 0) {
        perror("chdir /");
        return -1;
    }

    /* 5. Відмонтування старого кореня та видалення точки монтування */
    if (umount2("/.old_root", MNT_DETACH) < 0) {
        perror("umount2 .old_root");
        return -1;
    }
    rmdir("/.old_root");

    /* 6. Монтування приватних віртуальних файлових систем */
    mkdir("/proc", 0755);
    if (mount("proc", "/proc", "proc", MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL) < 0) {
        perror("mount /proc");
        return -1;
    }

    mkdir("/sys", 0755);
    if (mount("sysfs", "/sys", "sysfs", MS_RDONLY | MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL) < 0) {
        perror("mount /sys");
        return -1;
    }

    mkdir("/dev", 0755);
    mount("tmpfs", "/dev", "tmpfs", MS_NOSUID | MS_STRICTATIME, "mode=755");

    /* Створення мінімального набору файлів пристроїв */
    mknod("/dev/null", S_IFCHR | 0666, makedev(1, 3));
    mknod("/dev/zero", S_IFCHR | 0666, makedev(1, 5));
    mknod("/dev/urandom", S_IFCHR | 0666, makedev(1, 9));

    return 0;
}

static int container_entry(void *arg) {
    struct container_config *cfg = (struct container_config *)arg;

    /* Закриваємо записуючий дескриптор і чекаємо налаштування cgroups */
    close(cfg->sync_pipe[1]);
    char ch;
    if (read(cfg->sync_pipe[0], &ch, 1) != 0) {
        /* EOF означає успішну ініціалізацію батьківським процесом */
    }
    close(cfg->sync_pipe[0]);

    sethostname("minibox", 7);

    if (setup_rootfs(cfg->rootfs) < 0) {
        fprintf(stderr, "Помилка налаштування файлового середовища rootfs\n");
        return 1;
    }

    if (install_seccomp_filter() < 0) {
        fprintf(stderr, "Помилка завантаження фільтра seccomp\n");
        return 1;
    }

    /* Запуск цільової програми всередині контейнера */
    execvp(cfg->argv[0], cfg->argv);
    perror("execvp");
    return 1;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <шлях_до_rootfs> <команда> [аргументи...]\n", argv[0]);
        return 1;
    }

    if (getuid() != 0) {
        fprintf(stderr, "Помилка: потрібні права суперкористувача (root)\n");
        return 1;
    }

    struct container_config cfg;
    cfg.rootfs = argv[1];
    cfg.argv = &argv[2];

    if (pipe(cfg.sync_pipe) < 0) {
        perror("pipe");
        return 1;
    }

    char *stack = malloc(STACK_SIZE);
    if (!stack) {
        perror("malloc stack");
        return 1;
    }
    char *stack_top = stack + STACK_SIZE;

    int clone_flags = CLONE_NEWNS | CLONE_NEWPID | CLONE_NEWUTS |
                      CLONE_NEWIPC | CLONE_NEWNET | CLONE_NEWCGROUP | SIGCHLD;

    pid_t child_pid = clone(container_entry, stack_top, clone_flags, &cfg);
    if (child_pid < 0) {
        perror("clone");
        free(stack);
        return 1;
    }

    /* Батьківський процес закриває читаючий кінець каналу */
    close(cfg.sync_pipe[0]);

    /* Налаштування контрольних груп для дочірнього процесу */
    if (setup_cgroup(child_pid) < 0) {
        fprintf(stderr, "Не вдалося налаштувати cgroup для PID %d\n", child_pid);
        kill(child_pid, SIGKILL);
        close(cfg.sync_pipe[1]);
        free(stack);
        return 1;
    }

    /* Надсилаємо сигнал розблокування дочірньому процесу */
    close(cfg.sync_pipe[1]);

    int status;
    waitpid(child_pid, &status, 0);

    /* Зачистка каталогів cgroups */
    rmdir(CGROUP_PATH);
    free(stack);

    if (WIFEXITED(status)) {
        return WEXITSTATUS(status);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <array>
#include <memory>
#include <system_error>
#include <filesystem>
#include <fstream>
#include <cstddef>
#include <unistd.h>
#include <fcntl.h>
#include <sched.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/mount.h>
#include <sys/syscall.h>
#include <sys/prctl.h>
#include <sys/sysmacros.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>

namespace fs = std::filesystem;

class Pipe {
public:
    Pipe() {
        if (pipe(fds_.data()) < 0) {
            throw std::system_error(errno, std::generic_category(), "pipe failed");
        }
    }
    ~Pipe() {
        close_read();
        close_write();
    }
    Pipe(const Pipe&) = delete;
    Pipe& operator=(const Pipe&) = delete;

    int read_fd() const noexcept { return fds_[0]; }
    int write_fd() const noexcept { return fds_[1]; }

    void close_read() noexcept {
        if (fds_[0] >= 0) {
            close(fds_[0]);
            fds_[0] = -1;
        }
    }
    void close_write() noexcept {
        if (fds_[1] >= 0) {
            close(fds_[1]);
            fds_[1] = -1;
        }
    }

private:
    std::array<int, 2> fds_{-1, -1};
};

class CgroupScope {
public:
    explicit CgroupScope(const fs::path& path) : path_(path) {
        fs::create_directories(path_);
    }
    ~CgroupScope() {
        std::error_code ec;
        fs::remove(path_, ec);
    }
    CgroupScope(const CgroupScope&) = delete;
    CgroupScope& operator=(const CgroupScope&) = delete;

    void configure(pid_t pid, std::string_view memory_bytes,
                   std::string_view cpu_quota, std::string_view pids_max) {
        write_entry("cgroup.procs", std::to_string(pid) + "\n");
        write_entry("memory.max", std::string(memory_bytes) + "\n");
        write_entry("cpu.max", std::string(cpu_quota) + "\n");
        write_entry("pids.max", std::string(pids_max) + "\n");
    }

private:
    void write_entry(const std::string& filename, const std::string& data) {
        std::ofstream ofs(path_ / filename);
        if (!ofs) {
            throw std::runtime_error("Failed to open cgroup control file: " + filename);
        }
        ofs << data;
        if (!ofs) {
            throw std::runtime_error("Failed to write to cgroup control file: " + filename);
        }
    }
    fs::path path_;
};

struct ContainerConfig {
    std::string rootfs;
    std::vector<std::string> args;
    int read_pipe_fd;
};

class MiniContainer {
public:
    static void install_seccomp() {
        struct sock_filter filter[] = {
            BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

            BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_reboot, 5, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_kexec_load, 4, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_init_module, 3, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_finit_module, 2, 0),
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_swapon, 1, 0),

            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & 0xffff))
        };

        struct sock_fprog prog = {
            .len = static_cast<unsigned short>(sizeof(filter) / sizeof(filter[0])),
            .filter = filter,
        };

        if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "prctl(PR_SET_NO_NEW_PRIVS) failed");
        }

        if (syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog) < 0) {
            throw std::system_error(errno, std::generic_category(), "seccomp filter failed");
        }
    }

    static void setup_rootfs(const std::string& rootfs) {
        if (mount(nullptr, "/", nullptr, MS_REC | MS_PRIVATE, nullptr) < 0) {
            throw std::system_error(errno, std::generic_category(), "mount MS_PRIVATE failed");
        }

        if (mount(rootfs.c_str(), rootfs.c_str(), nullptr, MS_BIND | MS_REC, nullptr) < 0) {
            throw std::system_error(errno, std::generic_category(), "mount bind rootfs failed");
        }

        fs::path old_root_path = fs::path(rootfs) / ".old_root";
        fs::create_directories(old_root_path);

        if (syscall(SYS_pivot_root, rootfs.c_str(), old_root_path.c_str()) < 0) {
            throw std::system_error(errno, std::generic_category(), "pivot_root failed");
        }

        if (chdir("/") < 0) {
            throw std::system_error(errno, std::generic_category(), "chdir / failed");
        }

        if (umount2("/.old_root", MNT_DETACH) < 0) {
            throw std::system_error(errno, std::generic_category(), "umount2 .old_root failed");
        }
        fs::remove("/.old_root");

        fs::create_directories("/proc");
        if (mount("proc", "/proc", "proc", MS_NOSUID | MS_NODEV | MS_NOEXEC, nullptr) < 0) {
            throw std::system_error(errno, std::generic_category(), "mount /proc failed");
        }

        fs::create_directories("/sys");
        if (mount("sysfs", "/sys", "sysfs", MS_RDONLY | MS_NOSUID | MS_NODEV | MS_NOEXEC, nullptr) < 0) {
            throw std::system_error(errno, std::generic_category(), "mount /sys failed");
        }

        fs::create_directories("/dev");
        mount("tmpfs", "/dev", "tmpfs", MS_NOSUID | MS_STRICTATIME, "mode=755");

        mknod("/dev/null", S_IFCHR | 0666, makedev(1, 3));
        mknod("/dev/zero", S_IFCHR | 0666, makedev(1, 5));
        mknod("/dev/urandom", S_IFCHR | 0666, makedev(1, 9));
    }

    static int child_exec(void* arg) {
        auto* config = static_cast<ContainerConfig*>(arg);

        char byte_buf;
        while (read(config->read_pipe_fd, &byte_buf, 1) > 0) {}
        close(config->read_pipe_fd);

        sethostname("minibox", 7);

        try {
            setup_rootfs(config->rootfs);
            install_seccomp();
        } catch (const std::exception& ex) {
            std::cerr << "Container init error: " << ex.what() << "\n";
            return 1;
        }

        std::vector<char*> raw_args;
        raw_args.reserve(config->args.size() + 1);
        for (auto& s : config->args) {
            raw_args.push_back(s.data());
        }
        raw_args.push_back(nullptr);

        execvp(raw_args[0], raw_args.data());
        perror("execvp");
        return 1;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <rootfs_path> <cmd> [args...]\n";
        return 1;
    }

    if (getuid() != 0) {
        std::cerr << "Помилка: програма вимагає прав суперкористувача (root)\n";
        return 1;
    }

    try {
        Pipe sync_pipe;
        CgroupScope cgroup("/sys/fs/cgroup/minibox");

        ContainerConfig config;
        config.rootfs = argv[1];
        for (int i = 2; i < argc; ++i) {
            config.args.emplace_back(argv[i]);
        }
        config.read_pipe_fd = sync_pipe.read_fd();

        constexpr size_t stack_size = 1024 * 1024;
        auto stack = std::make_unique<char[]>(stack_size);
        char* stack_top = stack.get() + stack_size;

        int flags = CLONE_NEWNS | CLONE_NEWPID | CLONE_NEWUTS |
                    CLONE_NEWIPC | CLONE_NEWNET | CLONE_NEWCGROUP | SIGCHLD;

        pid_t child_pid = clone(MiniContainer::child_exec, stack_top, flags, &config);
        if (child_pid < 0) {
            throw std::system_error(errno, std::generic_category(), "clone failed");
        }

        sync_pipe.close_read();
        cgroup.configure(child_pid, "67108864", "20000 100000", "32");
        sync_pipe.close_write();

        int status = 0;
        waitpid(child_pid, &status, 0);

        if (WIFEXITED(status)) {
            return WEXITSTATUS(status);
        }
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
```
:::

---

### Покроковий розбір ключових механізмів

#### 1. Виділення стека та виклик clone()

Системний виклик `clone()` на відміну від `fork()` вимагає явної передачі адреси виділеної пам'яті під стек для нового процесу. Оскільки на архітектурі x86_64 стек росте зверху вниз (від старших адрес пам'яті до молодших), вказівник на початок виконання стека вираховується як `stack + STACK_SIZE`.

Прапорці створення просторів імен у виклику `clone()` виконують такі дії:
* `CLONE_NEWNS`: Створює незалежну копію дерева точок монтування VFS.
* `CLONE_NEWPID`: Створює нове дерево процесів. Перший дочірній процес отримує віртуальний PID 1 всередині нового простору, тоді як на хості він має звичайний унікальний PID (наприклад, 4192).
* `CLONE_NEWUTS`: Ізолює ім'я хоста (*nodename*) та доменне ім'я (*domainname*), дозволяючи безпечно викликати `sethostname("minibox", ...)`.
* `CLONE_NEWIPC`: Ізолює примітиви спільної пам'яті System V і черги повідомлень POSIX MQ, запобігаючи несанкціонованому перехопленню даних через спільну пам'ять хоста.
* `CLONE_NEWNET`: Створює порожній мережевий стек, що містить лише неактивний локальний інтерфейс `lo`. Контейнер повністю ізольований від мережевих з'єднань хоста.
* `CLONE_NEWCGROUP`: Забезпечує, що при читанні `/proc/self/cgroup` процес бачить свій підкаталог як корінь `/`.
* `SIGCHLD`: Забезпечує, що при завершенні дочірнього процесу батьківський процес отримає стандартний сигнал `SIGCHLD`, що дозволяє коректно виконати `waitpid()`.

#### 2. Синхронізація через неіменований канал (pipe)

Коли викликається `clone()`, дочірній процес починає виконання одночасно з батьківським. Якщо дочірній процес спробує запустити `execve()` до того, як батьківський процес запише його PID у `/sys/fs/cgroup/minibox/cgroup.procs`, дочірня програма виконуватиметься без обмежень пам'яті та процесора.

Щоб запобігти цьому стану гонитви (*race condition*), батьківський процес створює канал `pipe`. Дочірній процес відразу викликає `read(sync_pipe[0], ...)` і блокується ядром. Батьківський процес налаштовує файли cgroup і лише після цього закриває свій записуючий дескриптор `sync_pipe[1]`. Дочірній процес отримує ознаку кінця файлу (`EOF`) і продовжує безпечну ініціалізацію.

#### 3. Ізоляція VFS через pivot_root та відмонтування

Виклик `pivot_root` вимагає, щоб каталог нового кореня вже був зареєстрований у VFS як окрема точка монтування. Для цього виконується зворотне монтування прив'язки:

`mount(rootfs, rootfs, NULL, MS_BIND | MS_REC, NULL);`

Після виконання `pivot_root(rootfs, "/.old_root")` хостова файлова система залишається доступною у підкаталозі `/.old_root`. Щоб повністю закрити доступ до файлів хоста, виконується ліниве відмонтування з прапорцем `MNT_DETACH`: `umount2("/.old_root", MNT_DETACH); rmdir("/.old_root");`. Від цієї миті процес не має жодного шляху чи дескриптора, який вів би за межі призначеного кореня.

#### 4. Монтування віртуальних псевдофайлових систем

Програми простору користувача очікують наявності стандартних псевдофайлових систем:
* `/proc`: Змонтований примірник `procfs` прив'язаний до нового простору `pid_ns`. Команда `ps aux` бачить виключно процеси цього контейнера. Прапорці `MS_NOSUID | MS_NODEV | MS_NOEXEC` захищають від виконання шкідливих бінарників із псевдофайлів.
* `/sys`: Файлова система `sysfs` монтується в режимі тільки для читання (`MS_RDONLY`), щоб запобігти модифікації параметрів ядра та конфігурації пристроїв хоста.
* `/dev`: Монтується як чиста файлова система `tmpfs`, у якій через системний виклик `mknod()` створюються базові символьні пристрої `/dev/null` (мажорний номер 1, мінорний 3), `/dev/zero` (1:5) та `/dev/urandom` (1:9).

#### 5. Налаштування cgroups v2 безпосередньо через файлову систему

Замість складних бібліотек або зовнішніх утиліт програма взаємодіє з ядром через простий запис рядків у вузли `cgroupfs`:
* `memory.max = 67108864`: Обмежує використання пам'яті рівнем 64 МБ. У разі спроби виділення більшого обсягу ядро активує внутрішній OOM-killer для процесів контейнера, не зачіпаючи служби хоста.
* `cpu.max = 20000 100000`: На кожні 100 000 мікросекунд (100 мс) контейнер отримує щонайбільше 20 000 мікросекунд (20 мс) процесорного часу.
* `pids.max = 32`: Жорсткий захист від fork-бомб. Спроба створити 33-й процес повертає помилку `EAGAIN`.

#### 6. Завантаження фільтра seccomp-BPF

Контейнер захищає ядро від небезпечних системних викликів за допомогою BPF-байткоду:
* Перед завантаженням викликається `prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)`, що блокує отримання прав через setuid-файли.
* BPF-інструкції перевіряють архітектуру `AUDIT_ARCH_X86_64` і порівнюють номер системного виклику з чорним списком (`__NR_reboot`, `__NR_kexec_load`, `__NR_init_module`, `__NR_swapon`).
* Для дозволених викликів повертається `SECCOMP_RET_ALLOW`. Заборонені виклики негайно відхиляються з кодом `EPERM` без виконання коду в просторі ядра.

---

### Типові інженерні пастки та крайові випадки

1. **Успадкування спільних монтувань (MS_SHARED trap):**
   У більшості сучасних дистрибутивів Linux коренева файлова система змонтована зі спільним розповсюдженням (`MS_SHARED`). Якщо дочірній процес у новому Mount Namespace виконає `pivot_root` або `mount` без попереднього виклику `mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL)`, усі монтування та відмонтування контейнера розповсюдяться на хостову файлову систему, що може зламати роботу хоста.

2. **Обов'язки PID 1 щодо збирання процесів-зомбі:**
   Процес із номером 1 у новому PID Namespace бере на себе роль `init`. Якщо процеси всередині контейнера породжують дочірні задачі та завершуються раніше за них, ядро перепідпорядковує процеси-сироти процесу PID 1. Якщо головний процес контейнера не викликає `waitpid()` у циклі обробки `SIGCHLD`, таблиця процесів заповнюється записами зомбі (*zombies*), що зрештою вичерпує ліміт `pids.max`. У разі перехоплення сигналу батьківським процесом виклик `waitpid(-1, &status, WNOHANG)` виконується до вичерпання черги або отримання помилки `ECHILD`.

3. **Свопінг і OOM-killer у cgroups v2:**
   Якщо на хості увімкнено файл підкачки (*swap*), встановлення лише `memory.max` не зупиняє споживання пам'яті: процес продовжить виділяти анонімні сторінки, витісняючи старі в swap. Для повної ізоляції слід додатково обмежувати файл підкачки через запис `0` у файл `memory.swap.max`.

4. **Блокування необхідних системних викликів у seccomp:**
   При надто агресивному чорному списку seccomp можна випадково заблокувати виклики, необхідні динамічному завантажувачу `ld-linux.so` (наприклад, `mprotect`, `arch_prctl` або `futex`). Це призводить до аварійного завершення програми сигналом `SIGSYS` ще до входу у функцію `main()`.

5. **Безпека файлових дескрипторів і прапорець O_CLOEXEC:**
   Усі файлові дескриптори, відкриті батьківським процесом на хості (наприклад, сокети логування, дескриптори файлів конфігурації), автоматично успадковуються дочірнім процесом через `clone()` та зберігаються під час виклику `execve()`. Якщо батьківський процес не встановив на них прапорець `O_CLOEXEC` або дочірній процес не закрив зайві дескриптори перед `execve()`, програма всередині контейнера отримує прямий доступ до файлів або сокетів хоста через дескриптори `3`, `4`, `5`.

6. **Мережевий інтерфейс loopback та ізоляція netns:**
   При створенні нового простору `CLONE_NEWNET` інтерфейс зворотного зв'язку `lo` створюється ядром у вимкненому стані (`DOWN`). Будь-які спроби процесів зв'язатися з адресою `127.0.0.1` завершуються помилкою `ENETUNREACH`. Перед запуском серверних застосунків контейнерний рушій обов'язково повинен підняти інтерфейс `lo` через виклик `ioctl(SIOCSIFFLAGS)` або команду `ip link set lo up`.

7. **Керування інтерактивними терміналами (PTY allocation):**
   При запуску інтерактивної оболонки (наприклад, `sh` або `bash`) стандартні потоки вводу-виводу контейнера не можна просто прив'язувати до хостового термінала `/dev/tty`. Замість цього рушій виділяє пару псевдотерміналів через `posix_openpt()`, монтує приватний каталог `/dev/pts` усередині контейнера та робить підлеглий термінал керуючим терміналом сесії через `ioctl(slave_fd, TIOCSCTTY, 0)`. Крім того, батьківський процес на хості переводить свій термінал у неканонічний режим (*raw mode*) через `tcsetattr()`, перехоплює сигнали зміни розміру вікна `SIGWINCH` і транслює геометрію екрана через `ioctl(TIOCSWINSZ)`.

8. **Коректне завершення та пересилання сигналів:**
   Коли адміністратор зупиняє контейнер (надсилаючи `SIGINT` або `SIGTERM` батьківському процесу), батьківський процес не повинен завершуватися негайно, залишаючи дочірній процес сиротою. Він зобов'язаний переслати сигнал усім процесам групи через запис `1` у файл `cgroup.kill` або викликати `kill(child_pid, sig)` та очікувати фінального статусу через `waitpid()`.

9. **Маскування чутливих шляхів у procfs та sysfs:**
   У виробничих середовищах монтування стандартної `procfs` відкриває доступ до низки глобальних налаштувань хоста. Щоб унеможливити атаки через модифікацію параметрів ядра, промислові контейнерні рушії (наприклад, `runc`) перекривають чутливі вузли псевдофайлової системи:
   * Вузли `/proc/kcore`, `/proc/latency_stats`, `/proc/timer_list`, `/proc/sched_debug` маскуються через перекриття монтуванням `/dev/null` або порожнього каталогу `tmpfs`.
   * Шляхи `/proc/sys`, `/proc/sysrq-trigger`, `/proc/irq`, `/proc/bus` та `/sys/firmware` обов'язково перемонтовуються у режимі тільки для читання (`MS_RDONLY | MS_REMOUNT | MS_BIND`).

10. **Асинхронний моніторинг життєвого циклу через pidfd:**
    У сучасних версіях Linux (починаючи з ядра 5.3) для уникнення проблем із повторним використанням ідентифікаторів процесів (*PID recycling*) створення контейнера здійснюється через системний виклик `clone3` із прапорцем `CLONE_PIDFD`. Отриманий файловий дескриптор `pidfd` інтегрується в цикл подій `epoll` або `poll`, що дозволяє батьківському процесу відслідковувати смерть контейнера з нульовою затримкою та гарантованою відсутністю колізій із новоствореними процесами хоста.

11. **Підтримка Rootless режиму без привілеїв суперкористувача:**
    Для виконання контейнера звичайним користувачем прапорець `CLONE_NEWUSER` додається до списку прапорців виклику `clone()`. Батьківський процес призупиняє дочірній процес через канал синхронізації та запускає допоміжні системні програми `newuidmap` і `newgidmap` із передачею PID дочірнього процесу. Ці утиліти записують діапазони субрахунків з `/etc/subuid` та `/etc/subgid` у файли `/proc/[pid]/uid_map` та `/proc/[pid]/gid_map`, після чого дочірній процес продовжує ініціалізацію, володіючи повноправними можливостями всередині свого User Namespace без надання будь-яких привілеїв на хості.

12. **Аналіз змін у дереві точок монтування (/proc/self/mountinfo):**
    У процесі створення контейнера послідовність викликів `mount` та `pivot_root` безпосередньо відображається у файлі `/proc/self/mountinfo`. Під час виконання `mount(..., MS_REC | MS_PRIVATE)` теги `shared:X` замінюються на приватний режим, виклик `mount --bind rootfs rootfs` додає новий рядок із джерелом файлової системи, а `pivot_root` атомарно замінює запис із `mount point /` на новий кореневий каталог образу, перетворюючи старе хостове монтування на дочірній запис `/.old_root`, який остаточно видаляється викликом `umount2(..., MNT_DETACH)`.

13. **Проблема накладних витрат пам'яті та конструктори C в Go-рушіях:**
    При використанні системних викликів `fork()` чи `clone()` у багатопотокових середовищах (наприклад, у середовищі виконання мови Go, на якій написано `runc`) виникає фундаментальна несумісність: потік, що викликає `setns()` або `unshare()`, змінює стан лише для себе, тоді як планувальник Go мігрує горутини між різними системними потоками операційної системи. З цієї причини промислові рушії реалізують ініціалізацію просторів імен на чистому C у спеціальній бібліотеці `nsenter.c`, що позначається атрибутом `__attribute__((constructor))`. Цей код виконується завантажувачем динамічних бібліотек ще до запуску середовища виконання Go під час старту допоміжного процесу-трампліна.

14. **Політика відновлення при критичних помилках монтування:**
    Якщо під час покрокового налаштування файлового дерева або відмонтування старого кореня стається непередбачений системний збій, рушій повинен негайно виконати аварійне очищення: викликати `umount2("/.old_root", MNT_FORCE | MNT_DETACH)`, рекурсивно звільнити створені тимчасові каталоги та надіслати термінальний сигнал `SIGKILL` дочірньому процесу перед виходом, щоб гарантувати відсутність напівініціалізованих точок монтування та висячих дескрипторів у ядрі хоста.

---

### Відмінності реалізації на C та C++

* **Керування ресурсами (RAII):** У версії мовою C закриття файлових дескрипторів каналу `pipe`, вивільнення виділеного під стек буфера `malloc` та видалення каталогу cgroup `rmdir` вимагають ручного контролю в кожній гілці обробки помилок. У версії C++ класи `Pipe` та `CgroupScope` автоматично гарантують звільнення дескрипторів та видалення каталогу cgroup при виході з області видимості або при виникненні винятків (`std::system_error`).
* **Робота з файловою системою:** У C++ для створення та видалення каталогів використовується стандартна бібліотека `<filesystem>` (`fs::create_directories`, `fs::remove`), що спрощує обробку помилок і позбавляє від необхідності ручного формування буферів шляхів через `snprintf`.
* **Передача параметрів командного рядка:** Замість сирих покажчиків на рядки `char**` у C++ використовується `std::vector<std::string>` із безпечним виділенням динамічного масиву покажчиків `data()` безпосередньо перед викликом `execvp`.

---

### Підготовка тестового rootfs і запуск

Для перевірки роботи контейнера створимо мінімальне кореневе дерево на основі Alpine Linux:

```bash
# 1. Створення каталогу для кореня контейнера
mkdir -p /tmp/alpine-rootfs

# 2. Завантаження та розпакування мінімального образу Alpine
curl -sSL https://dl-cdn.alpinelinux.org/alpine/v3.20/releases/x86_64/alpine-minirootfs-3.20.0-x86_64.tar.gz \
  | tar -xz -C /tmp/alpine-rootfs

# 3. Компіляція утиліти
gcc -O2 -Wall minibox.c -o minibox

# 4. Запуск ізольованої оболонки
sudo ./minibox /tmp/alpine-rootfs /bin/sh
```

Перевірка ізоляції всередині контейнера:
```sh
# Перевірка PID (має бути PID 1)
ps aux
# PID   USER     TIME  COMMAND
#     1 root      0:00 /bin/sh

# Перевірка імені хоста
hostname
# minibox

# Перевірка обмеження пам'яті
cat /sys/fs/cgroup/memory.max
# 67108864

# Перевірка блокування системних викликів фільтром seccomp
reboot
# reboot: Operation not permitted
```
