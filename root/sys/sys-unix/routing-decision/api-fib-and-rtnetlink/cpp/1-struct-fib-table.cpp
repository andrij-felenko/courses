#include <cstdint>

// Моделювання таблиці FIB у C++ з використанням C++17/20 типів
namespace net::kernel_sim {
    struct FibTable {
        std::uint32_t id{254};         /* Numeric Table ID (254 = MAIN, 255 = LOCAL) */
        std::int32_t  num_default{0};  /* Кількість дефолтних маршрутів у таблиці */
        uintptr_t     trie_ptr{0};     /* Вказівник на корінь дерева LC-Trie */
    };
}
