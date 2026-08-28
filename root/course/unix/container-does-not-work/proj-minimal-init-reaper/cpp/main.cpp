#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <array>
#include <span>
#include <unistd.h>
#include <signal.h>
#include <sys/signalfd.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <poll.h>

class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_{fd} {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_{other.release()} {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_{-1};
};

struct ExecutionResult {
    bool exited{false};
    int raw_status{0};
};

static void reap_all_zombies(pid_t primary_pid, ExecutionResult& result) noexcept {
    pid_t pid = 0;
    int status = 0;

    while ((pid = ::waitpid(-1, &status, WNOHANG)) > 0) {
        if (pid == primary_pid) {
            result.raw_status = status;
            result.exited = true;
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <команда> [аргументи...]\n";
        return 1;
    }

    // 1. Оголошення себе subreaper
    ::prctl(PR_SET_CHILD_SUBREAPER, 1, 0, 0, 0);

    // 2. Налаштування маски та signalfd
    sigset_t mask;
    ::sigemptyset(&mask);
    ::sigaddset(&mask, SIGTERM);
    ::sigaddset(&mask, SIGINT);
    ::sigaddset(&mask, SIGQUIT);
    ::sigaddset(&mask, SIGHUP);
    ::sigaddset(&mask, SIGCHLD);

    if (::sigprocmask(SIG_BLOCK, &mask, nullptr) < 0) {
        std::cerr << "Помилка блокування сигналів у sigprocmask\n";
        return 1;
    }

    UniqueFd sfd{::signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC)};
    if (!sfd.valid()) {
        std::cerr << "Помилка створення signalfd\n";
        return 1;
    }

    // 3. Запуск дочірньої програми
    const pid_t child_pid = ::fork();
    if (child_pid < 0) {
        std::cerr << "Помилка системного виклику fork\n";
        return 1;
    }

    if (child_pid == 0) {
        ::sigprocmask(SIG_UNBLOCK, &mask, nullptr);
        sfd.reset();

        ::setpgid(0, 0);

        std::vector<char*> raw_args;
        raw_args.reserve(static_cast<size_t>(argc));
        for (int i = 1; i < argc; ++i) {
            raw_args.push_back(argv[i]);
        }
        raw_args.push_back(nullptr);

        ::execvp(raw_args[0], raw_args.data());
        std::_Exit(127);
    }

    // 4. Головний цикл моніторингу подій
    struct pollfd pfd{ .fd = sfd.get(), .events = POLLIN, .revents = 0 };
    ExecutionResult result{};

    while (!result.exited) {
        const int ret = ::poll(&pfd, 1, -1);
        if (ret < 0) {
            if (errno == EINTR) continue;
            break;
        }

        if (pfd.revents & POLLIN) {
            struct signalfd_siginfo fdsi{};
            const auto bytes = ::read(sfd.get(), &fdsi, sizeof(fdsi));
            if (bytes != sizeof(fdsi)) continue;

            if (fdsi.ssi_signo == SIGCHLD) {
                reap_all_zombies(child_pid, result);
            } else {
                // Доставка сигналу дочірній групі процесів
                ::kill(-child_pid, static_cast<int>(fdsi.ssi_signo));
            }
        }
    }

    // Дозбируємо залишкових сиріт після завершення головного процесу
    reap_all_zombies(child_pid, result);

    // 5. Трансляція статусу завершення
    if (WIFEXITED(result.raw_status)) {
        return WEXITSTATUS(result.raw_status);
    }
    if (WIFSIGNALED(result.raw_status)) {
        return 128 + WTERMSIG(result.raw_status);
    }

    return 1;
}
