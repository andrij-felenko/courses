#include <unistd.h>
#include <sys/wait.h>
#include <string>
#include <vector>
#include <span>
#include <system_error>

/* Безпечний запуск процесу в ідіоматичному C++20 */
int safe_exec_cpp(const std::string& branch) {
    pid_t pid = fork();
    if (pid == 0) {
        std::vector<const char*> argv = {"git", "checkout", branch.c_str(), nullptr};
        execvp("git", const_cast<char* const*>(argv.data()));
        _exit(127);
    }
    if (pid < 0) {
        throw std::system_error(errno, std::generic_category(), "fork failed");
    }
    int status = 0;
    waitpid(pid, &status, 0);
    return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
}
