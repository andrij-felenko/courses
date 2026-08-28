#include <iostream>
#include <vector>
#include <cstdint>
#include <random>
#include <span>
#include <concepts>
#include <utility>

// Шаблонний потоковий семплер Algorithm R
template <typename T>
class ReservoirSamplerR {
public:
    explicit ReservoirSamplerR(std::size_t capacity, std::uint64_t seed = 0x853c49e6748fea9bULL)
        : capacity_(capacity), total_count_(0), rng_state_(seed ? seed : 0x853c49e6748fea9bULL) {
        reservoir_.reserve(capacity_);
    }

    // Заборона небезпечного копіювання для запобігання дублюванню стану PRNG
    ReservoirSamplerR(const ReservoirSamplerR&) = delete;
    ReservoirSamplerR& operator=(const ReservoirSamplerR&) = delete;

    // Дозвіл переміщення стану
    ReservoirSamplerR(ReservoirSamplerR&&) noexcept = default;
    ReservoirSamplerR& operator=(ReservoirSamplerR&&) noexcept = default;

    // Обробка вхідного значення (передача за значенням для підтримки move-семантики)
    void push(T item) {
        total_count_++;
        if (reservoir_.size() < capacity_) {
            reservoir_.push_back(std::move(item));
        } else {
            std::uint64_t j = fast_rand_range(total_count_);
            if (j < capacity_) {
                reservoir_[j] = std::move(item);
            }
        }
    }

    // Доступ до поточної вибірки у вигляді безпечного span
    [[nodiscard]] std::span<const T> sample() const noexcept {
        return std::span<const T>(reservoir_.data(), reservoir_.size());
    }

    [[nodiscard]] std::size_t capacity() const noexcept { return capacity_; }
    [[nodiscard]] std::uint64_t total_processed() const noexcept { return total_count_; }

    void reset(std::uint64_t seed = 0) {
        reservoir_.clear();
        total_count_ = 0;
        if (seed != 0) rng_state_ = seed;
    }

private:
    inline std::uint64_t splitmix64() noexcept {
        std::uint64_t z = (rng_state_ += 0x9e3779b97f4a7c15ULL);
        z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
        z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
        return z ^ (z >> 31);
    }

    inline std::uint64_t fast_rand_range(std::uint64_t bound) noexcept {
        std::uint64_t r = splitmix64();
        return static_cast<std::uint64_t>((static_cast<unsigned __int128>(r) * bound) >> 64);
    }

    std::size_t capacity_;
    std::uint64_t total_count_;
    std::uint64_t rng_state_;
    std::vector<T> reservoir_;
};
