// main.cpp — порядок старту серійного виробу й нагляд за ним.
//
// Різниця з макетом видна вже в перших рядках main(): макет починає
// з ініціалізації давача, виріб — зі знеструмлення силової частини
// і з питання «а чому ми взагалі перезапустилися?».
#include "crash_report.hpp"
#include "platform.hpp"
#include "safety.hpp"
#include "telemetry.hpp"

#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>

namespace {

// ---- Час -----------------------------------------------------------------

std::atomic<std::uint32_t> g_ms{0};

[[nodiscard]] std::uint32_t now_ms() noexcept
{
    return g_ms.load(std::memory_order_relaxed);
}

void systick_init() noexcept
{
    stm32::systick::rvr::write(stm32::cpu_hz / 1000U - 1U);
    stm32::systick::cvr::write(0U);
    stm32::systick::csr::write(stm32::systick::enable);
}

// Різниця моментів, стійка до переповнення 32-бітного лічильника:
// через 49 діб безперервної роботи він піде на другий круг, і наївне
// порівняння «>=» тоді зупинило б телеметрію назавжди.
[[nodiscard]] bool reached(std::uint32_t deadline) noexcept
{
    return static_cast<std::int32_t>(now_ms() - deadline) >= 0;
}

// ---- Незалежний сторож із програмним вікном ------------------------------
//
// IWDG тактується власним RC ≈32 кГц: він переживе і тріснутий кварц,
// і зупинку основного тактування. Апаратного вікна у F4 немає, тож вікно
// робимо самі, і воно двобічне:
//
//   надто пізно -> сторож перезапустить нас апаратно;
//   надто рано  -> це ознака, що цикл провалився в порожнє коло зі
//                  скиданням сторожа, і ми зупиняємося самі.
//
// До цього додається перекличка: сторожа годуємо лише тоді, коли за
// період відзвітували ВСІ задачі. Інакше зависла задача ховалася б за
// живою сусідкою.

enum class Task : std::size_t { control, telemetry };
inline constexpr std::size_t task_count = 2U;

template <std::size_t TaskCount>
class WindowedWatchdog {
    static_assert(TaskCount > 0 && TaskCount <= 32U);

public:
    explicit WindowedWatchdog(std::uint32_t window_min_ms) noexcept
        : window_min_ms_{window_min_ms}
    {
    }

    void start() noexcept
    {
        using namespace stm32::iwdg;

        kr::write(key_unlock);
        pr::write(4U);     // дільник 64: 32000/64 = 500 Гц, крок 2 мс
        rlr::write(1023U); // 1024 кроки ≈ 2048 мс
        while (sr::read() != 0U) {
            // чекаємо, поки регістри перепишуться в домен сторожа
        }
        kr::write(key_feed);
        kr::write(key_start);

        last_feed_ms_ = now_ms();
        reported_ = 0U;
    }

    void check_in(Task task) noexcept
    {
        reported_ |= 1U << static_cast<std::size_t>(task);
    }

    void service() noexcept
    {
        if (reported_ != all_mask) {
            return; // хтось не відзвітував — сторожа не годуємо
        }

        if (now_ms() - last_feed_ms_ < window_min_ms_) {
            // Усі задачі відзвітували швидше, ніж фізично можливо:
            // керуючий цикл або крутиться порожнім колом, або зіпсовано
            // лічильник часу. Це аварія, а не привід годувати сторожа.
            safety::panic(diag::PanicReason::loop_too_fast);
        }

        stm32::iwdg::kr::write(stm32::iwdg::key_feed);
        last_feed_ms_ = now_ms();
        reported_ = 0U;
    }

private:
    static constexpr std::uint32_t all_mask = (1U << TaskCount) - 1U;

