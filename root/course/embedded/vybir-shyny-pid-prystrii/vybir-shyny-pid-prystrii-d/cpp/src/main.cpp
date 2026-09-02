// Польотний контролер на STM32H743: три шини, вісім чипів, жодного очікування
// в головному циклі.
//
//   SPI1 — ICM-42688P (IMU), режим 3, ~20 МГц, опитування 1 кГц від TIM6.
//          Контролер відданий давачеві повністю: чужі обміни не зсунуть вибірку.
//   SPI2 — MB85RS64 (FRAM журналу, режим 0) і ADS1118 (АЦП, режим 1).
//          Різні CPOL/CPHA на одній шині — диспетчер перемикає їх перед CS.
//   I2C1 — BMP280 (0x76), LIS3MDL (0x1E), INA226 (0x40), 24C64 (0x50) на 400 кГц.
#include "bus/dispatcher.hpp"

#include <algorithm>
#include <bit>
#include <cstring>

// Дескриптори периферії та ініціалізація — зі згенерованого CubeMX коду.
extern "C" {
extern SPI_HandleTypeDef hspi1;
extern SPI_HandleTypeDef hspi2;
extern I2C_HandleTypeDef hi2c1;
extern TIM_HandleTypeDef htim6;

void SystemClock_Config();
void MX_GPIO_Init();
void MX_DMA_Init();
void MX_SPI1_Init();
void MX_SPI2_Init();
void MX_I2C1_Init();
void MX_TIM6_Init();
}

namespace {

using bus::Command;
using bus::Completion;
using bus::Device;
using bus::Dispatcher;
using bus::Op;
using bus::Result;
using bus::SpiMode;
using bus::Transaction;

// ---- карта пристроїв -------------------------------------------------------

constexpr Device kImu{.cs_port = GPIOA,
                      .cs_pin = GPIO_PIN_4,
                      .spi_mode = SpiMode::Mode3,
                      .spi_prescaler = SPI_BAUDRATEPRESCALER_8};

constexpr Device kFram{.cs_port = GPIOB,
                       .cs_pin = GPIO_PIN_12,
                       .spi_mode = SpiMode::Mode0,
                       .spi_prescaler = SPI_BAUDRATEPRESCALER_4};

constexpr Device kExternalAdc{.cs_port = GPIOB,
                              .cs_pin = GPIO_PIN_1,
                              .spi_mode = SpiMode::Mode1,
                              .spi_prescaler = SPI_BAUDRATEPRESCALER_32};

constexpr Device kBarometer{.i2c_address = 0x76};
constexpr Device kMagnetometer{.i2c_address = 0x1E};
constexpr Device kPowerMonitor{.i2c_address = 0x40};
constexpr Device kEeprom{.i2c_address = 0x50};

constexpr bus::I2cLines kI2c1Lines{.scl_port = GPIOB,
                                   .scl_pin = GPIO_PIN_8,
                                   .sda_port = GPIOB,
                                   .sda_pin = GPIO_PIN_9,
                                   .alternate = GPIO_AF4_I2C1};

// ---- буфери DMA ------------------------------------------------------------
// Вирівняні на рядок кешу й лежать у секції, яку лінкер кладе в SRAM, доступну
// контролерам DMA. Узгодження кеша бере на себе диспетчер.
#define DMA_BUFFER __attribute__((section(".dma_buffer"), aligned(32)))

DMA_BUFFER std::array<std::uint8_t, 14> imu_raw{};
DMA_BUFFER std::array<std::uint8_t, 6> baro_raw{};
DMA_BUFFER std::array<std::uint8_t, 6> mag_raw{};
DMA_BUFFER std::array<std::uint8_t, 2> power_raw{};
DMA_BUFFER std::array<std::uint8_t, 2> adc_tx{};
DMA_BUFFER std::array<std::uint8_t, 2> adc_rx{};
DMA_BUFFER std::array<std::uint8_t, 32> eeprom_raw{};
DMA_BUFFER std::array<std::uint8_t, 16> log_record{};

// ---- шини ------------------------------------------------------------------

Dispatcher spi1_bus{hspi1};
Dispatcher spi2_bus{hspi2};
Dispatcher i2c1_bus{hi2c1, kI2c1Lines};

// ---- стан, який наповнюють колбеки -----------------------------------------

struct ImuSample {
    std::array<std::int16_t, 3> accel{};
    std::array<std::int16_t, 3> gyro{};
    std::int16_t temperature{};
};

ImuSample imu_sample;
volatile bool imu_fresh = false;
volatile std::uint32_t imu_missed = 0;

volatile bool baro_fresh = false;
volatile bool mag_fresh = false;
volatile std::uint16_t bus_voltage_raw = 0;
volatile std::int16_t external_adc_raw = 0;
volatile std::uint32_t i2c_failures = 0;

std::int16_t big_endian16(std::span<const std::uint8_t, 2> bytes) noexcept
{
    return static_cast<std::int16_t>((static_cast<std::uint16_t>(bytes[0]) << 8) | bytes[1]);
}

// ---- обробники завершення (контекст переривання) ----------------------------

struct ImuHandler {
    void operator()(Result result) noexcept
    {
        if (result != Result::Ok) {
            ++imu_missed;
            return;
        }
        if (imu_fresh) {
            ++imu_missed;   // головний цикл не забрав попередню вибірку
        }
        imu_sample.temperature = big_endian16(std::span<const std::uint8_t, 2>{imu_raw.data(), 2});
        for (std::size_t axis = 0; axis < 3; ++axis) {
            imu_sample.accel[axis] =
                big_endian16(std::span<const std::uint8_t, 2>{imu_raw.data() + 2 + 2 * axis, 2});
            imu_sample.gyro[axis] =
                big_endian16(std::span<const std::uint8_t, 2>{imu_raw.data() + 8 + 2 * axis, 2});
        }
        imu_fresh = true;
    }
};

struct FlagHandler {
    volatile bool* flag;

