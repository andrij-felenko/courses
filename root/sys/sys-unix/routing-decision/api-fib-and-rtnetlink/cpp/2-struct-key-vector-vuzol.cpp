#include <cstdint>
#include <variant>
#include <vector>

// Представлення вузла LC-Trie у C++ з використанням std::variant та std::vector
namespace net::kernel_sim {
    struct KeyVector {
        std::uint32_t key{0};     /* 32-бітне значення префіксу адреси */
        std::uint8_t  pos{0};     /* Позиція аналізованого біта (0..31) */
        std::uint8_t  bits{0};    /* Кількість біт у рівні (stride size, k = 1..8) */
        std::uint8_t  slen{0};    /* Максимальна довжина суфіксу піддерева */
        
        // Вузол розгалуження містить вектор дочірніх вузлів, а листок — списки маршрутів
        std::variant<std::vector<KeyVector*>, void*> node_data;
    };
}
