#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <concepts>
#include "stm32h7xx.h"

namespace hal::qspi {

enum class Error : uint8_t {
    Timeout,
    InvalidDevice,
    Busy,
    TransferFailed
};

struct FlashConfig {
    uint32_t base_address = 0x90000000U;
    uint32_t size_bytes   = 16 * 1024 * 1024; // 16 МБайт
    uint8_t  dummy_cycles = 4;
    uint8_t  prescaler    = 1;                // 100 МГц @ 200 МГц AHB
};

class QspiXipController {
public:
    explicit QspiXipController(const FlashConfig& cfg) noexcept : config_(cfg) {}

    // Драйвер володіє апаратним модулем: заборона копіювання
    QspiXipController(const QspiXipController&) = delete;
    QspiXipController& operator=(const QspiXipController&) = delete;

    [[nodiscard]] std::expected<void, Error> init_and_map() noexcept {
        init_gpio();
        init_peripheral();

        if (auto res = verify_jedec_id(); !res) {
            return std::unexpected(res.error());
        }

        if (auto res = enable_quad_mode(); !res) {
            return std::unexpected(res.error());
        }

        configure_memory_mapped_xip();
        configure_mpu_and_cache();

        return {};
    }

    [[nodiscard]] std::span<const uint8_t> memory_view() const noexcept {
        return {reinterpret_cast<const uint8_t*>(config_.base_address), config_.size_bytes};
    }

private:
    FlashConfig config_;

    static constexpr uint8_t CMD_READ_JEDEC_ID     = 0x9F;
    static constexpr uint8_t CMD_WRITE_ENABLE      = 0x06;
    static constexpr uint8_t CMD_READ_STATUS_REG1  = 0x05;
    static constexpr uint8_t CMD_WRITE_STATUS_REG2 = 0x31;
    static constexpr uint8_t CMD_FAST_READ_QUAD_IO = 0xEB;
    static constexpr uint8_t MODE_CONTINUOUS_READ  = 0xA5;

    void init_gpio() noexcept {
        RCC->AHB3ENR |= RCC_AHB3ENR_QSPIEN;
        RCC->AHB4ENR |= RCC_AHB4ENR_GPIOBEN | RCC_AHB4ENR_GPIOEEN;

        // Налаштування виводів: PB2 (CLK), PB6 (CS), PE7..PE10 (IO0..IO3)
        GPIOB->OSPEEDR |= (3U << 4) | (3U << 12);
        GPIOE->OSPEEDR |= (3U << 14) | (3U << 16) | (3U << 18) | (3U << 20);

        GPIOB->PUPDR |= (1U << 12); // Pull-up CS#
        GPIOE->PUPDR |= (1U << 14) | (1U << 16) | (1U << 18) | (1U << 20);

        GPIOB->AFR[0] |= (9U << 8) | (10U << 24);
        GPIOE->AFR[0] |= (10U << 28);
        GPIOE->AFR[1] |= 10U | (10U << 4) | (10U << 8);

        GPIOB->MODER = (GPIOB->MODER & ~((3U << 4) | (3U << 12))) | ((2U << 4) | (2U << 12));
        GPIOE->MODER = (GPIOE->MODER & ~0x003F4000U) | 0x002A8000U;
    }

    void init_peripheral() noexcept {
        QUADSPI->CR = (config_.prescaler << QUADSPI_CR_PRESCALER_Pos) | QUADSPI_CR_SSHIFT | QUADSPI_CR_EN;
        QUADSPI->DCR = (23U << QUADSPI_DCR_FSIZE_Pos) | (4U << QUADSPI_DCR_CSHT_Pos);
    }

