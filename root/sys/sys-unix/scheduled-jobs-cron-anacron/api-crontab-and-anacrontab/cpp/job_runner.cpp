#include "job_runner.hpp"

#include "posix.hpp"

#include <array>
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <format>
#include <iostream>
#include <stdexcept>
#include <string_view>
#include <utility>

#include <fcntl.h>
#include <grp.h>
#include <poll.h>
#include <pwd.h>
#include <csignal>
#include <sys/wait.h>
#include <unistd.h>

namespace minicron {
namespace {

constexpr std::size_t kChunk = 4096;

struct Pipe {
    UniqueFd read_end;
    UniqueFd write_end;
};

Pipe make_pipe()
{
    std::array<int, 2> fds{};
    // O_CLOEXEC на обох кінцях: у дитини потрібні дескриптори переживуть exec
    // лише тому, що dup2() знімає прапорець із копії.
    if (::pipe2(fds.data(), O_CLOEXEC) != 0) {
        throw_errno("pipe2");
    }
    return Pipe{UniqueFd{fds[0]}, UniqueFd{fds[1]}};
}

// Після fork() у дитині не можна ні кидати винятки, ні ходити в аллокатор:
// усі рядки й масиви готуємо заздалегідь, у батьківському процесі.
struct ChildPlan {
    std::vector<std::string> env_storage;
    std::vector<char*> envp;
    std::string shell;
    std::string argv0;
    std::string command;
};

ChildPlan make_plan(const Job& job)
{
    ChildPlan plan;
    plan.env_storage = job.env;
    plan.envp.reserve(plan.env_storage.size() + 1);
    for (auto& item : plan.env_storage) {
        plan.envp.push_back(item.data());
    }
    plan.envp.push_back(nullptr);

    plan.shell = job.shell.empty() ? std::string{"/bin/sh"} : job.shell;
    const auto slash = plan.shell.find_last_of('/');
    plan.argv0 = (slash == std::string::npos) ? plan.shell : plan.shell.substr(slash + 1);
    plan.command = job.command;
    return plan;
}

[[noreturn]] void child_fail(std::string_view text)
{
    const auto ignored = ::write(STDERR_FILENO, text.data(), text.size());
    static_cast<void>(ignored);
    ::_exit(127);
}

[[noreturn]] void run_child(const ChildPlan& plan, const passwd& pw, int in_fd, int out_fd)
{
    // Ізоляція сесії: завдання не отримує сигналів від термінала демона.
    if (::setsid() < 0) {
        child_fail("minicron: setsid\n");
    }

    // Обробники сигналів і маска успадковані від демона — повертаємо типові.
    struct sigaction dfl{};
    dfl.sa_handler = SIG_DFL;
    ::sigaction(SIGINT, &dfl, nullptr);
    ::sigaction(SIGTERM, &dfl, nullptr);
    ::sigaction(SIGPIPE, &dfl, nullptr);
    sigset_t empty;
    ::sigemptyset(&empty);
    ::sigprocmask(SIG_SETMASK, &empty, nullptr);

    if (::dup2(in_fd, STDIN_FILENO) < 0 || ::dup2(out_fd, STDOUT_FILENO) < 0 ||
        ::dup2(out_fd, STDERR_FILENO) < 0) {
        child_fail("minicron: dup2\n");
    }

    if (::getuid() == 0) {
        // Порядок незворотний і саме такий: групи, GID, аж тоді UID.
        if (::initgroups(pw.pw_name, pw.pw_gid) != 0) {
            child_fail("minicron: initgroups\n");
        }
        if (::setgid(pw.pw_gid) != 0) {
            child_fail("minicron: setgid\n");
        }
        if (::setuid(pw.pw_uid) != 0) {
            child_fail("minicron: setuid\n");
        }
    }

    if (::chdir(pw.pw_dir) != 0 && ::chdir("/") != 0) {
        child_fail("minicron: chdir\n");
    }

    // execle, а не execl: середовище завдання ми зібрали самі й не хочемо
    // нічого успадкувати від демона.
    ::execle(plan.shell.c_str(), plan.argv0.c_str(), "-c", plan.command.c_str(),
             nullptr, plan.envp.data());
    child_fail("minicron: exec\n");
}

// Одночасно допомпуємо stdin і вичитуємо вивід. По черзі не можна: команда,
// що надрукувала більше за буфер каналу, спинилася б на write(), поки ми
// чекаємо, доки вона дочитає свій stdin.
std::string pump_io(int read_fd, UniqueFd& write_fd, std::string_view in_data)
{
    std::string out;
    std::size_t written = 0;
    bool reading = true;

    while (reading || write_fd.valid()) {
        std::array<pollfd, 2> fds{};
        nfds_t count = 0;
        int read_idx = -1;
        int write_idx = -1;
        if (reading) {
            fds[count] = pollfd{read_fd, POLLIN, 0};
            read_idx = static_cast<int>(count++);
        }
        if (write_fd.valid()) {
            fds[count] = pollfd{write_fd.get(), POLLOUT, 0};
            write_idx = static_cast<int>(count++);
        }

        if (::poll(fds.data(), count, -1) < 0) {
            if (errno == EINTR) {
                continue;
            }
            throw_errno("poll");
        }

        if (write_idx >= 0 && fds[write_idx].revents != 0) {
            if ((fds[write_idx].revents & (POLLERR | POLLHUP)) != 0) {
                write_fd.reset();   // команда закрила stdin, не дочитавши
            } else {
                const ssize_t n = ::write(write_fd.get(), in_data.data() + written,
                                          in_data.size() - written);
                if (n > 0) {
                    written += static_cast<std::size_t>(n);
                    if (written == in_data.size()) {
                        write_fd.reset();
                    }
                } else if (n < 0 && errno != EINTR && errno != EAGAIN) {
                    write_fd.reset();
                }
            }
        }

        if (read_idx >= 0 && fds[read_idx].revents != 0) {
            std::array<char, kChunk> chunk{};
            const ssize_t n = ::read(read_fd, chunk.data(), chunk.size());
            if (n > 0) {
                out.append(chunk.data(), static_cast<std::size_t>(n));
            } else if (n == 0) {
                reading = false;   // дитина закрила записувальний кінець
            } else if (errno != EINTR && errno != EAGAIN) {
                throw_errno("read");
            }
        }
    }
    return out;
}

void write_all(int fd, std::string_view data)
{
    std::size_t done = 0;
    while (done < data.size()) {
        const ssize_t n = ::write(fd, data.data() + done, data.size() - done);
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            return;   // MTA пішов — звіт втрачено, але завдання вже виконано
        }
        done += static_cast<std::size_t>(n);
    }
}

// Контракт MTA: sendmail читає адресата із заголовків повідомлення (-t).
void deliver_mail(const Job& job, std::string_view body)
{
    Pipe mail = make_pipe();

    const pid_t pid = ::fork();
    if (pid < 0) {
        throw_errno("fork для sendmail");
    }
    if (pid == 0) {
        mail.write_end.reset();
        if (::dup2(mail.read_end.get(), STDIN_FILENO) < 0) {
            ::_exit(127);
        }
        ::execl("/usr/sbin/sendmail", "sendmail",
                "-FCronDaemon", "-odi", "-oem", "-oi", "-t", nullptr);
        ::_exit(127);
    }
    mail.read_end.reset();

    std::array<char, 256> host{};
    if (::gethostname(host.data(), host.size() - 1) != 0) {
        std::snprintf(host.data(), host.size(), "localhost");
    }

    std::string message = std::format(
        "From: root (Cron Daemon)\n"
        "To: {}\n"
        "Subject: Cron <{}@{}> {}\n"
        "MIME-Version: 1.0\n"
        "Content-Type: text/plain; charset=UTF-8\n"
        "Content-Transfer-Encoding: 8bit\n"
        "Auto-Submitted: auto-generated\n",
        job.mailto, job.user, host.data(), job.command);
    // Середовище завдання їде окремими заголовками X-Cron-Env.
    for (const auto& item : job.env) {
        message += std::format("X-Cron-Env: <{}>\n", item);
    }
    message += '\n';
    message += body;

    write_all(mail.write_end.get(), message);
    mail.write_end.reset();

    int status = 0;
    while (::waitpid(pid, &status, 0) < 0 && errno == EINTR) {
    }
    if (WIFEXITED(status) && WEXITSTATUS(status) != 0) {
        std::cerr << std::format("minicron: sendmail завершився кодом {}\n",
                                 WEXITSTATUS(status));
    }
}

}  // namespace

