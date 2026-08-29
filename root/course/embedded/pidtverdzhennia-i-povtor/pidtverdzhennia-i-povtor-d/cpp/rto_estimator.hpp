// rto_estimator.hpp — цілочисельний Якобсон (RFC 6298) з правилами Карна.
//
// Фіксована кома замість float: на Cortex-M0/M3 без FPU кожне множення
// з рухомою комою тягне бібліотечну емуляцію просто в обробнику таймера.
//   srttScaled_   = SRTT · 8    → множення на 1/8 це зсув >> 3
//   rttvarScaled_ = RTTVAR · 4  → множення на 1/4 це зсув >> 2
//   RTO = SRTT + 4·RTTVAR = (srttScaled_ >> 3) + rttvarScaled_
#pragma once

#include <algorithm>
#include <chrono>
#include <cstdint>

namespace arq {

class RtoEstimator {
public:
    using Ms = std::chrono::milliseconds;

    static constexpr Ms kMin{20};
    static constexpr Ms kMax{2000};
    static constexpr Ms kInitial{100};

    // Правило Карна №1: сюди потрапляє лише кадр, доставлений з першої спроби.
    void addSample(Ms rtt) noexcept
    {
        auto sample = static_cast<std::int32_t>(rtt.count());
        if (sample < 1) {
            sample = 1; // тік таймера 1 мс: нульового RTT не буває
        }

        if (!hasSample_) {
            srttScaled_   = sample << 3; // перший вимір задає оцінку цілком
            rttvarScaled_ = (sample / 2) << 2;
            hasSample_    = true;
        } else {
            const std::int32_t err = sample - (srttScaled_ >> 3);
            srttScaled_ += err;

            const std::int32_t absErr = err < 0 ? -err : err;
            rttvarScaled_ += absErr - (rttvarScaled_ >> 2);
            // різкий стрибок не має пускати відхилення в мінус
            rttvarScaled_ = std::max(rttvarScaled_, std::int32_t{0});
        }
        recompute();
    }

    // Правило Карна №2: кожен таймаут подвоює вікно очікування.
    void backoff() noexcept { rto_ = std::min(rto_ * 2, kMax); }

    [[nodiscard]] Ms value() const noexcept { return rto_; }
    [[nodiscard]] Ms smoothedRtt() const noexcept { return Ms{srttScaled_ >> 3}; }

private:
    // Свіжий вимір перераховує RTO з нуля — і цим сам скидає накопичене
    // подвоєння. Окремої «команди відновлення» протоколу не треба.
    void recompute() noexcept
    {
        rto_ = std::clamp(Ms{(srttScaled_ >> 3) + rttvarScaled_}, kMin, kMax);
    }

    std::int32_t srttScaled_{static_cast<std::int32_t>(kInitial.count()) << 3};
    std::int32_t rttvarScaled_{static_cast<std::int32_t>(kInitial.count() / 2) << 2};
    Ms   rto_{kInitial};
    bool hasSample_{false};
};

} // namespace arq
