// SPI1 + DMA1_Channel3, PA4 CS, PA5 SCK, PA6 MISO, PA7 MOSI.
// Мікросхема сімейства W25Q/AT25: сторінка 256 байтів, Deep Power-Down 0xB9.
#include "SpiFlashDriver.hpp"
#include "Mcu.hpp"

#include <new>
#include "stm32l4xx.h"

namespace emb::drv {
namespace {

constexpr std::byte CmdWren{0x06};
constexpr std::byte CmdPageProgram{0x02};
constexpr std::byte CmdReadStatus{0x05};
constexpr std::byte CmdDeepPowerDown{0xB9};
constexpr std::byte CmdReleaseDpd{0xAB};
constexpr std::byte StatusWip{0x01};

constexpr std::uint32_t kCsPin = 4;
constexpr std::uint32_t kSpins = 100'000;
// tRES1 — вихід із Deep Power-Down триває до 3 мкс; на 80 МГц це ~240 тактів.
constexpr std::uint32_t kResSpins = 300;

// Місце під блокування, яке переживає область видимості виклику.
alignas(pm::ScopedPowerLock) std::byte g_lockStorage[sizeof(pm::ScopedPowerLock)];

void csLow() noexcept  { GPIOA->BSRR = (1u << (kCsPin + 16u)); }
void csHigh() noexcept { GPIOA->BSRR = (1u << kCsPin); }

} // namespace

bool SpiFlashDriver::xfer(std::byte out, std::byte* in) noexcept
{
    std::uint32_t spins = kSpins;
    while ((SPI1->SR & SPI_SR_TXE) == 0u) {
        if (spins-- == 0u) { ++m_errors; return false; }
    }
    *reinterpret_cast<volatile std::uint8_t*>(&SPI1->DR) = std::to_integer<std::uint8_t>(out);

    spins = kSpins;
    while ((SPI1->SR & SPI_SR_RXNE) == 0u) {
        if (spins-- == 0u) { ++m_errors; return false; }
    }
    const auto got = std::byte{*reinterpret_cast<volatile std::uint8_t*>(&SPI1->DR)};
    if (in != nullptr) {
        *in = got;
    }
    return true;
}

// Після передачі через DMA приймальний FIFO лишається повним — інакше
// наступний обмін прочитає старе сміття.
void SpiFlashDriver::drainRx() noexcept
{
    std::uint32_t spins = kSpins;
    while ((SPI1->SR & SPI_SR_FRLVL) != 0u && spins-- != 0u) {
        static_cast<void>(*reinterpret_cast<volatile std::uint8_t*>(&SPI1->DR));
    }
}

void SpiFlashDriver::configurePins() noexcept
{
    GPIOA->MODER = (GPIOA->MODER & ~(0xFFu << (kCsPin * 2u)))
                 | (0x01u << (4u * 2u))   // PA4 — вихід CS
                 | (0x02u << (5u * 2u))   // PA5 — AF5 SCK
                 | (0x02u << (6u * 2u))   // PA6 — AF5 MISO
                 | (0x02u << (7u * 2u));  // PA7 — AF5 MOSI
    GPIOA->AFR[0] = (GPIOA->AFR[0] & ~0xFFF00000u)
                  | (5u << 20u) | (5u << 24u) | (5u << 28u);
    GPIOA->OSPEEDR |= (0x03u << (5u * 2u)) | (0x03u << (7u * 2u));
    csHigh();
}

void SpiFlashDriver::init() noexcept
{
    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;
    RCC->AHB1ENR |= RCC_AHB1ENR_DMA1EN;
    static_cast<void>(RCC->AHB1ENR);

    configurePins();

    // Майстер, fPCLK/8 = 10 МГц, програмний NSS, кадр 8 бітів, поріг FIFO 1 байт.
    SPI1->CR1 = SPI_CR1_MSTR | SPI_CR1_SSM | SPI_CR1_SSI | (2u << SPI_CR1_BR_Pos);
    SPI1->CR2 = SPI_CR2_FRXTH | (7u << SPI_CR2_DS_Pos);
    SPI1->CR1 |= SPI_CR1_SPE;

    // DMA1 канал 3 — це SPI1_TX (C3S = 1).
    DMA1_CSELR->CSELR = (DMA1_CSELR->CSELR & ~DMA_CSELR_C3S) | (1u << DMA_CSELR_C3S_Pos);
    DMA1_Channel3->CPAR = reinterpret_cast<std::uint32_t>(&SPI1->DR);
    DMA1_Channel3->CCR  = DMA_CCR_DIR | DMA_CCR_MINC | DMA_CCR_TCIE | DMA_CCR_TEIE;
    NVIC_SetPriority(DMA1_Channel3_IRQn, 2);
    NVIC_EnableIRQ(DMA1_Channel3_IRQn);

    m_state = State::Idle;
    pm::PowerManager::instance().registerClient(this);
}

std::expected<void, FlashError> SpiFlashDriver::writePageAsync(
    std::uint32_t address, std::span<const std::byte> data) noexcept
{
    if (m_state != State::Idle)      return std::unexpected(FlashError::Busy);
    if (data.empty())                return std::unexpected(FlashError::EmptyBuffer);
    if (data.size() > PageSize)      return std::unexpected(FlashError::TooLarge);
    if ((address % PageSize) + data.size() > PageSize) {
        return std::unexpected(FlashError::PageCrossing);
    }

    // Блокування береться ДО першої команди й тримається до кінця циклу запису.
    m_lock = new (g_lockStorage) pm::ScopedPowerLock{pm::Lock::NoStop};

    csLow();
    const bool wren = xfer(CmdWren);
    csHigh();
    if (!wren) {
        abort();
        return std::unexpected(FlashError::BusTimeout);
    }

    csLow();
    const auto addr = static_cast<std::uint32_t>(address);
    const bool header = xfer(CmdPageProgram)
                     && xfer(std::byte{static_cast<std::uint8_t>(addr >> 16)})
                     && xfer(std::byte{static_cast<std::uint8_t>(addr >> 8)})
                     && xfer(std::byte{static_cast<std::uint8_t>(addr)});
    if (!header) {
        abort();
        return std::unexpected(FlashError::BusTimeout);
    }

    m_state = State::Dma;
    DMA1_Channel3->CCR  &= ~DMA_CCR_EN;
    DMA1_Channel3->CMAR  = reinterpret_cast<std::uint32_t>(data.data());
    DMA1_Channel3->CNDTR = static_cast<std::uint32_t>(data.size());
    DMA1->IFCR = DMA_IFCR_CGIF3;
    DMA1_Channel3->CCR |= DMA_CCR_EN;
    SPI1->CR2 |= SPI_CR2_TXDMAEN;
    return {};
}

void SpiFlashDriver::abort() noexcept
{
    DMA1_Channel3->CCR &= ~DMA_CCR_EN;
    SPI1->CR2 &= ~SPI_CR2_TXDMAEN;
    drainRx();
    csHigh();
    m_state = State::Idle;
    if (m_lock != nullptr) {
        m_lock->~ScopedPowerLock(); // блокування знімається тут, а не «колись»
        m_lock = nullptr;
    }
}

std::expected<std::byte, FlashError> SpiFlashDriver::readStatus() noexcept
{
    std::byte sr{0xFF};
    csLow();
    const bool ok = xfer(CmdReadStatus) && xfer(std::byte{0xFF}, &sr);
    csHigh();
    if (!ok) {
        return std::unexpected(FlashError::BusTimeout);
    }
    return sr;
}

void SpiFlashDriver::poll() noexcept
{
    if (m_state != State::Program) {
        return;
    }
    const auto sr = readStatus();
    if (!sr) {
        ++m_errors;
        abort();
        return;
    }
    if ((*sr & StatusWip) == std::byte{0}) {
        m_state = State::Idle;
        if (m_lock != nullptr) {
            m_lock->~ScopedPowerLock(); // аж тепер глибокий сон безпечний
            m_lock = nullptr;
        }
    }
}

bool SpiFlashDriver::preSleep(pm::Mode targetMode) noexcept
{
    if (m_state != State::Idle) {
        return false; // під час запису мікросхему не чіпаємо
    }
    if (!pm::atLeastAsDeep(targetMode, pm::Mode::Stop)) {
        return true;  // у Sleep тактування SPI не зникає
    }

    // Одна команда на 10 МГц — це одиниці мікросекунд, у бюджет входу вкладається.
    csLow();
    const bool ok = xfer(CmdDeepPowerDown);
    csHigh();
    if (!ok) {
        ++m_errors;
        return false; // шина не відповіла — краще не засинати з живою мікросхемою
    }

    // Ізоляція виводів: аналоговий стан прибирає струм через підтяжки і
    // паразитне живлення мікросхеми через її захисні діоди.
    m_savedModer = GPIOA->MODER;
    GPIOA->MODER |= (0x03u << (4u * 2u)) | (0x03u << (5u * 2u))
                  | (0x03u << (6u * 2u)) | (0x03u << (7u * 2u));
    RCC->APB2ENR &= ~RCC_APB2ENR_SPI1EN;
    m_deepPowerDown = true;
    return true;
}

void SpiFlashDriver::postWakeup(pm::Mode) noexcept
{
    if (!m_deepPowerDown) {
        return;
    }
    RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;
    static_cast<void>(RCC->APB2ENR);
    // Регістри SPI1 переживають Stop разом із доменом VCORE — вертаємо лише виводи.
    GPIOA->MODER = m_savedModer;
    csHigh();

    csLow();
    static_cast<void>(xfer(CmdReleaseDpd));
    csHigh();
    for (std::uint32_t i = 0; i < kResSpins; ++i) {
        __NOP(); // витримка tRES1 до першої робочої команди
    }
    m_deepPowerDown = false;
}

void SpiFlashDriver::onDmaIrq() noexcept
{
    const std::uint32_t isr = DMA1->ISR;

    if ((isr & DMA_ISR_TEIF3) != 0u) {
        DMA1->IFCR = DMA_IFCR_CGIF3;
        ++m_errors;
        abort();
        return;
    }
    if ((isr & DMA_ISR_TCIF3) == 0u) {
        return;
    }
    DMA1->IFCR = DMA_IFCR_CGIF3;
    DMA1_Channel3->CCR &= ~DMA_CCR_EN;
    SPI1->CR2 &= ~SPI_CR2_TXDMAEN;

    // DMA скінчив віддавати байти у FIFO, але зсувний регістр ще жене останній:
    // зняти CS раніше за BSY означає обрубати кадр.
    std::uint32_t spins = kSpins;
    while ((SPI1->SR & SPI_SR_BSY) != 0u && spins-- != 0u) {
    }
    drainRx();
    csHigh();

    // Блокування НЕ знімаємо: мікросхема ще пече сторінку (до 3 мс), і команда
    // Deep Power-Down у цей час її зіпсує. Зніме poll() з головного циклу.
    m_state = State::Program;
}

} // namespace emb::drv

extern "C" void DMA1_Channel3_IRQHandler(void)
{
    emb::drv::SpiFlashDriver::instance().onDmaIrq();
}