    std::uint32_t window_min_ms_;
    std::uint32_t last_feed_ms_{0};
    std::uint32_t reported_{0};
};

// ---- Прикладна частина ---------------------------------------------------
//
// Давач вібрації віддає готовність рівнем на PA1 (DRDY). Макет чекав би
// на нього нескінченним while; виріб чекає з таймаутом і має відповідь
// на випадок «не дочекалися».

inline constexpr unsigned pin_sensor_drdy = 1U;
inline constexpr std::uint32_t sensor_timeout_ms = 50U;

void sensor_init() noexcept
{
    stm32::rcc::ahb1enr::set(stm32::rcc::gpioa_en);
    hw::dsb();

    stm32::gpioa::set_mode(pin_sensor_drdy, stm32::gpioa::Mode::input);
    stm32::gpioa::set_pull(pin_sensor_drdy, stm32::gpioa::Pull::down);
}

// Період силового ШІМ: 168 МГц / 8400 = 20 кГц — вище чутного діапазону
// і нижче за межу комутаційних втрат мосту.
void pwm_init() noexcept
{
    using namespace stm32;

    tim1::psc::write(0U);
    tim1::arr::write(8399U);
    tim1::ccr1::write(0U);
    // OC1M = 110 (ШІМ-режим 1) плюс попереднє завантаження CCR1.
    tim1::ccmr1::modify(0x7FU, (0b110U << 4) | (1U << 3));
}

[[nodiscard]] bool sensor_wait_ready(std::uint32_t timeout_ms) noexcept
{
    const std::uint32_t started = now_ms();
    while (!stm32::gpioa::read_pin(pin_sensor_drdy)) {
        if (now_ms() - started >= timeout_ms) {
            return false;
        }
    }
    return true;
}

void control_step() noexcept
{
    if (!sensor_wait_ready(sensor_timeout_ms)) {
        // Макет тут написав би printf і поїхав далі з торішніми даними.
        // Виріб не має права керувати приводом наосліп.
        safety::panic(diag::PanicReason::sensor_timeout);
    }

    // Тут була б обробка вимірювання; для розмови про безпечний стан
    // досить того, що вона задає шпаруватість силового ШІМ.
    const std::uint32_t period = stm32::tim1::arr::read();
    const std::uint32_t duty = period / 4U;
    safety::require(duty <= period); // інваріант: шпаруватість у межах періоду
    stm32::tim1::ccr1::write(duty);
}

// ---- Перевірка силового каскаду на старті --------------------------------
//
// Коротко подаємо живлення на міст із малою шпаруватістю й дивимося, чи
// відповідає давач і чи не просідає шина під навантаженням. Гілок виходу
// три, і в кожній каскад мусить лишитися знеструмленим: у C це рівно те
// місце, де пишуть goto out і де його забувають. Тут за всі три гілки
// відповідає час життя guard — забути неможливо.
[[nodiscard]] bool power_stage_self_test() noexcept
{
    safety::PowerStageGuard guard{true};
    if (!guard) {
        return false;
    }

    stm32::tim1::ccr1::write(stm32::tim1::arr::read() / 10U);

    if (!sensor_wait_ready(sensor_timeout_ms)) {
        return false;
    }

    const std::uint32_t started = now_ms();
    while (now_ms() - started < 5U) {
        if (safety::SupplyMonitor::sagging()) {
            return false;
        }
    }
    return true;
}

// ---- Цикл нагляду --------------------------------------------------------
//
// Дозвіл на силову частину прив'язаний до сеансу керування: поки guard
// живий — каскад працює. Аварійний вихід із циклу проходить через panic(),
// а той гасить каскад першою ж дією, ще до запису діагностики.
[[noreturn]] void run_supervised(bool allow_power) noexcept
{
    WindowedWatchdog<task_count> watchdog{200U};
    watchdog.start();

    // Guard створюємо навіть тоді, коли живлення заборонено: у цьому разі
    // він лишається незарядженим, і цикл працює як звичайний наглядач
    // без силової частини.
    safety::PowerStageGuard power_guard{allow_power};
    if (allow_power && !power_guard) {
        diag::Telemetry::line("FAIL: силову частину зафіксовано в аварії");
    }

    std::array<char, 192> scratch{};
    std::uint32_t telemetry_due = now_ms() + 1000U;

    for (;;) {
        // Живлення просіло під час роботи — гасимо силову частину НЕГАЙНО,
        // поки логіка ще детермінована, і не чекаємо, доки ядро дійде
        // до стану, в якому воно псує Flash.
        if (safety::SupplyMonitor::sagging()) [[unlikely]] {
            diag::Journal::note_uptime(now_ms());
            safety::panic(diag::PanicReason::brown_out);
        }

        if (power_guard) {
            control_step();
        }
        // Коли силову частину заблоковано, пристрій не вимикається і не
        // зациклюється мовчки: він далі годує сторожа й шле телеметрію,
        // щоб сервіс бачив живий вузол і причину блокування.
        watchdog.check_in(Task::control);

        if (reached(telemetry_due)) {
            if (const auto report = diag::Journal::load(); report) {
                diag::Telemetry::line(diag::Telemetry::render(*report, scratch));
            } else {
                diag::Telemetry::line(diag::to_string(report.error()));
            }
            diag::Journal::note_uptime(now_ms());
            telemetry_due = now_ms() + 1000U;
        }
        watchdog.check_in(Task::telemetry);

        watchdog.service();
    }
}

// Скільки поспіль аварій дозволяємо, перш ніж перестати заводити силову
// частину зовсім. Пристрій, який після кожного рестарту знову б'є приводом
// у механізм, небезпечніший за мовчазний.
inline constexpr std::uint32_t fault_lockout_threshold = 3U;

} // namespace

