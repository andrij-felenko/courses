#include <iostream>
#include <vector>
#include <cstdint>
#include <optional>
#include <variant>
#include <span>
#include <cstring>

enum class ColumnType {
    Int32,
    Float64
};

struct TableSchema {
    std::vector<ColumnType> types;
};

/* Ідіоматичний C++ кортеж із RAII-управлінням пам'яттю */
class Tuple {
public:
    Tuple() : null_bitmap_(0) {}

    void set_null(uint16_t col_idx) noexcept {
        null_bitmap_ &= ~(1U << col_idx);
    }

    void set_int32(uint16_t col_idx, int32_t val) {
        null_bitmap_ |= (1U << col_idx);
        const auto* src = reinterpret_cast<const uint8_t*>(&val);
        payload_.insert(payload_.end(), src, src + sizeof(int32_t));
    }

    [[nodiscard]] bool is_null(uint16_t col_idx) const noexcept {
        return !(null_bitmap_ & (1U << col_idx));
    }

    [[nodiscard]] std::optional<int32_t> get_int32(uint16_t col_idx, const TableSchema& schema) const noexcept {
        if (is_null(col_idx)) {
            return std::nullopt;
        }

        size_t offset = 0;
        for (uint16_t i = 0; i < col_idx; ++i) {
            if (!is_null(i)) {
                if (schema.types[i] == ColumnType::Int32) offset += sizeof(int32_t);
                else if (schema.types[i] == ColumnType::Float64) offset += sizeof(double);
            }
        }

        int32_t result = 0;
        std::memcpy(&result, payload_.data() + offset, sizeof(int32_t));
        return result;
    }

private:
    uint32_t null_bitmap_{0}; /* 1 = NOT NULL, 0 = IS NULL */
    std::vector<uint8_t> payload_;
};
