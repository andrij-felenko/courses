#include <cstdint>
#include <chrono>
#include <concepts>

// Концепт апаратної платформи керування живленням та виводами
template <typename T>
concept HardwareBoardOps = requires(T hw, bool en, uint32_t ms) {
    { hw.set_power_rail(en) } -> std::same_as<void>;
    { hw.isolate_all_gpios() } -> std::same_as<void>;
    { hw.restore_all_gpios() } -> std::same_as<void>;
    { hw.pwrkey_pulse(ms) } -> std::same_as<void>;
    { hw.is_status_active() } -> std::same_as<bool>;
    { hw.delay_ms(ms) } -> std::same_as<void>;
};

template <HardwareBoardOps HwImpl>
class SmartModulePowerController {
public:
    explicit constexpr SmartModulePowerController(HwImpl& hw) : hw_{hw} {}

    [[nodiscard]] bool hard_power_cycle() noexcept {
        // 1. Повна ізоляція пінів хоста для виключення паразитарного живлення
        hw_.isolate_all_gpios();

        // 2. Відключення силового живлення VBAT
        hw_.set_power_rail(false);

        // 3. Гарантована витримка для розряду ємностей декаплінгу
        hw_.delay_ms(1000);

        // 4. Подача напруги живлення
        hw_.set_power_rail(true);
        hw_.delay_ms(200);

        // 5. Відновлення цифрових функцій інтерфейсу
        hw_.restore_all_gpios();

        // 6. Імпульс запуску ядра PWRKEY
        hw_.pwrkey_pulse(1000);

        // 7. Опитування лінії підтвердження апаратної готовності
        for (int i = 0; i < 50; ++i) {
            hw_.delay_ms(100);
            if (hw_.is_status_active()) {
                return true;
            }
        }
        return false;
    }

private:
    HwImpl& hw_;
};
