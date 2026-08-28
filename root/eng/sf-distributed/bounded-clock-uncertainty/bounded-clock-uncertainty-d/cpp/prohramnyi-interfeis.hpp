namespace truetime {

struct Interval {
    std::int64_t earliest{0}; /* Найраніший момент фізичного часу */
    std::int64_t latest{0};   /* Найпізніший момент фізичного часу */
};

/* 1. Повертає поточний довірчий інтервал часу */
[[nodiscard]] Interval now();

/* 2. Перевіряє, чи момент t гарантовано минув у фізичному часі */
[[nodiscard]] bool after(std::int64_t t);

/* 3. Перевіряє, чи момент t гарантовано ще не настав */
[[nodiscard]] bool before(std::int64_t t);

} // namespace truetime
