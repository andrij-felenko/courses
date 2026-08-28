typedef enum {
    WIEFERICH_SUCCESS             = 0,  // Успішне завершення операції
    WIEFERICH_IS_PRIME_WIEFERICH  = 1,  // Число є простим Віферіха: a^(p-1) ≡ 1 (mod p²)
    WIEFERICH_IS_NON_WIEFERICH    = 2,  // Число є звичайним простим: a^(p-1) ≢ 1 (mod p²)
    WIEFERICH_ERROR_NOT_PRIME     = -1, // Передане число не є простим (композитне)
    WIEFERICH_ERROR_EVEN_NUMBER   = -2, // Число є парним (p = 2 не підтримується)
    WIEFERICH_ERROR_INVALID_BASE  = -3, // Некоректна основа порівняння (a < 2)
    WIEFERICH_ERROR_OUT_OF_MEMORY = -4, // Помилка виділення динамічної пам'яті
    WIEFERICH_ERROR_INVALID_RANGE = -5, // Некоректний діапазон пошуку (start > end)
    WIEFERICH_ERROR_NULL_POINTER  = -6  // Передано нулевий вказівник на обов'язковий буфер
} wieferich_status_t;
