namespace natural {
struct Config {
    uint32_t num_variables{4};         // Кількість булевих змінних n (від 1 до 20)
    double largeness_threshold{0.01};  // Поріг великості delta (від 0.0001 до 1.0)
    uint64_t max_time_us{1000000};     // Ліміт часу конструктивності T(N) у мікросекундах
    bool enable_walsh_transform{true}; // Прапорець обчислення спектру Уолша-Адамара
    bool enable_algebraic_degree{true};// Прапорець обчислення степеня полінома Жегалкіна
    uint32_t num_monte_carlo{1000};    // Кількість спроб Монте-Карло для оцінки великості
};
}
