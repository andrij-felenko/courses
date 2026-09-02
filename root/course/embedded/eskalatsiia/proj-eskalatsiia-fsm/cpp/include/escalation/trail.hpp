#pragma once

#include <array>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <optional>

namespace esc {

using namespace std::chrono_literals;

struct Pose {
    float                     x{}, y{}, z{};
    float                     yaw{};
    std::chrono::milliseconds stamp{0ms};
    std::int8_t               rssi_dbm{};
};

[[nodiscard]] inline float dist2d(const Pose& a, const Pose& b) noexcept {
    const float dx = a.x - b.x;
    const float dy = a.y - b.y;
    return std::sqrt(dx * dx + dy * dy);
}

inline constexpr float kAcceptRadiusM = 0.8f;
// Під час відкату одометрія дрейфує — радіус приймання точки подвоюємо
inline constexpr float kBacktrackRadiusM = 2.0f * kAcceptRadiusM;

// Кільцевий буфер історії руху. Точка лягає лише після реального зсуву:
// зависання на місці інакше витіснить усю траєкторію підльоту.
class Trail {
public:
    static constexpr std::size_t kCapacity = 64;
    static constexpr float       kStepM    = 1.5f;

    bool push_if_moved(const Pose& p) noexcept {
        if (count_ > 0 && dist2d(last(), p) < kStepM) {
            return false;
        }
        buf_[head_] = p;
        head_ = (head_ + 1) % kCapacity;
        if (count_ < kCapacity) {
            ++count_;
        }
        return true;
    }

    // Знімає найсвіжішу точку — рух назад іде саме в такому порядку
    [[nodiscard]] std::optional<Pose> pop_reverse() noexcept {
        if (count_ == 0) {
            return std::nullopt;
        }
        head_ = (head_ == 0) ? (kCapacity - 1) : (head_ - 1);
        --count_;
        return buf_[head_];
    }

    [[nodiscard]] std::size_t size() const noexcept { return count_; }
    void clear() noexcept { head_ = 0; count_ = 0; }

private:
    [[nodiscard]] const Pose& last() const noexcept {
        return buf_[(head_ + kCapacity - 1) % kCapacity];
    }

    std::array<Pose, kCapacity> buf_{};
    std::size_t                 head_{0};
    std::size_t                 count_{0};
};

}  // namespace esc
