// Перевизначення обробника порушення контрактів для мікроконтролера
namespace gsl {
    [[noreturn]] void fail_fast() noexcept {
        // 1. Апаратне вимкнення небезпечних виконавчих механізмів (двигунів, реле)
        disable_actuators_hardware();

        // 2. Запис діагностичного коду у Flash/NVRAM
        save_crash_dump();

        // 3. Перезавантаження мікроконтролера через Watchdog
        NVIC_SystemReset();
    }
}
