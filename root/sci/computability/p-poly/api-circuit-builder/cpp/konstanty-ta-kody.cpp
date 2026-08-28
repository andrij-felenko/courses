#include <cstdint>

namespace p_poly {

/**
 * @brief Перелічуваний тип помилок оцінювача P/poly (C++ API)
 */
enum class Status : int32_t {
    Ok                  =  0,  // Успішне виконання
    ErrNullPtr          = -1,  // Передано нулевий вказівник
    ErrInvalidCircuit   = -2,  // Некоректна топологія DAG
    ErrInputMismatch    = -3,  // Невідповідність довжини входу |x| != n
    ErrAdviceMismatch   = -4,  // Перевищення ліміту підказки
    ErrOutOfMemory      = -5   // Нестача пам'яті
};

} // namespace p_poly
