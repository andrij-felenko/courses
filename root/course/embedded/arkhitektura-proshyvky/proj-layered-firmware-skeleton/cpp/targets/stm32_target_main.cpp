// targets/stm32_target_main.cpp — прив'язка каркаса до конкретного чипа.
// ЄДИНЕ місце в проєкті, де згадуються stm32f4xx.h, RCC, I2C1 і номери виводів.
// Замінити STM32F401 на інший контролер означає переписати цей файл — і лише його.
#include "stm32f4xx.h"  // Вендорний CMSIS-заголовок: тільки тут і ніде більше

#include <chrono>
#include <cstdint>

#include "app/app_telemetry.hpp"
#include "bsp/bsp_bme280.hpp"
#include "bsp/power_rail.hpp"
#include "hal/clock.hpp"
#include "hal/critical_section.hpp"
#include "hal/hal_gpio.hpp"
#include "hal/hal_i2c.hpp"
#include "services/dispatcher.hpp"
#include "services/event_queue.hpp"
#include "services/power_manager.hpp"

namespace {

using namespace std::chrono_literals;

// --- Розкладка плати -----------------------------------------------------------
constexpr std::uint32_t kSclPin = 6;         // PB6, альтернативна функція AF4
constexpr std::uint32_t kSdaPin = 7;         // PB7, альтернативна функція AF4
constexpr std::uint32_t kSensorPwrPin = 5;   // PB5 → затвор ключа MOSFET
constexpr std::uint32_t kPclk1Hz = 42000000; // APB1 при ядрі 84 МГц
constexpr auto kI2cTimeout = 10ms;           // Ліміт очікування будь-якого прапорця
constexpr auto kTickPeriod = 100ms;          // Крок диспетчерського тику
constexpr std::uint16_t kSampleEveryTicks = 10;  // Опитування раз на секунду

using Queue = services::EventQueue<16>;

volatile std::uint32_t g_uptime_ms = 0;
Queue g_queue;  // Обробник переривання кладе події сюди

// --- Годинник на SysTick --------------------------------------------------------
class SysTickClock final : public hal::IClock {
public:
    time_point now() const override
    {
        return std::chrono::milliseconds{g_uptime_ms};  // 32-бітне читання неподільне
    }

    void sleep_for(duration d) override
    {
        const std::uint32_t start = g_uptime_ms;
        while (std::chrono::milliseconds{g_uptime_ms - start} < d) {
            __NOP();
        }
    }
};

// --- Ніжка GPIO поверх регістрів порту ------------------------------------------
class Stm32GpioPin final : public hal::IGpioPin {
public:
    Stm32GpioPin(GPIO_TypeDef* port, std::uint32_t pin) noexcept : port_(port), pin_(pin) {}

    std::expected<void, hal::GpioError> write(hal::Level level) override
    {
        // BSRR — неподільна установка/скидання без «читати-змінити-записати».
        port_->BSRR = (level == hal::Level::High) ? (1U << pin_) : (1U << (pin_ + 16U));
        return {};
    }

    std::expected<hal::Level, hal::GpioError> read() const override
    {
        return ((port_->IDR & (1U << pin_)) != 0U) ? hal::Level::High : hal::Level::Low;
    }

private:
    GPIO_TypeDef* port_;
    std::uint32_t pin_;
};

// --- Шина I2C поверх регістрів контролера ----------------------------------------
class Stm32I2cBus final : public hal::II2cBus {
public:
    Stm32I2cBus(I2C_TypeDef* i2c, hal::IClock& clock, std::chrono::milliseconds timeout) noexcept
        : i2c_(i2c), clock_(clock), timeout_(timeout)
    {
    }

