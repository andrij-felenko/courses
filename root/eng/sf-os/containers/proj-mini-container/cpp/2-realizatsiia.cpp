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
