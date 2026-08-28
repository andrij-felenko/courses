#include <iostream>
#include <chrono>
#include <iomanip>
#include <ctime>

void print_clock_cpp(clockid_t clk_id, const char* name) {
    struct timespec ts{};
    if (clock_gettime(clk_id, &ts) == 0) {
        std::cout << std::left << std::setw(20) << name << ": "
                  << ts.tv_sec << "." << std::setw(9) << std::setfill('0')
                  << ts.tv_nsec << " с\n";
    } else {
        std::cerr << "Помилка читання годинника: " << name << '\n';
    }
}

int main() {
    print_clock_cpp(CLOCK_REALTIME, "CLOCK_REALTIME");
    print_clock_cpp(CLOCK_MONOTONIC, "CLOCK_MONOTONIC");
    print_clock_cpp(CLOCK_BOOTTIME, "CLOCK_BOOTTIME");
    print_clock_cpp(CLOCK_TAI, "CLOCK_TAI");
    return 0;
}
