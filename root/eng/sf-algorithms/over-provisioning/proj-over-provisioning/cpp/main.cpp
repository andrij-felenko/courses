#include <iostream>
#include <memory>
#include <span>
#include <chrono>
#include <expected>
#include <string_view>

enum class GrowthPolicy {
    Geometric2_0,
    Geometric1_5,
    LinearFixed
};

struct BufferMetrics {
    std::size_t reallocations{0};
    std::size_t total_copies{0};
};

template <typename T>
class OverBuffer {
public:
    explicit OverBuffer(std::size_t initial_capacity = 8,
                        GrowthPolicy policy = GrowthPolicy::Geometric2_0,
                        std::size_t linear_step = 64)
        : capacity_(initial_capacity > 0 ? initial_capacity : 1),
          policy_(policy),
          linear_step_(linear_step > 0 ? linear_step : 64),
          data_(std::make_unique<T[]>(capacity_)) {}

    void push_back(const T& value) {
        if (size_ == capacity_) {
            reallocate(calculate_next_capacity());
        }
        data_[size_++] = value;
    }

    std::expected<T, std::string_view> pop_back() {
        if (size_ == 0) {
            return std::unexpected("Buffer underflow: vector is empty");
        }
        T val = data_[--size_];

        // Гістерезисне стиснення місткості при падінні заповненості нижче 25%
        if (size_ > 0 && size_ <= capacity_ / 4 && capacity_ > 16) {
            reallocate(capacity_ / 2);
        }
        return val;
    }

    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] std::size_t capacity() const noexcept { return capacity_; }
    [[nodiscard]] BufferMetrics metrics() const noexcept { return metrics_; }
    [[nodiscard]] std::span<const T> view() const noexcept { return {data_.get(), size_}; }

private:
    std::size_t calculate_next_capacity() const {
        switch (policy_) {
            case GrowthPolicy::Geometric2_0:
                return capacity_ * 2;
            case GrowthPolicy::Geometric1_5: {
                std::size_t next_cap = capacity_ + (capacity_ >> 1);
                return next_cap > capacity_ ? next_cap : capacity_ + 1;
            }
            case GrowthPolicy::LinearFixed:
                return capacity_ + linear_step_;
        }
        return capacity_ * 2;
    }

    void reallocate(std::size_t new_capacity) {
        auto new_data = std::make_unique<T[]>(new_capacity);
        for (std::size_t i = 0; i < size_; ++i) {
            new_data[i] = std::move(data_[i]);
        }
        metrics_.total_copies += size_;
        data_ = std::move(new_data);
        capacity_ = new_capacity;
        metrics_.reallocations++;
    }

    std::size_t size_{0};
    std::size_t capacity_{8};
    GrowthPolicy policy_{GrowthPolicy::Geometric2_0};
    std::size_t linear_step_{64};
    std::unique_ptr<T[]> data_;
    BufferMetrics metrics_{};
};

void run_cpp_benchmark(std::size_t total_ops, GrowthPolicy policy, std::string_view name) {
    OverBuffer<int> buf(8, policy, 1000);

    auto start = std::chrono::high_resolution_clock::now();
    for (std::size_t i = 0; i < total_ops; ++i) {
        buf.push_back(static_cast<int>(i));
    }
    auto end = std::chrono::high_resolution_clock::now();

    std::chrono::duration<double, std::milli> elapsed = end - start;
    auto m = buf.metrics();

    std::cout << "[" << name << "] N=" << total_ops
              << " | Час: " << elapsed.count() << " мс"
              << " | Реалокацій: " << m.reallocations
              << " | Копіювань: " << m.total_copies
              << " | Копій/N: " << static_cast<double>(m.total_copies) / total_ops
              << "\n";
}

int main() {
    constexpr std::size_t N = 100000;
    std::cout << "=== Бенчмарк режимів розширення пам'яті (C++20) ===\n";
    run_cpp_benchmark(N, GrowthPolicy::Geometric2_0, "Геометричний x2.0");
    run_cpp_benchmark(N, GrowthPolicy::Geometric1_5, "Геометричний x1.5");
    run_cpp_benchmark(N, GrowthPolicy::LinearFixed,  "Лінійний +1000  ");
    return 0;
}