JobResult run_job(const Job& job)
{
    const passwd* pw = ::getpwnam(job.user.c_str());
    if (pw == nullptr) {
        throw std::runtime_error(std::format("невідомий користувач «{}»", job.user));
    }

    const ChildPlan plan = make_plan(job);
    Pipe out = make_pipe();

    UniqueFd child_stdin;
    UniqueFd parent_stdin;
    if (job.stdin_data.empty()) {
        // Без даних після '%' stdin завдання — /dev/null: читання дає EOF.
        child_stdin.reset(::open("/dev/null", O_RDWR | O_CLOEXEC));
        if (!child_stdin.valid()) {
            throw_errno("open /dev/null");
        }
    } else {
        Pipe in = make_pipe();
        child_stdin = std::move(in.read_end);
        parent_stdin = std::move(in.write_end);
        // Записувальний кінець неблокуючий — інакше повний канал спинив би
        // демона, поки команда не почне читати.
        const int flags = ::fcntl(parent_stdin.get(), F_GETFL, 0);
        if (flags >= 0) {
            ::fcntl(parent_stdin.get(), F_SETFL, flags | O_NONBLOCK);
        }
    }

    const pid_t pid = ::fork();
    if (pid < 0) {
        throw_errno("fork");
    }
    if (pid == 0) {
        run_child(plan, *pw, child_stdin.get(), out.write_end.get());
    }

    out.write_end.reset();
    child_stdin.reset();

    JobResult result;
    result.output = pump_io(out.read_end.get(), parent_stdin, job.stdin_data);
    parent_stdin.reset();
    out.read_end.reset();

    int status = 0;
    while (::waitpid(pid, &status, 0) < 0) {
        if (errno != EINTR) {
            throw_errno("waitpid");
        }
    }
    if (WIFEXITED(status)) {
        result.exit_code = WEXITSTATUS(status);
    } else if (WIFSIGNALED(status)) {
        result.signal = WTERMSIG(status);
        result.exit_code = 128 + result.signal;
    }

    // Пошта йде лише тоді, коли MAILTO непорожній І вивід не порожній —
    // мовчазне завдання не турбує адміністратора хай там який код виходу.
    if (!job.mailto.empty() && !result.output.empty()) {
        deliver_mail(job, result.output);
    }
    return result;
}

}  // namespace minicron