    std::expected<void, hal::I2cError> write_reg(std::uint8_t dev_addr, std::uint8_t reg_addr,
                                                 std::span<const std::uint8_t> data) override
    {
        if (auto res = wait_not_busy(); !res) return res;
        if (auto res = start_and_address(dev_addr, false); !res) return res;
        clear_addr();

        if (auto res = wait_sr1(I2C_SR1_TXE); !res) return res;
        i2c_->DR = reg_addr;

        for (const std::uint8_t byte : data) {
            if (auto res = wait_sr1(I2C_SR1_TXE); !res) return res;
            i2c_->DR = byte;
        }

        if (auto res = wait_sr1(I2C_SR1_BTF); !res) return res;
        i2c_->CR1 |= I2C_CR1_STOP;
        return {};
    }

    std::expected<void, hal::I2cError> read_reg(std::uint8_t dev_addr, std::uint8_t reg_addr,
                                                std::span<std::uint8_t> data) override
    {
        if (data.empty()) return {};

        if (auto res = wait_not_busy(); !res) return res;

        // Фаза запису: назвати мікросхемі адресу регістра
        if (auto res = start_and_address(dev_addr, false); !res) return res;
        clear_addr();
        if (auto res = wait_sr1(I2C_SR1_TXE); !res) return res;
        i2c_->DR = reg_addr;
        if (auto res = wait_sr1(I2C_SR1_BTF); !res) return res;

        // Фаза читання: повторний старт без відпускання шини
        if (auto res = receive(dev_addr, data); !res) return res;
        return finish_stop();
    }

private:
    std::expected<void, hal::I2cError> abort(hal::I2cError error)
    {
        i2c_->CR1 |= I2C_CR1_STOP;
        i2c_->CR1 &= ~static_cast<std::uint32_t>(I2C_CR1_POS);
        i2c_->CR1 |= I2C_CR1_ACK;
        return std::unexpected(error);
    }

    // Очікування прапорця з жорстким лімітом часу: зависання в while(!flag)
    // перетворює одну несправну мікросхему на несправну прошивку.
    std::expected<void, hal::I2cError> wait_sr1(std::uint32_t mask)
    {
        const auto start = clock_.now();
        for (;;) {
            const std::uint32_t sr1 = i2c_->SR1;

            if ((sr1 & I2C_SR1_AF) != 0U) {
                i2c_->SR1 = static_cast<std::uint16_t>(~I2C_SR1_AF);
                return abort(hal::I2cError::Nack);
            }
            if ((sr1 & (I2C_SR1_BERR | I2C_SR1_ARLO | I2C_SR1_OVR)) != 0U) {
                i2c_->SR1 = static_cast<std::uint16_t>(~(I2C_SR1_BERR | I2C_SR1_ARLO | I2C_SR1_OVR));
                return abort(hal::I2cError::BusFailure);
            }
            if ((sr1 & mask) != 0U) {
                return {};
            }
            if (clock_.elapsed_since(start) > timeout_) {
                return abort(hal::I2cError::Timeout);
            }
        }
    }

    std::expected<void, hal::I2cError> wait_not_busy()
    {
        const auto start = clock_.now();
        while ((i2c_->SR2 & I2C_SR2_BUSY) != 0U) {
            if (clock_.elapsed_since(start) > timeout_) {
                // Лінію тримає хтось інший — STOP тут уже не поможе.
                return std::unexpected(hal::I2cError::BusFailure);
            }
        }
        return {};
    }

    std::expected<void, hal::I2cError> start_and_address(std::uint8_t dev_addr, bool read)
    {
        i2c_->CR1 |= I2C_CR1_START;
        if (auto res = wait_sr1(I2C_SR1_SB); !res) return res;

        i2c_->DR = static_cast<std::uint8_t>((dev_addr << 1) | (read ? 1U : 0U));
        return wait_sr1(I2C_SR1_ADDR);
    }

    // Прапорець ADDR знімається лише парою читань SR1 і SR2 — послідовність із довідника.
    void clear_addr()
    {
        volatile std::uint32_t tmp = i2c_->SR1;
        tmp = i2c_->SR2;
        (void)tmp;
    }

