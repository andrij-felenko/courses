#include "jobs.hpp"
#include "terminal.hpp"

#include <sys/wait.h>
#include <unistd.h>

#include <cerrno>
#include <cstdio>
#include <cstring>
#include <algorithm>
#include <system_error>

namespace {

JobTable* g_table = nullptr;

void sigchld_handler(int)
{
    // Обробник не має права зіпсувати errno основного потоку виконання.
    const int saved_errno = errno;
    if (g_table != nullptr) {
        g_table->reap();
    }
    errno = saved_errno;
}

}  // namespace

void Job::add_proc(::pid_t pid)
{
    if (pgid_ == 0) {
        pgid_ = pid;               // лідером групи стає перший процес конвеєра
    }
    procs_.push_back(Proc{pid, ProcState::Running, 0});
}

bool Job::update(::pid_t pid, int status) noexcept
{
    for (Proc& p : procs_) {
        if (p.pid != pid) {
            continue;
        }
        p.status = status;
        if (WIFSTOPPED(status)) {
            p.state = ProcState::Stopped;
        } else if (WIFCONTINUED(status)) {
            p.state = ProcState::Running;
        } else {
            p.state = ProcState::Done;
        }
        return true;
    }
    return false;
}

bool Job::done() const noexcept
{
    return std::all_of(procs_.begin(), procs_.end(),
                       [](const Proc& p) { return p.state == ProcState::Done; });
}

bool Job::stopped() const noexcept
{
    if (std::any_of(procs_.begin(), procs_.end(),
                    [](const Proc& p) { return p.state == ProcState::Running; })) {
        return false;
    }
    return std::any_of(procs_.begin(), procs_.end(),
                       [](const Proc& p) { return p.state == ProcState::Stopped; });
}

int Job::exit_code() const noexcept
{
    if (procs_.empty()) {
        return 0;
    }
    // Код конвеєра — це код ОСТАННЬОЇ ланки; решта губиться (звідси pipefail).
    const int status = procs_.back().status;
    if (WIFSIGNALED(status)) {
        return 128 + WTERMSIG(status);
    }
    return WIFEXITED(status) ? WEXITSTATUS(status) : 0;
}

JobTable::SigchldGuard::SigchldGuard() noexcept
{
    ::sigset_t mask{};
    ::sigemptyset(&mask);
    ::sigaddset(&mask, SIGCHLD);
    ::sigprocmask(SIG_BLOCK, &mask, &prev_);
}

JobTable::SigchldGuard::~SigchldGuard()
{
    ::sigprocmask(SIG_SETMASK, &prev_, nullptr);
}

JobTable::JobTable(TerminalControl& term) : term_(term)
{
    g_table = this;

    struct ::sigaction sa {};
    sa.sa_handler = &sigchld_handler;
    ::sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;      // SA_NOCLDSTOP не ставимо: зупинки нам потрібні
    if (::sigaction(SIGCHLD, &sa, nullptr) < 0) {
        g_table = nullptr;
        throw std::system_error(errno, std::generic_category(), "sigaction(SIGCHLD)");
    }
}

JobTable::~JobTable()
{
    ::signal(SIGCHLD, SIG_DFL);
    g_table = nullptr;
}

Job& JobTable::create(bool foreground, std::string text)
{
    jobs_.push_back(std::make_unique<Job>(next_id_++, foreground, std::move(text)));
    return *jobs_.back();
}

void JobTable::reap() noexcept
{
    int status = 0;
    ::pid_t pid = 0;

    // WNOHANG не дає заблокувати оболонку; WUNTRACED і WCONTINUED
    // приносять ще й зупинку (Ctrl+Z) та відновлення (SIGCONT).
    while ((pid = ::waitpid(-1, &status, WNOHANG | WUNTRACED | WCONTINUED)) > 0) {
        for (auto& job : jobs_) {
            if (job->update(pid, status)) {
                break;
            }
        }
    }
}

int JobTable::wait_foreground(Job& job)
{
    SigchldGuard guard;
    ::sigset_t idle = guard.previous();
    ::sigdelset(&idle, SIGCHLD);   // sigsuspend має ПРОПУСКАТИ SIGCHLD

    while (!job.done() && !job.stopped()) {
        ::sigsuspend(&idle);       // атомарно: відпустити сигнал і заснути
    }
    term_.reclaim();

    if (job.stopped()) {
        std::fprintf(stderr, "[%d]  Зупинено   %s\n", job.id(), job.text().c_str());
        job.to_background();
        job.mark_reported();
        return 128 + SIGTSTP;
    }

    const int code = job.exit_code();
    std::erase_if(jobs_, [&job](const std::unique_ptr<Job>& p) { return p.get() == &job; });
    return code;
}

bool JobTable::any_active() const noexcept
{
    return std::any_of(jobs_.begin(), jobs_.end(),
                       [](const std::unique_ptr<Job>& j) { return !j->done(); });
}

void JobTable::report()
{
    SigchldGuard guard;

    for (const auto& job : jobs_) {
        if (job->foreground()) {
            continue;
        }
        if (job->done()) {
            std::fprintf(stderr, "[%d]  Завершено (%d)  %s\n",
                         job->id(), job->exit_code(), job->text().c_str());
        } else if (job->stopped() && !job->reported()) {
            std::fprintf(stderr, "[%d]  Зупинено   %s\n", job->id(), job->text().c_str());
            job->mark_reported();
        }
    }
    std::erase_if(jobs_, [](const std::unique_ptr<Job>& j) {
        return !j->foreground() && j->done();
    });
}

void JobTable::wait_all()
{
    SigchldGuard guard;
    ::sigset_t idle = guard.previous();
    ::sigdelset(&idle, SIGCHLD);

    while (any_active()) {
        ::sigsuspend(&idle);
    }
}
