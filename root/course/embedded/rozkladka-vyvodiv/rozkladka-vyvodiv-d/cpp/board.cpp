#include "gpio.hpp"

#include <array>
#include <optional>

namespace {

using namespace mcu::gpio;

constexpr std::uint8_t kLedPin = 6;   // LED_STATUS на PB6

// Таблиці НЕ constexpr: GPIOA і сусіди — це reinterpret_cast адреси,
// у сталому виразі його не обчислити. Тому звичайні функції-конструктори.

// Таблиця виводів плати — одне джерело правди, звірене зі схемою.
// Рядки SWDIO/SWCLK стоять тут навмисно: розпіновка мусить називати
// системні ніжки, інакше їх «знайде» хтось інший.
[[nodiscard]] std::array<PinPlan, 13> board_layout() noexcept
{
    return {{
        {"SWDIO",      {GPIOA, 13}, Mode::Alternate, 0, Speed::VeryHigh, Pull::Up,   Drive::PushPull,  ElectricalClass::System, 0},
        {"SWCLK",      {GPIOA, 14}, Mode::Alternate, 0, Speed::VeryHigh, Pull::Down, Drive::PushPull,  ElectricalClass::System, 0},
        {"SPI1_SCK",   {GPIOA,  5}, Mode::Alternate, 5, Speed::High,     Pull::None, Drive::PushPull,  ElectricalClass::Tta,    0},
        {"SPI1_MISO",  {GPIOA,  6}, Mode::Alternate, 5, Speed::High,     Pull::None, Drive::PushPull,  ElectricalClass::Tta,    0},
        {"SPI1_MOSI",  {GPIOA,  7}, Mode::Alternate, 5, Speed::High,     Pull::None, Drive::PushPull,  ElectricalClass::Tta,    0},
        {"FLASH_CS",   {GPIOB,  0}, Mode::Output,    0, Speed::Medium,   Pull::Up,   Drive::PushPull,  ElectricalClass::Tta,    0},
        {"USART1_TX",  {GPIOA,  9}, Mode::Alternate, 7, Speed::Medium,   Pull::Up,   Drive::PushPull,  ElectricalClass::Ft,     0},
        {"USART1_RX",  {GPIOA, 10}, Mode::Alternate, 7, Speed::Medium,   Pull::Up,   Drive::PushPull,  ElectricalClass::Ft,     0},
        {"I2C1_SCL",   {GPIOB,  8}, Mode::Alternate, 4, Speed::Medium,   Pull::None, Drive::OpenDrain, ElectricalClass::Ft,     0},
        {"I2C1_SDA",   {GPIOB,  9}, Mode::Alternate, 4, Speed::Medium,   Pull::None, Drive::OpenDrain, ElectricalClass::Ft,     0},
        {"VBAT_SENSE", {GPIOA,  0}, Mode::Analog,    0, Speed::Low,      Pull::None, Drive::PushPull,  ElectricalClass::Tta,    0},
        {"LED_STATUS", {GPIOB, kLedPin}, Mode::Output, 0, Speed::Low,    Pull::None, Drive::PushPull,  ElectricalClass::Ft,     8},
        {"RTC_TICK",   {GPIOC, 13}, Mode::Output,    0, Speed::Low,      Pull::None, Drive::PushPull,  ElectricalClass::Backup, 1},
    }};
}

// Хибний запит 1: підсвічування дисплея повісили на лінію даних SWD.
[[nodiscard]] std::array<PinPlan, 1> request_backlight() noexcept
{
    return {{
        {"BACKLIGHT_EN", {GPIOA, 13}, Mode::Output, 0, Speed::Low, Pull::None, Drive::PushPull, ElectricalClass::Ft, 0},
    }};
}

// Хибний запит 2: світлодіод на 8 мА у домені резервного живлення.
[[nodiscard]] std::array<PinPlan, 1> request_rtc_led() noexcept
{
    return {{
        {"LED_ALARM", {GPIOC, 13}, Mode::Output, 0, Speed::Low, Pull::None, Drive::PushPull, ElectricalClass::Backup, 8},
    }};
}

// Хибний запит 3: вісім індикаторів по 15 мА на одному порту = 120 мА.
[[nodiscard]] std::array<PinPlan, 8> request_led_bank() noexcept
{
    std::array<PinPlan, 8> bank{};
    static constexpr std::array<std::string_view, 8> names{
        "LED_BAR0", "LED_BAR1", "LED_BAR2", "LED_BAR3",
        "LED_BAR4", "LED_BAR5", "LED_BAR6", "LED_BAR7"};

    for (std::uint8_t i = 0; i < bank.size(); ++i) {
        bank[i] = PinPlan{names[i], {GPIOE, i}, Mode::Output, 0, Speed::Low,
                          Pull::None, Drive::PushPull, ElectricalClass::Ft, 15};
    }
    return bank;
}

// Звіт лишається в пам'яті: SWO ми щойно віддали під GPIO, тож дивиться
// на нього відлагоджувач (у карті пам'яті — g_report).
struct Trial {
    std::string_view    what{};
    std::optional<Fault> fault{};
    std::string_view    reason{};
};

std::array<Trial, 5> g_report{};
volatile unsigned    g_report_len = 0;
volatile unsigned    g_rejected   = 0;
volatile unsigned    g_port_b_ma  = 0;
volatile unsigned    g_chip_ma    = 0;

bool record(std::string_view what, const std::expected<void, Fault>& result) noexcept
{
    if (g_report_len < g_report.size()) {
        Trial& slot = g_report[g_report_len++];
        slot.what = what;
        if (!result) {
            slot.fault  = result.error();
            slot.reason = describe(result.error().reason);
        }
    }
    if (!result) {
        ++g_rejected;
    }
    return result.has_value();
}

void delay_ticks(std::uint32_t ticks) noexcept
{
    for (volatile std::uint32_t i = 0; i < ticks; ++i) {
        __NOP();
    }
}

void led_blink(unsigned times) noexcept
{
    for (unsigned i = 0; i < times; ++i) {
        GPIOB->BSRR = (1u << kLedPin);              // увімкнути
        delay_ticks(400000);
        GPIOB->BSRR = (1u << (kLedPin + 16u));      // вимкнути
        delay_ticks(400000);
    }
}

}  // namespace

int main()
{
    // Спершу розкладка плати, потім замок: замкнені ніжки вже не змінити.
    const bool board_ok = record("таблиця плати", apply(board_layout()));

    if (board_ok) {
        record("замок SWD", secure_debug_port());
    }

    // Три хибні запити. Кожен відкидається ще до запису в регістр.
    record("підсвічування на PA13", apply(request_backlight()));
    record("LED 8 мА на PC13",      apply(request_rtc_led()));
    record("вісім LED по 15 мА",    apply(request_led_bank()));

    g_port_b_ma = port_budget_ma(GPIOB);
    g_chip_ma   = chip_budget_ma();

    while (true) {
        if (!board_ok) {
            // Плата не зійшлася з межами — світимо безперервно, не працюємо.
            GPIOB->BSRR = (1u << kLedPin);
            delay_ticks(2000000);
            continue;
        }
        led_blink(g_rejected);   // стільки спалахів, скільки запитів відкинуто
        delay_ticks(3000000);
    }
}
