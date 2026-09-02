// Таблиця завдань: облік груп процесів і збір їхніх статусів.
#pragma once

#include <sys/types.h>

#include <csignal>
#include <memory>
#include <string>
#include <vector>

class TerminalControl;

enum class ProcState { Running, Stopped, Done };

struct Proc {
    ::pid_t pid{};
    ProcState state{ProcState::Running};
    int status{};                  // сирий статус із waitpid()
};

class Job {
public:
    Job(int id, bool foreground, std::string text)
        : id_(id), foreground_(foreground), text_(std::move(text)) {}

    void add_proc(::pid_t pid);
    bool update(::pid_t pid, int status) noexcept;

    [[nodiscard]] bool done() const noexcept;
    [[nodiscard]] bool stopped() const noexcept;
    [[nodiscard]] int exit_code() const noexcept;

    [[nodiscard]] int id() const noexcept { return id_; }
    [[nodiscard]] ::pid_t pgid() const noexcept { return pgid_; }
    [[nodiscard]] bool foreground() const noexcept { return foreground_; }
    [[nodiscard]] bool empty() const noexcept { return procs_.empty(); }
    [[nodiscard]] const std::string& text() const noexcept { return text_; }

    void to_background() noexcept { foreground_ = false; }
    void mark_reported() noexcept { reported_ = true; }
    [[nodiscard]] bool reported() const noexcept { return reported_; }

private:
    int id_;
    ::pid_t pgid_ = 0;
    bool foreground_;
    bool reported_ = false;
    std::string text_;
    std::vector<Proc> procs_;
};

class JobTable {
public:
    // Блокує SIGCHLD на час свого життя: таблицю не можна міняти
    // одночасно з обробником.
    class SigchldGuard {
    public:
        SigchldGuard() noexcept;
        ~SigchldGuard();
        SigchldGuard(const SigchldGuard&) = delete;
        SigchldGuard& operator=(const SigchldGuard&) = delete;
        [[nodiscard]] const ::sigset_t& previous() const noexcept { return prev_; }
    private:
        ::sigset_t prev_{};
    };

    explicit JobTable(TerminalControl& term);
    ~JobTable();
    JobTable(const JobTable&) = delete;
    JobTable& operator=(const JobTable&) = delete;

    Job& create(bool foreground, std::string text);

    int wait_foreground(Job& job);
    void wait_all();
    void report();
    [[nodiscard]] bool any_active() const noexcept;

    void reap() noexcept;          // викликається з обробника SIGCHLD

private:
    TerminalControl& term_;
    // unique_ptr, щоб посилання Job& переживало ріст вектора.
    std::vector<std::unique_ptr<Job>> jobs_;
    int next_id_ = 1;
};
