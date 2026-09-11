#include <iostream>
#include <iomanip>
#include <chrono>
#include <thread>

/**
 * @brief Апаратна реалізація бекенду таймера МК (емуляція апаратури STM32 TIMx/GPIO).
 * 
 * У реальній прошивці під Cortex-M методи напряму звертаються до периферійних
 * регістрів таймера (наприклад, TIM3->PSC, TIM3->ARR, TIM3->CCR1) та портів GPIO.
 */
class Stm32HardwareTimer : public laser::HardwareTimerBackend {
public:
    void configure_timebase(uint32_t prescaler, uint32_t auto_reload) override {
        prescaler_reg_ = prescaler;
        auto_reload_reg_ = auto_reload;
        // Еквівалент: TIM3->PSC = prescaler; TIM3->ARR = auto_reload - 1;
        // Генерує тактову сітку 1 МГц (1 крок = 1 мкс)
    }

    void set_compare_value(uint32_t compare_value) override {
        compare_reg_ = compare_value;
        // Еквівалент: TIM3->CCR1 = compare_value; (тривалість імпульсу на затворі)
    }

    void start_strobe_timer() override {
        timer_running_ = true;
        gate_pin_active_ = true;
        // Еквівалент: TIM3->CCER |= TIM_CCER_CC1E; TIM3->CR1 |= TIM_CR1_CEN;
    }

    void stop_strobe_timer() override {
        timer_running_ = false;
        gate_pin_active_ = false;
        // Еквівалент: TIM3->CR1 &= ~TIM_CR1_CEN; TIM3->CCER &= ~TIM_CCER_CC1E;
    }

    void force_gate_low() override {
        gate_pin_active_ = false;
        // Апаратний скид піна GPIO в нуль: GPIOA->BSRR = GPIO_BSRR_BR6;
    }

    [[nodiscard]] bool is_gate_active() const noexcept { return gate_pin_active_; }
    [[nodiscard]] uint32_t auto_reload() const noexcept { return auto_reload_reg_; }
    [[nodiscard]] uint32_t compare_value() const noexcept { return compare_reg_; }

private:
    uint32_t prescaler_reg_{0};
    uint32_t auto_reload_reg_{0};
    uint32_t compare_reg_{0};
    bool timer_running_{false};
    bool gate_pin_active_{false};
};

/**
 * @brief Допоміжна функція для отримання системного монотонного часу в мілісекундах.
 */
static uint32_t get_system_time_ms() {
    using namespace std::chrono;
    static const auto start_time = steady_clock::now();
    const auto elapsed = duration_cast<milliseconds>(steady_clock::now() - start_time);
    return static_cast<uint32_t>(elapsed.count());
}

/**
 * @brief Текстовий опис робочого стану для телеметрії UART.
 */
static const char* state_to_string(laser::LaserState state) {
    switch (state) {
        case laser::LaserState::Disabled:     return "ВИМКНЕНО (Disabled)";
        case laser::LaserState::Standby:      return "ОЧІКУВАННЯ (Standby)";
        case laser::LaserState::Strobing:     return "СТРОБУВАННЯ (Strobing)";
        case laser::LaserState::FaultLockout: return "АВАРІЙНЕ БЛОКУВАННЯ (FaultLockout)";
        default:                              return "НЕВІДОМО";
    }
}

/**
 * @brief Точка входу вбудованої прошивки керування стробуванням лазера.
 */
