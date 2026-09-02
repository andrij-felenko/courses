#include "spi_master.hpp"

#include <atomic>

#include "dma_stream.hpp"

namespace drv {
namespace {

constexpr unsigned sckPin = 5u;
constexpr unsigned misoPin = 6u;
constexpr unsigned mosiPin = 7u;
constexpr unsigned csPin = 4u;
constexpr unsigned spi1AltFunction = 5u;

// Запити SPI1 у DMA2 (таблиця запитів RM0090): TX — потік 3, RX — потік 2, канал 3
mcu::DmaStream txStream{mcu::dma2Base, 3u, 3u};
mcu::DmaStream rxStream{mcu::dma2Base, 2u, 3u};

std::atomic<bool> dmaBusyFlag{false};
SpiMaster::DoneHandler dmaHandler = nullptr;
SpiMaster* dmaOwner = nullptr;

// Стан обміну на перериваннях: спани живуть тут, поки транзакція в польоті
struct IrqTransfer {
    std::span<const std::uint8_t> tx;
    std::span<std::uint8_t> rx;
    std::size_t count = 0;
    std::size_t sent = 0;
    std::size_t received = 0;
    SpiMaster::DoneHandler handler = nullptr;
};

IrqTransfer irqJob;
std::atomic<bool> irqBusyFlag{false};
SpiMaster* irqOwner = nullptr;

std::uint8_t sink = 0u;             // куди зливати непотрібні прийняті байти
const std::uint8_t filler = 0xFFu;  // чим заповнювати лінію під час читання

}  // namespace

SpiMaster::SpiMaster(mcu::SpiRegs& regs, Mode mode, std::uint8_t baudDiv) noexcept
    : regs_{regs}
{
    auto& rcc = mcu::rcc();
    rcc.ahb1enr |= mcu::rcc_bits::gpioaEn;
    rcc.apb2enr |= mcu::rcc_bits::spi1En;
    rcc.ahb1enr |= mcu::rcc_bits::dma2En;

    auto& port = mcu::gpioA();
    for (unsigned pin : {sckPin, misoPin, mosiPin}) {
        mcu::configurePin(port, pin, mcu::PinMode::Alternate, false, spi1AltFunction);
    }
    mcu::configurePin(port, csPin, mcu::PinMode::Output, false);
    mcu::writePin(port, csPin, true);

    // Налаштовувати можна лише вимкнений блок
    regs_.cr1 = 0u;
    regs_.cr2 = 0u;

    // SSM+SSI: внутрішній NSS завжди в одиниці, тому MODF не спрацює
    // від зовнішнього рівня на ніжці, а CS ми смикаємо звичайним GPIO.
    std::uint32_t cr1 = mcu::spi_cr1::mstr | mcu::spi_cr1::ssm | mcu::spi_cr1::ssi;
    cr1 |= static_cast<std::uint32_t>(baudDiv & 7u) << mcu::spi_cr1::brPos;
    if (mode == Mode::Mode1 || mode == Mode::Mode3) {
        cr1 |= mcu::spi_cr1::cpha;
    }
    if (mode == Mode::Mode2 || mode == Mode::Mode3) {
        cr1 |= mcu::spi_cr1::cpol;
    }

    regs_.cr1 = cr1 | mcu::spi_cr1::spe;
    mcu::enableIrq(mcu::Irq::Dma2Stream2);
}

void SpiMaster::selectChip() noexcept { mcu::writePin(mcu::gpioA(), csPin, false); }

void SpiMaster::releaseChip() noexcept { mcu::writePin(mcu::gpioA(), csPin, true); }

void SpiMaster::clearOverrun() noexcept
{
    // Регламент: читання DR, потім читання SR — інакше приймач лишиться глухим
    [[maybe_unused]] volatile std::uint32_t dr = regs_.dr;
    [[maybe_unused]] volatile std::uint32_t sr = regs_.sr;
}

void SpiMaster::recoverModeFault() noexcept
{
    // MODF уже скинув SPE й роль ведучого; прапорець знімає читання SR
    // із наступним записом у CR1, після чого роль треба повернути руками.
    [[maybe_unused]] volatile std::uint32_t sr = regs_.sr;
    const std::uint32_t cr1 = regs_.cr1 & ~mcu::spi_cr1::spe;
    regs_.cr1 = cr1 | mcu::spi_cr1::mstr | mcu::spi_cr1::ssm | mcu::spi_cr1::ssi;
    regs_.cr1 |= mcu::spi_cr1::spe;
}

std::expected<void, SpiError> SpiMaster::waitIdle() noexcept
{
    std::uint32_t left = pollBudget;
    while (regs_.sr & mcu::spi_sr::bsy) {
        if (--left == 0u) {
            return std::unexpected(SpiError::Timeout);
        }
    }
    return {};
}

std::expected<std::uint8_t, SpiError> SpiMaster::transferByte(std::uint8_t value) noexcept
{
    std::uint32_t left = pollBudget;
    while (!(regs_.sr & mcu::spi_sr::txe)) {
        if (regs_.sr & mcu::spi_sr::modf) {
            recoverModeFault();
            return std::unexpected(SpiError::ModeFault);
        }
        if (--left == 0u) {
            return std::unexpected(SpiError::Timeout);
        }
    }

    regs_.dr = value;  // запис у DR запускає генератор SCK

    left = pollBudget;
    while (!(regs_.sr & mcu::spi_sr::rxne)) {
        const std::uint32_t sr = regs_.sr;
        if (sr & mcu::spi_sr::ovr) {
            clearOverrun();
            return std::unexpected(SpiError::Overrun);
        }
        if (sr & mcu::spi_sr::modf) {
            recoverModeFault();
            return std::unexpected(SpiError::ModeFault);
        }
        if (--left == 0u) {
            return std::unexpected(SpiError::Timeout);
        }
    }

    return static_cast<std::uint8_t>(regs_.dr & 0xFFu);
}

std::expected<void, SpiError> SpiMaster::transfer(std::span<const std::uint8_t> tx,
                                                 std::span<std::uint8_t> rx) noexcept
{
    const std::size_t count = tx.empty() ? rx.size() : tx.size();
    if (count == 0u || (!tx.empty() && !rx.empty() && tx.size() != rx.size())) {
        return std::unexpected(SpiError::BadLength);
    }

    for (std::size_t i = 0; i < count; ++i) {
        auto received = transferByte(tx.empty() ? filler : tx[i]);
        if (!received) {
            return std::unexpected(received.error());
        }
        if (!rx.empty()) {
            rx[i] = *received;
        }
    }
    return waitIdle();
}

std::expected<void, SpiError> SpiMaster::startInterrupt(std::span<const std::uint8_t> tx,
                                                       std::span<std::uint8_t> rx,
                                                       DoneHandler handler) noexcept
{
    const std::size_t count = tx.empty() ? rx.size() : tx.size();
    if (count == 0u || (!tx.empty() && !rx.empty() && tx.size() != rx.size())) {
        return std::unexpected(SpiError::BadLength);
    }
    bool expected = false;
    if (!irqBusyFlag.compare_exchange_strong(expected, true, std::memory_order_acq_rel)) {
        return std::unexpected(SpiError::Busy);
    }

    irqJob = IrqTransfer{tx, rx, count, 0u, 0u, handler};
    irqOwner = this;
    selectChip();
    mcu::enableIrq(mcu::Irq::Spi1);

    // TXEIE навмисно лишається вимкненим: буфер передачі порожній майже
    // завжди, і дозволене TXE дало б безкінечний шторм переривань. Наступний
    // байт кладемо в DR у відповідь на RXNE — тоді в польоті рівно одне
    // слово, і OVR не виникає в принципі.
    regs_.cr2 |= mcu::spi_cr2::rxneie | mcu::spi_cr2::errie;
    regs_.dr = irqJob.tx.empty() ? filler : irqJob.tx[0];
    irqJob.sent = 1u;
    return {};
}

void SpiMaster::serviceInterrupt() noexcept
{
    const std::uint32_t sr = regs_.sr;

    auto finish = [this](std::expected<void, SpiError> result) {
        regs_.cr2 &= ~(mcu::spi_cr2::rxneie | mcu::spi_cr2::errie);
        releaseChip();
        irqBusyFlag.store(false, std::memory_order_release);
        if (irqJob.handler != nullptr) {
            irqJob.handler(result);
        }
    };

    if (sr & mcu::spi_sr::modf) {
        recoverModeFault();
        finish(std::unexpected(SpiError::ModeFault));
        return;
    }
    if (sr & mcu::spi_sr::ovr) {
        clearOverrun();
        finish(std::unexpected(SpiError::Overrun));
        return;
    }
    if (!(sr & mcu::spi_sr::rxne)) {
        return;
    }

    const auto received = static_cast<std::uint8_t>(regs_.dr & 0xFFu);
    if (!irqJob.rx.empty()) {
        irqJob.rx[irqJob.received] = received;
    }
    ++irqJob.received;

    if (irqJob.received == irqJob.count) {
        finish({});
        return;
    }
    regs_.dr = irqJob.tx.empty() ? filler : irqJob.tx[irqJob.sent];
    ++irqJob.sent;
}

bool SpiMaster::dmaBusy() const noexcept
{
    return dmaBusyFlag.load(std::memory_order_acquire) ||
           irqBusyFlag.load(std::memory_order_acquire);
}

std::expected<void, SpiError> SpiMaster::startDma(std::span<const std::uint8_t> tx,
                                                 std::span<std::uint8_t> rx,
                                                 DoneHandler handler) noexcept
{
    const std::size_t count = tx.empty() ? rx.size() : tx.size();
    if (count == 0u || (!tx.empty() && !rx.empty() && tx.size() != rx.size())) {
        return std::unexpected(SpiError::BadLength);
    }
    bool expected = false;
    if (!dmaBusyFlag.compare_exchange_strong(expected, true, std::memory_order_acq_rel)) {
        return std::unexpected(SpiError::Busy);
    }

    dmaHandler = handler;
    dmaOwner = this;
    selectChip();

    // Приймальний потік вмикаємо першим: інакше перший же прийнятий байт
    // не мав би кому дістатися і дав би OVR.
    rxStream.start(regs_.dr, mcu::DmaStream::Direction::PeriphToMem,
                   rx.empty() ? &sink : rx.data(), count, !rx.empty(), true);
    txStream.start(regs_.dr, mcu::DmaStream::Direction::MemToPeriph,
                   tx.empty() ? &filler : tx.data(), count, !tx.empty(), false);

    regs_.cr2 |= mcu::spi_cr2::rxdmaen | mcu::spi_cr2::txdmaen;
    return {};
}

namespace {

void finishDma(std::expected<void, SpiError> result) noexcept
{
    auto& regs = mcu::spi1();
    regs.cr2 &= ~(mcu::spi_cr2::rxdmaen | mcu::spi_cr2::txdmaen);
    rxStream.stop();
    txStream.stop();
    rxStream.clearFlags();
    txStream.clearFlags();
    if (dmaOwner != nullptr) {
        (void)dmaOwner->waitIdle();  // добігають кілька тактів, що вже в лінії
    }
    mcu::writePin(mcu::gpioA(), csPin, true);
    dmaBusyFlag.store(false, std::memory_order_release);
    if (dmaHandler != nullptr) {
        dmaHandler(result);
    }
}

}  // namespace

// Приймальний потік завершується останнім, тому саме його прапорець TC
// означає кінець повного обміну.
void serviceRxStreamIrq() noexcept
{
    if (rxStream.transferError()) {
        finishDma(std::unexpected(SpiError::Overrun));
        return;
    }
    if (rxStream.transferComplete()) {
        finishDma({});
    }
}

void serviceSpi1Irq() noexcept
{
    if (irqOwner != nullptr) {
        irqOwner->serviceInterrupt();
    }
}

}  // namespace drv

extern "C" void SPI1_IRQHandler()
{
    drv::serviceSpi1Irq();
}

extern "C" void DMA2_Stream2_IRQHandler()
{
    drv::serviceRxStreamIrq();
}
