#include <cstdint>

enum class WalkStatus : int32_t {
    Success             =  0,  // Операцію виконано успішно
    ErrInvalidArg       = -1,  // Некоректний аргумент
    ErrDisconnected     = -2,  // Граф незв'язний
    ErrPeriodic         = -3,  // Граф дводольний
    ErrDampingRange     = -4,  // Некоректний alpha
    ErrNoMemory         = -5,  // Брак пам'яті
    ErrMaxSteps         = -6   // Перевищено кроки
};
