// cpp
#include <cstdint>

enum class IoUringOp : std::uint8_t {
    Send        = 26,   // Стандартне копіювальне відправлення
    Recv        = 27,   // Стандартне копіювальне отримання
    Accept      = 28,   // Прийняття нових TCP-з'єднань
    Connect     = 31,   // Ініціалізація вихідного TCP-з'єднання
    SendZC      = 38,   // Zero-Copy відправлення даних (Linux 6.0+)
    RecvZC      = 52,   // Zero-Copy отримання даних (Linux 6.7+)
    UringCmd    = 46,   // Passthrough команди до сокетів/пристроїв
};
