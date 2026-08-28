#include <vector>
#include <cstdint>
#include <span>

struct ColumnVector {
    std::vector<int32_t> data;
    std::vector<uint8_t> null_mask; /* 1 = IS NULL, 0 = VALID */
};

/* Ідіоматична C++ векторизована фільтрація 3VL */
void filter_vector_3vl_cpp(std::span<const int32_t> data, 
                           std::span<const uint8_t> null_mask,
                           std::span<uint8_t> out_val,
                           std::span<uint8_t> out_is_null) noexcept {
    const size_t n = data.size();
    for (size_t i = 0; i < n; ++i) {
        if (null_mask[i] != 0) {
            out_is_null[i] = 1; /* UNKNOWN */
            out_val[i] = 0;
        } else {
            out_is_null[i] = 0; /* Чітке булеве значення */
            out_val[i] = (data[i] > 100) ? 1 : 0;
        }
    }
}
