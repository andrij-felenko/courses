#include "pipeline.hpp"

#include "fd.hpp"
#include "jobs.hpp"
#include "spawn.hpp"
#include "terminal.hpp"

#include <fcntl.h>
#include <unistd.h>

#include <cerrno>
#include <csignal>
#include <cstdio>
#include <cstring>
#include <initializer_list>
#include <system_error>

::pid_t PipelineRunner::fork_stage(const Stage& stage, const StageIo& io, bool foreground)
{
    // Вектор char* будуємо ДО fork(): у нащадку виділяти пам'ять уже не можна.
    std::vector<char*> argv;
    argv.reserve(stage.argv.size() + 1);
    for (const auto& a : stage.argv) {
        argv.push_back(const_cast<char*>(a.c_str()));
    }
    argv.push_back(nullptr);

    const ::pid_t child = ::fork();
    if (child < 0) {
        throw std::system_error(errno, std::generic_category(), "fork");
    }

    if (child == 0) {
        // --- нащадок ---
        const ::pid_t pgid = (io.pgid == 0) ? ::getpid() : io.pgid;

        // Ту саму дію робить і батько: хто перший встиг, той і створив групу.
        // Саме це знімає гонку між setpgid() у батька та execve() в нащадка.
        ::setpgid(0, pgid);
        if (foreground && term_.interactive()) {
            ::tcsetpgrp(term_.fd(), pgid);
        }
        // Оболонка ігнорувала термінальні сигнали — програмі потрібна типова дія.
        for (int sig : { SIGINT, SIGQUIT, SIGTSTP, SIGTTIN, SIGTTOU, SIGCHLD }) {
            ::signal(sig, SIG_DFL);
        }

        if (io.in_fd != STDIN_FILENO && ::dup2(io.in_fd, STDIN_FILENO) < 0) {
            ::_exit(126);
        }
        if (io.out_fd != STDOUT_FILENO && ::dup2(io.out_fd, STDOUT_FILENO) < 0) {
            ::_exit(126);
        }
        for (int fd : io.close_fds) {
            if (fd > STDERR_FILENO) {
                ::close(fd);
            }
        }

        ::execvp(argv[0], argv.data());

        // Після fork() у нащадку не можна ні кидати винятки, ні чіпати
        // потоки C++ — лишається сирий write().
        const int err = errno;
        static constexpr char tail[] = ": не вдалося запустити\n";
        ::write(STDERR_FILENO, argv[0], std::strlen(argv[0]));
        ::write(STDERR_FILENO, tail, sizeof tail - 1);
        ::_exit(err == ENOENT ? 127 : 126);
    }

    // --- батько ---
    const ::pid_t pgid = (io.pgid == 0) ? child : io.pgid;
    if (::setpgid(child, pgid) < 0 && errno != EACCES && errno != ESRCH) {
        throw std::system_error(errno, std::generic_category(), "setpgid");
    }
    if (foreground) {
        term_.give_to(pgid);
    }
    return child;
}

int PipelineRunner::run(const PipelineSpec& spec)
{
    if (spec.stages.empty()) {
        return 0;
    }

    // Нащадок може завершитися раніше, ніж потрапить у таблицю завдань,
    // тому SIGCHLD блокуємо на весь час побудови конвеєра.
    JobTable::SigchldGuard guard;
    Job& job = jobs_.create(spec.foreground, spec.text);

    Fd upstream;                   // читальний кінець попереднього каналу
    int rc = 0;

    for (std::size_t i = 0; i < spec.stages.size(); ++i) {
        const bool last = (i + 1 == spec.stages.size());
        Pipe channel;
        Fd sink;
        int out_fd = STDOUT_FILENO;

        try {
            if (!last) {
                // O_CLOEXEC ставить саме ядро, у момент створення дескрипторів:
                // вікна між pipe() та fcntl() більше немає.
                channel = Pipe::make();
                out_fd = channel.write_end.get();
            } else if (spec.outfile) {
                const int flags = O_WRONLY | O_CREAT | O_CLOEXEC
                                | (spec.append ? O_APPEND : O_TRUNC);
                sink = Fd::open_file(*spec.outfile, flags);
                out_fd = sink.get();
            }

            std::vector<int> closes;
            for (const Fd* fd : { &upstream, &channel.read_end, &channel.write_end }) {
                if (fd->valid()) {
                    closes.push_back(fd->get());
                }
            }

            const StageIo io{ upstream.valid() ? upstream.get() : STDIN_FILENO,
                              out_fd, closes, job.pgid() };
            const ::pid_t pid = spec.use_spawn
                ? spawn_stage(spec.stages[i].argv.front(), spec.stages[i].argv, io)
                : fork_stage(spec.stages[i], io, spec.foreground);
            job.add_proc(pid);
        } catch (const std::system_error& e) {
            std::fprintf(stderr, "конвеєр: %s\n", e.what());
            rc = 1;
            break;
        }

        // Свої копії батько закриває ЗАВЖДИ: поки живий бодай один дескриптор
        // запису, читач наступної ланки не побачить EOF. Тут це роблять
        // деструктори — sink і channel.write_end гинуть наприкінці витка.
        upstream = std::move(channel.read_end);
    }
    upstream.reset();

    if (job.empty()) {
        return 1;
    }

    // Шлях через posix_spawn не має батьківської половини fork_stage,
    // тож термінал завданню віддаємо тут.
    if (spec.use_spawn && spec.foreground) {
        term_.give_to(job.pgid());
    }

    if (spec.foreground) {
        const int code = jobs_.wait_foreground(job);
        return rc == 0 ? code : 1;
    }
    std::fprintf(stderr, "[%d] %ld\n", job.id(), static_cast<long>(job.pgid()));
    return rc;
}
