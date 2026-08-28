#include <iostream>
#include <vector>
#include <queue>
#include <cstdint>
#include <cmath>
#include <random>
#include <span>
#include <concepts>
#include <utility>

// Шаблонний клас зваженого семплера A-Res
template <typename T>
class WeightedReservoirSampler {
public:
    struct WeightedEntry {
        double key; // r_i = -ln(u_i) / w_i
        T item;

        // Перевантаження оператора порівняння для підтримки max-heap
        bool operator<(const WeightedEntry& other) const noexcept {
            return key < other.key;
        }
    };

    explicit WeightedReservoirSampler(std::size_t capacity, std::uint64_t seed = 0x1f83d9abfb41b7eULL)
        : capacity_(capacity), total_count_(0), rng_state_(seed ? seed : 0x1f83d9abfb41b7eULL) {}

    void push(T item, double weight) {
        if (weight <= 0.0 || std::isnan(weight)) return;
        total_count_++;

        double u = uniform_double();
        double key = -std::log(u) / weight;

        if (heap_.size() < capacity_) {
            heap_.push(WeightedEntry{key, std::move(item)});
        } else if (key < heap_.top().key) {
            heap_.pop();
            heap_.push(WeightedEntry{key, std::move(item)});
        }
    }

    // Вивантаження вибірки у вектор (порядок від найменшого ключа до найбільшого)
    [[nodiscard]] std::vector<T> extract_sample() const {
        std::vector<T> result;
        result.reserve(heap_.size());
        auto copy_heap = heap_;
        while (!copy_heap.empty()) {
            result.push_back(copy_heap.top().item);
            copy_heap.pop();
        }
        return result;
    }

    [[nodiscard]] std::size_t size() const noexcept { return heap_.size(); }
    [[nodiscard]] std::size_t capacity() const noexcept { return capacity_; }
    [[nodiscard]] std::uint64_t total_processed() const noexcept { return total_count_; }

private:
    inline std::uint64_t splitmix64() noexcept {
        std::uint64_t z = (rng_state_ += 0x9e3779b97f4a7c15ULL);
        z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
        z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
        return z ^ (z >> 31);
    }

    inline double uniform_double() noexcept {
        std::uint64_t r = splitmix64();
        return ((r >> 11) * (1.0 / 9007199254740992.0)) + 1e-16;
    }

    std::size_t capacity_;
    std::uint64_t total_count_;
    std::uint64_t rng_state_;
    std::priority_queue<WeightedEntry> heap_; // Корінь тримає найбільший r_i (найгірший кандидат)
};
