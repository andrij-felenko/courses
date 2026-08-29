// SpiEmergencyDump.cpp — прямий побайтовий запис дампа в SPI-носій.
#include "SpiEmergencyDump.hpp"

#include "FlightRecorderCore.hpp"
#include "McuPort.hpp"

#include <algorithm>

namespace embedded::drivers {
namespace {

// Зсуви регістрів SPI (розкладка ARM Cortex-M, STM32F4)
constexpr std::uintptr_t kCr1 = 0x00U;
constexpr std::uintptr_t kCr2 = 0x04U;
constexpr std::uintptr_t kSr  = 0x08U;
constexpr std::uintptr_t kDr  = 0x0CU;

constexpr std::uint32_t kCr1Spe     = 1U << 6;
constexpr std::uint32_t kCr2RxDmaEn = 1U << 0;
constexpr std::uint32_t kCr2TxDmaEn = 1U << 1;
constexpr std::uint32_t kCr2ErrIe   = 1U << 5;
constexpr std::uint32_t kCr2RxNeIe  = 1U << 6;
constexpr std::uint32_t kCr2TxeIe   = 1U << 7;

constexpr std::uint32_t kSrRxNe = 1U << 0;
constexpr std::uint32_t kSrTxe  = 1U << 1;
constexpr std::uint32_t kSrBsy  = 1U << 7;

// Команди FRAM (FM25V) і NOR Flash (W25Q, MX25) — набір спільний
constexpr std::uint8_t kOpWren        = 0x06U;
constexpr std::uint8_t kOpWrite       = 0x02U; // FRAM WRITE / Flash PAGE PROGRAM
constexpr std::uint8_t kOpRdsr        = 0x05U;
constexpr std::uint8_t kOpRead        = 0x03U;
constexpr std::uint8_t kOpSectorErase = 0x20U;

constexpr std::uint8_t kStatusWip = 1U << 0; // Flash: операція триває
constexpr std::uint8_t kStatusWel = 1U << 1; // запис дозволено

constexpr std::size_t kPageSize   = 256;
constexpr std::size_t kSectorSize = 4096;

// Стеля очікування прапорця: більше, ніж треба справному SPI, і менше,
// ніж вікно сторожового таймера. Нескінченного очікування в панічному
// шляху бути не може — мертва шина повісила б ядро назавжди.
constexpr std::uint32_t kSpinLimit = 200000U;

} // namespace

EmergencySpiMemory::ChipSelect::ChipSelect(const EmergencySpiMemory& bus) noexcept : bus_{bus} {
    mcu::reg(bus_.cs_bsrr_) = 1U << (bus_.cs_pin_ + 16U); // CS = Low
}

EmergencySpiMemory::ChipSelect::~ChipSelect() {
    mcu::reg(bus_.cs_bsrr_) = 1U << bus_.cs_pin_; // CS = High
}

// Забрати шину в того, хто нею користувався до аварії: зняти запити DMA й
// переривання (обслуговувати їх нікому), дочекатися кінця обміну, злити
// недочитаний байт з приймача й переконатися, що блок увімкнений.
FlushResult EmergencySpiMemory::takeover() const noexcept {
    auto& cr2 = mcu::reg(spi_base_ + kCr2);
    cr2 = cr2 & ~(kCr2TxDmaEn | kCr2RxDmaEn | kCr2TxeIe | kCr2RxNeIe | kCr2ErrIe);

    for (std::uint32_t spins = kSpinLimit; (mcu::reg(spi_base_ + kSr) & kSrBsy) != 0U; --spins) {
        if (spins == 0U) {
            return std::unexpected{FlushError::Timeout};
        }
    }
    if ((mcu::reg(spi_base_ + kSr) & kSrRxNe) != 0U) {
        (void)mcu::reg<std::uint8_t>(spi_base_ + kDr); // викинути чужий байт
    }

    auto& cr1 = mcu::reg(spi_base_ + kCr1);
    cr1 = cr1 | kCr1Spe;
    mcu::reg(cs_bsrr_) = 1U << cs_pin_; // CS у спокій, хай там що лишив попередник
    return {};
}

// Повний дуплекс опитуванням: чекаємо TXE, кладемо байт у DR восьмибітним
// доступом (32-бітний запис зібрав би кадр із двох байтів), чекаємо RXNE,
// забираємо відповідь. Без читання RXNE приймач переповниться на другій сотні.
std::expected<std::uint8_t, FlushError> EmergencySpiMemory::xfer(std::uint8_t out) const noexcept {
    for (std::uint32_t spins = kSpinLimit; (mcu::reg(spi_base_ + kSr) & kSrTxe) == 0U; --spins) {
        if (spins == 0U) {
            return std::unexpected{FlushError::Timeout};
        }
    }
    mcu::reg<std::uint8_t>(spi_base_ + kDr) = out;

    for (std::uint32_t spins = kSpinLimit; (mcu::reg(spi_base_ + kSr) & kSrRxNe) == 0U; --spins) {
        if (spins == 0U) {
            return std::unexpected{FlushError::Timeout};
        }
    }
    return mcu::reg<std::uint8_t>(spi_base_ + kDr);
}

FlushResult EmergencySpiMemory::send(std::uint8_t byte) const noexcept {
    if (auto answer = xfer(byte); !answer) {
        return std::unexpected{answer.error()};
    }
    return {};
}

FlushResult EmergencySpiMemory::send_command(std::uint8_t opcode, std::uint32_t addr) const noexcept {
    const std::uint8_t sequence[] = {opcode, static_cast<std::uint8_t>((addr >> 16) & 0xFFU),
                                     static_cast<std::uint8_t>((addr >> 8) & 0xFFU),
                                     static_cast<std::uint8_t>(addr & 0xFFU)};
    for (const std::uint8_t byte : sequence) {
        if (auto rc = send(byte); !rc) {
            return rc;
        }
    }
    return {};
}

std::expected<std::uint8_t, FlushError> EmergencySpiMemory::read_status() const noexcept {
    ChipSelect cs{*this};
    if (auto rc = send(kOpRdsr); !rc) {
        return std::unexpected{rc.error()};
    }
    return xfer(0xFFU);
}

// Дозвіл запису й перевірка, що мікросхема справді відповідає: якщо WEL не
// піднявся, далі писати нема куди — краще повернути помилку, ніж мовчки
// протактувати чотири кілобайти в порожнечу.
FlushResult EmergencySpiMemory::write_enable() const noexcept {
    {
        ChipSelect cs{*this};
        if (auto rc = send(kOpWren); !rc) {
            return rc;
        }
    }
    const auto status = read_status();
    if (!status) {
        return std::unexpected{status.error()};
    }
    if ((*status & kStatusWel) == 0U) {
        return std::unexpected{FlushError::NoDevice};
    }
    return {};
}

FlushResult EmergencySpiMemory::wait_write_done() const noexcept {
    for (std::uint32_t spins = kSpinLimit; spins > 0U; --spins) {
        const auto status = read_status();
        if (!status) {
            return std::unexpected{status.error()};
        }
        if ((*status & kStatusWip) == 0U) {
            return {};
        }
    }
    return std::unexpected{FlushError::Timeout};
}

FlushResult EmergencySpiMemory::write_fram(std::uint32_t dst_addr,
                                           std::span<const std::byte> image) const noexcept {
    if (auto rc = takeover(); !rc) {
        return rc;
    }
    if (auto rc = write_enable(); !rc) {
        return rc;
    }

    ChipSelect cs{*this};
    if (auto rc = send_command(kOpWrite, dst_addr); !rc) {
        return rc;
    }
    for (const std::byte byte : image) {
        if (auto rc = send(std::to_integer<std::uint8_t>(byte)); !rc) {
            return rc;
        }
    }
    return {};
}

FlushResult EmergencySpiMemory::erase_flash_slot(std::uint32_t dst_addr,
                                                 std::size_t size) const noexcept {
    if (auto rc = takeover(); !rc) {
        return rc;
    }

    const std::uint32_t first = dst_addr & ~static_cast<std::uint32_t>(kSectorSize - 1);
    const std::uint32_t last =
        (dst_addr + static_cast<std::uint32_t>(size) - 1U) & ~static_cast<std::uint32_t>(kSectorSize - 1);

    for (std::uint32_t sector = first; sector <= last; sector += kSectorSize) {
        if (auto rc = write_enable(); !rc) {
            return rc;
        }
        {
            ChipSelect cs{*this};
            if (auto rc = send_command(kOpSectorErase, sector); !rc) {
                return rc;
            }
        }
        if (auto rc = wait_write_done(); !rc) { // стирання сектора — десятки мілісекунд
            return rc;
        }
    }
    return {};
}

FlushResult EmergencySpiMemory::write_flash(std::uint32_t dst_addr,
                                            std::span<const std::byte> image) const noexcept {
    if (auto rc = takeover(); !rc) {
        return rc;
    }

    std::size_t written = 0;
    while (written < image.size()) {
        // Перша сторінка може починатися не з її межі — довжину ріжемо так,
        // щоб запис не перескочив через край і не загорнувся на початок сторінки.
        const std::uint32_t page_addr = dst_addr + static_cast<std::uint32_t>(written);
        const std::size_t page_offset = page_addr & (kPageSize - 1);
        const std::size_t chunk = std::min(kPageSize - page_offset, image.size() - written);

        if (auto rc = write_enable(); !rc) {
            return rc;
        }
        {
            ChipSelect cs{*this};
            if (auto rc = send_command(kOpWrite, page_addr); !rc) {
                return rc;
            }
            for (const std::byte byte : image.subspan(written, chunk)) {
                if (auto rc = send(std::to_integer<std::uint8_t>(byte)); !rc) {
                    return rc;
                }
            }
        }
        if (auto rc = wait_write_done(); !rc) {
            return rc;
        }
        written += chunk;
    }
    return verify_head(dst_addr, image);
}

// Швидка перевірка першого слова: у не стертий сектор NOR лише гасить біти,
// тож замість дампа там була б суміш зі старим вмістом.
FlushResult EmergencySpiMemory::verify_head(std::uint32_t dst_addr,
                                            std::span<const std::byte> image) const noexcept {
    ChipSelect cs{*this};
    if (auto rc = send_command(kOpRead, dst_addr); !rc) {
        return rc;
    }
    const std::size_t probe = std::min<std::size_t>(4, image.size());
    for (std::size_t i = 0; i < probe; ++i) {
        const auto answer = xfer(0xFFU);
        if (!answer) {
            return std::unexpected{answer.error()};
        }
        if (*answer != std::to_integer<std::uint8_t>(image[i])) {
            return std::unexpected{FlushError::NotErased};
        }
    }
    return {};
}

FlushResult dump_recorder_to_fram(std::uint32_t dst_addr) noexcept {
    const auto image = diagnostics::recorder().raw_image();
    mcu::clean_dcache(image.data(), image.size());
    return kNvBus.write_fram(dst_addr, image);
}

FlushResult prepare_flash_slot(std::uint32_t dst_addr) noexcept {
    return kNvBus.erase_flash_slot(dst_addr, diagnostics::recorder().raw_image().size());
}

} // namespace embedded::drivers