extern "C" void SysTick_Handler()
{
    g_ms.fetch_add(1U, std::memory_order_relaxed);
}

int main()
{
    // 1. Механіка. До будь-чого іншого.
    safety::PowerStage::arm_outputs();

    // 2. Чому ми тут. Прапорці причини читаємо й гасимо одразу, поки
    //    ніхто їх не затер.
    const diag::ResetCause cause = diag::Journal::begin_boot();

    // 3. Годинник, монітор живлення, діагностичний порт.
    systick_init();
    safety::SupplyMonitor::init();
    diag::Telemetry::init();
    sensor_init();
    pwm_init();

    // 4. Рішення про запуск силової частини. Журнал приходить як
    //    std::expected: полів не прочитати, не розібравшись спершу,
    //    чи він узагалі цілий.
    std::array<char, 192> scratch{};
    bool allow_power = true;

    if (const auto report = diag::Journal::load(); report) {
        diag::Telemetry::line(diag::Telemetry::render(*report, scratch));

        if (report->fault_count >= fault_lockout_threshold) {
            diag::Telemetry::line("LOCKOUT: забагато аварій поспіль, силова частина заблокована");
            allow_power = false;
        }
    } else {
        diag::Telemetry::line(diag::to_string(report.error()));
        // Без достовірної історії аварій ми не знаємо, скільки разів уже
        // падали. Обережність дорожча за один зайвий виїзд сервісу.
        allow_power = false;
    }

    if (cause == diag::ResetCause::brown_out || safety::SupplyMonitor::sagging()) {
        diag::Telemetry::line("HOLD: живлення нижче порога PVD, чекаємо відновлення");
        allow_power = false;
    }

    // 5. Коротка перевірка силового каскаду під навантаженням. Макет
    //    цього не робить узагалі: там людина бачить прилад на столі.
    if (allow_power && !power_stage_self_test()) {
        diag::Telemetry::line("SELFTEST: силовий каскад не пройшов перевірку");
        allow_power = false;
    }

    // 6. Сторожа заводимо ПІСЛЯ ініціалізації, але ДО прикладного циклу:
    //    завислий старт теж мусить закінчитися рестартом.
    run_supervised(allow_power);
}