    void operator()(Result result) noexcept
    {
        if (result == Result::Ok) {
            *flag = true;
        } else {
            ++i2c_failures;
        }
    }
};

struct PowerHandler {
    void operator()(Result result) noexcept
    {
        if (result != Result::Ok) {
            ++i2c_failures;
            return;
        }
        bus_voltage_raw = static_cast<std::uint16_t>((power_raw[0] << 8) | power_raw[1]);
    }
};

struct AdcHandler {
    void operator()(Result result) noexcept
    {
        if (result == Result::Ok) {
            external_adc_raw = big_endian16(std::span<const std::uint8_t, 2>{adc_rx.data(), 2});
        }
    }
};

struct IgnoreHandler {
    void operator()(Result) noexcept {}   // запис у журнал загубився — політ це не спиняє
};

ImuHandler imu_handler;
FlagHandler baro_handler{&baro_fresh};
FlagHandler mag_handler{&mag_fresh};
PowerHandler power_handler;
AdcHandler adc_handler;
IgnoreHandler ignore_handler;

// ---- планування транзакцій -------------------------------------------------

void request_barometer()
{
    static_cast<void>(i2c1_bus.submit(Transaction{.device = &kBarometer,
                                                  .op = Op::Read,
                                                  .command = Command::reg8(0xF7),
                                                  .rx = baro_raw,
                                                  .done = Completion{baro_handler}}));
}

void request_magnetometer()
{
    // 0x80 у під-адресі вмикає автоінкремент регістрів LIS3MDL.
    static_cast<void>(i2c1_bus.submit(Transaction{.device = &kMagnetometer,
                                                  .op = Op::Read,
                                                  .command = Command::reg8(0x28 | 0x80),
                                                  .rx = mag_raw,
                                                  .done = Completion{mag_handler}}));
}

void request_power_monitor()
{
    static_cast<void>(i2c1_bus.submit(Transaction{.device = &kPowerMonitor,
                                                  .op = Op::Read,
                                                  .command = Command::reg8(0x02),
                                                  .rx = power_raw,
                                                  .done = Completion{power_handler}}));
}

void request_external_adc()
{
    // ADS1118 повнодуплексний: поки ми віддаємо нову конфігурацію, чип зсуває
    // результат попереднього перетворення.
    adc_tx[0] = 0x85;   // одиночне перетворення, AIN0-GND, ±4.096 В
    adc_tx[1] = 0x8B;   // 128 SPS, DOUT з підтяжкою

    static_cast<void>(spi2_bus.submit(Transaction{.device = &kExternalAdc,
                                                  .op = Op::Transfer,
                                                  .tx = adc_tx,
                                                  .rx = adc_rx,
                                                  .done = Completion{adc_handler}}));
}

// Журнал у FRAM: спершу дозвіл запису окремою командою без даних, далі сам
// запис за 16-бітною адресою. Дві транзакції в черзі однієї шини підуть саме
// в цьому порядку, і між ними CS підніметься, як вимагає чип.
void append_log_record(std::uint16_t slot)
{
    const std::uint32_t now = HAL_GetTick();
    const auto address = static_cast<std::uint16_t>(slot * log_record.size());

    std::memcpy(log_record.data(), &now, sizeof now);
    std::ranges::copy(baro_raw, log_record.begin() + 4);
    log_record[10] = static_cast<std::uint8_t>(bus_voltage_raw >> 8);
    log_record[11] = static_cast<std::uint8_t>(bus_voltage_raw);
    std::memcpy(log_record.data() + 12, &imu_sample.gyro[2], sizeof(std::int16_t));
    const std::uint32_t missed = imu_missed;
    log_record[14] = static_cast<std::uint8_t>(missed >> 8);
    log_record[15] = static_cast<std::uint8_t>(missed);

    const auto write_enable = spi2_bus.submit(Transaction{
        .device = &kFram, .op = Op::Write, .command = Command::raw({0x06})});

    if (write_enable.has_value()) {
        static_cast<void>(spi2_bus.submit(
            Transaction{.device = &kFram,
                        .op = Op::Write,
                        .command = Command::raw({0x02,
                                                 static_cast<std::uint8_t>(address >> 8),
                                                 static_cast<std::uint8_t>(address)}),
                        .tx = log_record,
                        .done = Completion{ignore_handler}}));
    }
}

void load_calibration()
{
    // 24C64 адресується двома байтами — Command::reg16 сам переводить це
    // в 16-бітний режим апаратного блока I2C.
    static_cast<void>(i2c1_bus.submit(Transaction{.device = &kEeprom,
                                                  .op = Op::Read,
                                                  .command = Command::reg16(0x0000),
                                                  .rx = eeprom_raw,
                                                  .timeout_ms = 20}));
}

}  // namespace

