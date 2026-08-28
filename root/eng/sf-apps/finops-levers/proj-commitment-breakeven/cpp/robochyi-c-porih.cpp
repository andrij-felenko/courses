#include <cstdint>

// Усі ставки — у мілідоларах за годину (1 $ = 1000).
// Гроші — у мілідоларах. Цілі, щоб не тягнути float у рахунок.

// ── Рахунок за період на РОЗДРІБІ: платимо лише за ввімкнені години ──────
// used_hours — реально ввімкнені години за період.
std::uint64_t retail_cost_md(std::uint32_t retail_md_per_h, std::uint32_t used_hours)
{
    return static_cast<std::uint64_t>(retail_md_per_h) * used_hours;
}

// ── Рахунок за період на ОБІЦЯНЦІ: платимо за ВСІ години строку ──────────
// period_hours — усього годин у періоді (місяць ≈ 720), байдуже до завантаження.
std::uint64_t committed_cost_md(std::uint32_t committed_md_per_h, std::uint32_t period_hours)
{
    return static_cast<std::uint64_t>(committed_md_per_h) * period_hours;
}