    std::expected<void, hal::I2cError> receive(std::uint8_t dev_addr, std::span<std::uint8_t> data)
    {
        if (data.size() == 1) {
            i2c_->CR1 &= ~static_cast<std::uint32_t>(I2C_CR1_ACK);
            if (auto res = start_and_address(dev_addr, true); !res) return res;
            {
                const hal::CriticalSection guard;
                clear_addr();
                i2c_->CR1 |= I2C_CR1_STOP;
            }
            if (auto res = wait_sr1(I2C_SR1_RXNE); !res) return res;
            data[0] = static_cast<std::uint8_t>(i2c_->DR);
            return {};
        }

        if (data.size() == 2) {
            // Для рівно двох байтів довідник вимагає прапорця POS: NACK готується
            // на другий байт іще до того, як прийшов перший.
            i2c_->CR1 |= I2C_CR1_ACK | I2C_CR1_POS;
            if (auto res = start_and_address(dev_addr, true); !res) return res;
            {
                const hal::CriticalSection guard;
                clear_addr();
                i2c_->CR1 &= ~static_cast<std::uint32_t>(I2C_CR1_ACK);
            }
            if (auto res = wait_sr1(I2C_SR1_BTF); !res) return res;
            {
                const hal::CriticalSection guard;
                i2c_->CR1 |= I2C_CR1_STOP;
                data[0] = static_cast<std::uint8_t>(i2c_->DR);
            }
            data[1] = static_cast<std::uint8_t>(i2c_->DR);
            i2c_->CR1 &= ~static_cast<std::uint32_t>(I2C_CR1_POS);
            return {};
        }

        i2c_->CR1 |= I2C_CR1_ACK;
        if (auto res = start_and_address(dev_addr, true); !res) return res;
        clear_addr();

        std::size_t idx = 0;
        while (data.size() - idx > 3) {
            if (auto res = wait_sr1(I2C_SR1_RXNE); !res) return res;
            data[idx++] = static_cast<std::uint8_t>(i2c_->DR);
        }

        // Лишилось три байти: зняти ACK треба рівно тут, інакше мікросхема
        // почне четвертий і зіпсує кадр.
        if (auto res = wait_sr1(I2C_SR1_BTF); !res) return res;
        i2c_->CR1 &= ~static_cast<std::uint32_t>(I2C_CR1_ACK);
        {
            const hal::CriticalSection guard;
            data[idx++] = static_cast<std::uint8_t>(i2c_->DR);
            i2c_->CR1 |= I2C_CR1_STOP;
            data[idx++] = static_cast<std::uint8_t>(i2c_->DR);
        }
        if (auto res = wait_sr1(I2C_SR1_RXNE); !res) return res;
        data[idx] = static_cast<std::uint8_t>(i2c_->DR);
        return {};
    }

    // Дочекатись завершення STOP і повернути ACK для наступної передачі.
    std::expected<void, hal::I2cError> finish_stop()
    {
        const auto start = clock_.now();
        while ((i2c_->CR1 & I2C_CR1_STOP) != 0U) {
            if (clock_.elapsed_since(start) > timeout_) {
                return std::unexpected(hal::I2cError::Timeout);
            }
        }
        i2c_->CR1 |= I2C_CR1_ACK;
        return {};
    }

    I2C_TypeDef* i2c_;
    hal::IClock& clock_;
    std::chrono::milliseconds timeout_;
};

// --- Ініціалізація периферії -----------------------------------------------------
void board_clocks_init()
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;
    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;
    (void)RCC->APB1ENR;  // Затримка на такт шини після ввімкнення тактування
}

