// stm32_board.cpp — усе, що знає про конкретний кремній і конкретну плату.
//
// Розводка: LED_STATUS = PB12, LED_WARN = PA4, ключ давачів = PE3,
//           ключ радіо = PE4 (обидва — P-MOSFET, активний нуль),
//           АЦП батареї = ADC1 через дільник 100к/200к, BME280 на I2C1 @ 0x76.
#include "stm32_board.hpp"

#include "stm32f4xx_hal.h"

extern "C" {
extern ADC_HandleTypeDef hadc1;
extern I2C_HandleTypeDef hi2c1;
extern RTC_HandleTypeDef hrtc;
void SystemClock_Config(void);
}

namespace bsp {
namespace {

constexpr std::uint32_t kVrefMv = 3300;
constexpr std::uint32_t kAdcFullScale = 4095;

constexpr std::uint16_t kBmeAddr = 0x76 << 1;
constexpr std::uint8_t kBmeId = 0x60;
constexpr std::uint8_t kRegId = 0xD0;
constexpr std::uint8_t kRegCalib = 0x88;
constexpr std::uint8_t kRegCtrlHum = 0xF2;
constexpr std::uint8_t kRegStatus = 0xF3;
constexpr std::uint8_t kRegCtrlMeas = 0xF4;
constexpr std::uint8_t kRegData = 0xF7;
constexpr std::uint8_t kForcedT2x = 0x41;  // osrs_t = x2, osrs_p = skip, forced
constexpr std::uint32_t kI2cTimeoutMs = 50;

Status bme_read(std::uint8_t reg, std::uint8_t* buf, std::uint16_t len) noexcept
{
    return HAL_I2C_Mem_Read(&hi2c1, kBmeAddr, reg, I2C_MEMADD_SIZE_8BIT,
                            buf, len, kI2cTimeoutMs) == HAL_OK
               ? Status::Ok
               : Status::BusFault;
}

Status bme_write(std::uint8_t reg, std::uint8_t value) noexcept
{
    return HAL_I2C_Mem_Write(&hi2c1, kBmeAddr, reg, I2C_MEMADD_SIZE_8BIT,
                             &value, 1, kI2cTimeoutMs) == HAL_OK
               ? Status::Ok
               : Status::BusFault;
}

Status rtc_arm_wakeup(std::chrono::milliseconds timeout) noexcept
{
    auto seconds = static_cast<std::uint32_t>(timeout.count() / 1000);
    if (seconds == 0) {
        seconds = 1;
    }
    if (seconds > 0xFFFF) {  // стеля 16-бітного лічильника на ck_spre
        seconds = 0xFFFF;
    }
    HAL_RTCEx_DeactivateWakeUpTimer(&hrtc);
    return HAL_RTCEx_SetWakeUpTimer_IT(&hrtc, seconds - 1,
                                       RTC_WAKEUPCLOCK_CK_SPRE_16BITS) == HAL_OK
               ? Status::Ok
               : Status::Timeout;
}

} // namespace

Status Stm32Board::led_set(LedId led, LedState state) noexcept
{
    const auto pin = (state == LedState::On) ? GPIO_PIN_SET : GPIO_PIN_RESET;
    switch (led) {
    case LedId::SystemStatus:
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, pin);
        return Status::Ok;
    case LedId::Warning:
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, pin);
        return Status::Ok;
    }
    return Status::InvalidParam;
}

Status Stm32Board::power_domain_set(PowerDomain domain, bool enable) noexcept
{
    // P-MOSFET: нуль на затворі — домен під напругою.
    const auto pin = enable ? GPIO_PIN_RESET : GPIO_PIN_SET;
    switch (domain) {
    case PowerDomain::Sensors:
        HAL_GPIO_WritePin(GPIOE, GPIO_PIN_3, pin);
        return Status::Ok;
    case PowerDomain::Radio:
        HAL_GPIO_WritePin(GPIOE, GPIO_PIN_4, pin);
        return Status::Ok;
    }
    return Status::InvalidParam;
}

std::expected<BatteryMetrics, Status> Stm32Board::get_battery_metrics() noexcept
{
    if (HAL_ADC_Start(&hadc1) != HAL_OK) {
        return std::unexpected(Status::BusFault);
    }
    if (HAL_ADC_PollForConversion(&hadc1, 10) != HAL_OK) {
        HAL_ADC_Stop(&hadc1);
        return std::unexpected(Status::Timeout);
    }

    const std::uint32_t raw = HAL_ADC_GetValue(&hadc1);
    HAL_ADC_Stop(&hadc1);

    const std::uint32_t v_pin_mv = (raw * kVrefMv) / kAdcFullScale;
    const std::uint32_t v_bat_mv = (v_pin_mv * 3) / 2;  // дільник 1:1.5

    BatteryMetrics m;
    m.voltage_mv = static_cast<std::uint16_t>(v_bat_mv);
    m.charge_percent = v_bat_mv >= 4200   ? 100
                       : v_bat_mv <= 3000 ? 0
                                          : static_cast<std::uint8_t>((v_bat_mv - 3000) / 12);
    return m;
}

