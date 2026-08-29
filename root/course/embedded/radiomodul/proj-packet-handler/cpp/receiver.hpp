#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <deque>
#include <optional>
#include <vector>

#include "frame.hpp"
#include "whitening.hpp"

namespace radio {

// Приймач їсть саме БІТИ: межі байта в ефірі не існує, її створює лише
// строб корелятора синхрослова.
class BitReceiver {
public:
    // Скільки чергувань 0/1 треба побачити, щоб узагалі ввімкнути корелятор
    // (апаратний аналог — Preamble Detect / Carrier Sense).
    static constexpr int kPreambleDetectBits = 16;
    // Вікно пошуку синхрослова після преамбули.
    static constexpr int kSyncSearchBits = 256;
    // Глибина пакетного FIFO трансивера.
    static constexpr std::size_t kFifoDepth = 2;

    struct Stats {
        std::uint32_t arms{};         // спрацювань детектора преамбули
        std::uint32_t syncs{};        // спрацювань корелятора синхрослова
        std::uint32_t frames{};       // кадрів із правильним CRC
        std::uint32_t crcErrors{};    // кадрів, відкинутих по CRC
        std::uint32_t lengthErrors{}; // неможлива довжина в заголовку
        std::uint32_t overruns{};     // кадрів, загублених у переповненому FIFO
    };

    void pushBit(bool bit);
    void pushByteMsbFirst(std::uint8_t byte);

    [[nodiscard]] std::optional<std::vector<std::uint8_t>> pop();
    [[nodiscard]] bool overrun() const noexcept { return overrun_; }
    [[nodiscard]] const Stats& stats() const noexcept { return stats_; }

    // Строб CMD_FLUSHRX: скидає FIFO, ознаку переповнення й кадровий автомат.
    void flush();

private:
    enum class State { Hunt, Length, Data, Crc };

    void onByte(std::uint8_t raw);
    void deliver();
    void toHunt();

    // бітовий рівень
    std::uint32_t shift_{};
    int  altRun_{};
    int  searchLeft_{};
    bool lastBit_{};
    bool armed_{};

    // байтовий рівень
    std::uint8_t acc_{};
    int bitCount_{};

    // кадровий автомат
    State state_{State::Hunt};
    Whitener whitener_{};
    std::uint16_t crc_{};
    std::size_t need_{};
    std::vector<std::uint8_t> body_{};
    std::array<std::uint8_t, 2> crcRx_{};
    std::size_t crcPos_{};

    std::deque<std::vector<std::uint8_t>> fifo_{};
    bool overrun_{};
    Stats stats_{};
};

} // namespace radio