void board_gpio_init()
{
    // PB6, PB7 — альтернативна функція AF4, відкритий стік, підтяжка вгору
    GPIOB->MODER &= ~((3U << (kSclPin * 2)) | (3U << (kSdaPin * 2)));
    GPIOB->MODER |= (2U << (kSclPin * 2)) | (2U << (kSdaPin * 2));
    GPIOB->OTYPER |= (1U << kSclPin) | (1U << kSdaPin);
    GPIOB->OSPEEDR |= (3U << (kSclPin * 2)) | (3U << (kSdaPin * 2));
    GPIOB->PUPDR &= ~((3U << (kSclPin * 2)) | (3U << (kSdaPin * 2)));
    GPIOB->PUPDR |= (1U << (kSclPin * 2)) | (1U << (kSdaPin * 2));
    GPIOB->AFR[0] &= ~((0xFU << (kSclPin * 4)) | (0xFU << (kSdaPin * 4)));
    GPIOB->AFR[0] |= (4U << (kSclPin * 4)) | (4U << (kSdaPin * 4));

    // PB5 — звичайний вихід на затвор ключа живлення давачів
    GPIOB->MODER &= ~(3U << (kSensorPwrPin * 2));
    GPIOB->MODER |= (1U << (kSensorPwrPin * 2));
    GPIOB->OTYPER &= ~(1U << kSensorPwrPin);
    GPIOB->BSRR = (1U << kSensorPwrPin);  // Живлення давачів увімкнено
}

void board_i2c_init()
{
    I2C1->CR1 |= I2C_CR1_SWRST;  // Скидання логіки контролера після можливого зависання
    I2C1->CR1 &= ~static_cast<std::uint32_t>(I2C_CR1_SWRST);

    I2C1->CR2 = kPclk1Hz / 1000000U;  // FREQ у мегагерцах
    I2C1->CCR = static_cast<std::uint16_t>(kPclk1Hz / (2U * 100000U));  // 100 кГц
    I2C1->TRISE = static_cast<std::uint16_t>(kPclk1Hz / 1000000U + 1U);
    I2C1->CR1 |= I2C_CR1_PE | I2C_CR1_ACK;
}

// --- Перехідник відновлення -------------------------------------------------------
class SensorRecovery final : public services::IRecoverable {
public:
    SensorRecovery(bsp::Bme280& sensor, app::TelemetryCoordinator& app) noexcept
        : sensor_(sensor), app_(app)
    {
    }

    bool reinitialize() override { return sensor_.initialize().has_value(); }
    void on_recovered() override { app_.notify_recovered(); }

private:
    bsp::Bme280& sensor_;
    app::TelemetryCoordinator& app_;
};

}  // namespace

extern "C" void SysTick_Handler(void)
{
    ++g_uptime_ms;
    if ((g_uptime_ms % static_cast<std::uint32_t>(kTickPeriod.count())) == 0U) {
        // Подія народжується в перериванні, а обробляється в головному циклі:
        // саме заради цього розриву черга й існує.
        g_queue.push(services::Event{
            .type = services::EventType::TimerTick,
            .timestamp = std::chrono::milliseconds{g_uptime_ms},
            .payload = {},
        });
    }
}

int main()
{
    SystemCoreClockUpdate();
    board_clocks_init();
    board_gpio_init();
    board_i2c_init();
    SysTick_Config(SystemCoreClock / 1000U);  // Тик щомілісекунди

    SysTickClock clock;
    Stm32I2cBus bus(I2C1, clock, kI2cTimeout);
    Stm32GpioPin power_pin(GPIOB, kSensorPwrPin);

    bsp::Bme280 sensor(bus, bsp::Bme280::kPrimaryAddress);
    bsp::PowerRail rail(power_pin, clock, hal::Level::High, 50ms, 100ms);

    if (!sensor.initialize()) {
        // Давач не озвався на холодному старті: одне скидання живлення й друга спроба.
        rail.power_cycle();
        (void)sensor.initialize();
    }

    services::QueueSink<Queue> sink(g_queue);
    services::Dispatcher<Queue> dispatcher(g_queue);

    app::TelemetryCoordinator app(sensor, sink, 35.0F, kSampleEveryTicks);
    SensorRecovery recovery(sensor, app);
    services::PowerManager power(rail, clock, recovery, 5000ms);

    dispatcher.subscribe(app::TelemetryCoordinator::subscription(), app);
    dispatcher.subscribe(services::PowerManager::subscription(), power);

    for (;;) {
        // Головний цикл нічого не рахує сам: він лише крутить диспетчер.
        if (dispatcher.drain() == 0) {
            __WFI();  // Черга порожня — спимо до найближчого переривання
        }
    }
}
