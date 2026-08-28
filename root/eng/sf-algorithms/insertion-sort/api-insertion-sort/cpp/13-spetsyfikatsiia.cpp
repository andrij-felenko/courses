#include <vector>
#include <algorithm>
#include <concepts>

template <typename T, typename Compare = std::less<T>>
class SortedStreamBufferCpp {
public:
    explicit SortedStreamBufferCpp(std::size_t max_capacity, Compare comp = Compare{})
        : capacity_(max_capacity), comp_(comp) {
        data_.reserve(max_capacity);
    }

    bool insert(T val) {
        if (data_.size() >= capacity_) {
            return false;
        }

        // Бінарний пошук точки вставки у відсортованому векторі
        auto pos = std::upper_bound(data_.begin(), data_.end(), val, comp_);
        data_.insert(pos, std::move(val));
        return true;
    }

    [[nodiscard]] std::span<const T> view() const noexcept {
        return data_;
    }

private:
    std::vector<T> data_;
    std::size_t capacity_;
    Compare comp_;
};
