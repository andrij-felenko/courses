#include <iostream>
#include <system_error>
#include <utility>
#include <string_view>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <cerrno>
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
constexpr unsigned int pidfs_magic = 0xFF;
#else
constexpr unsigned int pidfs_magic = PIDFS_IOCTL_MAGIC;
#endif

#ifndef PIDFD_GET_NET_NAMESPACE
#define PIDFD_GET_NET_NAMESPACE _IO(0xFF, 4)
#endif

struct pidfd_info_layout {
    std::uint64_t mask;
    std::uint64_t cgroupid;
    std::uint32_t pid;
    std::uint32_t tgid;
    std::uint32_t ppid;
    std::uint32_t ruid;
    std::uint32_t rgid;
    std::uint32_t euid;
    std::uint32_t egid;
    std::uint32_t suid;
    std::uint32_t sgid;
    std::uint32_t fsuid;
    std::uint32_t fsgid;
    std::int32_t  exit_code;
};

#ifndef PIDFD_GET_INFO
#define PIDFD_GET_INFO _IOWR(0xFF, 11, pidfd_info_layout)
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

    [[nodiscard]] struct statx fetch_statx() const {
        struct statx stx{};
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
        info.mask = (1U << 0) | (1U << 1); // PIDFD_INFO_PID | PIDFD_INFO_CREDS
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
