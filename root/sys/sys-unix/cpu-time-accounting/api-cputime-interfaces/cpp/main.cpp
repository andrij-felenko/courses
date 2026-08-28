#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <iomanip>
#include <cerrno>
#include <ctime>
#include <unistd.h>
#include <sys/times.h>
#include <sys/resource.h>

static double cpu_seconds(clockid_t c) {
    timespec t{};
    if (clock_gettime(c, &t) != 0) return -1.0;
    return t.tv_sec + t.tv_nsec / 1e9;
}

int main() {
    const double tck = static_cast<double>(sysconf(_SC_CLK_TCK));

    // 1. times() — тики USER_HZ
    tms tm{};
    errno = 0;
    if (times(&tm) == static_cast<clock_t>(-1) && errno != 0) {
        std::perror("times");
        return 1;
    }
    std::cout << std::fixed << std::setprecision(2)
              << "times    user " << (tm.tms_utime / tck)
              << "  sys " << (tm.tms_stime / tck)
              << "  нащадки " << ((tm.tms_cutime + tm.tms_cstime) / tck) << "\n";

    // 2. getrusage() — мікросекунди
    rusage ru{};
    getrusage(RUSAGE_SELF, &ru);
    std::cout << std::setprecision(6)
              << "rusage   user " << (ru.ru_utime.tv_sec + ru.ru_utime.tv_usec / 1e6)
              << "  sys " << (ru.ru_stime.tv_sec + ru.ru_stime.tv_usec / 1e6) << "\n";

    // 3. процесорні годинники — наносекунди
    std::cout << std::setprecision(9)
              << "clock    процес " << cpu_seconds(CLOCK_PROCESS_CPUTIME_ID)
              << "  потік " << cpu_seconds(CLOCK_THREAD_CPUTIME_ID) << "\n";

    // 4. schedstat
    if (std::ifstream f{"/proc/self/schedstat"}; f.is_open()) {
        unsigned long long run = 0, wait = 0;
        unsigned long slices = 0;
        if (f >> run >> wait >> slices) {
            std::cout << "sched    на процесорі " << (run / 1e9)
                      << "  у черзі " << (wait / 1e9)
                      << "  вибрано " << slices << " разів\n";
        }
    }

    // 5. /proc/self/stat
    if (std::ifstream f{"/proc/self/stat"}; f.is_open()) {
        std::string line;
        if (std::getline(f, line)) {
            auto pos = line.rfind(')');
            if (pos != std::string::npos && pos + 2 < line.size()) {
                std::istringstream iss(line.substr(pos + 2));
                char state;
                int ppid, pgrp, session, tty, tpgid;
                unsigned flags;
                unsigned long minflt, cminflt, majflt, cmajflt, ut, st;
                if (iss >> state >> ppid >> pgrp >> session >> tty >> tpgid
                        >> flags >> minflt >> cminflt >> majflt >> cmajflt >> ut >> st) {
                    std::cout << std::setprecision(2)
                              << "stat     user " << (ut / tck) << "  sys " << (st / tck) << "\n";
                }
            }
        }
    }
    return 0;
}
