/* nff_stress_suite.cpp - C++20 реалізація шаблонних методів стрес-комплексу */
#include "nff_stress_suite.hpp"
#include <cstdio>

namespace notary::stress {

template <size_t BufferSizeBytes, size_t MaxLogs>
uint32_t StressSuite<BufferSizeBytes, MaxLogs>::next_prbs31() noexcept {
    uint32_t b31 = (prbs_state_ >> 30) & 1U;
    uint32_t b28 = (prbs_state_ >> 27) & 1U;
    uint32_t new_bit = b31 ^ b28;
    prbs_state_ = ((prbs_state_ << 1U) | new_bit) & 0x7FFFFFFFU;
    return prbs_state_;
}

template <size_t BufferSizeBytes, size_t MaxLogs>
void StressSuite<BufferSizeBytes, MaxLogs>::log_fault(uint32_t offset, uint32_t expected,
                                                     uint32_t actual, PatternType pattern,
                                                     uint32_t time_ms) noexcept {
    stats_.error_count++;
    uint32_t diff = expected ^ actual;

    if ((actual & diff) == diff) {
        stats_.stuck_at_ones++;
    } else if ((~actual & diff) == diff) {
        stats_.stuck_at_zeros++;
    } else {
        stats_.bridge_faults++;
    }

    if (log_count_ < MaxLogs) {
        error_logs_[log_count_++] = ErrorLogEntry{
            .timestamp_ms = time_ms,
            .memory_offset = offset,
            .expected_val = expected,
            .actual_val = actual,
            .xor_diff = diff,
            .pattern = pattern
        };
    }
}

template <size_t BufferSizeBytes, size_t MaxLogs>
void StressSuite<BufferSizeBytes, MaxLogs>::execute_pattern_test(PatternType type, uint32_t current_time_ms) noexcept {
    switch (type) {
    case PatternType::Checkerboard: {
        constexpr uint32_t p1 = 0x55555555U;
        constexpr uint32_t p2 = 0xAAAAAAAAU;
        for (size_t i = 0; i < WordCount; ++i) {
            buffer_[i] = (i & 1U) ? p1 : p2;
        }
        for (size_t i = 0; i < WordCount; ++i) {
            uint32_t expected = (i & 1U) ? p1 : p2;
            if (buffer_[i] != expected) {
                log_fault(static_cast<uint32_t>(i * 4), expected, buffer_[i], type, current_time_ms);
            }
        }
        stats_.total_words_tested += WordCount;
        break;
    }
    case PatternType::WalkingOnes:
    case PatternType::WalkingZeros: {
        const bool is_zero = (type == PatternType::WalkingZeros);
        for (uint8_t bit = 0; bit < 32; ++bit) {
            const uint32_t val = is_zero ? ~(1U << bit) : (1U << bit);
            std::fill(buffer_.begin(), buffer_.end(), val);
            for (size_t i = 0; i < WordCount; ++i) {
                if (buffer_[i] != val) {
                    log_fault(static_cast<uint32_t>(i * 4), val, buffer_[i], type, current_time_ms);
                }
            }
        }
        stats_.total_words_tested += (WordCount * 32);
        break;
    }
    case PatternType::BusInversion: {
        for (size_t i = 0; i < WordCount; ++i) {
            buffer_[i] = (i & 1U) ? 0x00000000U : 0xFFFFFFFFU;
        }
        for (size_t i = 0; i < WordCount; ++i) {
            uint32_t expected = (i & 1U) ? 0x00000000U : 0xFFFFFFFFU;
            if (buffer_[i] != expected) {
                log_fault(static_cast<uint32_t>(i * 4), expected, buffer_[i], type, current_time_ms);
            }
        }
        stats_.total_words_tested += WordCount;
        break;
    }
    case PatternType::Prbs31Random: {
        uint32_t seed = prbs_state_;
        for (size_t i = 0; i < WordCount; ++i) {
            buffer_[i] = next_prbs31();
        }
        prbs_state_ = seed;
        for (size_t i = 0; i < WordCount; ++i) {
            uint32_t expected = next_prbs31();
            if (buffer_[i] != expected) {
                log_fault(static_cast<uint32_t>(i * 4), expected, buffer_[i], type, current_time_ms);
            }
        }
        stats_.total_words_tested += WordCount;
        break;
    }
    default:
        break;
    }
}

template <size_t BufferSizeBytes, size_t MaxLogs>
bool StressSuite<BufferSizeBytes, MaxLogs>::run_iteration(uint32_t current_time_ms) noexcept {
    execute_pattern_test(PatternType::Checkerboard, current_time_ms);
    execute_pattern_test(PatternType::WalkingOnes, current_time_ms);
    execute_pattern_test(PatternType::WalkingZeros, current_time_ms);
    execute_pattern_test(PatternType::BusInversion, current_time_ms);
    execute_pattern_test(PatternType::Prbs31Random, current_time_ms);

    stats_.total_cycles++;
    return (stats_.error_count == 0);
}

template <size_t BufferSizeBytes, size_t MaxLogs>
void StressSuite<BufferSizeBytes, MaxLogs>::print_summary_report(std::span<char> out_report) const noexcept {
    if (out_report.empty()) return;

    std::snprintf(out_report.data(), out_report.size(),
                  "=== C++20 NFF DIAGNOSTIC REPORT ===\n"
                  "Cycles Completed: %zu\n"
                  "Words Tested:     %zu\n"
                  "Errors Detected:  %u\n"
                  "Stuck at 1 / 0:   %u / %u\n"
                  "Bridge Faults:    %u\n"
                  "Result:           %s\n",
                  stats_.total_cycles,
                  stats_.total_words_tested,
                  stats_.error_count,
                  stats_.stuck_at_ones,
                  stats_.stuck_at_zeros,
                  stats_.bridge_faults,
                  (stats_.error_count == 0) ? "PASS" : "HARDWARE FAULT DETECTED");
}

/* Явна інстанціація типового розміру 16 КБ */
template class StressSuite<16 * 1024, 32>;

} // namespace notary::stress
