// cgroup2_manager.cpp — Об'єктно-орієнтоване управління cgroups v2 мовою C++20
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <system_error>
#include <memory>
#include <chrono>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/epoll.h>
#include <sys/vfs.h>

namespace fs = std::filesystem;

/* Обгортка RAII для файлових дескрипторів Linux */
class scoped_fd {
    int m_fd{-1};
public:
    explicit scoped_fd(int fd) noexcept : m_fd(fd) {}
    ~scoped_fd() { if (m_fd >= 0) ::close(m_fd); }
    scoped_fd(const scoped_fd&) = delete;
    scoped_fd& operator=(const scoped_fd&) = delete;
    scoped_fd(scoped_fd&& o) noexcept : m_fd(o.m_fd) { o.m_fd = -1; }
    scoped_fd& operator=(scoped_fd&& o) noexcept {
        if (this != &o) {
            if (m_fd >= 0) ::close(m_fd);
            m_fd = o.m_fd;
            o.m_fd = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }
};

/* Клас управління листовим вузлом cgroups v2 */
class cgroupv2_leaf {
    fs::path m_path;
public:
    static constexpr uint64_t cgroup2_magic = 0x63677232;

    explicit cgroupv2_leaf(const fs::path& parent_name, const fs::path& leaf_name) {
        fs::path root = "/sys/fs/cgroup";
        struct statfs st{};
        if (::statfs(root.c_str(), &st) != 0 || st.f_type != cgroup2_magic) {
            throw std::runtime_error("Файлова система /sys/fs/cgroup не є cgroup2");
        }

        fs::path parent = root / parent_name;
        fs::create_directories(parent);

        /* Активація контролерів у батьківському вузлі */
        write_control(parent / "cgroup.subtree_control", "+memory +cpu");

        m_path = parent / leaf_name;
        fs::create_directories(m_path);
    }

    void set_memory_max(size_t bytes) {
        write_control(m_path / "memory.max", std::to_string(bytes));
    }

    void set_cpu_quota(uint64_t max_us, uint64_t period_us) {
        std::string val = std::to_string(max_us) + " " + std::to_string(period_us);
        write_control(m_path / "cpu.max", val);
    }

    void attach_current_process() {
        write_control(m_path / "cgroup.procs", std::to_string(::getpid()));
    }

    void monitor_psi_memory(std::chrono::milliseconds timeout) {
        scoped_fd pfd(::open((m_path / "memory.pressure").c_str(), O_RDWR | O_CLOEXEC));
        if (!pfd.valid()) return;

        std::string_view trigger = "some 150000 1000000";
        if (::write(pfd.get(), trigger.data(), trigger.size()) <= 0) return;

        scoped_fd epfd(::epoll_create1(EPOLL_CLOEXEC));
        if (!epfd.valid()) return;

        epoll_event ev{.events = EPOLLPRI, .data{.fd = pfd.get()}};
        ::epoll_ctl(epfd.get(), EPOLL_CTL_ADD, pfd.get(), &ev);

        epoll_event events[1];
        int nfds = ::epoll_wait(epfd.get(), events, 1, static_cast<int>(timeout.count()));
        if (nfds > 0) {
            std::cout << "[C++] Увага: Зареєстровано PSI поріг тиску пам'яті!\n";
        } else {
            std::cout << "[C++] Стан пам'яті cgroup стабільний.\n";
        }
    }

private:
    static void write_control(const fs::path& p, std::string_view val) {
        std::ofstream ofs(p);
        if (!ofs) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити " + p.string());
        }
        ofs << val;
        if (!ofs) {
            throw std::runtime_error("Помилка запису у " + p.string());
        }
    }
};

int main() {
    try {
        cgroupv2_leaf cg("myapp_cpp", "worker");
        cg.set_memory_max(256 * 1024 * 1024); // 256 МіБ
        cg.set_cpu_quota(50000, 100000);       // 50% CPU
        cg.attach_current_process();
        std::cout << "[C++] Процес " << ::getpid() << " переміщено у cgroup\n";

        cg.monitor_psi_memory(std::chrono::milliseconds(2000));
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
