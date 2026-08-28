#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#include <expected>
#include <memory>
#include <string>
#include <system_error>
#include <vector>

class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_(-1) {}
    explicit constexpr UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        reset(other.release());
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

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

struct PtyProcess {
    pid_t pid;
    UniqueFd master_fd;
};

std::expected<PtyProcess, std::error_code> spawn_under_pty(
    const std::string& file,
    const std::vector<std::string>& args) 
{
    int master = ::posix_openpt(O_RDWR | O_NOCTTY);
    if (master < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    UniqueFd master_guard(master);

    if (::grantpt(master) < 0 || ::unlockpt(master) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    const char* slave_name = ::ptsname(master);
    if (!slave_name) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    pid_t pid = ::fork();
    if (pid < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (pid == 0) {
        master_guard.reset();

        if (::setsid() < 0) {
            ::_exit(1);
        }

        int slave = ::open(slave_name, O_RDWR);
        if (slave < 0) {
            ::_exit(1);
        }

        if (::ioctl(slave, TIOCSCTTY, 0) < 0) {
            ::_exit(1);
        }

        ::dup2(slave, STDIN_FILENO);
        ::dup2(slave, STDOUT_FILENO);
        ::dup2(slave, STDERR_FILENO);

        if (slave > STDERR_FILENO) {
            ::close(slave);
        }

        std::vector<char*> c_args;
        c_args.reserve(args.size() + 2);
        c_args.push_back(const_cast<char*>(file.c_str()));
        for (const auto& arg : args) {
            c_args.push_back(const_cast<char*>(arg.c_str()));
        }
        c_args.push_back(nullptr);

        ::execvp(file.c_str(), c_args.data());
        ::_exit(127);
    }

    return PtyProcess{pid, std::move(master_guard)};
}
