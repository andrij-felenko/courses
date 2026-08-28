#include <cstdint>

enum class TwistStatus : std::uint32_t {
    kSuccess          = 0x00, // Операцію виконано успішно
    kNullPointer      = 0x01, // Передано порожній вказівник
    kInvalidX         = 0x02, // Координата x не належить полю 𝔽_{p^2}
    kNotOnCurve       = 0x03, // Точка не задовольняє рівняння E'
    kSubgroupFailed   = 0x04, // Перевірка порядку r * Q' != O провалилася
    kInvalidFlags     = 0x05, // Неприпустима комбінація прапорців
    kDecompressFailed = 0x06  // Корінь для y' не існує в 𝔽_{p^2}
};
