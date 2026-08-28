#include <iostream>
#include <thread>
#include <unistd.h>
#include <sys/syscall.h>

int main()
{
    auto print_ids = [](const char *label) {
        std::cout << label << ": getpid()=" << getpid()
                  << "  gettid()=" << syscall(SYS_gettid) << '\n';
    };

    print_ids("головний");
    std::thread t([print_ids] { print_ids("потік"); });
    t.join();
}
