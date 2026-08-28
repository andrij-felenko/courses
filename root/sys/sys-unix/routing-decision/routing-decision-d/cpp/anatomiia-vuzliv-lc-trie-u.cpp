#include <cstdint>
#include <variant>
#include <vector>

// Структурне представлення вузла LC-Trie мовою C++ з використанням std::variant
namespace net::kernel_sim {
    struct KeyVector {
        std::uint32_t key{0};  /* Префікс адреси */
        std::uint8_t  pos{0};  /* Позиція аналізованого біта (0..31) */
        std::uint8_t  bits{0}; /* Кількість біт у рівні (stride k) */
        std::uint8_t  slen{0}; /* Максимальна довжина суфіксу */

        std::variant<std::vector<KeyVector*>, void*> node_data;
    };
}
