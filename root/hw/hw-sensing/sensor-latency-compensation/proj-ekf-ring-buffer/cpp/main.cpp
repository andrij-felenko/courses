#include <iostream>
#include <array>
#include <optional>
#include <chrono>
#include <cstdint>
#include <algorithm>

namespace navigation {

constexpr size_t StateDim = 6;
constexpr size_t BufferCapacity = 128;

using Microseconds = std::chrono::microseconds;

struct StateSnapshot {
    Microseconds timestamp{0};
    std::array<float, StateDim> state{};
    std::array<float, StateDim> transitionDiag{};
};

class StateDelayBuffer {
public:
    StateDelayBuffer() = default;

    void push(Microseconds timestamp,
              const std::array<float, StateDim>& state,
              const std::array<float, StateDim>& phiDiag) noexcept {
        buffer_[head_] = StateSnapshot{timestamp, state, phiDiag};
        head_ = (head_ + 1) % BufferCapacity;
        if (count_ < BufferCapacity) {
            ++count_;
        }
    }

    [[nodiscard]] std::optional<std::array<float, StateDim>> getInterpolatedState(Microseconds targetTime) const noexcept {
        if (count_ < 2) {
            return std::nullopt;
        }

        const size_t newestIdx = (head_ + BufferCapacity - 1) % BufferCapacity;
        const size_t oldestIdx = (head_ + BufferCapacity - count_) % BufferCapacity;

        const auto tNewest = buffer_[newestIdx].timestamp;
        const auto tOldest = buffer_[oldestIdx].timestamp;

        if (targetTime > tNewest || targetTime < tOldest) {
            return std::nullopt; /* Затримка виходить за межі історії буфера */
        }

        for (size_t i = 0; i < count_ - 1; ++i) {
            const size_t idxCurr = (newestIdx + BufferCapacity - i) % BufferCapacity;
            const size_t idxPrev = (idxCurr + BufferCapacity - 1) % BufferCapacity;

            const auto tCurr = buffer_[idxCurr].timestamp;
            const auto tPrev = buffer_[idxPrev].timestamp;

            if (targetTime >= tPrev && targetTime <= tCurr) {
                const auto dtTotal = (tCurr - tPrev).count();
                const float alpha = (dtTotal > 0)
                    ? static_cast<float>((targetTime - tPrev).count()) / static_cast<float>(dtTotal)
                    : 0.0f;

                std::array<float, StateDim> interpolated{};
                for (size_t j = 0; j < StateDim; ++j) {
                    interpolated[j] = (1.0f - alpha) * buffer_[idxPrev].state[j] +
                                      alpha * buffer_[idxCurr].state[j];
                }
                return interpolated;
            }
        }
        return std::nullopt;
    }

    [[nodiscard]] size_t size() const noexcept { return count_; }

private:
    std::array<StateSnapshot, BufferCapacity> buffer_{};
    size_t head_{0};
    size_t count_{0};
};

class DelayedKalmanFilter {
public:
    static bool fuseDelayedPosition(const StateDelayBuffer& buffer,
                                    Microseconds measurementTime,
                                    const std::array<float, 3>& zMeas,
                                    const std::array<float, 3>& rCov,
                                    std::array<float, StateDim>& currentState) noexcept {
        const auto histStateOpt = buffer.getInterpolatedState(measurementTime);
        if (!histStateOpt.has_value()) {
            return false;
        }

        const auto& histState = *histStateOpt;
        std::array<float, 3> innovation{};
        for (size_t i = 0; i < 3; ++i) {
            innovation[i] = zMeas[i] - histState[i];
        }

        /* Оновлення поточного стану з коефіцієнтом підсилення Калмана */
        for (size_t i = 0; i < 3; ++i) {
            constexpr float pCov = 1.0f;
            const float kGain = pCov / (pCov + rCov[i]);
            const float deltaPos = kGain * innovation[i];

            currentState[i] += deltaPos;
            currentState[i + 3] += deltaPos * 0.5f; /* Корекція оцінки швидкості */
        }

        return true;
    }
};

} // namespace navigation

int main() {
    using namespace std::chrono_literals;
    navigation::StateDelayBuffer buffer;

    std::array<float, navigation::StateDim> currentState{0.0f, 0.0f, 0.0f, 10.0f, 0.0f, 0.0f};
    constexpr std::array<float, navigation::StateDim> phiDiag{1.0f, 1.0f, 1.0f, 1.0f, 1.0f, 1.0f};

    auto currentTime = 1'000'000us;
    constexpr auto dt = 10'000us;

    for (int k = 0; k < 30; ++k) {
        currentTime += dt;
        currentState[0] += currentState[3] * (std::chrono::duration<float>(dt).count());
        buffer.push(currentTime, currentState, phiDiag);
    }

    constexpr auto gnssDelay = 150'000us;
    const auto gnssTimestamp = currentTime - gnssDelay;

    constexpr std::array<float, 3> zGnss{1.55f, 0.0f, 0.0f};
    constexpr std::array<float, 3> rCov{0.25f, 0.25f, 0.25f};

    std::cout << "Час: " << currentTime.count()
              << " мкс, Поточна позиція X до корекції: " << currentState[0] << " м\n";

    if (navigation::DelayedKalmanFilter::fuseDelayedPosition(buffer, gnssTimestamp, zGnss, rCov, currentState)) {
        std::cout << "Злиття успішне. Скоригована позиція X: " << currentState[0] << " м\n";
    } else {
        std::cout << "Помилка відкладеного злиття!\n";
    }

    return 0;
}
