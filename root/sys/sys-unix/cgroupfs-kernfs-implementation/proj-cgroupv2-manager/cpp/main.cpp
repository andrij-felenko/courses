#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <string_view>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <poll.h>

namespace fs = std::filesystem;

/* RAII-обгортка для безпечного управління файловими дескрипторами у C++ */
class ScopedFd {
public:
    explicit ScopedFd(int fd = -1) noexcept : fd_(fd) {}
    ~ScopedFd() { reset(); }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;

    ScopedFd(ScopedFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_;
};

class CgroupV2Manager {
public:
    explicit CgroupV2Manager(fs::path root_path = "/sys/fs/cgroup")
        : root_(std::move(root_path)) {}

    void enable_controllers(std::string_view controllers) const {
        write_control_file(root_ / "cgroup.subtree_control", controllers);
    }

    void create_cgroup(const fs::path& rel_path) const {
        fs::create_directories(root_ / rel_path);
    }

    void set_memory_max(const fs::path& rel_path, uint64_t bytes) const {
        write_control_file(root_ / rel_path / "memory.max", std::to_string(bytes));
    }

    void set_cpu_max(const fs::path& rel_path, uint64_t quota_us, uint64_t period_us) const {
        std::string val = std::to_string(quota_us) + " " + std::to_string(period_us);
        write_control_file(root_ / rel_path / "cpu.max", val);
    }

    void attach_process(const fs::path& rel_path, pid_t pid) const {
        write_control_file(root_ / rel_path / "cgroup.procs", std::to_string(pid));
    }

    void monitor_events(const fs::path& rel_path, int timeout_ms) const {
        fs::path events_path = root_ / rel_path / "cgroup.events";
        ScopedFd fd(::open(events_path.c_str(), O_RDONLY));
        if (!fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Помилка відкриття cgroup.events");
        }

        pollfd pfd{.fd = fd.get(), .events = POLLPRI | POLLERR, .revents = 0};
        int ret = ::poll(&pfd, 1, timeout_ms);
        if (ret < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка виконання poll()");
        }
    }

private:
    static void write_control_file(const fs::path& file_path, std::string_view value) {
        std::ofstream ofs(file_path);
        if (!ofs.is_open()) {
            throw std::runtime_error("Не вдалося відкрити файл керування: " + file_path.string());
        }
        ofs << value << "\n";
        if (!ofs.good()) {
            throw std::runtime_error("Помилка запису даних у файл: " + file_path.string());
        }
    }

    fs::path root_;
};

int main() {
    try {
        CgroupV2Manager mgr;
        const fs::path workload_dir = "cpp_workload";

        mgr.enable_controllers("+cpu +memory");
        mgr.create_cgroup(workload_dir);
        mgr.set_memory_max(workload_dir, 536870912); // 512 MiB
        mgr.set_cpu_max(workload_dir, 50000, 100000); // 50 ms на 100 ms = 0.5 ядра
        mgr.attach_process(workload_dir, ::getpid());

        std::cout << "Процес C++ [PID " << ::getpid() << "] успішно додано до cgroup v2\n";
        mgr.monitor_events(workload_dir, 1000);
    } catch (const std::exception& ex) {
        std::cerr << "Помилка керування cgroup v2: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
