#pragma once

#include <cstdint>
#include <random>
#include <span>

#include "constant_time.hpp"

namespace ct {

/// Як приймач звіряє тег кадру.
enum class CompareMode : std::uint8_t {
    Naive,         ///< memcmp: вихід на першому незбігу
    ConstantTime,  ///< ct::verify: завжди всі kTagLen байтів
};

/// Те, що нападник дістає з одного кадру: двійкову відповідь і час.
struct Reply {
    bool accepted{false};
    std::uint32_t cost{0};  ///< «час» відповіді в умовних одиницях
};

/// Приймач очима нападника.
///
/// На стенді нападник міряє час осцилографом по лінії живлення; тут час
/// моделює кількість фактично зчитаних байтів тегу — рівно та величина,
/// яка витікає з наївного порівняння. Джитер додано навмисно: чистих
/// вимірювань на живому залізі не буває.
class TimingOracle {
public:
    TimingOracle(const Tag& secret, CompareMode mode, std::uint32_t seed);

    [[nodiscard]] Reply ask(std::span<const std::uint8_t> guess);

    [[nodiscard]] std::uint64_t queries() const noexcept { return queries_; }

private:
    [[nodiscard]] std::size_t bytes_read_naively(std::span<const std::uint8_t> guess) const noexcept;

    Secret secret_;
    CompareMode mode_;
    std::uint64_t queries_{0};
    std::mt19937 jitter_;
    std::uniform_int_distribution<std::uint32_t> spread_{0, 32};
};

}  // namespace ct
