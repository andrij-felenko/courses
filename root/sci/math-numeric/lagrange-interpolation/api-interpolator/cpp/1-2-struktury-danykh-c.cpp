/**
 * @brief Перелічувальний тип статусів виконання операцій у C++20 API.
 */
enum class InterpStatus : int32_t {
    Success             =  0,  ///< Операцію виконано успішно
    ErrNullPointer      = -1,  ///< Передано нульовий вказівник
    ErrInvalidSize      = -2,  ///< Некоректний розмір масиву
    ErrDuplicateNode    = -3,  ///< Знайдено однакові x-вузли
    ErrAllocFailed      = -4,  ///< Помилка виділення пам'яті
    ErrOutOfBounds     = -5,  ///< Точка x виходить за межі інтервалу
    ErrSingularModulo   = -6   ///< Нульовий або складний модуль u
};

/**
 * @brief Внутрішній стан барицентричного інтерполятора у C++20.
 */
struct BarycentricInterpState {
    std::vector<double> x_nodes;  ///< Контейнер вузлів x_k
    std::vector<double> y_nodes;  ///< Контейнер значень y_k
    std::vector<double> weights;  ///< Попередньо обчислені ваги w_k
    double              eps{1e-12};
    bool                is_ready{false};
};

/**
 * @brief Внутрішній стан криптографічного інтерполятора GF(p) у C++20.
 */
struct GFInterpState {
    std::vector<int64_t> x_shares;  ///< Контейнер x-координат часток
    std::vector<int64_t> y_shares;  ///< Контейнер y-координат часток
    int64_t              prime_mod;  ///< Просте число p (модуль поля)
};
