// sieve.hpp — C++17 Header-only Interface
#ifndef SIEVE_HPP
#define SIEVE_HPP

#include <cstdint>
#include <vector>
#include <string_view>
#include <system_error>
#include <optional>

namespace sieve {

enum class WheelType : std::uint8_t {
    None    = 0,
    Mod2    = 1,
    Mod30   = 2,
    Mod210  = 3
};

struct Configuration {
    std::uint64_t startRange{2};
    std::uint64_t endRange{100'000'000};
    std::uint32_t segmentSizeBytes{0}; // 0 = Auto-detect L1 Cache
    std::uint32_t threads{0};          // 0 = Hardware concurrency
    WheelType     wheel{WheelType::Mod30};
    bool          countOnly{true};
};

struct ExecutionReport {
    std::uint64_t totalPrimes{0};
    double        executionTimeMs{0.0};
    std::size_t   peakMemoryBytes{0};
    std::vector<std::uint64_t> primes;
};

class SieveEngine {
public:
    explicit SieveEngine(Configuration config = {}) : config_(config) {}

    [[nodiscard]] ExecutionReport run() const;

    void setConfig(Configuration config) { config_ = config; }
    [[nodiscard]] const Configuration& config() const noexcept { return config_; }

private:
    Configuration config_;
};

} // namespace sieve

#endif // SIEVE_HPP
