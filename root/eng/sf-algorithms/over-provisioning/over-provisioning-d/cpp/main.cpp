#include <iostream>
#include <memory>
#include <span>
#include <expected>
#include <string_view>

template <typename T>
class DynamicBufferCPP {
public:
    explicit DynamicBufferCPP(std::size_t initial_capacity = 4)
        : capacity_(initial_capacity > 0 ? initial_capacity : 4),
          data_(std::make_unique<T[]>(capacity_)) {}

    void push_back(const T& value) {
        // 1. Геометричний Over-provisioning x1.5
        if (size_ == capacity_) {
            std::size_t new_capacity = capacity_ + (capacity_ >> 1);
            reallocate(new_capacity);
        }
        data_[size_++] = value;
    }

    std::expected<T, std::string_view> pop_back() {
        if (size_ == 0) {
            return std::unexpected("Buffer is empty");
        }
        T val = std::move(data_[--size_]);

        // 2. Гістерезисне стиснення при заповненій менше 25%
        if (size_ > 0 && size_ <= capacity_ / 4 && capacity_ > 16) {
            reallocate(capacity_ / 2);
        }
        return val;
    }

    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] std::size_t capacity() const noexcept { return capacity_; }
    [[nodiscard]] std::size_t reallocations() const noexcept { return realloc_count_; }
    [[nodiscard]] std::span<const T> view() const noexcept { return {data_.get(), size_}; }

private:
    void reallocate(std::size_t new_capacity) {
        auto new_data = std::make_unique<T[]>(new_capacity);
        for (std::size_t i = 0; i < size_; ++i) {
            new_data[i] = std::move(data_[i]);
        }
        data_ = std::move(new_data);
        capacity_ = new_capacity;
        realloc_count_++;
    }

    std::size_t size_{0};
    std::size_t capacity_{4};
    std::size_t realloc_count_{0};
    std::unique_ptr<T[]> data_;
};
