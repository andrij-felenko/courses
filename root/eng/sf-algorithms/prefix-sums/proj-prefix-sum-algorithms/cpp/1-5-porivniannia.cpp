// Реалізація мовою C++: RAII-обгортка з std::vector та std::span
#include <vector>
#include <span>
#include <cstdint>
#include <stdexcept>

class PrefixSum1D {
private:
    std::vector<int64_t> pref_;

public:
    // Конструктор приймає будь-який безперервний контейнер через std::span
    explicit PrefixSum1D(std::span<const int32_t> data) 
        : pref_(data.size() + 1, 0) {
        for (size_t i = 0; i < data.size(); ++i) {
            pref_[i + 1] = pref_[i] + static_cast<int64_t>(data[i]);
        }
    }

    // Повертає суму на відрізку [l, r] включно в 0-індексації за O(1)
    [[nodiscard]] int64_t query(size_t l, size_t r) const {
        if (l > r || r >= pref_.size() - 1) {
            throw std::out_of_range("Некоректні межі відрізка в PrefixSum1D::query");
        }
        return pref_[r + 1] - pref_[l];
    }

    [[nodiscard]] size_t size() const noexcept {
        return pref_.empty() ? 0 : pref_.size() - 1;
    }
};
