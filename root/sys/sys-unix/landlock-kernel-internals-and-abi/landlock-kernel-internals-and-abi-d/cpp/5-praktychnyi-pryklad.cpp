#include <iostream>
#include <vector>
#include <string_view>
#include <filesystem>
#include <system_error>
#include <utility>
#include <unistd.h>
#include <fcntl.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/landlock.h>

#ifndef landlock_create_ruleset
static inline int landlock_create_ruleset(const struct landlock_ruleset_attr *attr,
                                          size_t size, uint32_t flags) {
    return static_cast<int>(syscall(SYS_landlock_create_ruleset, attr, size, flags));
}

static inline int landlock_add_rule(int ruleset_fd,
                                    enum landlock_rule_type rule_type,
                                    const void *rule_attr, uint32_t flags) {
    return static_cast<int>(syscall(SYS_landlock_add_rule, ruleset_fd, rule_type, rule_attr, flags));
}

static inline int landlock_restrict_self(int ruleset_fd, uint32_t flags) {
    return static_cast<int>(syscall(SYS_landlock_restrict_self, ruleset_fd, flags));
}
#endif

/* RAII-обгортка для безпечного управління файловими дескрипторами */
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(std::exchange(other.fd_, -1)) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = std::exchange(other.fd_, -1);
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
};

struct PathPermission {
    std::filesystem::path path;
    uint64_t access_mask;
};

class LandlockSandbox {
    UniqueFd ruleset_fd_;
    uint32_t abi_version_{0};

public:
    LandlockSandbox() {
        int abi = landlock_create_ruleset(nullptr, 0, LANDLOCK_CREATE_RULESET_VERSION);
        if (abi < 1) {
            throw std::system_error(errno, std::generic_category(), "Landlock не підтримується ядром");
        }
        abi_version_ = static_cast<uint32_t>(abi);

        uint64_t handled_fs = LANDLOCK_ACCESS_FS_EXECUTE |
                             LANDLOCK_ACCESS_FS_WRITE_FILE |
                             LANDLOCK_ACCESS_FS_READ_FILE |
                             LANDLOCK_ACCESS_FS_READ_DIR |
                             LANDLOCK_ACCESS_FS_REMOVE_DIR |
                             LANDLOCK_ACCESS_FS_REMOVE_FILE |
                             LANDLOCK_ACCESS_FS_MAKE_CHAR |
                             LANDLOCK_ACCESS_FS_MAKE_DIR |
                             LANDLOCK_ACCESS_FS_MAKE_REG |
                             LANDLOCK_ACCESS_FS_MAKE_SOCK |
                             LANDLOCK_ACCESS_FS_MAKE_FIFO |
                             LANDLOCK_ACCESS_FS_MAKE_BLOCK |
                             LANDLOCK_ACCESS_FS_MAKE_SYM;

        if (abi_version_ >= 2) {
            handled_fs |= LANDLOCK_ACCESS_FS_REFER;
        }
        if (abi_version_ >= 3) {
            handled_fs |= LANDLOCK_ACCESS_FS_TRUNCATE;
        }

        landlock_ruleset_attr attr{};
        attr.handled_access_fs = handled_fs;

        int fd = landlock_create_ruleset(&attr, sizeof(attr), 0);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка landlock_create_ruleset");
        }
        ruleset_fd_.reset(fd);
    }

    void allow_path(const std::filesystem::path& p, uint64_t access_mask) {
        UniqueFd path_fd(::open(p.c_str(), O_PATH | O_CLOEXEC));
        if (!path_fd.valid()) {
            return; /* Пропускаємо відсутні шляхи */
        }

        landlock_path_beneath_attr path_attr{};
        path_attr.allowed_access = access_mask;
        path_attr.parent_fd = path_fd.get();

        if (landlock_add_rule(ruleset_fd_.get(), LANDLOCK_RULE_PATH_BENEATH, &path_attr, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка landlock_add_rule для " + p.string());
        }
    }

    void apply() {
        if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка prctl(PR_SET_NO_NEW_PRIVS)");
        }

        if (landlock_restrict_self(ruleset_fd_.get(), 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка landlock_restrict_self");
        }

        ruleset_fd_.reset(); /* Закриваємо дескриптор після успішного накладання */
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <команда> [аргументи...]\n";
        return 1;
    }

    try {
        LandlockSandbox sandbox;

        constexpr uint64_t read_exec = LANDLOCK_ACCESS_FS_READ_FILE | 
                                       LANDLOCK_ACCESS_FS_READ_DIR | 
                                       LANDLOCK_ACCESS_FS_EXECUTE;

        constexpr uint64_t read_only = LANDLOCK_ACCESS_FS_READ_FILE | 
                                       LANDLOCK_ACCESS_FS_READ_DIR;

        std::vector<PathPermission> permissions = {
            {"/usr", read_exec},
            {"/bin", read_exec},
            {"/lib", read_exec},
            {"/lib64", read_exec},
            {"/etc", read_only}
        };

        for (const auto& perm : permissions) {
            sandbox.allow_path(perm.path, perm.access_mask);
        }

        sandbox.apply();

        ::execvp(argv[1], &argv[1]);
        throw std::system_error(errno, std::generic_category(), "Помилка execvp");

    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка пісочниці: " << ex.what() << '\n';
        return 1;
    }
}
