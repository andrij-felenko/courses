# ⚙️ Драйвер коронного іонізатора: керування високою напругою та захист від дуги

У цій практичній вставці розглядається розробка програмно-апаратного драйвера для керування високовольтним джерелом живлення коронного розряду (5–15 кВ) на базі мікроконтролера. Пристрій призначений для живлення електростатичного очисника повітря (ESP), побутового іонізатора або лабораторного озонізатора.

### Апаратне завдання та небезпека іскрового пробою

Живлення коронного розряду виконується від імпульсного підвищувального перетворювача (Flyback або розкачка високовольтного трансформатора з помножувачем напруги Коккрофта-Волтона). Мікроконтролер генерує ШІМ-сигнал з частотою 30–80 кГц, варіюючи коефіцієнт заповнення для регулювання напруги та струму корони.

Головна вимога до схеми живлення — забезпечення надзвичайно швидкої реакції на динаміку навантаження. Коронний розряд є стійким лише у вузькому діапазоні струмів (від десятків мікроампер до 1–2 міліампер). Якщо напруга перевищить поріг іскроутворення або між електродами пролетить велика частинка пилу чи крапля вологи, локальне поле зросте і коронний розряд за лічені мікросекунди переросте у короткі згубні **іскри або дугу**. 

Дуговий пробій має від'ємний диференціальний опір: струм через пробійний канал стрімко росте, а напруга падає до десятків вольтів. Це загрожує виходом з ладу ключових транзисторів перетворювача та пробоєм високовольтного трансформатора.

Драйвер мусить вирішувати три головні задачі:
1. **Точне вимірювання струму:** вимірювати струм корони за допомогою вимірювального шунта у заземленій гілці повернення струму катода та швидкісного аналого-цифрового перетворювача (АЦП/ADC).
2. **ПІД-стабілізація:** підтримувати заданий струм корони (наприклад, 200 мкА) за допомогою цифрового регулятора, адаптуючи коефіцієнт заповнення ШІМ під зміни вологості та температури повітря.
3. **Аварійне придушення дуги:** реагувати на сплески струму. Якщо струм перевищує аварійну межу (наприклад, 1.5 мА), що свідчить про початок іскрового пробою, ШІМ-генератор мусить негайно вимикатися за 1–2 мікросекунди, а після паузи в 50 мс плавно перезапускати розряд у режимі м'якого старту (Soft-start).

### Топологія силової частини та високовольтного перетворювача

Силова частина драйвера складається з однотактного зворотньоходового перетворювача (Flyback). Первинна обмотка високовольтного трансформатора комутується силовим N-канальним MOSFET-транзистором (наприклад, TK15A60D, `V_ds = 600 В`, `R_ds(on) = 0.3 Ом`). Для затвора MOSFET використовується спеціалізований драйвер нижнього плеча (TC4420 або MIC4427), який забезпечує вхідний струм перезарядки ємності затвора до 6 Ампер. Це гарантує тривалість фронту вмикання й вимикання менше 20 наносекунд, мінімізуючи динамічні втрати на транзисторі.

Вторинна обмотка трансформатора видає імпульсну напругу амплітудою 2–3 кіловольти, яка подається на 4-каскадний симетричний помножувач напруги Коккрофта-Волтона, зібраний на високочастотних високовольтних діодах (2CL77, `15 кВ, 100 нс`) та керамічних конденсаторах (`1 нФ, 6 кВ`). На виході помножувача формується постійна від'ємна напруга до -15 кіловольт.

Для обмеження максимального струму короткого замикання послідовно з високовольтним виходом вмикається безиндуктивний захисний резистор `R_out = 100 кОм` (потужністю 5 Вт, розрахований на високу напругу). Цей резистор виконує роль першої лінії захисту: він обмежує піковий струм розряду ємності помножувача при раптовому іскровому пробої.

### Архітектура аналогового фронтенду (AFE) та захист мікроконтролера

Вимірювальний шунт `R_sense = 1.0 кОм` (точність 1%) включається у розрив між заземленим анодом (чи катодом) і загальною шиною схеми. При робочому струмі корони 200 мкА падіння напруги на шунті становить `U_sense = 200 мкА · 1 кОм = 0.2 В`. При аварійному дуговому пробої струм може підскочити до 100 міліампер, що створило б на шунті імпульс напруги до 100 вольтів, здатний миттєво спалити порт АЦП мікроконтролера.

