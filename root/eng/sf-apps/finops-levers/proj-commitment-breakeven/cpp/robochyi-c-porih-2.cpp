// ── Поріг завантаження В ГОДИНАХ: скільки годин/період машина має ────────
// пропрацювати, щоб обіцянка зрівнялася з роздробом.
//   рівність:  retail·H_used = committed·H_period
//     →  H_used = committed·H_period / retail
std::uint32_t breakeven_hours(std::uint32_t committed_md_per_h,
                              std::uint32_t retail_md_per_h,
                              std::uint32_t period_hours)
{
    // множимо ДО ділення — інакше цілочислове ділення занулить результат
    std::uint64_t num = static_cast<std::uint64_t>(committed_md_per_h) * period_hours;
    return static_cast<std::uint32_t>(num / retail_md_per_h);
}

// ── Порада: чи варто обіцянка при очікуваному завантаженні? ──────────────
// expected_used — скільки годин/період машина реально працюватиме.
bool commitment_pays(std::uint32_t committed_md_per_h, std::uint32_t retail_md_per_h,
                     std::uint32_t period_hours, std::uint32_t expected_used)
{
    return expected_used >= breakeven_hours(committed_md_per_h,
                                            retail_md_per_h, period_hours);
}
