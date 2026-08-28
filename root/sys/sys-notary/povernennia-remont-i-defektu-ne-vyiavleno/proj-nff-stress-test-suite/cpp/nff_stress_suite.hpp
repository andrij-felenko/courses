/* nff_stress_suite.hpp - C++20 об'єктно-орієнтований стрес-комплекс */
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <string_view>
#include <expected>
#include <algorithm>
#include <numeric>
#include <bit>

namespace notary::stress {

enum class PatternType : uint8_t {
    Checkerboard = 0,
    WalkingOnes,
    WalkingZeros,
    BusInversion,
    Prbs31Random,
    Count
};

struct ErrorLogEntry {
    uint32_t timestamp_ms{0};
    uint32_t memory_offset{0};
    uint32_t expected_val{0};
    uint32_t actual_val{0};
    uint32_t xor_diff{0};
    PatternType pattern{PatternType::Checkerboard};

    [[nodiscard]] constexpr uint32_t flipped_bits_count() const noexcept {
        return static_cast<uint32_t>(std::popcount(xor_diff));
    }
};

struct StressStats {
    uint64_t total_cycles{0};
    uint64_t total_words_tested{0};
    uint32_t error_count{0};
    uint32_t stuck_at_ones{0};
    uint32_t stuck_at_zeros{0};
    uint32_t bridge_faults{0};
    uint32_t duration_ms{0};
    bool is_aborted{false};
};

enum class SuiteError {
    BufferTooSmall,
    ExecutionTimeout,
    CriticalMemoryFailure
};

template <size_t BufferSizeBytes = 16 * 1024, size_t MaxLogs = 32>
class StressSuite {
public:
    static constexpr size_t WordCount = BufferSizeBytes / sizeof(uint32_t);

    constexpr StressSuite() noexcept {
        reset();
    }

    void reset() noexcept {
        std::fill(buffer_.begin(), buffer_.end(), 0U);
        stats_ = {};
        log_count_ = 0;
        prbs_state_ = 0x55AA55AAU;
    }

    bool run_iteration(uint32_t current_time_ms) noexcept;
    
    [[nodiscard]] const StressStats& get_stats() const noexcept { return stats_; }
    [[nodiscard]] std::span<const ErrorLogEntry> get_logs() const noexcept {
        return std::span<const ErrorLogEntry>(error_logs_.data(), log_count_);
    }

    void print_summary_report(std::span<char> out_report) const noexcept;

private:
    void execute_pattern_test(PatternType type, uint32_t current_time_ms) noexcept;
    void log_fault(uint32_t offset, uint32_t expected, uint32_t actual,
                   PatternType pattern, uint32_t time_ms) noexcept;
    uint32_t next_prbs31() noexcept;

    std::array<uint32_t, WordCount> buffer_{};
    std::array<ErrorLogEntry, MaxLogs> error_logs_{};
    size_t log_count_{0};
    StressStats stats_{};
    uint32_t prbs_state_{0x55AA55AAU};
};

} // namespace notary::stress
