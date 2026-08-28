#include <iostream>
#include <sys/wait.h>

void inspect_cpp(int wstatus) {
    if (WIFEXITED(wstatus)) {
        std::cout << "Нормальний вихід з кодом: " << WEXITSTATUS(wstatus) << "\n";
    } else if (WIFSIGNALED(wstatus)) {
        std::cout << "Вбито сигналом: " << WTERMSIG(wstatus) << "\n";
        if (WCOREDUMP(wstatus)) {
            std::cout << "Записано core dump.\n";
        }
    } else if (WIFSTOPPED(wstatus)) {
        std::cout << "Зупинено сигналом: " << WSTOPSIG(wstatus) << "\n";
    }
}
