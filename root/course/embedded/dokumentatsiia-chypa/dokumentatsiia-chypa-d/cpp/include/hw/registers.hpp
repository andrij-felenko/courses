/* registers.hpp — карта регістрів, набрана з документації вручну.
 *
 * Джерела: RM0090 (Reference Manual STM32F405/407/415/417), DS8626
 * (Datasheet STM32F407xx), PM0214 (Programming Manual Cortex-M4),
 * ES0182 (Errata Sheet). Кожен рядок структури — рядок карти регістрів;
 * Reserved-слова лишаються на місці, інакше зміщення наступних полів
 * поповзуть. Наприкінці файла — static_assert, механічна звірка з довідником.
 */
#pragma once

#include <cstddef>
#include <cstdint>

#include "hw/mmio.hpp"

namespace hw {

/* --- Блок керування скиданням і тактуванням (RM0090 §6.3) --------------- */
struct RccBlock {
    volatile std::uint32_t cr;          // 0x00 R/W
    volatile std::uint32_t pllcfgr;     // 0x04 R/W
    volatile std::uint32_t cfgr;        // 0x08 R/W
    volatile std::uint32_t cir;         // 0x0C R/W
    volatile std::uint32_t ahb1rstr;    // 0x10 R/W
    volatile std::uint32_t ahb2rstr;    // 0x14 R/W
    volatile std::uint32_t ahb3rstr;    // 0x18 R/W
    volatile std::uint32_t reserved0;   // 0x1C
    volatile std::uint32_t apb1rstr;    // 0x20 R/W
    volatile std::uint32_t apb2rstr;    // 0x24 R/W
    volatile std::uint32_t reserved1[2];// 0x28..0x2C
    volatile std::uint32_t ahb1enr;     // 0x30 R/W
    volatile std::uint32_t ahb2enr;     // 0x34 R/W
    volatile std::uint32_t ahb3enr;     // 0x38 R/W
    volatile std::uint32_t reserved2;   // 0x3C
    volatile std::uint32_t apb1enr;     // 0x40 R/W
    volatile std::uint32_t apb2enr;     // 0x44 R/W
};

/* --- Порт введення-виведення (RM0090 §8.4) ------------------------------ */
struct GpioBlock {
    volatile std::uint32_t moder;   // 0x00 R/W  режим, 2 біти на ніжку
    volatile std::uint32_t otyper;  // 0x04 R/W  push-pull / open-drain
    volatile std::uint32_t ospeedr; // 0x08 R/W
    volatile std::uint32_t pupdr;   // 0x0C R/W  підтяжка
    volatile std::uint32_t idr;     // 0x10 RO   рівень на ніжці
    volatile std::uint32_t odr;     // 0x14 R/W  засувка виходу
    volatile std::uint32_t bsrr;    // 0x18 WO   W1S [15:0], W1C [31:16]
    volatile std::uint32_t lckr;    // 0x1C R/W
    volatile std::uint32_t afr[2];  // 0x20 R/W  номер альтернативної функції
};

/* --- Таймер загального призначення (RM0090 §18.4) ---------------------- */
struct TimerBlock {
    volatile std::uint32_t cr1;         // 0x00 R/W
    volatile std::uint32_t cr2;         // 0x04 R/W
    volatile std::uint32_t smcr;        // 0x08 R/W
    volatile std::uint32_t dier;        // 0x0C R/W
    volatile std::uint32_t sr;          // 0x10 rc_w0 прапорці стану
    volatile std::uint32_t egr;         // 0x14 WO   генерація подій
    volatile std::uint32_t ccmr1;       // 0x18 R/W
    volatile std::uint32_t ccmr2;       // 0x1C R/W
    volatile std::uint32_t ccer;        // 0x20 R/W
    volatile std::uint32_t cnt;         // 0x24 R/W
    volatile std::uint32_t psc;         // 0x28 R/W буферований предільник
    volatile std::uint32_t arr;         // 0x2C R/W буферований поріг
    volatile std::uint32_t reserved0;   // 0x30
    volatile std::uint32_t ccr[4];      // 0x34..0x40
    volatile std::uint32_t reserved1;   // 0x44
    volatile std::uint32_t dcr;         // 0x48 R/W
    volatile std::uint32_t dmar;        // 0x4C R/W
    volatile std::uint32_t opt;         // 0x50 R/W (TIMx_OR)
};

/* --- Контролер шини I2C (RM0090 §27.6) --------------------------------- */
struct I2cBlock {
    volatile std::uint32_t cr1;    // 0x00 R/W
    volatile std::uint32_t cr2;    // 0x04 R/W  поле FREQ
    volatile std::uint32_t oar1;   // 0x08 R/W
    volatile std::uint32_t oar2;   // 0x0C R/W
    volatile std::uint32_t dr;     // 0x10 R/W
    volatile std::uint32_t sr1;    // 0x14 змішаний доступ
    volatile std::uint32_t sr2;    // 0x18 RO
    volatile std::uint32_t ccr;    // 0x1C R/W
    volatile std::uint32_t trise;  // 0x20 R/W
    volatile std::uint32_t fltr;   // 0x24 R/W
};

/* --- Ідентифікація кристала (RM0090 §38.6.1) --------------------------- */
struct DebugBlock {
    volatile std::uint32_t idcode;  // 0x00 RO  REV_ID [31:16], DEV_ID [11:0]
    volatile std::uint32_t cr;      // 0x04 R/W
    volatile std::uint32_t apb1fz;  // 0x08 R/W
    volatile std::uint32_t apb2fz;  // 0x0C R/W
};

/* --- Адреси (RM0090, табл. «Register boundary addresses») --------------- */
inline constexpr std::uintptr_t periph_base = 0x40000000UL;
inline constexpr std::uintptr_t apb1_base   = periph_base;
inline constexpr std::uintptr_t ahb1_base   = periph_base + 0x20000UL;

inline constexpr std::uintptr_t tim2_address   = apb1_base + 0x0000UL;
inline constexpr std::uintptr_t i2c1_address   = apb1_base + 0x5400UL;
inline constexpr std::uintptr_t gpiob_address  = ahb1_base + 0x0400UL;
inline constexpr std::uintptr_t rcc_address    = ahb1_base + 0x3800UL;
inline constexpr std::uintptr_t dbgmcu_address = 0xE0042000UL;
inline constexpr std::uintptr_t nvic_iser_addr = 0xE000E100UL;
inline constexpr std::uintptr_t nvic_icer_addr = 0xE000E180UL;
inline constexpr std::uintptr_t nvic_ipr_addr  = 0xE000E400UL;

[[nodiscard]] inline RccBlock&    rcc()    noexcept { return block<RccBlock>(rcc_address); }
[[nodiscard]] inline GpioBlock&   gpiob()  noexcept { return block<GpioBlock>(gpiob_address); }
[[nodiscard]] inline TimerBlock&  tim2()   noexcept { return block<TimerBlock>(tim2_address); }
[[nodiscard]] inline I2cBlock&    i2c1()   noexcept { return block<I2cBlock>(i2c1_address); }
[[nodiscard]] inline DebugBlock&  dbgmcu() noexcept { return block<DebugBlock>(dbgmcu_address); }

/* --- Бітові поля ------------------------------------------------------- */
namespace rcc_bits {
inline constexpr std::uint32_t ahb1en_gpiob = bit(1);
inline constexpr std::uint32_t apb1en_tim2  = bit(0);
inline constexpr std::uint32_t apb1en_i2c1  = bit(21);
inline constexpr std::uint32_t apb1rst_tim2 = bit(0);
inline constexpr std::uint32_t apb1rst_i2c1 = bit(21);
} // namespace rcc_bits

namespace tim_bits {
inline constexpr std::uint32_t cr1_cen  = bit(0);
inline constexpr std::uint32_t cr1_urs  = bit(2);
inline constexpr std::uint32_t cr1_arpe = bit(7);
inline constexpr std::uint32_t dier_uie = bit(0);
inline constexpr std::uint32_t sr_uif   = bit(0);   // доступ rc_w0
inline constexpr std::uint32_t egr_ug   = bit(0);
} // namespace tim_bits

namespace i2c_bits {
inline constexpr std::uint32_t cr1_pe    = bit(0);
inline constexpr std::uint32_t cr1_stop  = bit(9);
inline constexpr std::uint32_t cr1_swrst = bit(15);
inline constexpr std::uint32_t sr2_busy  = bit(1);  // RO
inline constexpr std::uint32_t fltr_anoff = bit(4);
inline constexpr std::uint32_t cr2_freq_mask = 0x3FU;
} // namespace i2c_bits

namespace gpio_mode {
inline constexpr std::uint32_t input  = 0U;
inline constexpr std::uint32_t output = 1U;
inline constexpr std::uint32_t alternate = 2U;
inline constexpr std::uint32_t analog = 3U;
} // namespace gpio_mode

namespace gpio_pull {
inline constexpr std::uint32_t none = 0U;
inline constexpr std::uint32_t up   = 1U;
inline constexpr std::uint32_t down = 2U;
} // namespace gpio_pull

/* DS8626, таблиця альтернативних функцій: I2C1 сидить на PB6/PB7, AF4. */
inline constexpr unsigned i2c1_scl_pin = 6U;
inline constexpr unsigned i2c1_sda_pin = 7U;
inline constexpr std::uint32_t i2c1_af = 4U;

/* PM0214 §4.2: дозвіл вектора переривання. */
inline constexpr unsigned tim2_irqn = 28U;

inline void nvic_enable(unsigned irqn, std::uint8_t priority) noexcept
{
    auto* ipr  = reinterpret_cast<volatile std::uint8_t*>(nvic_ipr_addr);
    auto* iser = reinterpret_cast<volatile std::uint32_t*>(nvic_iser_addr);

    ipr[irqn] = static_cast<std::uint8_t>(priority << 4);  // значущі лише старші 4 біти
    iser[irqn / 32U] = bit(irqn % 32U);                    // W1S: сусідів не чіпає
    dsb();
    isb();
}

inline void nvic_disable(unsigned irqn) noexcept
{
    auto* icer = reinterpret_cast<volatile std::uint32_t*>(nvic_icer_addr);
    icer[irqn / 32U] = bit(irqn % 32U);
    dsb();
}

/* --- Звірка набраної карти з довідником -------------------------------- */
static_assert(offsetof(RccBlock, apb1rstr) == 0x20, "RCC_APB1RSTR: зміщення 0x20");
static_assert(offsetof(RccBlock, ahb1enr)  == 0x30, "RCC_AHB1ENR: зміщення 0x30");
static_assert(offsetof(RccBlock, apb1enr)  == 0x40, "RCC_APB1ENR: зміщення 0x40");
static_assert(offsetof(GpioBlock, bsrr)    == 0x18, "GPIOx_BSRR: зміщення 0x18");
static_assert(offsetof(GpioBlock, afr)     == 0x20, "GPIOx_AFRL: зміщення 0x20");
static_assert(offsetof(TimerBlock, sr)     == 0x10, "TIMx_SR: зміщення 0x10");
static_assert(offsetof(TimerBlock, psc)    == 0x28, "TIMx_PSC: зміщення 0x28");
static_assert(offsetof(TimerBlock, arr)    == 0x2C, "TIMx_ARR: зміщення 0x2C");
static_assert(offsetof(I2cBlock, sr2)      == 0x18, "I2C_SR2: зміщення 0x18");
static_assert(offsetof(I2cBlock, fltr)     == 0x24, "I2C_FLTR: зміщення 0x24");

} // namespace hw
