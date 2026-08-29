/* main.cpp — маршрут із п'яти кроків, пройдений кодом.
 *
 * Datasheet          → ніжки PB6/PB7 і номер альтернативної функції 4;
 * Reference Manual   → шини, тактування, карта регістрів, порядок ініціалізації;
 * Programming Manual → NVIC, пріоритет вектора, бар'єри DSB/ISB;
 * Errata Sheet       → ревізія кремнію й обхід зависання шини I2C.
 *
 * Збирається як -std=c++23 -fno-exceptions -fno-rtti -fno-threadsafe-statics:
 * без винятків, тому помилки їдуть у std::expected, а не летять угору.
 */
#include <cstdint>

#include "hw/i2c_bus.hpp"
#include "hw/periodic_timer.hpp"
#include "hw/silicon.hpp"

namespace {

/* Числа з Datasheet і розділу тактування Reference Manual для плати з
 * кварцом 8 МГц і PLL на 168 МГц. Таймери APB1 бачать подвоєну частоту
 * шини, бо дільник APB1 не одиничний (RM0090 §6.2). */
constexpr hw::Hertz cpu_clock  = 168'000'000U;
constexpr hw::Hertz apb1_clock =  42'000'000U;
constexpr hw::Hertz tim2_clock =  84'000'000U;

/* Останній код помилки лишається в пам'яті: у пристрої без консолі це все,
 * що побачить інженер, підключившись налагоджувачем до зупиненої плати. */
volatile std::uint32_t g_last_error = 0;

[[noreturn]] void halt(std::uint32_t code) noexcept
{
    g_last_error = code;
    for (;;) {
        /* Тут у справжньому виробі спрацював би сторожовий таймер. */
    }
}

} // namespace

int main()
{
    /* Перше питання до заліза: чи це той чип, під який набрано карту
     * регістрів і таблицю еррати? Чужий DEV_ID означає, що всі наші
     * зміщення вказують у порожнечу. */
    const auto identity = hw::silicon::identify();
    if (!identity) {
        halt(0xDEAD0001U);
    }

    /* Ревізія вирішує, які обходи вмикати: на новому кремнії гілка нижче
     * не виконається, і старт не сповільниться. */
    const bool lock_possible = hw::silicon::affected(hw::silicon::Erratum::i2c_busy_lock);

    auto bus = hw::I2cBus::open(apb1_clock, cpu_clock);
    if (!bus) {
        halt(0xDEAD0002U);
    }

    /* Шина може бути зайнята вже на старті: пристрій міг перезавантажитися
     * посеред кадру, лишивши веденого з недорахованим байтом. */
    if (bus->busy()) {
        if (!lock_possible) {
            /* Ревізія не уражена, а BUSY стоїть: еррата тут ні до чого,
             * але сама послідовність звільнення шини лишається правильною. */
            g_last_error = 0x1BADC0DEU;
        }
        if (!bus->recover()) {
            halt(0xDEAD0003U);
        }
    }

    auto timer = hw::PeriodicTimer::start_1khz(tim2_clock);
    if (!timer) {
        halt(0xDEAD0004U);
    }

    std::uint32_t last_second = timer->ticks();

    for (;;) {
        const std::uint32_t now = timer->ticks();

        /* Віднімання без порівняння «більше»: коли лічильник переповниться
         * через 49 діб, різниця беззнакових лишиться правильною. */
        if (now - last_second >= 1'000U) {
            last_second += 1'000U;

            /* Раз на секунду дивимося, чи не завис контролер знову: еррата
             * спрацьовує не на старті, а посеред роботи. */
            if (bus->busy()) {
                (void)bus->recover();
            }
        }
    }
}
