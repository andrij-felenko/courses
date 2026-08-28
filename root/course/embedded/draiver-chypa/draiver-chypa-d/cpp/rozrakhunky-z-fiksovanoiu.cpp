// C++20: Конвертація з фіксованою комою без використання плаваючої точки
template <typename T>
[[nodiscard]] constexpr std::int32_t rawToMilliG(std::int16_t raw_code, Range range) noexcept {
    std::int32_t sensitivity_ug = 61;
    switch (range) {
        case Range::G2:  sensitivity_ug = 61; break;
        case Range::G4:  sensitivity_ug = 122; break;
        case Range::G8:  sensitivity_ug = 244; break;
        case Range::G16: sensitivity_ug = 732; break;
    }

    const auto product = static_cast<std::int64_t>(raw_code) * sensitivity_ug;
    return static_cast<std::int32_t>(product / 1000);
}
