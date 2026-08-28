// C++ API: tree_complexity.hpp
#ifndef TREE_COMPLEXITY_HPP
#define TREE_COMPLEXITY_HPP

#include <vector>
#include <string>
#include <span_view.hpp>
#include <expected>
#include <chrono>
#include <cstdint>

namespace complexity {

enum class ErrorCode {
    InvalidNumVars,
    NullPointer,
    InvalidTableSize,
    OutOfMemory,
    Timeout
};

struct AnalysisOptions {
    bool calc_sensitivity{true};
    bool calc_block_sensitivity{true};
    bool calc_certificate{true};
    bool calc_degree{true};
    bool calc_decision_tree{true};
    std::chrono::milliseconds timeout{5000};
};

struct AnalysisReport {
    size_t num_variables{0};
    size_t sensitivity{0};
    size_t block_sensitivity{0};
    size_t cert_0{0};
    size_t cert_1{0};
    size_t cert_total{0};
    size_t degree{0};
    size_t decision_tree_depth{0};
    std::chrono::microseconds elapsed_time{0};

    [[nodiscard]] std::string to_json() const;
};

class BooleanAnalyzer {
public:
    explicit BooleanAnalyzer(size_t num_vars, std::span<const uint8_t> truth_table);

    [[nodiscard]] std::expected<AnalysisReport, ErrorCode> analyze(
        const AnalysisOptions& opts = {}
    ) const noexcept;
};

} // namespace complexity

#endif // TREE_COMPLEXITY_HPP
