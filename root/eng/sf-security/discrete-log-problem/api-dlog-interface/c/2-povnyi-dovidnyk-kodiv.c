typedef enum {
    DLOG_SUCCESS             = 0,   // Логарифм успішно знайдено
    DLOG_NOT_FOUND           = 1,   // Логарифм не існує у вказаній групі або діапазоні
    DLOG_INVALID_PARAM       = 2,   // Некоректні вхідні аргументи (p <= 2, g = 0, y >= p)
    DLOG_OUT_OF_MEMORY       = 3,   // Недостатньо пам'яті для виділення хеш-таблиці BSGS
    DLOG_TIMEOUT             = 4,   // Перевищено встановлений ліміт часу виконання
    DLOG_MAX_STEPS_EXCEEDED  = 5,   // Перевищено максимальну кількість кроків алгоритму
    DLOG_COLLISION_FAILED    = 6,   // Непридатна колізія в Pollard Rho (НСД(Δb, N) > 1)
    DLOG_COMPUTE_ERROR       = 7,   // Арифметичне переповнення або ділення на нуль
    DLOG_NOT_IMPLEMENTED     = 99   // Метод не підтримується для даної конфігурації
} dlog_status_t;
