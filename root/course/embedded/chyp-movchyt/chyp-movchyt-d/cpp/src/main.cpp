// main.cpp — сканер шини I2C на STM32: адаптер над HAL, звіт і розбір
// адреси, надрукованої в даташиті.
#include "i2c/address.hpp"
#include "i2c/scanner.hpp"

#include "stm32f4xx_hal.h"

#include <algorithm>
#include <array>
#include <cstdio>
#include <format>
#include <optional>
#include <string_view>
#include <utility>

extern "C" void SystemClock_Config(void); // із згенерованого CubeMX модуля
extern "C" void Error_Handler(void);

namespace {

I2C_HandleTypeDef hi2c1{};

// Друк без купи: форматуємо в буфер на стеку й віддаємо готовий рядок.
template <class... Args>
void say(std::format_string<Args...> fmt, Args&&... args)
{
    std::array<char, 192> line{};
    const auto res =
        std::format_to_n(line.data(), line.size() - 1, fmt, std::forward<Args>(args)...);
    *res.out = '\0';
    std::fputs(line.data(), stdout);
}

struct Hint {
    std::uint8_t addr7;
    std::string_view text;
};

// Підказка «що зазвичай сидить за цією адресою» — саме підказка: збіги
// адрес у різних родин мікросхем звичайні й саме вони збивають з пантелику.
constexpr auto kHints = std::to_array<Hint>({
    { 0x0D, "QMC5883L (магнітометр)" },
    { 0x1E, "HMC5883L (магнітометр)" },
    { 0x23, "BH1750 (люксметр)" },
    { 0x27, "PCF8574 (розширювач портів, типовий модуль LCD)" },
    { 0x39, "APDS-9960 (жести й освітленість)" },
    { 0x3C, "SSD1306 (OLED-дисплей)" },
    { 0x40, "INA219 (монітор струму)" },
    { 0x48, "ADS1115 (зовнішній АЦП)" },
    { 0x50, "AT24Cxx (EEPROM, займає весь блок 0x50..0x57)" },
    { 0x53, "ADXL345 (акселерометр; конфлікт з блоком EEPROM)" },
    { 0x5A, "MLX90614 (безконтактний термометр)" },
    { 0x68, "MPU6050 з AD0=0 або DS3231 (годинник)" },
    { 0x69, "MPU6050 з AD0=1" },
    { 0x76, "BMP280/BME280 з SDO=0" },
    { 0x77, "BMP280/BME280 з SDO=1" },
});

[[nodiscard]] std::optional<std::string_view> hint_for(i2c::Address addr)
{
    const auto it = std::ranges::find(kHints, addr.value(), &Hint::addr7);
    if (it == kHints.end()) {
        return std::nullopt;
    }
    return it->text;
}

// Адаптер над STM32 HAL: рівно ті три дії, яких хоче концепт Master.
class HalMaster {
  public:
    explicit HalMaster(I2C_HandleTypeDef& bus) noexcept : bus_{bus} {}

    [[nodiscard]] bool busy() const noexcept
    {
        return __HAL_I2C_GET_FLAG(&bus_, I2C_FLAG_BUSY) != RESET;
    }

    [[nodiscard]] i2c::Probe probe(i2c::Address addr) noexcept
    {
        // HAL приймає вже зсунутий байт кадру — саме тому write_byte().
        const HAL_StatusTypeDef st =
            HAL_I2C_IsDeviceReady(&bus_, addr.write_byte(), kTrials, kTimeoutMs);
        const std::uint32_t err = HAL_I2C_GetError(&bus_);
        drop_error_state();

        if (st == HAL_OK) {
            return i2c::Probe::ack;
        }
        if (st == HAL_BUSY || st == HAL_TIMEOUT) {
            return i2c::Probe::busy; // кадр не почався або застряг на SCL
        }
        if ((err & (HAL_I2C_ERROR_BERR | HAL_I2C_ERROR_ARLO | HAL_I2C_ERROR_OVR)) != 0u) {
            return i2c::Probe::error;
        }
        return i2c::Probe::nack; // самий лише AF: адреса порожня
    }

    void settle() noexcept { HAL_Delay(1); }

  private:
    void drop_error_state() noexcept
    {
        // NACK порожньої адреси HAL позначає прапорцем AF. Для сканера це
        // штатна відповідь шини, і залишковий стан помилки треба прибрати,
        // інакше наступна проба впаде ще до START.
        __HAL_I2C_CLEAR_FLAG(&bus_, I2C_FLAG_AF);
        bus_.ErrorCode = HAL_I2C_ERROR_NONE;
        if (HAL_I2C_GetState(&bus_) == HAL_I2C_STATE_ERROR) {
            bus_.State = HAL_I2C_STATE_READY;
        }
    }

