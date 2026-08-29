#include "link_quality.hpp"

#include <algorithm>

namespace linkmux {
namespace {
constexpr int kEwmaShift = 3;   // alpha = 1/8: згладжує, але не запізнюється на секунди
}  // namespace

void LinkQuality::pushBit(bool ok) noexcept {
    windowMask_ = (windowMask_ << 1) | (ok ? 1u : 0u);
    if (ok) {
        ++received_;
    } else {
        ++lost_;
    }
}

void LinkQuality::recompute() noexcept {
    std::uint32_t mask = windowMask_;
    std::uint32_t ok   = 0;
    for (std::size_t i = 0; i < kWindow; ++i) {
        ok += (mask & 1u);
        mask >>= 1;
    }
    per_ = static_cast<std::uint8_t>(((kWindow - ok) * 100) / kWindow);

    // Бал якості: втрати важать найбільше, рівень і шум лише додають штраф
    int score = 100 - static_cast<int>(per_);
    const std::int16_t rssi = rssiDbm();
    if (rssi < -100) {
        score -= 20;            // біля порога чутливості приймача
    } else if (rssi < -90) {
        score -= 10;
    }
    if (snrDb() < 0) {
        score -= 10;            // сигнал під шумом — типовий почерк завади
    }
    score_ = static_cast<std::uint8_t>(std::clamp(score, 0, 100));
}

std::uint16_t LinkQuality::onFrame(std::uint16_t seq, std::int16_t rssiDbmRaw,
                                   std::int8_t snrDbRaw, Millis now) noexcept {
    std::uint16_t missed = 0;

    if (!haveSeq_) {
        haveSeq_ = true;
        lastSeq_ = seq;
    } else {
        // Знакова різниця переживає обгортання uint16 без жодного «якщо»
        const auto gap = static_cast<std::int16_t>(seq - lastSeq_);
        if (gap <= 0) {
            return 0;   // спізнілий або дубльований кадр вікна втрат не рухає
        }
        missed = static_cast<std::uint16_t>(gap - 1);
        for (std::uint16_t i = 0; i < missed && i < kWindow; ++i) {
            pushBit(false);
        }
        lastSeq_ = seq;
    }
    pushBit(true);

    if (!seeded_) {
        rssiQ8_ = static_cast<std::int32_t>(rssiDbmRaw) << 8;
        snrQ8_  = static_cast<std::int32_t>(snrDbRaw) << 8;
        seeded_ = true;
    } else {
        rssiQ8_ += ((static_cast<std::int32_t>(rssiDbmRaw) << 8) - rssiQ8_) >> kEwmaShift;
        snrQ8_  += ((static_cast<std::int32_t>(snrDbRaw) << 8) - snrQ8_) >> kEwmaShift;
    }

    lastRx_       = now;
    slotDeadline_ = now + slot_;
    recompute();
    return missed;
}

void LinkQuality::onTick(Millis now) noexcept {
    // Тиша — теж вимір: за кожен прострочений слот у вікно падає нуль
    while (now >= slotDeadline_) {
        pushBit(false);
        slotDeadline_ += slot_;
        recompute();
    }
}

void LinkQuality::resume(Millis now) noexcept {
    // Поки приймач спав, кадрів не було не через ефір, а через нас:
    // у втрати цей час не пишемо, лише відсуваємо очікування слота.
    slotDeadline_ = now + slot_;
}

void LinkQuality::reset(Millis now) noexcept {
    windowMask_   = 0xFFFFFFFFu;
    per_          = 0;
    slotDeadline_ = now + slot_;
    recompute();
}

bool DedupWindow::accept(std::uint16_t seq) noexcept {
    if (!primed_) {
        primed_    = true;
        newestSeq_ = seq;
        seenMask_  = 1u;
        return true;
    }

    const auto diff = static_cast<std::int16_t>(seq - newestSeq_);
    if (diff > 0) {
        if (diff >= static_cast<std::int16_t>(LinkQuality::kWindow)) {
            seenMask_ = 0u;             // стрибок далі за вікно — починаємо заново
        } else {
            seenMask_ <<= diff;
        }
        seenMask_ |= 1u;
        newestSeq_ = seq;
        return true;
    }

    const auto back = static_cast<std::uint16_t>(-diff);
    if (back >= LinkQuality::kWindow) {
        ++tooOld_;                      // відстав більше як на вікно
        return false;
    }
    const std::uint32_t bit = 1u << back;
    if ((seenMask_ & bit) != 0u) {
        ++duplicates_;                  // той самий кадр прийшов другим носієм
        return false;
    }
    seenMask_ |= bit;
    return true;                        // спізнився, але новий — беремо
}

}  // namespace linkmux
