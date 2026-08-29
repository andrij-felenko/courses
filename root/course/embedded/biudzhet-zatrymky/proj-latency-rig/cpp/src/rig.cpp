#include "rig.hpp"

extern "C" {
#include "stm32f4xx.h"
}

namespace latency {

MeasurementRig &rig() noexcept
{
    static MeasurementRig instance;
    return instance;
}

void MeasurementRig::on_capture(board::Microseconds timestamp) noexcept
{
    if (!armed_.load(std::memory_order_acquire)) {
        return; // спрацювання поза вікном виміру: шум, дзвін фронту, відлуння
    }
    armed_.store(false, std::memory_order_relaxed);

    const board::Microseconds start{start_us_.load(std::memory_order_relaxed)};
    capture_us_.store((timestamp - start).count(), std::memory_order_relaxed);
    ready_.store(true, std::memory_order_release);
}

std::optional<board::Microseconds> MeasurementRig::run_trial() noexcept
{
    ready_.store(false, std::memory_order_relaxed);

    // Вікно чутливості відкриваємо ДО спалаху: на короткому тракті фронт
    // відгуку інакше прийшов би в замасковане переривання й пропав би.
    board::OpticalWindow window;
    board::LedFlash flash;

    const board::Microseconds start = board::now();
    start_us_.store(start.count(), std::memory_order_relaxed);
    armed_.store(true, std::memory_order_release);
    // Між запалюванням світлодіода і зведенням armed_ лежить кількасот
    // наносекунд. Жоден відеотракт за цей час не відповідає, тож фронт,
    // що прийшов би сюди, був би не відгуком, а засвіткою.

    while (true) {
        if (ready_.load(std::memory_order_acquire)) {
            window.close();
            return board::Microseconds{capture_us_.load(std::memory_order_relaxed)};
        }

        if ((board::now() - start) >= kTimeout) {
            // Знімаємо готовність до захоплення ПЕРШИМ ділом: фронт, що
            // прийде за мить, уже не має права додати зразок поверх
            // зарахованого таймауту.
            armed_.store(false, std::memory_order_release);
            window.close();

            // Але той, хто встиг до зняття, — законний вимір, а не втрата.
            if (ready_.load(std::memory_order_acquire)) {
                return board::Microseconds{capture_us_.load(std::memory_order_relaxed)};
            }
            return std::nullopt;
        }
    }
}

} // namespace latency

// Вектор переривання від компаратора фотоприймача.
extern "C" void EXTI0_IRQHandler(void)
{
    // Найперший рядок — зняття часу; усе інше на вимір уже не впливає.
    const auto timestamp = board::now();
    board::clear_optical_flag();
    latency::rig().on_capture(timestamp);
}
