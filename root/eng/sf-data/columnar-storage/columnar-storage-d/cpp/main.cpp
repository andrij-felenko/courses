#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>

namespace columnar {

constexpr size_t VECTOR_LEN = 1024;

/* Ідіоматична векторизована фільтрація на сучасному C++20 з використанням std::span */
size_t filter_vector(std::span<const int32_t> column, 
                     int32_t threshold, 
                     std::span<uint16_t> sel_vector) noexcept {
    size_t matches = 0;
    const size_t count = column.size();
    
    for (size_t i = 0; i < count; ++i) {
        const bool pass = (column[i] > threshold);
        sel_vector[matches] = static_cast<uint16_t>(i);
        matches += pass ? 1 : 0;
    }
    
    return matches;
}

} // namespace columnar
