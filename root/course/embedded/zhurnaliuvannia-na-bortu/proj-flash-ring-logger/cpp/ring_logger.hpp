// Кільцевий журнал у SPI NOR Flash.
//
// Клас не знає ні про RTOS, ні про переривання, ні про годинник: мітку часу
// подає викликач, доступ до кристала — посилання на FlashDevice. Купи немає
// зовсім: найбільший буфер це один кадр на стеку.

#pragma once

#include <bitset>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>

#include "flash_device.hpp"
#include "record_codec.hpp"

namespace fl {

enum class LoggerError {
    Hal,              // кристал відмовив
    PayloadTooBig,    // навантаження не влазить у кадр
    BufferTooSmall,   // буфер вивантаження менший за сектор
    SectorRange,      // індекс сектора поза кільцем
    NothingToUpload,  // жодного заповненого сектора
    RingExhausted,    // усі сектори дефектні
};

// Пачка на вивантаження — сирі кадри одного сектора, як вони лежать у Flash.
struct Batch {
    std::uint32_t sector{0};
    std::span<const std::byte> bytes;
    std::size_t records{0};
};

class RingLogger {
public:
    explicit RingLogger(FlashDevice& device, std::uint32_t baseAddress = 0) noexcept
        : device_{device}, baseAddress_{baseAddress} {}

    // Сканує кільце, знаходить голову й хвіст, відновлює покажчик запису
    // після аварійного скидання. Якщо активного сектора немає — відкриває новий.
    std::expected<void, LoggerError> init();

    // Додає кадр. Сам ротує сектор, обходить дефектні й доповідає про них
    // окремим службовим записом.
    std::expected<void, LoggerError> append(Level level, std::uint8_t moduleId,
                                            std::uint32_t timestampMs, std::uint32_t tokenId,
                                            std::span<const std::byte> payload = {});

    // Віддає найстаріший ЗАПОВНЕНИЙ сектор. Активний не віддається: він росте.
    // buffer має вміщати kSectorSize байтів.
    std::expected<Batch, LoggerError> readBatch(std::span<std::byte> buffer);

    // Сервер підтвердив пачку — сектор стає Dirty, хвіст їде далі.
    std::expected<void, LoggerError> commitTail(std::uint32_t sectorIdx);

    [[nodiscard]] std::uint32_t activeSector() const noexcept { return active_; }
    [[nodiscard]] std::uint32_t tailSector() const noexcept { return tail_; }
    [[nodiscard]] std::uint32_t writeOffset() const noexcept { return offset_; }
    [[nodiscard]] std::uint32_t lastTimestampMs() const noexcept { return lastTimestampMs_; }
    [[nodiscard]] const std::bitset<kSectorCount>& badSectors() const noexcept { return bad_; }

private:
    struct ScanResult {
        std::uint32_t endOffset{0};
        std::uint32_t records{0};
    };

    [[nodiscard]] std::uint32_t sectorAddress(std::uint32_t idx) const noexcept;
    [[nodiscard]] std::uint32_t nextLive(std::uint32_t from) const noexcept;

    std::expected<SectorHeader, LoggerError> readHeader(std::uint32_t idx);
    std::expected<void, LoggerError> writeState(std::uint32_t idx, SectorState state);
    std::expected<void, LoggerError> verify(std::uint32_t address, std::span<const std::byte> expected);
    std::expected<void, LoggerError> openSector(std::uint32_t idx, std::uint32_t eraseCount,
                                                std::uint32_t seq);
    std::expected<void, LoggerError> rotate();
    ScanResult scanRecords(std::uint32_t idx);
    void markBad(std::uint32_t idx);
    void reportPendingBad();

    FlashDevice& device_;
    std::uint32_t baseAddress_{0};
    std::uint32_t active_{0};
    std::uint32_t offset_{kSectorHeaderSize};
    std::uint32_t tail_{0};
    std::uint32_t seqNum_{0};
    std::uint32_t lastTimestampMs_{0};
    std::bitset<kSectorCount> bad_{};
    std::optional<std::uint32_t> pendingBad_{};
    bool inServiceWrite_{false};
};

}  // namespace fl
