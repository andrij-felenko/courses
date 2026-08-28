// container_runner.cpp — Ідіоматична реалізація контейнерного рушія на C++20
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <memory>
#include <system_error>
#include <sched.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/mount.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

class OverlayContainer {
public:
    struct Config {
        fs::path base_path = "/tmp/cpp_container";
        std::string hostname = "cpp-isolated-node";
    };

    explicit OverlayContainer(Config cfg)
        : config_(std::move(cfg)),
          lower_dir_(config_.base_path / "lower"),
          upper_dir_(config_.base_path / "upper"),
          work_dir_(config_.base_path / "work"),
          merged_dir_(config_.base_path / "merged") {}

    ~OverlayContainer() {
        cleanup();
    }

    // Заборона копіювання через управління системними ресурсами
    OverlayContainer(const OverlayContainer&) = delete;
    OverlayContainer& operator=(const OverlayContainer&) = delete;

    void prepare_environment() {
        std::error_code ec;
        fs::create_directories(lower_dir_, ec);
        fs::create_directories(upper_dir_, ec);
        fs::create_directories(work_dir_, ec);
        fs::create_directories(merged_dir_, ec);

        if (ec) {
            throw std::system_error(ec, "Failed to create OverlayFS structure");
        }
    }

    void run() {
        prepare_environment();

        constexpr std::size_t stack_size = 1024 * 1024;
        auto stack = std::make_unique<char[]>(stack_size);
        char* stack_top = stack.get() + stack_size;

        int flags = CLONE_NEWNS | CLONE_NEWPID | CLONE_NEWUTS | SIGCHLD;
        
        std::cout << "[Host C++] Launching isolated child via clone()...\n";
        pid_t pid = clone(&OverlayContainer::child_entry, stack_top, flags, this);

        if (pid < 0) {
            throw std::system_error(errno, std::generic_category(), "clone failed");
        }

        int status = 0;
        ::waitpid(pid, &status, 0);
        std::cout << "[Host C++] Container exited with status: " << WEXITSTATUS(status) << "\n";
    }

private:
    Config config_;
    fs::path lower_dir_;
    fs::path upper_dir_;
    fs::path work_dir_;
    fs::path merged_dir_;

    void cleanup() noexcept {
        // RAII-розмонтування OverlayFS при знищенні об'єкта
        std::error_code ec;
        if (fs::exists(merged_dir_, ec)) {
            ::umount2(merged_dir_.c_str(), MNT_DETACH);
        }
    }

    static int child_entry(void* arg) noexcept {
        auto* self = static_cast<OverlayContainer*>(arg);
        return self->execute_inside_container();
    }

    int execute_inside_container() noexcept {
        if (::sethostname(config_.hostname.c_str(), config_.hostname.size()) < 0) {
            std::perror("sethostname failed");
            return -1;
        }

        if (::mount(nullptr, "/", nullptr, MS_REC | MS_PRIVATE, nullptr) < 0) {
            std::perror("mount MS_PRIVATE failed");
            return -1;
        }

        std::string opts = "lowerdir=" + lower_dir_.string() +
                           ",upperdir=" + upper_dir_.string() +
                           ",workdir=" + work_dir_.string();

        if (::mount("overlay", merged_dir_.c_str(), "overlay", 0, opts.c_str()) < 0) {
            std::perror("mount overlay failed");
            return -1;
        }

        if (::chroot(merged_dir_.c_str()) < 0 || ::chdir("/") < 0) {
            std::perror("chroot/chdir failed");
            return -1;
        }

        fs::create_directory("/proc");
        if (::mount("proc", "/proc", "proc", 0, nullptr) < 0) {
            std::perror("mount /proc failed");
            return -1;
        }

        std::cout << "[Child C++] Shell running in container (PID=" << ::getpid() << ")\n";

        char* const argv[] = { const_cast<char*>("/bin/sh"), nullptr };
        char* const envp[] = { const_cast<char*>("PATH=/bin:/usr/bin"), nullptr };

        ::execve("/bin/sh", argv, envp);
        std::perror("execve failed");
        return -1;
    }
};

int main() {
    try {
        OverlayContainer::Config cfg;
        OverlayContainer container(cfg);
        container.run();
    } catch (const std::exception& ex) {
        std::cerr << "Fatal Error: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
