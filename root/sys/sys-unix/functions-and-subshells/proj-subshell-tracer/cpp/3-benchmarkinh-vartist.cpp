#include <iostream>
#include <chrono>
#include <vector>
#include <system_error>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/resource.h>

constexpr int ITERATIONS = 5000;

void benchmark_in_process() {
    volatile int counter = 0;
    auto start = std::chrono::high_resolution_clock::now();

    for (int i = 0; i < ITERATIONS; ++i) {
        counter += 1;
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::micro> elapsed = end - start;
    std::cout << "In-process Calls: " << elapsed.count() << " us (" 
              << elapsed.count() / ITERATIONS << " us/call)\n";
}

void benchmark_subshells() {
    auto start = std::chrono::high_resolution_clock::now();

    for (int i = 0; i < ITERATIONS; ++i) {
        pid_t pid = ::fork();
        if (pid < 0) {
            throw std::system_error(errno, std::generic_category(), "fork failed");
        }
        if (pid == 0) {
            ::_exit(0);
        }
        ::waitpid(pid, nullptr, 0);
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::micro> elapsed = end - start;
    std::cout << "Subshell Forks:   " << elapsed.count() << " us (" 
              << elapsed.count() / ITERATIONS << " us/fork)\n";
}

int main() {
    try {
        std::cout << "Running benchmark for " << ITERATIONS << " iterations...\n";
        benchmark_in_process();
        benchmark_subshells();

        rusage usage{};
        if (::getrusage(RUSAGE_CHILDREN, &usage) == 0) {
            std::cout << "Kernel Telemetry for " << ITERATIONS << " child subshells:\n";
            std::cout << "  Minor Page Faults (COW events): " << usage.ru_minflt << "\n";
            std::cout << "  Voluntary Context Switches:     " << usage.ru_nvcsw << "\n";
            std::cout << "  Involuntary Context Switches:   " << usage.ru_nivcsw << "\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Benchmark Error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