    std::expected<void, Error> verify_jedec_id() noexcept {
        uint8_t id[3] = {};
        QUADSPI->DLR = sizeof(id) - 1;
        QUADSPI->CCR = (1U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_DMODE_Pos) |
                       (1U << QUADSPI_CCR_IMODE_Pos) | CMD_READ_JEDEC_ID;

        for (auto& byte : id) {
            while (!(QUADSPI->SR & (QUADSPI_SR_FTF | QUADSPI_SR_TCF))) {}
            byte = static_cast<uint8_t>(QUADSPI->DR);
        }
        wait_idle();

        if (id[0] != 0xEF) { // Код виробника Winbond
            return std::unexpected(Error::InvalidDevice);
        }
        return {};
    }

    std::expected<void, Error> enable_quad_mode() noexcept {
        // Дозвіл запису
        QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_IMODE_Pos) | CMD_WRITE_ENABLE;
        wait_idle();

        // Запис у Status Register 2 біта QE = 1
        QUADSPI->DLR = 0;
        QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_DMODE_Pos) |
                       (1U << QUADSPI_CCR_IMODE_Pos) | CMD_WRITE_STATUS_REG2;
        *(reinterpret_cast<volatile uint8_t*>(&QUADSPI->DR)) = 0x02; // Біт QE
        wait_idle();

        // Апаратне автоопитування прапорця зайнятості WIP
        QUADSPI->PSMKR = 0x01;
        QUADSPI->PSMAR = 0x00;
        QUADSPI->PIR   = 0x10;
        QUADSPI->CR   |= (QUADSPI_CR_APMS | QUADSPI_CR_PMM);
        QUADSPI->CCR   = (2U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_DMODE_Pos) |
                         (1U << QUADSPI_CCR_IMODE_Pos) | CMD_READ_STATUS_REG1;

        uint32_t timeout = 1'000'000;
        while (!(QUADSPI->SR & QUADSPI_SR_SMF)) {
            if (--timeout == 0) {
                QUADSPI->CR |= QUADSPI_CR_ABORT;
                wait_idle();
                return std::unexpected(Error::Timeout);
            }
        }
        QUADSPI->FCR = QUADSPI_FCR_CSMF;
        wait_idle();
        return {};
    }

    void configure_memory_mapped_xip() noexcept {
        QUADSPI->ABR = MODE_CONTINUOUS_READ;
        QUADSPI->CCR = (3U << QUADSPI_CCR_FMODE_Pos) | QUADSPI_CCR_SIOO |
                       (config_.dummy_cycles << QUADSPI_CCR_DCYC_Pos) |
                       (1U << QUADSPI_CCR_ABSIZE_Pos) | (3U << QUADSPI_CCR_ABMODE_Pos) |
                       (2U << QUADSPI_CCR_ADSIZE_Pos) | (3U << QUADSPI_CCR_ADMODE_Pos) |
                       (3U << QUADSPI_CCR_DMODE_Pos)  | (1U << QUADSPI_CCR_IMODE_Pos)  |
                       CMD_FAST_READ_QUAD_IO;
    }

    void configure_mpu_and_cache() noexcept {
        ARM_MPU_Disable();
        ARM_MPU_SetRegion(
            ARM_MPU_RBAR(0, config_.base_address),
            ARM_MPU_RASR(
                0, ARM_MPU_AP_RO,
                ARM_MPU_ACCESS_NORMAL(ARM_MPU_CACHEP_WB_WRA, ARM_MPU_CACHEP_WB_WRA),
                0x00, ARM_MPU_REGION_SIZE_16MB
            )
        );
        ARM_MPU_Enable(MPU_CTRL_PRIVDEFENA_Msk);

        SCB_InvalidateICache();
        SCB_EnableICache();
        SCB_InvalidateDCache();
        SCB_EnableDCache();
    }

    void wait_idle() noexcept {
        while (!(QUADSPI->SR & QUADSPI_SR_TCF) && (QUADSPI->SR & QUADSPI_SR_BUSY)) {}
        QUADSPI->FCR = QUADSPI_FCR_CTCF;
        while (QUADSPI->SR & QUADSPI_SR_BUSY) {}
    }
};

} // namespace hal::qspi
