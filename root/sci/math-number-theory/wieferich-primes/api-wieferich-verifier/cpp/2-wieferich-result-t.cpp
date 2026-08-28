namespace wieferich {

struct result {
    std::uint64_t       prime{0};          // Перевірене просте число p
    std::uint64_t       base{2};           // Основа порівняння a
    std::uint64_t       remainder{0};      // Остачка (a^(p-1) mod p²)
    std::uint64_t       fermat_quotient{0};// Частка Віферіха
    bool                is_wieferich{false}; // Прапорець Віферіха
    double              execution_time{0.0}; // Час виконання в мікросекундах
};

} // namespace wieferich
