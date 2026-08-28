#include <iostream>
#include <vector>
#include <string>
#include <variant>
#include <expected>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

struct ProcessSuccess {
    int exit_code;
};

struct ProcessKilled {
    int signal_number;
    bool core_dumped;
};

using ProcessExitStatus = std::variant<ProcessSuccess, ProcessKilled>;

class ProcessRunner {
public:
    static std::expected<ProcessExitStatus, std::string> 
    execute(const std::vector<std::string>& args) {
        if (args.empty()) {
            return std::unexpected("Порожній список аргументів");
        }

        pid_t pid = ::fork();
        if (pid < 0) {
            return std::unexpected("Системна помилка fork()");
        }

        if (pid == 0) {
            std::vector<char*> c_args;
            for (const auto& arg : args) {
                c_args.push_back(const_cast<char*>(arg.c_str()));
            }
            c_args.push_back(nullptr);

            ::execvp(c_args[0], c_args.data());
            ::_exit(127);
        }

        int wstatus = 0;
        if (::waitpid(pid, &wstatus, 0) < 0) {
            return std::unexpected("Системна помилка waitpid()");
        }

        if (WIFEXITED(wstatus)) {
            return ProcessSuccess{WEXITSTATUS(wstatus)};
        } else if (WIFSIGNALED(wstatus)) {
            return ProcessKilled{
                WTERMSIG(wstatus), 
                static_cast<bool>(WCOREDUMP(wstatus))
            };
        }

        return std::unexpected("Невідомий стан процесa");
    }
};
