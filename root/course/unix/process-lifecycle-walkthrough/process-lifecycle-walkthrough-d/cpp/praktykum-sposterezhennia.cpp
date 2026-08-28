#include <iostream>
#include <format>
#include <chrono>
#include <thread>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

class ProcessSupervisor {
public:
    static void run_lifecycle_demo() {
        std::cout << std::format("[Батько PID {}] Запуск життєвого циклу процесу...\n", ::getpid());

        const pid_t pid = ::fork();

        if (pid < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка виклику fork");
        }

        if (pid == 0) {
            // Дитина: Фаза 1 і 2
            std::cout << std::format("  [Дитина PID {}] Я народилася! Батько PPID = {}\n",
                                     ::getpid(), ::getppid());
            std::cout << std::format("  [Дитина PID {}] Працюю (TASK_RUNNING)...\n", ::getpid());
            std::this_thread::sleep_for(std::chrono::milliseconds(100));

            std::cout << std::format("  [Дитина PID {}] Сон (TASK_INTERRUPTIBLE)...\n", ::getpid());
            std::this_thread::sleep_for(std::chrono::seconds(1));

            std::cout << std::format("  [Дитина PID {}] Завершення exit(42)...\n", ::getpid());
            std::_Exit(42); // Фаза 3: вхід у do_exit()
        }

        // Батьківський процес
        std::cout << std::format("[Батько PID {}] Дитину створено: PID {}. Чекаю 2 с...\n",
                                 ::getpid(), pid);
        std::this_thread::sleep_for(std::chrono::seconds(2)); // Дитина стає зомбі (Фаза 4)

        std::cout << std::format("[Батько PID {}] Прибирання через waitid() (Фаза 5)...\n",
                                 ::getpid());

        siginfo_t info{};
        if (::waitid(P_PID, static_cast<id_t>(pid), &info, WEXITED) == -1) {
            throw std::system_error(errno, std::generic_category(), "Помилка виклику waitid");
        }

        if (info.si_code == CLD_EXITED) {
            std::cout << std::format("[Батько PID {}] Дитина PID {} прибрана. Код виходу = {}\n",
                                     ::getpid(), info.si_pid, info.si_status);
        } else {
            std::cout << std::format("[Батько PID {}] Дитина PID {} завершилася сигналом {}\n",
                                     ::getpid(), info.si_pid, info.si_status);
        }

        std::cout << std::format("[Батько PID {}] Ресурси вивільнено, завершення.\n", ::getpid());
    }
};

int main() {
    try {
        ProcessSupervisor::run_lifecycle_demo();
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "Помилка супервізора: " << ex.what() << '\n';
        return 1;
    }
}
