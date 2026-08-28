#include <iostream>
#include <sys/prctl.h>
#include <unistd.h>
#include <system_error>

#ifndef PR_SCHED_CORE
#define PR_SCHED_CORE 62
#define PR_SCHED_CORE_CREATE 1
#define PR_SCHED_CORE_SCOPE_THREAD 0
#endif

// Створення ізольованого домену безпеки для поточного потоку/процесу
void isolate_thread_group() {
    int res = prctl(PR_SCHED_CORE, PR_SCHED_CORE_CREATE, 0, PR_SCHED_CORE_SCOPE_THREAD, 0);
    if (res < 0) {
        throw std::system_error(errno, std::generic_category(), "Не вдалося увімкнути PR_SCHED_CORE");
    }
    std::cout << "[PID " << getpid() << "] Створено ізольований домен Core Scheduling
";
}
