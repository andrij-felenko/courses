#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <expected>
#include <system_error>
#include <format>
#include <fcntl.h>
#include <unistd.h>

class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_{fd} {}
    ~UniqueFd() noexcept { if (fd_ >= 0) ::close(fd_); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_{other.fd_} { other.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

private:
    int fd_{-1};
};

struct EnergySample {
    double duration_seconds{0.0};
    double package_joules{0.0};
    double core_joules{0.0};
    double dram_joules{0.0};

    [[nodiscard]] double package_power_watts() const noexcept {
        return (duration_seconds > 0.0) ? (package_joules / duration_seconds) : 0.0;
    }
    [[nodiscard]] double core_power_watts() const noexcept {
        return (duration_seconds > 0.0) ? (core_joules / duration_seconds) : 0.0;
    }
    [[nodiscard]] double dram_power_watts() const noexcept {
        return (duration_seconds > 0.0) ? (dram_joules / duration_seconds) : 0.0;
    }
};

class ScopedEnergyProfiler {
public:
    static std::expected<ScopedEnergyProfiler, std::error_code> create() {
        ScopedEnergyProfiler profiler;
        profiler.fd_pkg_ = open_sensor("/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj");
        if (!profiler.fd_pkg_.valid()) {
            return std::unexpected(std::make_error_code(std::errc::permission_denied));
        }
        profiler.fd_core_ = open_sensor("/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0/energy_uj");
        profiler.fd_dram_ = open_sensor("/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:2/energy_uj");

        profiler.start_pkg_uj_ = profiler.read_energy(profiler.fd_pkg_);
        profiler.start_core_uj_ = profiler.read_energy(profiler.fd_core_);
        profiler.start_dram_uj_ = profiler.read_energy(profiler.fd_dram_);
        profiler.start_time_ = std::chrono::steady_clock::now();

        return profiler;
    }

    [[nodiscard]] EnergySample finish() const {
        const auto end_time = std::chrono::steady_clock::now();
        const std::chrono::duration<double> diff = end_time - start_time_;

        const uint64_t end_pkg = read_energy(fd_pkg_);
        const uint64_t end_core = read_energy(fd_core_);
        const uint64_t end_dram = read_energy(fd_dram_);

        const uint64_t d_pkg = (end_pkg >= start_pkg_uj_) ? (end_pkg - start_pkg_uj_) : 0;
        const uint64_t d_core = (end_core >= start_core_uj_) ? (end_core - start_core_uj_) : 0;
        const uint64_t d_dram = (end_dram >= start_dram_uj_) ? (end_dram - start_dram_uj_) : 0;

        return EnergySample{
            .duration_seconds = diff.count(),
            .package_joules = static_cast<double>(d_pkg) / 1e6,
            .core_joules = static_cast<double>(d_core) / 1e6,
            .dram_joules = static_cast<double>(d_dram) / 1e6
        };
    }

private:
    ScopedEnergyProfiler() = default;

    static UniqueFd open_sensor(std::string_view path) {
        int fd = ::open(path.data(), O_RDONLY);
        return UniqueFd(fd);
    }

    static uint64_t read_energy(const UniqueFd& fd) {
        if (!fd.valid()) return 0;
        char buf[32];
        ssize_t bytes = ::pread(fd.get(), buf, sizeof(buf) - 1, 0);
        if (bytes <= 0) return 0;
        buf[bytes] = '\0';
        return std::stoull(buf);
    }

    UniqueFd fd_pkg_;
    UniqueFd fd_core_;
    UniqueFd fd_dram_;
    uint64_t start_pkg_uj_{0};
    uint64_t start_core_uj_{0};
    uint64_t start_dram_uj_{0};
    std::chrono::steady_clock::time_point start_time_;
};

void run_vector_computation(std::vector<double>& data) {
    for (size_t iter = 0; iter < 100; ++iter) {
        for (double& val : data) {
            val = (val * 1.00001) + 0.5;
        }
    }
}

int main() {
    auto profiler_exp = ScopedEnergyProfiler::create();
    if (!profiler_exp.has_value()) {
        std::cerr << "Помилка ініціалізації RAPL: переконайтеся у наявності прав root.\n";
        return 1;
    }

    std::vector<double> benchmark_data(20'000'000, 1.25);
    std::cout << "Запуск обчислень для профілювання енергії (C++20)...\n";

    const auto& profiler = profiler_exp.value();
    run_vector_computation(benchmark_data);
    const auto result = profiler.finish();

    std::cout << "\n=== Енергетичний звіт (C++ RAII Profiler) ===\n";
    std::cout << std::format("Час виконання:      {:.4f} с\n", result.duration_seconds);
    std::cout << std::format("Енергія Package:    {:.4f} Дж  (Потужність: {:.2f} Вт)\n", 
                             result.package_joules, result.package_power_watts());
    std::cout << std::format("Енергія Cores:      {:.4f} Дж  (Потужність: {:.2f} Вт)\n", 
                             result.core_joules, result.core_power_watts());
    if (result.dram_joules > 0.0) {
        std::cout << std::format("Енергія DRAM:       {:.4f} Дж  (Потужність: {:.2f} Вт)\n", 
                                 result.dram_joules, result.dram_power_watts());
    }

    return 0;
}
