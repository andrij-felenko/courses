#include <vector>
#include <bit>
#include <optional>
#include <cstdint>
#include <algorithm>

class SparseTable2D {
public:
    SparseTable2D(const std::vector<std::vector<int32_t>>& matrix) {
        if (matrix.empty() || matrix[0].empty()) return;
        rows_ = matrix.size();
        cols_ = matrix[0].size();
        kx_ = std::bit_width(rows_);
        ky_ = std::bit_width(cols_);

        table_.assign(kx_ * ky_ * rows_ * cols_, 0);

        for (std::size_t x = 0; x < rows_; ++x) {
            for (std::size_t y = 0; y < cols_; ++y) {
                table_[idx(0, 0, x, y)] = matrix[x][y];
            }
        }

        for (std::size_t jy = 1; jy < ky_; ++jy) {
            std::size_t half_y = std::size_t{1} << (jy - 1);
            for (std::size_t x = 0; x < rows_; ++x) {
                for (std::size_t y = 0; y + (std::size_t{1} << jy) <= cols_; ++y) {
                    table_[idx(0, jy, x, y)] = std::min(
                        table_[idx(0, jy - 1, x, y)],
                        table_[idx(0, jy - 1, x, y + half_y)]
                    );
                }
            }
        }

        for (std::size_t jx = 1; jx < kx_; ++jx) {
            std::size_t half_x = std::size_t{1} << (jx - 1);
            for (std::size_t jy = 0; jy < ky_; ++jy) {
                for (std::size_t x = 0; x + (std::size_t{1} << jx) <= rows_; ++x) {
                    for (std::size_t y = 0; y < cols_; ++y) {
                        table_[idx(jx, jy, x, y)] = std::min(
                            table_[idx(jx - 1, jy, x, y)],
                            table_[idx(jx - 1, jy, x + half_x, y)]
                        );
                    }
                }
            }
        }
    }

    [[nodiscard]] std::optional<int32_t> query(std::size_t x1, std::size_t y1, 
                                               std::size_t x2, std::size_t y2) const noexcept {
        if (rows_ == 0 || cols_ == 0 || x1 > x2 || y1 > y2 || x2 >= rows_ || y2 >= cols_) {
            return std::nullopt;
        }

        std::size_t kx = std::bit_width(x2 - x1 + 1) - 1;
        std::size_t ky = std::bit_width(y2 - y1 + 1) - 1;

        std::size_t shift_x = std::size_t{1} << kx;
        std::size_t shift_y = std::size_t{1} << ky;

        int32_t q1 = table_[idx(kx, ky, x1, y1)];
        int32_t q2 = table_[idx(kx, ky, x2 - shift_x + 1, y1)];
        int32_t q3 = table_[idx(kx, ky, x1, y2 - shift_y + 1)];
        int32_t q4 = table_[idx(kx, ky, x2 - shift_x + 1, y2 - shift_y + 1)];

        return std::min({q1, q2, q3, q4});
    }

private:
    [[nodiscard]] inline std::size_t idx(std::size_t jx, std::size_t jy, 
                                         std::size_t x, std::size_t y) const noexcept {
        return (((jx * ky_ + jy) * rows_ + x) * cols_ + y);
    }

    std::size_t rows_{0};
    std::size_t cols_{0};
    std::size_t kx_{0};
    std::size_t ky_{0};
    std::vector<int32_t> table_;
};
