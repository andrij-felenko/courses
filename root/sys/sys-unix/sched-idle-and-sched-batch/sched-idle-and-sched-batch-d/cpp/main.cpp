#include <iostream>
#include <system_error>
#include <cerrno>
#include <sched.h>
#include <unistd.h>

class ThreadScheduler {
public:
    static void set_current_policy(int policy) {
        sched_param param{};
        param.sched_priority = 0; // Для не-RT класів пріоритет завжди 0

        if (::sched_setscheduler(0, policy, &param) != 0) {
            throw std::system_error(errno, std::generic_category(),
                                    "Не вдалося змінити політику планування");
        }
    }
};

int main() {
    try {
        std::cout << "Поточний PID: " << ::getpid() << ". Перехід у SCHED_BATCH...\n";
        ThreadScheduler::set_current_policy(SCHED_BATCH);
        std::cout << "Успішно встановлено SCHED_BATCH.\n";

        volatile double val = 1.0;
        for (long i = 0; i < 500000000L; ++i) {
            val += i * 0.0000001;
        }

        std::cout << "Перехід у SCHED_IDLE...\n";
        ThreadScheduler::set_current_policy(SCHED_IDLE);
        std::cout << "Успішно встановлено SCHED_IDLE.\n";
    } catch (const std::system_error& e) {
        std::cerr << "Помилка планувальника: " << e.what() << '\n';
        return 1;
    }

    return 0;
}
