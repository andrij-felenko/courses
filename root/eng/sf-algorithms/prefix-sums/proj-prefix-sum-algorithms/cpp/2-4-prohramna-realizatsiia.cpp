// Реалізація мовою C++: клас із підтримкою ланцюгових викликів (Fluent API)
#include <vector>
#include <span>
#include <cstdint>
#include <stdexcept>

class DifferenceArray1D {
private:
    std::vector<int64_t> diff_;
    size_t size_;

public:
    explicit DifferenceArray1D(size_t size) 
        : diff_(size + 1, 0), size_(size) {}

    explicit DifferenceArray1D(std::span<const int32_t> init_data) 
        : diff_(init_data.size() + 1, 0), size_(init_data.size()) {
        if (!init_data.empty()) {
            diff_[0] = init_data[0];
            for (size_t i = 1; i < init_data.size(); ++i) {
                diff_[i] = static_cast<int64_t>(init_data[i]) - init_data[i - 1];
            }
        }
    }

    // Додавання на відрізку [l, r] за O(1)
    DifferenceArray1D& add_range(size_t l, size_t r, int64_t val) {
        if (l > r || r >= size_) {
            throw std::out_of_range("Некоректний відрізок у DifferenceArray1D::add_range");
        }
        diff_[l] += val;
        diff_[r + 1] -= val;
        return *this;
    }

    // Відновлення підсумкового масиву префіксними сумами за O(N)
    [[nodiscard]] std::vector<int64_t> build() const {
        std::vector<int64_t> result(size_);
        int64_t current = 0;
        for (size_t i = 0; i < size_; ++i) {
            current += diff_[i];
            result[i] = current;
        }
        return result;
    }
};
