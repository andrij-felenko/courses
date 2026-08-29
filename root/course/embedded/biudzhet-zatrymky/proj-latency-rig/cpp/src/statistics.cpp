#include "statistics.hpp"

#include <algorithm>
#include <cstdint>
#include <numeric>

namespace latency {
namespace {

// Перцентиль за методом найближчого рангу: індекс = ceil(p/100 * n) - 1.
// Наївне (n * p) / 100 зсуває оцінку вниз — на 256 зразках P99 показав би
// 253-й елемент замість 254-го, тобто саме той сплеск, заради якого міряють.
board::Microseconds percentile(std::span<const board::Microseconds> sorted,
                               std::size_t p) noexcept
{
    const std::size_t rank = (sorted.size() * p + 99u) / 100u;
    const std::size_t index = std::min(rank == 0u ? 0u : rank - 1u, sorted.size() - 1u);
    return sorted[index];
}

} // namespace

std::optional<Summary> analyse(std::span<board::Microseconds> samples,
                               std::size_t lost) noexcept
{
    if (samples.empty()) {
        return std::nullopt;
    }

    std::sort(samples.begin(), samples.end());

    Summary summary;
    summary.count = samples.size();
    summary.lost  = lost;
    summary.min   = samples.front();
    summary.max   = samples.back();

    // Сума 256 чвертьсекундних інтервалів не влазить у 32 біти — рахуємо в 64.
    const std::uint64_t total = std::accumulate(
        samples.begin(), samples.end(), std::uint64_t{0},
        [](std::uint64_t acc, board::Microseconds v) { return acc + v.count(); });
    summary.mean = board::Microseconds{static_cast<std::uint32_t>(total / samples.size())};

    summary.p50 = percentile(samples, 50);
    summary.p95 = percentile(samples, 95);
    summary.p99 = percentile(samples, 99);

    // Джитер міряємо відносно МЕДІАНИ, а не середнього: одна ретрансмісія на
    // межі дальності тягне середнє за собою, і джитер роздувся б від того
    // самого викиду, який медіана вже відсіяла.
    const std::uint64_t deviation = std::accumulate(
        samples.begin(), samples.end(), std::uint64_t{0},
        [median = summary.p50](std::uint64_t acc, board::Microseconds v) {
            return acc + (v > median ? (v - median).count() : (median - v).count());
        });
    summary.jitter =
        board::Microseconds{static_cast<std::uint32_t>(deviation / samples.size())};

    return summary;
}

} // namespace latency