Для захисту порту використовується двокаскадна схема:
- Паралельно шунту встановлюється швидкодіючий захисний TVS-діод (супресор SMBJ3.3A) із напругою обмеження 3.3 В та диференційним опором у кілька міліом у відкритому стані.
- Сигнал із шунта подається через захисний резистор 4.7 кОм на аналоговий вимірювальний підсилювач із низькочастотним RC-фільтром (`f_cut = 50 кГц`), що зрізає високочастотні наводки від імпульсів Трічеля.
- Сигнал також подається на аналоговий компаратор мікроконтролера (або зовнішній аналоговий компаратор LM319), вихід якого підключений до апаратного входу блокування таймера `BRK` (Break Input). Це забезпечує залізне апаратне вимкнення ШІМ за 50–100 наносекунд без участі процесорного ядра.

### Програмна реалізація та алгоритм цифрового регулятора

Програмне забезпечення керування розбито на два шари:
1. **Швидкий контур (ISR / АЦП):** обробник переривання АЦП, що виконується з частотою 10 кілогерц. Він виконує первинне зчитування вибірки струму, перевіряє ліміт аварійного струму `TRIP_CURRENT` та розраховує черговий крок ПІД-регулятора.
2. **Повільний контур (System Tick / 1 мс):** системний фоновий процес, що керує автоматом станів (State Machine), обробляє таймери затримки відновлення після пробою та передає дані по протоколу зв'язку Modbus RTU.

Нижче наведено приклад реалізації керуючого програмного забезпечення драйвера у двох варіантах: процедурний C та об'єктно-орієнтований C++.

:::tabs
```c
/* corona_driver.c — Реалізація драйвера високовольтної корони мовою C */

#include <stdint.h>
#include <stdbool.h>

#define PWM_MAX_DUTY        1024U
#define CORONA_SETPOINT_UA  200U   /* Цільовий струм корони: 200 мкА */
#define TRIP_CURRENT_UA     1500U  /* Поріг аварійного обриву дуги: 1.5 мА */
#define RECOVERY_DELAY_MS   50U

typedef enum {
    CORONA_STATE_OFF = 0,
    CORONA_STATE_SOFT_START,
    CORONA_STATE_RUNNING,
    CORONA_STATE_ARC_TRIPPED
} corona_state_t;

typedef struct {
    corona_state_t state;
    uint32_t current_ua;      /* Поточний виміряний струм (мкА) */
    uint32_t target_ua;       /* Уставка струму (мкА) */
    uint16_t pwm_duty;        /* Поточний ШІМ (0..1024) */
    uint32_t trip_count;      /* Лічильник спрацьовувань захисту */
    uint32_t recovery_timer;  /* Таймер відновлення */
    
    /* Коефіцієнти ПІД-регулятора */
    int32_t kp;
    int32_t ki;
    int32_t integral;
} corona_driver_t;

/* Глобальний екземпляр драйвера */
static corona_driver_t g_corona;

/* Апаратні функції-заглушки для виклику периферії MCU */
static inline void hardware_pwm_set_duty(uint16_t duty) {
    /* Запис у регістр порівняння таймера ШІМ (наприклад, TIM1->CCR1) */
    (void)duty;
}

static inline void hardware_pwm_disable(void) {
    /* Негайне аварійне вимкнення виходу ШІМ */
    hardware_pwm_set_duty(0);
}

static inline uint32_t hardware_adc_read_current_ua(void) {
    /* Зчитування АЦП із падіння напруги на шунті R_sense */
    /* 1 В на шунті 1 кОм відповідає 1000 мкА */
    return g_corona.current_ua; /* У симуляції повертаємо поточний струм */
}

void corona_init(corona_driver_t *drv, uint32_t target_ua) {
    drv->state = CORONA_STATE_OFF;
    drv->current_ua = 0;
    drv->target_ua = target_ua;
    drv->pwm_duty = 0;
    drv->trip_count = 0;
    drv->recovery_timer = 0;
    drv->kp = 2;
    drv->ki = 1;
    drv->integral = 0;
    hardware_pwm_disable();
}

void corona_start(corona_driver_t *drv) {
    drv->state = CORONA_STATE_SOFT_START;
    drv->pwm_duty = 50; /* Початковий мінімальний ШІМ */
    drv->integral = 0;
    hardware_pwm_set_duty(drv->pwm_duty);
}

/* Швидкий обробник вибірки АЦП (викликається у перериванні АЦП/Таймера, наприклад 10 кГц) */
void corona_fast_isr_loop(corona_driver_t *drv) {
    if (drv->state == CORONA_STATE_OFF) {
        return;
    }

    uint32_t i_meas = hardware_adc_read_current_ua();
    drv->current_ua = i_meas;

    /* КРИТИЧНИЙ ЗАХИСТ: Негайний детектор дугового пробою */
    if (i_meas >= TRIP_CURRENT_UA) {
        hardware_pwm_disable();
        drv->pwm_duty = 0;
        drv->state = CORONA_STATE_ARC_TRIPPED;
        drv->trip_count++;
        drv->recovery_timer = RECOVERY_DELAY_MS;
        return;
    }

    /* ПІД-регулювання струму у робочих режимах */
    if (drv->state == CORONA_STATE_RUNNING || drv->state == CORONA_STATE_SOFT_START) {
        int32_t error = (int32_t)drv->target_ua - (int32_t)i_meas;
        drv->integral += error;
        
        /* Анти-вінд-ап обмеження інтеграла */
        if (drv->integral > 5000) drv->integral = 5000;
        if (drv->integral < -5000) drv->integral = -5000;

        int32_t output = (drv->kp * error) + ((drv->ki * drv->integral) / 100);
        int32_t new_duty = (int32_t)drv->pwm_duty + (output / 10);

        if (new_duty > (int32_t)PWM_MAX_DUTY) new_duty = PWM_MAX_DUTY;
        if (new_duty < 0) new_duty = 0;

        drv->pwm_duty = (uint16_t)new_duty;
        hardware_pwm_set_duty(drv->pwm_duty);

        if (drv->state == CORONA_STATE_SOFT_START && i_meas >= (drv->target_ua * 8 / 10)) {
            drv->state = CORONA_STATE_RUNNING;
        }
    }
}

/* Фоновий системний такт (викликається кожні 1 мс) */
void corona_process_tick_1ms(corona_driver_t *drv) {
    if (drv->state == CORONA_STATE_ARC_TRIPPED) {
        if (drv->recovery_timer > 0) {
            drv->recovery_timer--;
        } else {
            /* Перезапуск після аварії */
            corona_start(drv);
        }
    }
}
```

