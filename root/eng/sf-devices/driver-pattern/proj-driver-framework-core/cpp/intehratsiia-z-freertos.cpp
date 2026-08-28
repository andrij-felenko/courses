/* ============================================================================
 * Інтеграція з FreeRTOS на C++20 через RAII та Co-routines / Notifiers
 * ============================================================================ */
#include "driver_core_impl.hpp"

namespace embed::driver {

template <HardwareBusRegister THardware>
class RtosSyncDriverWrapper {
public:
    explicit RtosSyncDriverWrapper(StaticI2cDriver<THardware>& async_driver) noexcept
        : async_driver_(async_driver) {}

    [[nodiscard]] std::expected<size_t, Status> transfer_blocking(Transaction trans) noexcept {
        // 1. Захоплюємо м'ютекс шини (RAII Lock)
        // BusMutexGuard lock(bus_mutex_);

        // 2. Подаємо транзакцію в асинхронний драйвер
        auto st = async_driver_.submit(trans);
        if (st != Status::Ok) {
            return std::unexpected(st);
        }

        // 3. Очікуємо Task Notification
        // if (!wait_for_notification(trans.timeout_us)) {
        //     return std::unexpected(Status::Timeout);
        // }

        return trans.tx_data.size();
    }

private:
    StaticI2cDriver<THardware>& async_driver_;
};

} // namespace embed::driver
