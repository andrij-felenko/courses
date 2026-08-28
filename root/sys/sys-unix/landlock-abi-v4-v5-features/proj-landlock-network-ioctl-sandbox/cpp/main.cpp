#include <iostream>
#include <string_view>
#include <system_error>
#include <utility>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <linux/landlock.h>

#ifndef LANDLOCK_ACCESS_NET_BIND_TCP
#define LANDLOCK_ACCESS_NET_BIND_TCP (1ULL << 0)
#define LANDLOCK_ACCESS_NET_CONNECT_TCP (1ULL << 1)
#endif

#ifndef LANDLOCK_ACCESS_FS_IOCTL_DEV
#define LANDLOCK_ACCESS_FS_IOCTL_DEV (1ULL << 15)
#endif

#ifndef LANDLOCK_RULE_NET_PORT
#define LANDLOCK_RULE_NET_PORT 2
struct landlock_net_port_attr {
    __u64 allowed_access;
    __u64 port;
};
#endif

class ScopedFd {
    int fd_{-1};
public:
    explicit ScopedFd(int fd = -1) : fd_(fd) {}
    ~ScopedFd() { if (fd_ >= 0) ::close(fd_); }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& o) noexcept : fd_(std::exchange(o.fd_, -1)) {}
    ScopedFd& operator=(ScopedFd&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = std::exchange(o.fd_, -1);
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    explicit operator bool() const noexcept { return fd_ >= 0; }
};

class LandlockSandbox {
    static int sys_landlock_create_ruleset(const struct landlock_ruleset_attr *attr, size_t size, __u32 flags) {
        return static_cast<int>(::syscall(__NR_landlock_create_ruleset, attr, size, flags));
    }
    static int sys_landlock_add_rule(int ruleset_fd, enum landlock_rule_type rule_type, const void *rule_attr, __u32 flags) {
        return static_cast<int>(::syscall(__NR_landlock_add_rule, ruleset_fd, rule_type, rule_attr, flags));
    }
    static int sys_landlock_restrict_self(int ruleset_fd, __u32 flags) {
        return static_cast<int>(::syscall(__NR_landlock_restrict_self, ruleset_fd, flags));
    }

public:
    static void apply(std::uint16_t allowed_port, std::string_view allowed_path) {
        int abi = sys_landlock_create_ruleset(nullptr, 0, LANDLOCK_CREATE_RULESET_VERSION);
        if (abi < 1) {
            throw std::system_error(ENOSYS, std::generic_category(), "Landlock unsupported");
        }

        landlock_ruleset_attr attr{};
        attr.handled_access_fs = LANDLOCK_ACCESS_FS_READ_FILE | LANDLOCK_ACCESS_FS_READ_DIR;
        if (abi >= 5) {
            attr.handled_access_fs |= LANDLOCK_ACCESS_FS_IOCTL_DEV;
        }
        if (abi >= 4) {
            attr.handled_access_net = LANDLOCK_ACCESS_NET_BIND_TCP | LANDLOCK_ACCESS_NET_CONNECT_TCP;
        }

        ScopedFd ruleset{sys_landlock_create_ruleset(&attr, sizeof(attr), 0)};
        if (!ruleset) {
            throw std::system_error(errno, std::generic_category(), "landlock_create_ruleset failed");
        }

        ScopedFd dir{::open(allowed_path.data(), O_PATH | O_CLOEXEC)};
        if (dir) {
            landlock_path_beneath_attr path_attr{
                .allowed_access = LANDLOCK_ACCESS_FS_READ_FILE | LANDLOCK_ACCESS_FS_READ_DIR,
                .parent_fd = dir.get()
            };
            if (sys_landlock_add_rule(ruleset.get(), LANDLOCK_RULE_PATH_BENEATH, &path_attr, 0) < 0) {
                throw std::system_error(errno, std::generic_category(), "add VFS rule failed");
            }
        }

        if (abi >= 4) {
            landlock_net_port_attr net_attr{
                .allowed_access = LANDLOCK_ACCESS_NET_BIND_TCP,
                .port = allowed_port
            };
            if (sys_landlock_add_rule(ruleset.get(), LANDLOCK_RULE_NET_PORT, &net_attr, 0) < 0) {
                throw std::system_error(errno, std::generic_category(), "add Net rule failed");
            }
        }

        if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "prctl NO_NEW_PRIVS failed");
        }

        if (sys_landlock_restrict_self(ruleset.get(), 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "restrict_self failed");
        }

        std::cout << "[Landlock C++] Sandboxing active (ABI v" << abi << ")\n";
    }
};

int main() {
    try {
        LandlockSandbox::apply(8080, "/tmp");

        ScopedFd s1{::socket(AF_INET, SOCK_STREAM, 0)};
        sockaddr_in addr1{.sin_family = AF_INET, .sin_port = htons(8080)};
        if (::bind(s1.get(), reinterpret_cast<sockaddr*>(&addr1), sizeof(addr1)) == 0) {
            std::cout << "SUCCESS: bind(8080) permitted\n";
        }

        ScopedFd s2{::socket(AF_INET, SOCK_STREAM, 0)};
        sockaddr_in addr2{.sin_family = AF_INET, .sin_port = htons(9090)};
        if (::bind(s2.get(), reinterpret_cast<sockaddr*>(&addr2), sizeof(addr2)) < 0 && errno == EACCES) {
            std::cout << "SUCCESS: bind(9090) blocked with EACCES\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
