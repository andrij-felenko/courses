namespace wieferich {

struct config {
    std::uint64_t       start_range{3};    // Початкове значення діапазону p
    std::uint64_t       end_range{1000000};// Кінцеве значення діапазону p
    std::uint64_t       base{2};           // Основа піднесення до степеня
    std::uint32_t       num_threads{0};    // Кількість робочих потоків (0 = auto)
    bool                use_montgomery{true}; // Арифметика Монтгомері
    bool                verbose{false};    // Детальний вивід прогресу
};

} // namespace wieferich