    static constexpr std::uint32_t kTrials = 1;
    static constexpr std::uint32_t kTimeoutMs = 5;

    I2C_HandleTypeDef& bus_;
};

void init_i2c()
{
    hi2c1.Instance = I2C1;
    // Для першого оживлення беремо 100 кГц: на 400 кГц завалені фронти
    // вбивають кадр раніше, ніж ми встигнемо побачити ACK.
    hi2c1.Init.ClockSpeed = 100000;
    hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
    hi2c1.Init.OwnAddress1 = 0;
    hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
    hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
    hi2c1.Init.OwnAddress2 = 0;
    hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
    // Ведений має право притримати SCL: заборона розтягування такту
    // обриває обмін з повільним АЦП чи криптомікросхемою.
    hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;

    if (HAL_I2C_Init(&hi2c1) != HAL_OK) {
        Error_Handler();
    }
}

void explain_datasheet_value(std::uint8_t printed)
{
    const auto parsed = i2c::Address::from_datasheet(printed);
    if (parsed) {
        say("0x{:02X} — 7-бітна адреса: у кадрі запис 0x{:02X}, читання 0x{:02X}.\r\n",
            printed, parsed->write_byte(), parsed->read_byte());
        say("  Wire / ESP-IDF / i2c-dev беруть 0x{:02X}, STM32 HAL — 0x{:02X}.\r\n",
            parsed->value(), parsed->write_byte());
        return;
    }

    switch (parsed.error().kind) {
    case i2c::AddrError::shifted: {
        const auto twice = static_cast<std::uint8_t>(
            static_cast<std::uint8_t>(printed << 1) >> 1);
        say("0x{:02X} — це вже байт кадру, а не адреса: чіп сидить на 0x{:02X}.\r\n",
            printed, parsed.error().suggested);
        say("  Другий зсув перетворив би його на 0x{:02X} — стукали б у чужу EEPROM.\r\n",
            twice);
        break;
    }
    case i2c::AddrError::reserved:
        say("0x{:02X} — службовий діапазон стандарту, пристрою тут бути не може.\r\n",
            printed);
        break;
    }
}

void print_report(const i2c::Report& report)
{
    say("\r\n--- Прохід шини: опитано {} адрес, збоїв {} ---\r\n",
        report.probed(), report.errors());

    if (report.bus_stuck()) {
        say("ШИНА ЗАВИСЛА: SDA тримається в нулі, START не проходить.\r\n");
        say("  Ведений не добіг до кінця байта й чекає такту SCL.\r\n");
        say("  Лікує не перезапуск прошивки, а апаратне вивільнення:\r\n");
        say("  дев'ять тактів на SCL у режимі GPIO та примусовий STOP.\r\n");
        return;
    }

    if (report.count() == 0) {
        say("Тиша на всіх адресах. Спускаємося на рівень нижче:\r\n");
        say("  1. VDD і GND — осцилографом на НІЖКАХ чіпа, не мультиметром;\r\n");
        say("  2. nRST / EN — у високому рівні, а не в повітрі;\r\n");
        say("  3. зовнішні підтяжки 2.2..4.7 кОм на SDA і SCL;\r\n");
        say("  4. SDA і SCL не переплутані місцями.\r\n");
        return;
    }

    if (report.looks_fake()) {
        say("УВАГА: підтверджено {} адрес — стільки пристроїв на шині немає.\r\n",
            report.count());
        say("  Замкнена на землю SDA дає ACK на кожній адресі.\r\n");
    }

    for (const i2c::Address addr : report.found()) {
        say("0x{:02X}  запис 0x{:02X}  читання 0x{:02X}  {}\r\n", addr.value(),
            addr.write_byte(), addr.read_byte(), hint_for(addr).value_or(""));
    }
}

} // namespace

int main()
{
    HAL_Init();
    SystemClock_Config();
    init_i2c();

    say("\r\n=== Сканер шини I2C ===\r\n");
    explain_datasheet_value(0x68); // так адресу друкує один даташит
    explain_datasheet_value(0xD0); // а так — інший, і це те саме залізо

    HalMaster master{hi2c1};
    for (;;) {
        const i2c::Report report = i2c::scan(master);
        print_report(report);
        HAL_Delay(2000);
    }
}

extern "C" void Error_Handler(void)
{
    __disable_irq();
    for (;;) {
    }
}
