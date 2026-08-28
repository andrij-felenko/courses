// Ручка компромісу — рівно один рядок: CAP.
// Малий CAP: мало RAM, але швидко переповнюється на сплеску.
// Великий CAP: переживе сплеск, але з'їсть пам'ять, якої мало.
static constexpr std::size_t CAP = 64;   // ← ця константа і є точкою компромісу

static std::array<std::uint16_t, CAP> buf;
static std::uint8_t head = 0, count = 0;

// Повертає false, якщо буфер повний — зразок втрачено (ціна малого CAP).
bool push_sample(std::uint16_t v) {
    if (count == CAP) return false;      // переповнення: платимо втратою даних
    buf[(head + count) % CAP] = v;
    count++;
    return true;
}
