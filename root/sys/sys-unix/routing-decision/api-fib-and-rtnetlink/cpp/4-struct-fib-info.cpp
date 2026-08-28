#include <cstdint>
#include <atomic>
#include <vector>

// Запис fib_info у C++ з використанням std::atomic та std::vector для next-hop структур
namespace net::kernel_sim {
    struct FibInfo {
        std::atomic<std::int32_t> treeref{0};  /* Атомарний лічильник посилань від дерев */
        std::atomic<std::int32_t> clntref{0};  /* Атомарний лічильник посилань від сокетів */
        std::uint32_t             metrics{0};  /* Метрики (MTU, rtt, window) */
        std::uint32_t             priority{0}; /* Метрика/пріоритет (RTA_PRIORITY) */
        std::uint32_t             prefsrc{0};  /* Preferred Source IP */
        std::uint32_t             flags{0};    /* Прапорці */
        std::uint8_t              protocol{0}; /* Протокол джерела */
        std::vector<std::uint32_t> nexthops;   /* Масив індексів nexthop */
    };
}