std::expected<EnvironmentMetrics, Status> Stm32Board::read_environment() noexcept
{
    if (!bme_ready_) {
        return std::unexpected(Status::Unsupported);
    }

    // Давач щойно ввімкнули з холодного стану — режим задаємо заново.
    if (auto st = bme_write(kRegCtrlHum, 0x01); st != Status::Ok) {
        return std::unexpected(st);
    }
    if (auto st = bme_write(kRegCtrlMeas, kForcedT2x); st != Status::Ok) {
        return std::unexpected(st);
    }

    // Перетворення при x2 триває ~6 мс; чекаємо падіння біта measuring.
    std::uint8_t status = 0x08;
    for (std::uint32_t waited = 0; (status & 0x08) != 0; ++waited) {
        if (waited > 20) {
            return std::unexpected(Status::Timeout);
        }
        HAL_Delay(1);
        if (auto st = bme_read(kRegStatus, &status, 1); st != Status::Ok) {
            return std::unexpected(st);
        }
    }

    std::uint8_t raw[6]{};
    if (auto st = bme_read(kRegData, raw, sizeof(raw)); st != Status::Ok) {
        return std::unexpected(st);
    }

    const std::int32_t adc_t = (static_cast<std::int32_t>(raw[3]) << 12) |
                               (static_cast<std::int32_t>(raw[4]) << 4) |
                               (static_cast<std::int32_t>(raw[5]) >> 4);
    if (adc_t == 0x80000) {  // канал вимкнено — даних немає
        return std::unexpected(Status::BusFault);
    }

    // Компенсація за формулою з даташита BME280 (розділ 4.2.3).
    const std::int32_t var1 =
        (((adc_t >> 3) - (static_cast<std::int32_t>(dig_t1_) << 1)) * dig_t2_) >> 11;
    const std::int32_t d = (adc_t >> 4) - static_cast<std::int32_t>(dig_t1_);
    const std::int32_t var2 = (((d * d) >> 12) * dig_t3_) >> 14;
    const std::int32_t t_fine = var1 + var2;

    EnvironmentMetrics env;
    env.temperature_centi_c = static_cast<std::int16_t>((t_fine * 5 + 128) >> 8);
    return env;
}

Status Stm32Board::enter_low_power(SleepMode mode, std::chrono::milliseconds timeout) noexcept
{
    if (auto st = rtc_arm_wakeup(timeout); st != Status::Ok) {
        return st;
    }

    if (mode == SleepMode::Deep) {
        HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
        SystemClock_Config();  // після STOP ядро тактується від HSI
    } else {
        // У Sleep тик SysTick будив би ядро щомілісекунди — глушимо його.
        HAL_SuspendTick();
        HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
        HAL_ResumeTick();
    }

    HAL_RTCEx_DeactivateWakeUpTimer(&hrtc);
    return Status::Ok;
}

void Stm32Board::delay(std::chrono::milliseconds duration) noexcept
{
    HAL_Delay(static_cast<std::uint32_t>(duration.count()));
}

std::chrono::milliseconds Stm32Board::uptime() const noexcept
{
    return std::chrono::milliseconds(HAL_GetTick());
}

Status Stm32Board::init() noexcept
{
    led_set(LedId::SystemStatus, LedState::Off);
    led_set(LedId::Warning, LedState::Off);
    power_domain_set(PowerDomain::Sensors, false);
    power_domain_set(PowerDomain::Radio, false);

    // Щоб прочитати калібрування, давач треба ненадовго ввімкнути.
    PowerDomainGuard sensors(*this, PowerDomain::Sensors, std::chrono::milliseconds(15));
    if (!sensors.is_active()) {
        return Status::BusFault;
    }

    std::uint8_t id = 0;
    if (auto st = bme_read(kRegId, &id, 1); st != Status::Ok) {
        return st;
    }
    if (id != kBmeId) {
        return Status::Unsupported;  // на шині щось інше
    }

    std::uint8_t calib[6]{};
    if (auto st = bme_read(kRegCalib, calib, sizeof(calib)); st != Status::Ok) {
        return st;
    }

    dig_t1_ = static_cast<std::uint16_t>(calib[0] | (calib[1] << 8));
    dig_t2_ = static_cast<std::int16_t>(calib[2] | (calib[3] << 8));
    dig_t3_ = static_cast<std::int16_t>(calib[4] | (calib[5] << 8));
    bme_ready_ = true;
    return Status::Ok;
}

} // namespace bsp
