#include <iostream>
#include <thread>
#include <filesystem>
#include <sched.h>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <unistd.h>

static void report(const char *tag)
{
    cpu_set_t set;
    CPU_ZERO(&set);
    sched_getaffinity(0, sizeof set, &set);
    std::cout << tag << " tid=" << syscall(SYS_gettid)
              << " nice=" << getpriority(PRIO_PROCESS, 0)
              << " ядер=" << CPU_COUNT(&set)
              << " cwd=" << std::filesystem::current_path().string() << '\n';
}

int main()
{
    report("головний");
    std::thread t([]() {
        report("потік");
        setpriority(PRIO_PROCESS, 0, 5);          // своє для задачі
        cpu_set_t one;
        CPU_ZERO(&one); CPU_SET(0, &one);
        sched_setaffinity(0, sizeof one, &one);   // своє для задачі
        std::filesystem::current_path("/tmp");    // спільне для всієї програми!
        report("потік*");
    });
    t.join();
    report("головний*");
}
