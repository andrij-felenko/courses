#include <cstdint>

namespace ribbon {

enum class Status : std::int32_t {
    Ok                     =  0,  // Успішне завершення операції
    InvalidArgument        = -1,  // Некоректні вхідні аргументи
    UnresolvableSystem     = -2,  // Не вдалося розв'язати систему лінійних рівнянь
    OutOfMemory            = -3,  // Недостатньо оперативної пам'яті
    BufferTooSmall         = -4,  // Наданий буфер замалий для серіалізації
    CorruptedData          = -5,  // Пошкодження магічного числа або заголовка
    UnsupportedVersion     = -6   // Непідтримувана версія формату
};

} // namespace ribbon
