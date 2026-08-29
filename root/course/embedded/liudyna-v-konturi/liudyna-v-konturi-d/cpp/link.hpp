#pragma once

#include <algorithm>
#include <cstdint>
#include <deque>
#include <random>
#include <stdexcept>

namespace hitl {

// Телеметрія борту: одним кадром їдуть і кут, і кутова швидкість.
struct Telemetry {
    float angle_rad{0.0f};
    float rate_rad_s{0.0f};
};

// Черга чистої транспортної затримки. Payload довільний: у бік оператора
// їде телеметрія, у бік машини — положення стіка. Амплітуду черга не
// чіпає взагалі, лише зсуває пакет у часі.
template <class Payload>
class DelayLine {
public:
    DelayLine(float base_delay, float jitter, bool buffered, std::uint32_t seed)
        : base_delay_{base_delay},
          jitter_{std::min(jitter, base_delay)},
          buffered_{buffered},
          rng_{seed} {
        if (base_delay < 0.0f || jitter < 0.0f) {
            throw std::invalid_argument{"затримка й джитер не можуть бути від'ємні"};
        }
    }

    void Push(const Payload& payload, float now) {
        // Буфер джитера прибирає розкид, але платить за це КОЖЕН пакет —
        // сталим лагом найгіршого випадку.
        const float delay =
            buffered_ ? base_delay_ + jitter_
                      : std::max(0.0f, base_delay_ + jitter_ * spread_(rng_));
        queue_.push_back(Slot{payload, now + delay});
    }

    // Найсвіжіший пакет, що вже дійшов. Потік упорядкований: той, що
    // спізнився, тримає за собою й ті, що встигли, — звідси «застигання»
    // картинки й наступні за ними ривки.
    const Payload& Pop(float now) {
        bool released = false;
        while (!queue_.empty() && queue_.front().available <= now) {
            last_ = queue_.front().payload;
            queue_.pop_front();
            released = true;
        }
        if (!released) {
            ++freezes_;
        }
        return last_;
    }

    [[nodiscard]] float effective_delay() const noexcept {
        return buffered_ ? base_delay_ + jitter_ : base_delay_;
    }
    [[nodiscard]] int freezes() const noexcept { return freezes_; }

private:
    struct Slot {
        Payload payload;
        float available;
    };

    std::deque<Slot> queue_;
    Payload last_{};
    float base_delay_;
    float jitter_;
    bool buffered_;
    std::mt19937 rng_;
    std::uniform_real_distribution<float> spread_{-1.0f, 1.0f};
    int freezes_{0};
};

}  // namespace hitl
