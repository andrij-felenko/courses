#include <iostream>
#include <vector>
#include <string>
#include <unistd.h>
#include <sys/wait.h>
#include <span>

/* Безпечна RAII-обгортка запуску дочірнього процесу у C++ */
class SafeProcessLauncher {
public:
    static int execute(std::string_view program, std::span<const std::string> arguments) {
        pid_t pid = fork();
        if (pid < 0) {
            throw std::runtime_error("Не вдалося виконати fork()");
        }
        if (pid == 0) {
            std::vector<char*> argv;
            argv.reserve(arguments.size() + 2);
            
            std::string prog_str(program);
            argv.push_back(prog_str.data());
            
            std::vector<std::string> args_storage(arguments.begin(), arguments.end());
            for (auto& arg : args_storage) {
                argv.push_back(arg.data());
            }
            argv.push_back(nullptr);

            execvp(prog_str.c_str(), argv.data());
            _exit(127);
        }

        int status = 0;
        waitpid(pid, &status, 0);
        return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
    }
};
