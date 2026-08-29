#include "spi_flash.hpp"
#include "telemetry.hpp"

namespace node {
namespace {

constexpr std::uint8_t kCmdWriteEnable = 0x06;
constexpr std::uint8_t kCmdReadStatus1 = 0x05;
constexpr std::uint8_t kCmdReadData    = 0x03;
constexpr std::uint8_t kCmdPageProgram = 0x02;
constexpr std::uint8_t kCmdSectorErase = 0x20;
constexpr std::uint8_t kCmdJedecId     = 0x9F;

constexpr std::uint8_t kStatusBusy = 0x01;
constexpr std::uint8_t kStatusWel  = 0x02;

}  // namespace

void SpiFlash::begin() noexcept {
    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;

    sck_.alternate(5);    // AF5 = SPI1
    miso_.alternate(5);
    mosi_.alternate(5);
    sck_.fast();
    mosi_.fast();

    cs_.mode(mcu::Pin::Mode::Output);
    cs_.write(true);

    // Ведучий, режим 0, SYSCLK/8 = 10 МГц, програмний NSS, кадр 8 бітів.
    SPI1->CR1 = SPI_CR1_MSTR | SPI_CR1_SSM | SPI_CR1_SSI | (2u << SPI_CR1_BR_Pos);
    SPI1->CR2 = SPI_CR2_FRXTH | (7u << SPI_CR2_DS_Pos);
    SPI1->CR1 |= SPI_CR1_SPE;
}

std::uint8_t SpiFlash::transfer(std::uint8_t out) noexcept {
    while ((SPI1->SR & SPI_SR_TXE) == 0u) { }
    // Саме байтовий доступ до DR: 16-бітний запис відправив би два кадри.
    *reinterpret_cast<volatile std::uint8_t*>(&SPI1->DR) = out;
    while ((SPI1->SR & SPI_SR_RXNE) == 0u) { }
    return *reinterpret_cast<volatile std::uint8_t*>(&SPI1->DR);
}

void SpiFlash::sendAddress(std::uint32_t addr) noexcept {
    transfer(static_cast<std::uint8_t>(addr >> 16));
    transfer(static_cast<std::uint8_t>(addr >> 8));
    transfer(static_cast<std::uint8_t>(addr));
}

std::uint8_t SpiFlash::readStatus1() noexcept {
    const ChipSelect select{cs_};
    transfer(kCmdReadStatus1);
    return transfer(0xFF);
}

void SpiFlash::writeEnable() noexcept {
    const ChipSelect select{cs_};
    transfer(kCmdWriteEnable);
}

bool SpiFlash::busy() noexcept {
    return (readStatus1() & kStatusBusy) != 0u;
}

bool SpiFlash::lastOperationAccepted() noexcept {
    return (readStatus1() & (kStatusBusy | kStatusWel)) == 0u;
}

FlashResult<void> SpiFlash::probe() noexcept {
    std::uint8_t id[3]{};
    {
        const ChipSelect select{cs_};
        transfer(kCmdJedecId);
        for (std::uint8_t& byte : id) {
            byte = transfer(0xFF);
        }
    }

    if (id[0] != 0xEF || id[1] != 0x40 || id[2] != 0x18) {
        return std::unexpected{FlashError::WrongChip};
    }
    return {};
}

FlashResult<void> SpiFlash::read(std::uint32_t addr, std::span<std::byte> dst) noexcept {
    if (addr + dst.size() > kFlashTotalSize) return std::unexpected{FlashError::OutOfRange};
    if (busy()) return std::unexpected{FlashError::Busy};

    const ChipSelect select{cs_};
    transfer(kCmdReadData);
    sendAddress(addr);
    for (std::byte& b : dst) {
        b = static_cast<std::byte>(transfer(0xFF));
    }
    return {};
}

FlashResult<void> SpiFlash::startPageProgram(std::uint32_t addr,
                                             std::span<const std::byte> src) noexcept {
    if (src.empty() || src.size() > kFlashPageSize) return std::unexpected{FlashError::OutOfRange};
    // Запис не переходить межу сторінки: чип загорнув би адресу на її
    // початок і тихо зіпсував уже записане.
    if ((addr % kFlashPageSize) + src.size() > kFlashPageSize) {
        return std::unexpected{FlashError::OutOfRange};
    }
    if (addr + src.size() > kFlashTotalSize) return std::unexpected{FlashError::OutOfRange};
    if (busy()) return std::unexpected{FlashError::Busy};

    writeEnable();
    if ((readStatus1() & kStatusWel) == 0u) return std::unexpected{FlashError::NotAccepted};

    const ChipSelect select{cs_};
    transfer(kCmdPageProgram);
    sendAddress(addr);
    for (std::byte b : src) {
        transfer(static_cast<std::uint8_t>(b));
    }
    return {};   // програмування (~0.7 мс) стартує на підйомі CS у деструкторі
}

FlashResult<void> SpiFlash::startSectorErase(std::uint32_t sectorAddr) noexcept {
    if (sectorAddr % kFlashSectorSize != 0u) return std::unexpected{FlashError::OutOfRange};
    if (sectorAddr >= kFlashTotalSize) return std::unexpected{FlashError::OutOfRange};
    if (busy()) return std::unexpected{FlashError::Busy};

    writeEnable();
    if ((readStatus1() & kStatusWel) == 0u) return std::unexpected{FlashError::NotAccepted};

    const ChipSelect select{cs_};
    transfer(kCmdSectorErase);
    sendAddress(sectorAddr);
    return {};   // стирання 4 КБ: 45 мс типово, до 400 мс за паспортом
}

}  // namespace node
