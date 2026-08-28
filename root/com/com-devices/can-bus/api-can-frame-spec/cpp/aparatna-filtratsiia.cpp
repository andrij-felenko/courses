// C++: Структура фільтра з методикою конструювання
#include <cstdint>

namespace can {

struct Filter {
    std::uint32_t id{0};   // Цільовий ID
    std::uint32_t mask{0}; // Маска перевірки бітів

    [[nodiscard]] constexpr bool matches(std::uint32_t input_id) const noexcept {
        return (input_id & mask) == (id & mask);
    }
};

} // namespace can
