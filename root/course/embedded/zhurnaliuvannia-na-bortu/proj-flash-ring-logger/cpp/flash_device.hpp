// Доступ до кристала SPI NOR Flash.
//
// Три операції, які вміє будь-який кристал цього класу, і жодної більше.
// Помилка повертається через std::expected: код виклику мусить її розібрати,
// а не проґавити, як проґавлюють -1 від функції, що повертає int.

#pragma once

#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

namespace fl {

enum class FlashError {
    Io,          // кристал не відповів або відмовив на команді
    OutOfRange,  // адреса поза межами відведеної області
};

class FlashDevice {
public:
    virtual ~FlashDevice() = default;

    FlashDevice(const FlashDevice&) = delete;
    FlashDevice& operator=(const FlashDevice&) = delete;
    FlashDevice(FlashDevice&&) = delete;
    FlashDevice& operator=(FlashDevice&&) = delete;

    virtual std::expected<void, FlashError> read(std::uint32_t address,
                                                 std::span<std::byte> destination) = 0;

    // Запис лише гасить біти: одиницю в нуль можна, назад — тільки стиранням.
    virtual std::expected<void, FlashError> write(std::uint32_t address,
                                                  std::span<const std::byte> source) = 0;

    virtual std::expected<void, FlashError> eraseSector(std::uint32_t sectorAddress) = 0;

protected:
    FlashDevice() = default;
};

}  // namespace fl
