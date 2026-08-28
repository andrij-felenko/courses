// C++: Типізовані бітові константи та enum class
#include <cstdint>

namespace can {

enum class Flag : std::uint32_t {
    Extended  = 0x80000000U, // 29-бітний розширений ID
    Remote    = 0x40000000U, // Запит передачі Remote Frame
    Error     = 0x20000000U  // Повідомлення про помилку шини
};

enum class Mask : std::uint32_t {
    StandardId = 0x000007FFU, // Маска 11-бітного ID
    ExtendedId = 0x1FFFFFFFU, // Маска 29-бітного ID
    ErrorId    = 0x1FFFFFFFU  // Маска коду помилки
};

} // namespace can
