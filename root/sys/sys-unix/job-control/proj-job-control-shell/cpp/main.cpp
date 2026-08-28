#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <memory>
#include <csignal>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <termios.h>

enum class JobStatus { Running, Stopped, Completed };

struct Job {
    int id;
    pid_t pgid;
    std::string command;
    JobStatus status;
    termios tmodes;
};

class TerminalRAII {
    int fd_;
    termios original_modes_;
public:
    explicit TerminalRAII(int fd) : fd_(fd) {
        tcgetattr(fd_, &original_modes_);
    }
    ~TerminalRAII() {
        tcsetattr(fd_, TCSADRAIN, &original_modes_);
    }
    void restore() const {
        tcsetattr(fd_, TCSADRAIN, &original_modes_);
    }
};

class MiniShell {
    pid_t shell_pgid_;
    int tty_fd_{STDIN_FILENO};
    termios shell_tmodes_;
    std::vector<Job> jobs_;

public:
    MiniShell() {
        if (!isatty(tty_fd_)) {
            throw std::runtime_error("Shell must be run in a interactive TTY");
        }

        while (tcgetpgrp(tty_fd_) != (shell_pgid_ = getpgrp())) {
            kill(-shell_pgid_, SIGTTIN);
        }

        // Ігноруємо сигнали термінала в процесі оболонки
        std::signal(SIGINT, SIG_IGN);
        std::signal(SIGQUIT, SIG_IGN);
        std::signal(SIGTSTP, SIG_IGN);
        std::signal(SIGTTIN, SIG_IGN);
        std::signal(SIGTTOU, SIG_IGN);

        shell_pgid_ = getpid();
        if (setpgid(shell_pgid_, shell_pgid_) < 0) {
            std::perror("setpgid shell");
            std::exit(EXIT_FAILURE);
        }

        tcsetpgrp(tty_fd_, shell_pgid_);
        tcgetattr(tty_fd_, &shell_tmodes_);
    }

    void run() {
        std::string line;
        while (true) {
            std::cout << "cpp-job-shell> " << std::flush;
            if (!std::getline(std::cin, line) || line == "exit") break;
            if (line.empty()) continue;

            auto tokens = parse_command(line);
            if (tokens.empty()) continue;

            bool is_bg = false;
            if (tokens.back() == "&") {
                is_bg = true;
                tokens.pop_back();
            }

            if (tokens[0] == "jobs") {
                print_jobs();
            } else if (tokens[0] == "fg") {
                bring_to_fg();
            } else if (tokens[0] == "bg") {
                resume_in_bg();
            } else {
                spawn_job(tokens, is_bg, line);
            }
        }
    }

private:
    std::vector<std::string> parse_command(const std::string& cmd) {
        std::stringstream ss(cmd);
        std::string token;
        std::vector<std::string> res;
        while (ss >> token) res.push_back(token);
        return res;
    }

    void print_jobs() {
        for (const auto& job : jobs_) {
            if (job.status != JobStatus::Completed) {
                std::cout << "[" << job.id << "] "
                          << (job.status == JobStatus::Stopped ? "Stopped" : "Running")
                          << "   " << job.command << "\n";
            }
        }
    }

    void bring_to_fg() {
        for (auto it = jobs_.rbegin(); it != jobs_.rend(); ++it) {
            if (it->status != JobStatus::Completed) {
                std::cout << it->command << "\n";
                tcsetattr(tty_fd_, TCSADRAIN, &it->tmodes);
                tcsetpgrp(tty_fd_, it->pgid);
                
                if (it->status == JobStatus::Stopped) {
                    kill(-it->pgid, SIGCONT);
                }
                it->status = JobStatus::Running;
                wait_for_pgid(it->pgid);
                return;
            }
        }
    }

    void resume_in_bg() {
        for (auto it = jobs_.rbegin(); it != jobs_.rend(); ++it) {
            if (it->status == JobStatus::Stopped) {
                kill(-it->pgid, SIGCONT);
                it->status = JobStatus::Running;
                std::cout << "[" << it->id << "] " << it->pgid << "\n";
                return;
            }
        }
    }

    void wait_for_pgid(pid_t pgid) {
        int status;
        while (waitpid(-pgid, &status, WUNTRACED) > 0) {
            if (WIFSTOPPED(status)) {
                for (auto& job : jobs_) {
                    if (job.pgid == pgid) {
                        job.status = JobStatus::Stopped;
                        tcgetattr(tty_fd_, &job.tmodes);
                        std::cout << "\n[" << job.id << "]+ Stopped   " << job.command << "\n";
                        break;
                    }
                }
                break;
            }
        }
        tcsetpgrp(tty_fd_, shell_pgid_);
        tcsetattr(tty_fd_, TCSADRAIN, &shell_tmodes);
    }

    void spawn_job(const std::vector<std::string>& args, bool is_bg, const std::string& full_cmd) {
        pid_t pid = fork();

        if (pid == 0) {
            pid_t cpid = getpid();
            setpgid(cpid, cpid);
            if (!is_bg) tcsetpgrp(tty_fd_, cpid);

            std::signal(SIGINT, SIG_DFL);
            std::signal(SIGQUIT, SIG_DFL);
            std::signal(SIGTSTP, SIG_DFL);
            std::signal(SIGTTIN, SIG_DFL);
            std::signal(SIGTTOU, SIG_DFL);

            std::vector<char*> c_args;
            for (const auto& arg : args) c_args.push_back(const_cast<char*>(arg.c_str()));
            c_args.push_back(nullptr);

            execvp(c_args[0], c_args.data());
            std::perror("execvp");
            std::_Exit(EXIT_FAILURE);
        } else if (pid > 0) {
            setpgid(pid, pid);
            termios job_tmodes;
            tcgetattr(tty_fd_, &job_tmodes);
            int job_id = static_cast<int>(jobs_.size()) + 1;
            jobs_.push_back({job_id, pid, full_cmd, is_bg ? JobStatus::Running : JobStatus::Stopped, job_tmodes});

            if (!is_bg) {
                tcsetpgrp(tty_fd_, pid);
                wait_for_pgid(pid);
            } else {
                std::cout << "[" << job_id << "] " << pid << "\n";
            }
        }
    }
};

int main() {
    try {
        MiniShell shell;
        shell.run();
    } catch (const std::exception& e) {
        std::cerr << "Fatal shell error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
