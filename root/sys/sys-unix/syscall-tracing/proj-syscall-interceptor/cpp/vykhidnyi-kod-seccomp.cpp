#include <iostream>
#include <memory>
#include <vector>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <linux/seccomp.h>
#include <linux/filter.h>

/* RAII обгортка для файлового дескриптора */
class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& o) noexcept {
        if (this != &o) {
            reset();
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }

    void reset(int newFd = -1) {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = newFd;
    }

    [[nodiscard]] int get() const { return fd_; }
    [[nodiscard]] bool valid() const { return fd_ >= 0; }

private:
    int fd_;
};

/* Налаштування Seccomp фільтра у C++ style */
static UniqueFd setupSeccompFilter() {
    struct sock_filter filter[] = {
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_mkdirat, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_USER_NOTIF),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };
    
    struct sock_fprog prog = {
        static_cast<unsigned short>(sizeof(filter) / sizeof(filter[0])),
        filter
    };

    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
        throw std::system_error(errno, std::generic_category(), "prctl PR_SET_NO_NEW_PRIVS failed");
    }

    int rawFd = static_cast<int>(syscall(__NR_seccomp, SECCOMP_SET_MODE_FILTER, SECCOMP_FILTER_FLAG_NEW_LISTENER, &prog));
    if (rawFd < 0) {
        throw std::system_error(errno, std::generic_category(), "seccomp syscall failed");
    }
    return UniqueFd(rawFd);
}

int main() {
    try {
        UniqueFd notifyFd = setupSeccompFilter();

        pid_t pid = fork();
        if (pid < 0) {
            perror("fork");
            return 1;
        }

        if (pid == 0) {
            std::cout << "[C++ Target] Викликаємо mkdir('/tmp/cpp_virtual_dir')...\n";
            int res = ::mkdir("/tmp/cpp_virtual_dir", 0755);
            std::cout << "[C++ Target] Результат виклику mkdir: " << res
                      << " (errno: " << errno << ")\n";
            return 0;
        }

        struct seccomp_notif req{};
        struct seccomp_notif_resp resp{};

        std::cout << "[C++ Supervisor] Очікування сповіщення від цільового процесу...\n";

        if (ioctl(notifyFd.get(), SECCOMP_IOCTL_NOTIF_RECV, &req) >= 0) {
            std::cout << "[C++ Supervisor] Перехоплено системний виклик #"
                      << req.data.nr << " від PID " << req.pid << "\n";

            resp.id = req.id;
            resp.val = 0;    // Успішне симульоване повернення
            resp.error = 0;
            resp.flags = 0;

            if (ioctl(notifyFd.get(), SECCOMP_IOCTL_NOTIF_SEND, &resp) < 0) {
                perror("ioctl SECCOMP_IOCTL_NOTIF_SEND");
            } else {
                std::cout << "[C++ Supervisor] Відповідь успішно надіслано в ядро.\n";
            }
        }

        waitpid(pid, nullptr, 0);

    } catch (const std::exception& e) {
        std::cerr << "Критична помилка супервізора: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
