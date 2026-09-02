#include "sensor/adapter.hpp"

#include "vendor/vendor_sensor.h"   /* заголовок сам загорнутий у extern "C" */

#include <chrono>
#include <cstdint>
#include <mutex>
#include <span>
#include <utility>

#if defined(SYS_PORT_FREERTOS)
#include "FreeRTOS.h"
#include "semphr.h"
#include "task.h"
#include "stm32f4xx.h"
#else
#include <thread>
#endif

namespace sensor {
namespace {

constexpr std::uint32_t kLongDelayUs = 1000U;
constexpr auto kMeasureTimeout = std::chrono::milliseconds(200);
constexpr std::uint32_t kMeasurePollUs = 2000U;

#if defined(SYS_PORT_FREERTOS)

/* М'ютекс RTOS у мінімальній обгортці: рівно стільки, скільки треба
   стандартному std::scoped_lock — lock() і unlock(). */
class RtosMutex {
public:
    RtosMutex() : handle_(xSemaphoreCreateMutex()) {}
    ~RtosMutex() { if (handle_ != nullptr) vSemaphoreDelete(handle_); }
    RtosMutex(const RtosMutex&) = delete;
    RtosMutex& operator=(const RtosMutex&) = delete;

    void lock() { xSemaphoreTake(handle_, portMAX_DELAY); }
    void unlock() { xSemaphoreGive(handle_); }
    bool valid() const noexcept { return handle_ != nullptr; }

private:
    SemaphoreHandle_t handle_;
};

using Mutex = RtosMutex;

void delay_us(std::uint32_t period_us)
{
    if (period_us >= kLongDelayUs) {
        /* Довга пауза належить планувальнику, а не порожньому циклу. */
        vTaskDelay(pdMS_TO_TICKS((period_us + 999U) / 1000U));
    } else {
        const std::uint32_t start = DWT->CYCCNT;
        const std::uint32_t ticks = period_us * (SystemCoreClock / 1000000U);
        while ((DWT->CYCCNT - start) < ticks) {
            __NOP();
        }
    }
}

#else  /* хостова збірка під модульні тести */

using Mutex = std::mutex;

void delay_us(std::uint32_t period_us)
{
    if (period_us >= kLongDelayUs) {
        std::this_thread::sleep_for(std::chrono::microseconds(period_us));
    } else {
        const auto deadline =
            std::chrono::steady_clock::now() + std::chrono::microseconds(period_us);
        while (std::chrono::steady_clock::now() < deadline) {
        }
    }
}

#endif

SensorStatus map_vendor_error(std::int8_t rc) noexcept
{
    switch (rc) {
    case VENDOR_OK:              return SensorStatus::Ok;
    case VENDOR_E_NULL_PTR:      return SensorStatus::InvalidParameter;
    case VENDOR_E_COMM_FAIL:     return SensorStatus::CommunicationError;
    case VENDOR_E_DEV_NOT_FOUND: return SensorStatus::InvalidDevice;
    case VENDOR_E_CALIB:         return SensorStatus::CalibrationInvalid;
    default:                     return SensorStatus::CommunicationError;
    }
}

/* Містки мають C-компонування: саме такі вказівники очікує чужий драйвер. */
extern "C" {
std::int8_t bridge_read(std::uint8_t reg, std::uint8_t* data,
                        std::uint32_t len, void* intf_ptr) noexcept;
std::int8_t bridge_write(std::uint8_t reg, const std::uint8_t* data,
                         std::uint32_t len, void* intf_ptr) noexcept;
void bridge_delay(std::uint32_t period_us, void* intf_ptr) noexcept;
}

}  // namespace

namespace detail {

class AdapterImpl {
public:
    AdapterImpl(II2cBus& bus, std::uint8_t i2c_addr) noexcept
        : bus_(bus), i2c_addr_(i2c_addr)
    {
        /* Адреса цього об'єкта — весь контекст, який чужий драйвер
           поверне в кожен колбек. Тому Impl нерухомий (див. нижче). */
        dev_.intf_ptr = this;
        dev_.read = &bridge_read;
        dev_.write = &bridge_write;
        dev_.delay_us = &bridge_delay;
    }

    ~AdapterImpl()
    {
        if (ready_) {
            /* RAII: чип засинає й на нормальному виході, і на розкрутці
               стека після винятку. Забути про це — розрядити акумулятор. */
            static_cast<void>(vendor_sensor_set_mode(&dev_, VENDOR_MODE_SLEEP));
        }
    }

    /* Ані копіювати, ані переміщати саму реалізацію не можна: intf_ptr
       прибитий до її адреси. Рухається лише unique_ptr в SensorAdapter. */
    AdapterImpl(const AdapterImpl&) = delete;
    AdapterImpl& operator=(const AdapterImpl&) = delete;
    AdapterImpl(AdapterImpl&&) = delete;
    AdapterImpl& operator=(AdapterImpl&&) = delete;

