#include <sys/mman.h>
#include <sys/resource.h>
#include <unistd.h>
#include <chrono>
#include <iostream>
#include <iomanip>
#include <string_view>
#include <system_error>

constexpr std::size_t BenchTotalBytes = 1024ULL * 1024ULL * 1024ULL;

struct BenchmarkResult {
    std::string_view name;
    double wall_time_sec{0.0};
    double user_cpu_sec{0.0};
    double sys_cpu_sec{0.0};
    long voluntary_ctxt_switches{0};
    long involuntary_ctxt_switches{0};
    double throughput_gbps{0.0};
};

class FileDescriptor {
public:
    explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
    ~FileDescriptor() noexcept {
        if (fd_ >= 0) ::close(fd_);
    }
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;
    [[nodiscard]] int get() const noexcept { return fd_; }

private:
    int fd_{-1};
};

void print_benchmark_table(const std::vector<BenchmarkResult>& results) {
    std::cout << std::left << std::setw(22) << "Стратегія"
              << std::right << std::setw(12) << "Wall (с)"
              << std::setw(12) << "Sys CPU (с)"
              << std::setw(14) << "Ctx Switches"
              << std::setw(14) << "Throughput\n";
    std::cout << std::string(74, '-') << "\n";

    for (const auto& r : results) {
        std::cout << std::left << std::setw(22) << r.name
                  << std::right << std::fixed << std::setprecision(3)
                  << std::setw(12) << r.wall_time_sec
                  << std::setw(12) << r.sys_cpu_sec
                  << std::setw(14) << (r.voluntary_ctxt_switches + r.involuntary_ctxt_switches)
                  << std::setprecision(2)
                  << std::setw(10) << r.throughput_gbps << " GB/s\n";
    }
}