```cpp
// corona_driver.cpp — Ідіоматична реалізація драйвера корони мовою C++20

#include <cstdint>
#include <optional>
#include <system_error>

namespace PowerElectronics {

enum class CoronaState : uint8_t {
    Off,
    SoftStart,
    Running,
    ArcTripped,
    FaultHardware
};

struct CoronaConfig {
    uint32_t targetCurrentUa{200};
    uint32_t tripCurrentUa{1500};
    uint16_t maxPwmDuty{1024};
    uint32_t recoveryDelayMs{50};
    int32_t kp{2};
    int32_t ki{1};
};

class CoronaPowerSupply {
public:
    explicit CoronaPowerSupply(CoronaConfig config)
        : config_(config), state_(CoronaState::Off) {}

    ~CoronaPowerSupply() {
        stopHardwarePwm();
    }

    // Заборона копіювання (RAII керування високою напругою)
    CoronaPowerSupply(const CoronaPowerSupply&) = delete;
    CoronaPowerSupply& operator=(const CoronaPowerSupply&) = delete;

    CoronaPowerSupply(CoronaPowerSupply&&) noexcept = default;
    CoronaPowerSupply& operator=(CoronaPowerSupply&&) noexcept = default;

    void start() noexcept {
        state_ = CoronaState::SoftStart;
        pwmDuty_ = 50;
        integral_ = 0;
        applyHardwarePwm(pwmDuty_);
    }

    void stop() noexcept {
        state_ = CoronaState::Off;
        stopHardwarePwm();
    }

    // Швидкий обробник АЦП (викликається з ISR)
    void processAdcSample(uint32_t measuredCurrentUa) noexcept {
        currentUa_ = measuredCurrentUa;

        if (state_ == CoronaState::Off || state_ == CoronaState::FaultHardware) {
            return;
        }

        // Аварійний захист від пробою дуги
        if (measuredCurrentUa >= config_.tripCurrentUa) {
            stopHardwarePwm();
            state_ = CoronaState::ArcTripped;
            tripCount_++;
            recoveryTimerMs_ = config_.recoveryDelayMs;
            return;
        }

        if (state_ == CoronaState::Running || state_ == CoronaState::SoftStart) {
            updateControlLoop(measuredCurrentUa);
        }
    }

    void handleSysTick1ms() noexcept {
        if (state_ == CoronaState::ArcTripped) {
            if (recoveryTimerMs_ > 0) {
                --recoveryTimerMs_;
            } else {
                start(); // М'який перезапуск
            }
        }
    }

    [[nodiscard]] CoronaState state() const noexcept { return state_; }
    [[nodiscard]] uint32_t currentUa() const noexcept { return currentUa_; }
    [[nodiscard]] uint16_t pwmDuty() const noexcept { return pwmDuty_; }
    [[nodiscard]] uint32_t tripCount() const noexcept { return tripCount_; }

private:
    void updateControlLoop(uint32_t iMeas) noexcept {
        const int32_t error = static_cast<int32_t>(config_.targetCurrentUa) - static_cast<int32_t>(iMeas);
        integral_ += error;

        if (integral_ > 5000) integral_ = 5000;
        if (integral_ < -5000) integral_ = -5000;

        const int32_t output = (config_.kp * error) + ((config_.ki * integral_) / 100);
        int32_t newDuty = static_cast<int32_t>(pwmDuty_) + (output / 10);

        if (newDuty > static_cast<int32_t>(config_.maxPwmDuty)) newDuty = config_.maxPwmDuty;
        if (newDuty < 0) newDuty = 0;

        pwmDuty_ = static_cast<uint16_t>(newDuty);
        applyHardwarePwm(pwmDuty_);

        if (state_ == CoronaState::SoftStart && iMeas >= (config_.targetCurrentUa * 8 / 10)) {
            state_ = CoronaState::Running;
        }
    }

    void applyHardwarePwm(uint16_t duty) noexcept {
        // Реєстровий виклик периферії MCU
        pwmDuty_ = duty;
    }

    void stopHardwarePwm() noexcept {
        pwmDuty_ = 0;
        applyHardwarePwm(0);
    }

    CoronaConfig config_;
    CoronaState state_;
    uint32_t currentUa_{0};
    uint16_t pwmDuty_{0};
    uint32_t tripCount_{0};
    uint32_t recoveryTimerMs_{0};
    int32_t integral_{0};
};

} // namespace PowerElectronics
```
:::

