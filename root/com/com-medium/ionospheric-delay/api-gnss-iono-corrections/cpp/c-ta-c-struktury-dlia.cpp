#include <vector>
#include <cstdint>
#include <cmath>
#include <cstddef>

namespace gnss::api {

struct IonexHeader {
    double       lat1_deg{-87.5};
    double       lat2_deg{87.5};
    double       dlat_deg{2.5};
    double       lon1_deg{-180.0};
    double       lon2_deg{180.0};
    double       dlon_deg{5.0};
    double       height_km{350.0};
    std::int32_t exponent{-1};
};

class IonexMapGrid {
public:
    IonexMapGrid(std::size_t rows, std::size_t cols, std::int32_t exp_val)
        : num_rows_(rows), num_cols_(cols), exponent_(exp_val), data_(rows * cols, 0) {}

    void setRawValue(std::size_t row, std::size_t col, std::int16_t val) noexcept {
        if (row < num_rows_ && col < num_cols_) {
            data_[row * num_cols_ + col] = val;
        }
    }

    [[nodiscard]] double getVtecTecu(std::size_t row, std::size_t col) const noexcept {
        if (row >= num_rows_ || col >= num_cols_) return 0.0;
        return static_cast<double>(data_[row * num_cols_ + col]) * std::pow(10.0, exponent_);
    }

private:
    std::size_t num_rows_;
    std::size_t num_cols_;
    std::int32_t exponent_;
    std::vector<std::int16_t> data_;
};

} // namespace gnss::api
