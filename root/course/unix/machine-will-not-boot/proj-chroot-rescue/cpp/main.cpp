#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <expected>
#include <system_error>
#include <memory>
#include <span>
#include <unistd.h>
#include <sys/mount.h>
#include <sys/wait.h>

namespace fs = std::filesystem;

enum class RescueError {
    PermissionDenied,
    PathNotFound,
    MountFailed,
    ChrootFailed,
    ExecutionFailed
};

struct MountPoint {
    fs::path target;
    bool is_mounted{false};
};

class ChrootEnvironmentManager {
public:
    explicit ChrootEnvironmentManager(fs::path root) : target_root_(std::move(root)) {}

    ~ChrootEnvironmentManager() {
        teardown();
    }

    // Заборона копіювання для гарантії ексклюзивного володіння ресурсами
    ChrootEnvironmentManager(const ChrootEnvironmentManager&) = delete;
    ChrootEnvironmentManager& operator=(const ChrootEnvironmentManager&) = delete;

    // Дозвіл переміщення
    ChrootEnvironmentManager(ChrootEnvironmentManager&& other) noexcept
        : target_root_(std::move(other.target_root_)),
          active_mounts_(std::move(other.active_mounts_)) {}

    ChrootEnvironmentManager& operator=(ChrootEnvironmentManager&& other) noexcept {
        if (this != &other) {
            teardown();
            target_root_ = std::move(other.target_root_);
            active_mounts_ = std::move(other.active_mounts_);
        }
        return *this;
    }

    [[nodiscard]] std::expected<void, RescueError> prepare_pseudo_filesystems() {
        if (::geteuid() != 0) {
            std::cerr << "Помилка: потрібні адміністративні привілеї CAP_SYS_ADMIN (root)\n";
            return std::unexpected(RescueError::PermissionDenied);
        }

        std::error_code ec;
        if (!fs::exists(target_root_, ec) || !fs::is_directory(target_root_, ec)) {
            std::cerr << "Помилка: цільовий шлях " << target_root_ << " не існує або не є каталогом\n";
            return std::unexpected(RescueError::PathNotFound);
        }

        // 1. procfs
        auto proc_path = target_root_ / "proc";
        fs::create_directories(proc_path, ec);
        if (auto res = perform_mount("proc", proc_path, "proc", 0, nullptr); !res) {
            return res;
        }

        // 2. sysfs (rbind + make-rslave)
        auto sys_path = target_root_ / "sys";
        fs::create_directories(sys_path, ec);
        if (auto res = perform_mount("/sys", sys_path, "", MS_BIND | MS_REC, nullptr); !res) {
            return res;
        }
        ::mount(nullptr, sys_path.c_str(), nullptr, MS_SLAVE | MS_REC, nullptr);

        // 3. devtmpfs (rbind + make-rslave)
        auto dev_path = target_root_ / "dev";
        fs::create_directories(dev_path, ec);
        if (auto res = perform_mount("/dev", dev_path, "", MS_BIND | MS_REC, nullptr); !res) {
            return res;
        }
        ::mount(nullptr, dev_path.c_str(), nullptr, MS_SLAVE | MS_REC, nullptr);

        // 4. tmpfs /run (rbind + make-rslave)
        auto run_path = target_root_ / "run";
        fs::create_directories(run_path, ec);
        if (auto res = perform_mount("/run", run_path, "", MS_BIND | MS_REC, nullptr); !res) {
            return res;
        }
        ::mount(nullptr, run_path.c_str(), nullptr, MS_SLAVE | MS_REC, nullptr);

        // Копіювання конфігурації DNS
        auto resolv_src = fs::path("/etc/resolv.conf");
        auto resolv_dst = target_root_ / "etc/resolv.conf";
        if (fs::exists(resolv_src, ec)) {
            fs::copy_file(resolv_src, resolv_dst, fs::copy_options::overwrite_existing, ec);
        }

        return {};
    }

    [[nodiscard]] std::expected<int, RescueError> run_isolated(std::span<char* const> cmd) {
        pid_t pid = ::fork();
        if (pid < 0) {
            std::cerr << "Помилка fork(): " << std::strerror(errno) << '\n';
            return std::unexpected(RescueError::ExecutionFailed);
        }

        if (pid == 0) {
            if (::chroot(target_root_.c_str()) != 0) {
                std::cerr << "Помилка chroot(): " << std::strerror(errno) << '\n';
                std::_Exit(EXIT_FAILURE);
            }
            if (::chdir("/") != 0) {
                std::cerr << "Помилка chdir(\"/\"): " << std::strerror(errno) << '\n';
                std::_Exit(EXIT_FAILURE);
            }

            ::setenv("PATH", "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", 1);
            ::setenv("HOME", "/root", 1);
            ::setenv("TERM", "xterm-256color", 0);

            std::vector<char*> exec_args(cmd.begin(), cmd.end());
            exec_args.push_back(nullptr);

            std::cout << "\n=== [C++ RAII] Успішний вхід у ремонтне оточення ===\n\n";
            ::execv(exec_args[0], exec_args.data());

            std::cerr << "Помилка запуску: " << exec_args[0] << " (" << std::strerror(errno) << ")\n";
            std::_Exit(EXIT_FAILURE);
        }

        int status = 0;
        ::waitpid(pid, &status, 0);
        return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
    }

    void teardown() noexcept {
        while (!active_mounts_.empty()) {
            const auto& mp = active_mounts_.back();
            if (mp.is_mounted) {
                std::cout << "[RAII Teardown] Розмонтування: " << mp.target << '\n';
                if (::umount2(mp.target.c_str(), MNT_DETACH) != 0) {
                    std::cerr << "Попередження: не вдалося розмонтувати " << mp.target 
                              << ": " << std::strerror(errno) << '\n';
                }
            }
            active_mounts_.pop_back();
        }
    }

private:
    std::expected<void, RescueError> perform_mount(const char* src, const fs::path& target,
                                                  const char* fstype, unsigned long flags,
                                                  const void* data) {
        std::cout << "[Mount] " << src << " -> " << target << '\n';
        if (::mount(src, target.c_str(), fstype, flags, data) != 0) {
            std::cerr << "Помилка монтування " << target << ": " << std::strerror(errno) << '\n';
            return std::unexpected(RescueError::MountFailed);
        }
        active_mounts_.push_back({target, true});
        return {};
    }

    fs::path target_root_;
    std::vector<MountPoint> active_mounts_;
};

int main(int argc, char* argv[]) {
    fs::path target = (argc > 1) ? argv[1] : "/mnt";
    char default_shell[] = "/bin/bash";
    char flag_l[] = "-l";
    char* default_args[] = {default_shell, flag_l};

    std::span<char* const> command = (argc > 2) 
        ? std::span<char* const>(&argv[2], argc - 2)
        : std::span<char* const>(default_args, 2);

    ChrootEnvironmentManager manager(target);
    auto setup_result = manager.prepare_pseudo_filesystems();
    if (!setup_result) {
        std::cerr << "Підготовка середовища зазнала невдачі.\n";
        return 1;
    }

    auto run_result = manager.run_isolated(command);
    if (!run_result) {
        std::cerr << "Виконання у chroot завершилося з аварією.\n";
        return 1;
    }

    return *run_result;
}
