namespace wieferich {

enum class status : int32_t {
    success             = 0,  // Успішне завершення операції
    is_prime_wieferich  = 1,  // Число є простим Віферіха: a^(p-1) ≡ 1 (mod p²)
    is_non_wieferich    = 2,  // Число є звичайним простим: a^(p-1) ≢ 1 (mod p²)
    error_not_prime     = -1, // Передане число не є простим
    error_even_number   = -2, // Число є парним
    error_invalid_base  = -3, // Некоректна основа порівняння
    error_out_of_memory = -4, // Помилка виділення пам'яті
    error_invalid_range = -5, // Некоректний діапазон пошуку
    error_null_pointer  = -6  // Некоректний вказівник
};

} // namespace wieferich
