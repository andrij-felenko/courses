#include "timing_oracle.hpp"

#include <algorithm>
#include <iterator>
#include <ranges>

namespace {

/// Одна зчитана пара байтів коштує стільки умовних одиниць часу.
constexpr std::uint32_t kCostPerByte = 16;

}  // namespace

namespace ct {

TimingOracle::TimingOracle(const Tag& secret, CompareMode mode, std::uint32_t seed)
    : secret_{secret}, mode_{mode}, jitter_{seed}
{
}

std::size_t TimingOracle::bytes_read_naively(std::span<const std::uint8_t> guess) const noexcept
{
    // Рівно семантика memcmp: іде зліва направо й спиняється на першому
    // незбігу. mismatch віддає позицію розходження; байт, на якому воно
    // сталося, приймач теж устиг прочитати — звідси +1.
    const auto secret = secret_.view();
    const auto [it, _] = std::ranges::mismatch(guess, secret);
    const auto prefix = static_cast<std::size_t>(std::ranges::distance(guess.begin(), it));
    return (it == guess.end()) ? prefix : prefix + 1;
}

Reply TimingOracle::ask(std::span<const std::uint8_t> guess)
{
    ++queries_;

    const auto secret = secret_.view();
    bool accepted = false;
    std::size_t read_bytes = 0;

    switch (mode_) {
        case CompareMode::Naive:
            read_bytes = bytes_read_naively(guess);
            accepted = (read_bytes == secret.size()) && (guess.size() == secret.size());
            break;
        case CompareMode::ConstantTime:
            accepted = verify(guess, secret);
            read_bytes = secret.size();  // прочитано все, хоч би де був незбіг
            break;
    }

    const std::uint32_t cost =
        static_cast<std::uint32_t>(read_bytes) * kCostPerByte + spread_(jitter_);
    return Reply{accepted, cost};
}

}  // namespace ct
