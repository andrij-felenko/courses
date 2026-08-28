#include <cstddef>
#include <cstdint>
#include <optional>
#include <string_view>

enum class CuckooStatus : int32_t {
    Ok             =  0,  // Операція успішна
    NotFound       = -1,  // Ключ не знайдено
    KeyExists      = -2,  // Ключ уже присутній
    NoMemory       = -3,  // Недостатньо пам'яті
    RehashFailed   = -4,  // Помилка перехешування
    StashUsed      =  1   // Використано схованку
};

struct CuckooStats {
    std::size_t total_elements{0};
    std::size_t table_capacity{0};
    std::size_t stash_count{0};
    std::size_t rehash_count{0};
    double load_factor{0.0};
};