int main() {
    std::cout << "========================================================\n"
              << "  Прошивка МК: Синхронізатор стробування лазерної лінії  \n"
              << "========================================================\n\n";

    // 1. Апаратна ініціалізація таймера та виводу керування N-MOSFET
    Stm32HardwareTimer timer_hw;
    laser::LaserStrobeController laser_ctrl(timer_hw);

    // 2. Базова конфігурація для камери тріангулятора (50 FPS, експозиція 250 мкс)
    laser::StrobeConfig cfg;
    cfg.pulse_width_us = 250;          // 250 мкс спалах діода на кадр
    cfg.period_us = 20000;             // 20000 мкс = 50 кадрів на секунду
    cfg.watchdog_timeout_ms = 120;     // Якщо хост мовчить понад 120 мс - аварія
    cfg.max_pulse_width_us = 1000;     // Апаратне обмеження діода
    cfg.max_duty_cycle_permille = 100; // Дозволено до 10% заповнення (250/20000 = 1.25%)
    cfg.sync_mode = laser::SyncMode::ExternalTrigger; // Синхронізація від камери

    uint32_t now = get_system_time_ms();
    if (!laser_ctrl.init(cfg)) {
        std::cerr << "[ПОМИЛКА] Збій ініціалізації параметрів лазера!\n";
        return 1;
    }

    std::cout << "[ІНІЦІАЛІЗАЦІЯ] Таймер налаштовано: період " << cfg.period_us
              << " мкс, імпульс " << cfg.pulse_width_us
              << " мкс, тайм-аут сторожового захисту " << cfg.watchdog_timeout_ms << " мс\n";

    // 3. Активація контролера
    laser_ctrl.enable(now);
    std::cout << "[СТАН] Контролер активовано: " << state_to_string(laser_ctrl.state()) << "\n\n";

    // 4. Головний цикл: симуляція 5 штатних кадрів синхронізації
    std::cout << "--- Фаза 1: Нормальна синхронізована робота (5 кадрів по 20 мс) ---\n";
    for (int frame = 1; frame <= 5; ++frame) {
        now = get_system_time_ms();

        // Симуляція heartbeat від хоста (камера активна)
        laser_ctrl.feed_watchdog(now);

        // Зовнішній імпульс синхронізації від камери (Strobe Out камери -> Ext Trig МК)
        laser_ctrl.trigger_single_strobe();

        // Фонова перевірка сторожового таймера
        laser_ctrl.poll_failsafe(now);

        std::cout << "  Кадр " << frame << " [" << std::setw(4) << now << " мс]: "
                  << "Строб згенеровано! Затвор: " << (timer_hw.is_gate_active() ? "HIGH" : "LOW")
                  << " | Всього стробів: " << laser_ctrl.telemetry().total_strobes
                  << " | Стан: " << state_to_string(laser_ctrl.state()) << "\n";

        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    }

    // 5. Фаза 2: Симуляція зависання хоста / обриву кабелю (зупинка пінгу на 150 мс)
    std::cout << "\n--- Фаза 2: Імітація збою хоста (відсутність пінгу 150 мс) ---\n";
    std::cout << "[УВАГА] Хост перестав надсилати heartbeat-пакети...\n";

    for (int step = 1; step <= 3; ++step) {
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
        now = get_system_time_ms();

        // Спроба викликати строб від камери під час збою
        laser_ctrl.trigger_single_strobe();

        // Перевірка умов безпеки
        laser_ctrl.poll_failsafe(now);

        std::cout << "  Моніторинг [" << std::setw(4) << now << " мс]: "
                  << "Затвор: " << (timer_hw.is_gate_active() ? "HIGH" : "LOW (Захищено)")
                  << " | Стан: " << state_to_string(laser_ctrl.state()) << "\n";

        if (laser_ctrl.state() == laser::LaserState::FaultLockout) {
            std::cout << "  -> [ЗАХИСНЕ БЛОКУВАННЯ СПРАЦЮВАЛО!] Причина: Watchdog Timeout.\n"
                      << "     N-MOSFET ключ апаратно знеструмлено, випромінювання припинено.\n";
            break;
        }
    }

    // 6. Фаза 3: Відновлення зв'язку та безпечний перезапуск
    std::cout << "\n--- Фаза 3: Відновлення хоста та скидання блокування ---\n";
    now = get_system_time_ms();
    laser_ctrl.reset_lockout(now);
    std::cout << "[СКИДАННЯ] Аварійний стан знято: " << state_to_string(laser_ctrl.state()) << "\n";

    laser_ctrl.enable(now);
    laser_ctrl.feed_watchdog(now);
    laser_ctrl.trigger_single_strobe();
    std::cout << "[РОБОТА ВІДНОВЛЕНА] Строб після відновлення успішно згенеровано. Всього імпульсів: "
              << laser_ctrl.telemetry().total_strobes << "\n\n";

    return 0;
}\n