### Особливості апаратної реалізації, ізоляції та моніторингу

При практичній збірці драйвера коронного розряду необхідно дотримуватися суворих правил високовольтного монтажу та проектування печатних плат:

1. **Ізоляційні зазори (Creepage & Clearance):** відстань між високовольтною частиною (помножувачем напруги) та низьковольтною мікроконтролерною частиною мусить становити не менше 10 мм на кожен 10 кіловольт напруги. У печатній платі виконують фрезеровані ізоляційні пази (slots), щоб запобігти витоку струму по поверхні текстоліту FR-4 під дією накопичення пилу й вологи.
2. **Заливку компаундом:** високовольтну частину (трансформатор та помножувач) після збірки та випробувань заливають двокомпонентним силіконовим або епоксидним високовольтним компаундом (електрична міцність понад 20 кВ/мм). Це запобігає виникненню паразитного коронного розряду безпосередньо між елементами самій друкованої плати.
3. **Алгоритм м'якого старту (Soft-start):** після спрацьовування захисту від дуги відновлення напруги не повинно відбуватися стрибком. Початок подачі ШІМ із мінімального значення (5% коефіцієнта заповнення) із поступовим плаваючим підвищенням запобігає виникненню повторних дугових пробоїв у гарячому іонізованому каналі, який ще не встиг повністю деіонізуватися.
4. **Фільтрація завад від імпульсів Трічеля:** при використанні від'ємної корони високочастотні струмові імпульси можуть створювати фальшиві спрацьовування відсічки. Аналоговий фільтр на вході АЦП підбирають так, щоб він згладжував імпульси Трічеля (тривалістю 50 нс), але миттєво пропускав справжній дуговий сплеск тривалістю понад 2 мікросекунди.
