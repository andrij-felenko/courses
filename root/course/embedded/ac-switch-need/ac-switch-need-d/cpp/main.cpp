// Опто-драйвер симістора (MOC3021) керується логічним рівнем через резистор.
// GPIO живить лише вхідний світлодіод драйвера; мережа — за оптичним бар'єром.
#include <driver/gpio.h>

namespace mains {

// Ключ володіє виводом як ресурсом: конструктор налаштовує ніжку й одразу
// гасить нагрівач, деструктор гасить його ще раз. Забути вимкнути мережеве
// навантаження на виході зі своєї області видимості вже неможливо.
class OptoTriacSwitch {
public:
    explicit OptoTriacSwitch(gpio_num_t pin) noexcept : pin_{pin} {
        gpio_set_direction(pin_, GPIO_MODE_OUTPUT);
        apply(false); // нагрівач вимкнено, доки не накажемо
    }

    ~OptoTriacSwitch() noexcept { apply(false); }

    // Ніжка — унікальний ресурс: два об'єкти на одному виводі гасили б
    // навантаження один одному, тому копіювання заборонено назовсім.
    OptoTriacSwitch(const OptoTriacSwitch&) = delete;
    OptoTriacSwitch& operator=(const OptoTriacSwitch&) = delete;

    // Світлодіод світить → внутрішній симістор драйвера відмикає силовий.
    void on() noexcept { apply(true); }

    // Світло гасне — але силовий симістор догорає до найближчого переходу
    // струму через нуль: защіпка тримається, поки струм більший за I_H.
    // Тобто це «наказ вимкнутися», а не миттєве вимкнення.
    void off() noexcept { apply(false); }

    void set(bool state) noexcept { apply(state); }

    [[nodiscard]] bool isOn() const noexcept { return on_; }

private:
    void apply(bool state) noexcept {
        on_ = state;
        gpio_set_level(pin_, state ? 1 : 0);
    }

    gpio_num_t pin_;
    bool on_{false};
};

// GPIO ESP32 → 120 Ом → світлодіод MOC3021 → 330 Ом → затвор силового симістора.
inline constexpr gpio_num_t kHeaterPin = GPIO_NUM_4;

} // namespace mains

extern "C" void app_main() {
    // Час життя об'єкта = час, поки нагрівачем узагалі можна керувати.
    mains::OptoTriacSwitch heater{mains::kHeaterPin};

    heater.on();
    // …тут працює регулятор температури: heater.set(потрібноГріти)…
    heater.off();

    // Вихід із області видимості гасить ключ навіть на аварійному шляху.
}
