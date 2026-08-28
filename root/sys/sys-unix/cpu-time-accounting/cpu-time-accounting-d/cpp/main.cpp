#include <iostream>
#include <iomanip>
#include <time.h>
#include <sys/resource.h>

int main() {
    timespec t{};
    rusage r{};

    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &t);   // точна сума
    getrusage(RUSAGE_SELF, &r);                    // поділ на user/sys

    double exact = t.tv_sec + t.tv_nsec / 1e9;
    double user  = r.ru_utime.tv_sec + r.ru_utime.tv_usec / 1e6;
    double sys   = r.ru_stime.tv_sec + r.ru_stime.tv_usec / 1e6;

    std::cout << std::fixed << std::setprecision(6)
              << "точно: " << exact << "   user+sys: " << (user + sys)
              << "   (user " << user << ", sys " << sys << ")\n";
    return 0;
}
