#include <memory_resource>

// Використання PMR арени з std::expected
using PmrString = std::pmr::string;

std::expected<PmrString, ConfigError> read_fast(std::pmr::memory_resource* arena) {
    PmrString str(arena);
    str.reserve(1024);
    // Зчитування в локальну арену без викликів глобального new
    return str;
}