    SensorStatus init()
    {
        const std::int8_t rc = vendor_sensor_init(&dev_);
        if (rc != VENDOR_OK) {
            return map_vendor_error(rc);
        }
        ready_ = true;
        return SensorStatus::Ok;
    }

    std::expected<EnvironmentReading, SensorStatus> read()
    {
        if (!ready_) {
            return std::unexpected(SensorStatus::InvalidParameter);
        }
        /* Блокування знімається на будь-якому виході, включно з винятком:
           жодного «звільнити перед кожним return» у гілках нижче немає. */
        const std::scoped_lock guard(lock_);

        if (const std::int8_t rc = vendor_sensor_set_mode(&dev_, VENDOR_MODE_FORCED);
            rc != VENDOR_OK) {
            return std::unexpected(map_vendor_error(rc));
        }

        const auto deadline = std::chrono::steady_clock::now() + kMeasureTimeout;
        for (;;) {
            std::uint8_t busy = 0U;
            if (const std::int8_t rc = vendor_sensor_is_measuring(&dev_, &busy);
                rc != VENDOR_OK) {
                return std::unexpected(map_vendor_error(rc));
            }
            if (busy == 0U) {
                break;
            }
            if (std::chrono::steady_clock::now() >= deadline) {
                return std::unexpected(SensorStatus::Timeout);
            }
            delay_us(kMeasurePollUs);
        }

        vendor_data_t raw{};
        if (const std::int8_t rc = vendor_sensor_get_data(&dev_, &raw);
            rc != VENDOR_OK) {
            return std::unexpected(map_vendor_error(rc));
        }

        /* Вендорські одиниці (соті градуса й Q24.8 Па) стають величинами,
           якими оперує застосунок. */
        return EnvironmentReading{
            static_cast<float>(raw.temperature) / 100.0F,
            static_cast<float>(raw.pressure_q24_8) / 256.0F / 100.0F};
    }

    /* Викликається лише містками — тому й публічне. */
    bool bus_read(std::uint8_t reg, std::span<std::uint8_t> dst)
    {
        return bus_.read_registers(i2c_addr_, reg, dst);
    }

    bool bus_write(std::uint8_t reg, std::span<const std::uint8_t> src)
    {
        return bus_.write_registers(i2c_addr_, reg, src);
    }

private:
    II2cBus& bus_;
    std::uint8_t i2c_addr_;
    vendor_sensor_dev_t dev_{};
    Mutex lock_{};
    bool ready_{false};
};

}  // namespace detail

namespace {

extern "C" {

std::int8_t bridge_read(std::uint8_t reg, std::uint8_t* data,
                        std::uint32_t len, void* intf_ptr) noexcept
{
    if (intf_ptr == nullptr || data == nullptr || len == 0U) {
        return VENDOR_E_NULL_PTR;
    }
    auto* self = static_cast<detail::AdapterImpl*>(intf_ptr);
    /* Сирий вказівник із довжиною живе рівно один рядок — далі span. */
    return self->bus_read(reg, std::span<std::uint8_t>(data, len))
               ? VENDOR_OK
               : VENDOR_E_COMM_FAIL;
}

std::int8_t bridge_write(std::uint8_t reg, const std::uint8_t* data,
                         std::uint32_t len, void* intf_ptr) noexcept
{
    if (intf_ptr == nullptr || data == nullptr || len == 0U) {
        return VENDOR_E_NULL_PTR;
    }
    auto* self = static_cast<detail::AdapterImpl*>(intf_ptr);
    return self->bus_write(reg, std::span<const std::uint8_t>(data, len))
               ? VENDOR_OK
               : VENDOR_E_COMM_FAIL;
}

void bridge_delay(std::uint32_t period_us, void* intf_ptr) noexcept
{
    static_cast<void>(intf_ptr);
    delay_us(period_us);
}

}  // extern "C"
}  // namespace

std::expected<SensorAdapter, SensorStatus> SensorAdapter::create(
    II2cBus& bus, std::uint8_t i2c_addr)
{
    auto impl = std::make_unique<detail::AdapterImpl>(bus, i2c_addr);
    if (const SensorStatus st = impl->init(); st != SensorStatus::Ok) {
        return std::unexpected(st);
    }
    return SensorAdapter(std::move(impl));
}

SensorAdapter::SensorAdapter(std::unique_ptr<detail::AdapterImpl> impl) noexcept
    : impl_(std::move(impl))
{
}

SensorAdapter::SensorAdapter(SensorAdapter&&) noexcept = default;
SensorAdapter& SensorAdapter::operator=(SensorAdapter&&) noexcept = default;
SensorAdapter::~SensorAdapter() = default;

std::expected<EnvironmentReading, SensorStatus> SensorAdapter::read()
{
    if (!impl_) {
        return std::unexpected(SensorStatus::InvalidParameter);
    }
    return impl_->read();
}

}  // namespace sensor
