#include <iostream>
#include <vector>
#include <cstdint>
#include <cmath>
#include <random>
#include <span>
#include <concepts>
#include <utility>

// Шаблонний клас високошвидкісного семплера Algorithm L
template <typename T>
class ReservoirSamplerL {
public:
    explicit ReservoirSamplerL(std::size_t capacity, std::uint64_t seed = 0x4d595df4d0f33173ULL)
        : capacity_(capacity), total_count_(0), skip_count_(0), W_(1.0),
          rng_state_(seed ? seed : 0x4d595df4d0f33173ULL) {
        reservoir_.reserve(capacity_);
    }

    ReservoirSamplerL(const ReservoirSamplerL&) = delete;
    ReservoirSamplerL& operator=(const ReservoirSamplerL&) = delete;

    ReservoirSamplerL(ReservoirSamplerL&&) noexcept = default;
    ReservoirSamplerL& operator=(ReservoirSamplerL&&) noexcept = default;

    void push(T item) {
        total_count_++;
        if (reservoir_.size() < capacity_) {
            reservoir_.push_back(std::move(item));
            if (reservoir_.size() == capacity_) {
                double u = uniform_double();
                W_ = std::exp(std::log(u) / static_cast<double>(capacity_));
                skip_count_ = compute_skip();
            }
        } else {
            if (skip_count_ == 0) {
                std::uint64_t slot = fast_rand_range(capacity_);
                reservoir_[slot] = std::move(item);

                double u = uniform_double();
                W_ *= std::exp(std::log(u) / static_cast<double>(capacity_));
                skip_count_ = compute_skip();
            } else {
                skip_count_--;
            }
        }
    }

    // Пакетна обробка контейнера або фрагмента пам'яті
    void push_batch(std::span<const T> items) {
        std::size_t idx = 0;
        const std::size_t count = items.size();
        while (idx < count) {
            if (reservoir_.size() < capacity_) {
                push(items[idx++]);
            } else if (skip_count_ >= (count - idx)) {
                std::size_t remaining = count - idx;
                total_count_ += remaining;
                skip_count_ -= remaining;
                break;
            } else {
                idx += skip_count_;
                total_count_ += skip_count_;
                skip_count_ = 0;
                if (idx < count) {
                    push(items[idx++]);
                }
            }
        }
    }

    [[nodiscard]] std::span<const T> sample() const noexcept {
        return std::span<const T>(reservoir_.data(), reservoir_.size());
    }

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

    inline std::uint64_t fast_rand_range(std::uint64_t bound) noexcept {
        std::uint64_t r = splitmix64();
        return static_cast<std::uint64_t>((static_cast<unsigned __int128>(r) * bound) >> 64);
    }

    inline std::uint64_t compute_skip() noexcept {
        double u = uniform_double();
        return static_cast<std::uint64_t>(std::log(u) / std::log(1.0 - W_));
    }

    std::size_t capacity_;
    std::uint64_t total_count_;
    std::uint64_t skip_count_;
    double W_;
    std::uint64_t rng_state_;
    std::vector<T> reservoir_;
};
