#pragma once

#include <chrono>
#include <cstddef>
#include <cstdint>

namespace linkmux {

using Millis = std::chrono::milliseconds;

// Метрики одного носія. RSSI та SNR тримаємо у форматі Q8 (одиниця = 1/256 dBm):
// ціле згладжування без жодної плаваючої крапки.
class LinkQuality {
public:
    static constexpr std::size_t kWindow = 32;   // ширина вікна втрат у кадрах

    explicit LinkQuality(Millis slot) noexcept
        : slot_(slot.count() > 0 ? slot : Millis{100}) {}

    // Повертає, скільки кадрів загубилося перед цим (за розривом у seq)
    std::uint16_t onFrame(std::uint16_t seq, std::int16_t rssiDbm, std::int8_t snrDb,
                          Millis now) noexcept;
    void onTick(Millis now) noexcept;
    void resume(Millis now) noexcept;   // приймач знову слухає
    void reset(Millis now) noexcept;    // чиста сторінка вимірювання

    [[nodiscard]] std::int16_t rssiDbm() const noexcept {
        return static_cast<std::int16_t>((rssiQ8_ + 128) >> 8);
    }
    [[nodiscard]] std::int8_t snrDb() const noexcept {
        return static_cast<std::int8_t>((snrQ8_ + 128) >> 8);
    }
    [[nodiscard]] std::uint8_t per() const noexcept { return per_; }
    [[nodiscard]] std::uint8_t score() const noexcept { return score_; }
    [[nodiscard]] Millis silence(Millis now) const noexcept { return now - lastRx_; }
    [[nodiscard]] std::uint32_t received() const noexcept { return received_; }
    [[nodiscard]] std::uint32_t lost() const noexcept { return lost_; }

private:
    void pushBit(bool ok) noexcept;
    void recompute() noexcept;

    Millis        slot_;
    Millis        lastRx_{0};
    Millis        slotDeadline_{0};
    std::int32_t  rssiQ8_{0};
    std::int32_t  snrQ8_{0};
    std::uint32_t windowMask_{0xFFFFFFFFu};   // 1 = очікуваний кадр дійшов
    std::uint32_t received_{0};
    std::uint32_t lost_{0};
    std::uint16_t lastSeq_{0};
    std::uint8_t  per_{0};
    std::uint8_t  score_{100};
    bool          seeded_{false};
    bool          haveSeq_{false};
};

// Ковзне вікно дедуплікації на приймачі. LoRa віддає кадр за 40..120 мс,
// Wi-Fi за 2..5 мс: після перемикання старий кадр із резерву прилітає ПІСЛЯ
// свіжого з основного, а критичні команди ми ще й навмисно дублюємо.
class DedupWindow {
public:
    bool accept(std::uint16_t seq) noexcept;

    [[nodiscard]] std::uint32_t duplicates() const noexcept { return duplicates_; }
    [[nodiscard]] std::uint32_t tooOld() const noexcept { return tooOld_; }

private:
    std::uint16_t newestSeq_{0};
    std::uint32_t seenMask_{0};
    std::uint32_t duplicates_{0};
    std::uint32_t tooOld_{0};
    bool          primed_{false};
};

}  // namespace linkmux
