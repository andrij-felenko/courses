// Реалізація мовою C++: матричний клас із підтримкою двовимірних векторів
#include <vector>
#include <cstdint>
#include <stdexcept>

class PrefixSum2D {
private:
    std::vector<std::vector<int64_t>> pref_;
    size_t rows_;
    size_t cols_;

public:
    explicit PrefixSum2D(const std::vector<std::vector<int32_t>>& grid) {
        if (grid.empty() || grid[0].empty()) {
            rows_ = cols_ = 0;
            return;
        }
        rows_ = grid.size();
        cols_ = grid[0].size();
        
        pref_.assign(rows_ + 1, std::vector<int64_t>(cols_ + 1, 0));
        
        for (size_t r = 0; r < rows_; ++r) {
            for (size_t c = 0; c < cols_; ++c) {
                pref_[r + 1][c + 1] = static_cast<int64_t>(grid[r][c])
                                    + pref_[r][c + 1]
                                    + pref_[r + 1][c]
                                    - pref_[r][c];
            }
        }
    }

    [[nodiscard]] int64_t query(size_t r1, size_t c1, size_t r2, size_t c2) const {
        if (r1 > r2 || c1 > c2 || r2 >= rows_ || c2 >= cols_) {
            throw std::out_of_range("Некоректна прямокутна область у PrefixSum2D::query");
        }
        return pref_[r2 + 1][c2 + 1] 
             - pref_[r1][c2 + 1] 
             - pref_[r2 + 1][c1] 
             + pref_[r1][c1];
    }
};