// IMU опитуємо з переривання таймера: 1 кГц треба тримати рівно, а головний
// цикл гуляє за часом залежно від того, що саме він щойно порахував.
extern "C" void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef* htim)
{
    if (htim->Instance != TIM6) {
        return;
    }

    const auto queued = spi1_bus.submit(Transaction{
        .device = &kImu,
        .op = Op::Read,
        .command = Command::reg8(0x1D | 0x80),   // TEMP_DATA1, старший біт — читання
        .rx = imu_raw,
        .done = Completion{imu_handler},
        .timeout_ms = 2});

    if (!queued.has_value()) {
        ++imu_missed;
    }
}

int main()
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_DMA_Init();
    MX_SPI1_Init();
    MX_SPI2_Init();
    MX_I2C1_Init();
    MX_TIM6_Init();

    // Ведений міг лишитися завислим ще від попереднього польоту: перше, що
    // робимо на I2C, — знімаємо з нього можливий замок.
    static_cast<void>(bus::recover_i2c_bus(hi2c1, kI2c1Lines));

    // CS усіх чипів тримаємо у високому стані з першої ж мілісекунди.
    for (const Device* device : {&kImu, &kFram, &kExternalAdc}) {
        HAL_GPIO_WritePin(device->cs_port, device->cs_pin, GPIO_PIN_SET);
    }

    load_calibration();
    HAL_TIM_Base_Start_IT(&htim6);   // 1 кГц: опитування IMU

    std::uint32_t next_baro = HAL_GetTick();
    std::uint32_t next_mag = next_baro;
    std::uint32_t next_power = next_baro;
    std::uint32_t next_adc = next_baro;
    std::uint32_t next_log = next_baro;
    std::uint16_t log_slot = 0;

    for (;;) {
        const std::uint32_t now = HAL_GetTick();
        const auto due = [now](std::uint32_t deadline) {
            return static_cast<std::int32_t>(now - deadline) >= 0;
        };

        if (due(next_baro)) {
            next_baro += 20;    // 50 Гц
            request_barometer();
        }
        if (due(next_mag)) {
            next_mag += 10;     // 100 Гц
            request_magnetometer();
        }
        if (due(next_power)) {
            next_power += 100;  // 10 Гц
            request_power_monitor();
        }
        if (due(next_adc)) {
            next_adc += 100;
            request_external_adc();
        }
        if (due(next_log)) {
            next_log += 200;    // 5 Гц
            append_log_record(log_slot);
            log_slot = static_cast<std::uint16_t>((log_slot + 1) % 512);
        }

        if (imu_fresh) {
            imu_fresh = false;
            // Тут працює контур стабілізації: свіжий вектор уже в imu_sample,
            // і жоден виклик шини його не затримав.
        }
        if (baro_fresh) {
            baro_fresh = false;
        }
        if (mag_fresh) {
            mag_fresh = false;
        }

        // Нагляд за таймаутами й відкладене лікування шини I2C.
        spi1_bus.poll();
        spi2_bus.poll();
        i2c1_bus.poll();
    }
}
