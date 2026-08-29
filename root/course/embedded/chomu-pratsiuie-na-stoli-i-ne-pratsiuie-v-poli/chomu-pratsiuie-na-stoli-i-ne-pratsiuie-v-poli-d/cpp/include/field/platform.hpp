// platform.hpp — контракт заліза для польового модуля.
//
// Усе, що вище цього шару, про регістри не знає нічого. Порт один —
// STM32F407, src/platform_stm32f4.cpp.
//
// Дві речі тут навмисно не такі, як у сишному аналозі. Помилка заліза —
// це значення (std::expected), а не −1 з окремим прапорцем: «АЦП не встиг»
// і «на вході 0 мВ» неможливо переплутати, бо перше просто не має типу
// напруги. А ручне тактування шини віддано об'єктові з деструктором:
// вийти з процедури порятунку, не повернувши ніжки периферії, — це
// назавжди мертва шина, і покладатися тут на дисципліну не варто.
#pragma once

#include <chrono>
#include <cstdint>
#include <expected>
#include <span>

namespace field::plat {

inline constexpr std::uint32_t kHclkBaseHz = 168'000'000;

// Керовані навантаження: усе, що в полі здатне посадити шину живлення
// або перегріти корпус, вмикається ЛИШЕ через цей перелік.
enum class Load : std::uint8_t {
    Radio,   // передавач: імпульс до 2 А
    Heater,  // плівковий підігрів плати
    Charger  // дозвіл заряду акумулятора
};

enum class Channel : std::uint8_t {
    Ntc = 0,  // PA0: дільник 10 кОм + NTC 10 кОм на землю
    Vbat = 1  // PA1: дільник 100к/100к від акумулятора
};

inline constexpr std::uint16_t kAdcFullScale = 4095;
inline constexpr std::uint16_t kAdcVrefMv = 3300;
inline constexpr std::uint8_t kBkpWords = 20;  // BKP0R..BKP19R

enum class HwError : std::uint8_t {
    Timeout,   // подія не настала у відведений час — кандидат на порятунок
    Nack,      // пристрій не відповів, але лінії живі
    Busy,      // лінію тримають низько ще до старту
    BadIndex   // звернення поза межами резервного домену
};

void init();

// Прапори RCC_CSR, зняті один раз при старті. Розшифровує їх FaultLog:
// саме там живе політика, а не тут.
[[nodiscard]] std::uint32_t resetFlagsRaw() noexcept;

[[nodiscard]] std::chrono::milliseconds now() noexcept;
void delayFor(std::chrono::microseconds span) noexcept;

// 0 → /1, 1 → /2, 2 → /4, 3 → /8, 4 → /16. Знижувати частоту можна без
// правки затримок флешу; піднімати — лише назад до вихідної.
void setCoreDivider(unsigned log2) noexcept;
[[nodiscard]] std::uint32_t coreHz() noexcept;

void setLoad(Load load, bool on) noexcept;
[[nodiscard]] bool loadOn(Load load) noexcept;

[[nodiscard]] std::expected<std::uint16_t, HwError> readAdc(Channel channel) noexcept;

[[nodiscard]] std::expected<std::uint32_t, HwError> bkpRead(std::uint8_t index) noexcept;
std::expected<void, HwError> bkpWrite(std::uint8_t index, std::uint32_t value) noexcept;

void i2cInit() noexcept;

// Коротка транзакція «чи ти тут»: адреса плюс нуль байтів даних.
[[nodiscard]] std::expected<void, HwError> i2cProbe(std::uint8_t addr7) noexcept;
[[nodiscard]] std::expected<void, HwError> i2cReadReg(std::uint8_t addr7, std::uint8_t reg,
                                                      std::span<std::uint8_t> buf) noexcept;

// Поки живий цей об'єкт, SCL/SDA належать нам, а не блокові I2C. Деструктор
// повертає ніжки під альтернативну функцію разом із повним скиданням блока:
// після ручного тактування периферія лишається посеред уявної транзакції.
class PinControl {
public:
    PinControl() noexcept;
    ~PinControl();

    PinControl(const PinControl&) = delete;
    PinControl& operator=(const PinControl&) = delete;

    // Ніжки з відкритим стоком: writeX(true) — це не «видати одиницю»,
    // а відпустити лінію на зовнішню підтяжку.
    void writeScl(bool high) noexcept;
    void writeSda(bool high) noexcept;
    [[nodiscard]] bool readScl() const noexcept;
    [[nodiscard]] bool readSda() const noexcept;
};

void watchdogStart(std::chrono::milliseconds timeout) noexcept;
void watchdogKick() noexcept;
[[noreturn]] void systemReset() noexcept;

}  // namespace field::plat
