namespace std {
    // Неволодіючий спостерігач стану скасування
    class stop_token;

    // Володіюче джерело ініціації сигналу скасування
    class stop_source;

    // RAII-підписка на подію скасування
    template<class Callback>
    class stop_callback;

    // Теговий тип і константа для створення без спільного стану
    struct nostopstate_t { explicit nostopstate_t() = default; };
    inline constexpr nostopstate_t nostopstate{};
}
