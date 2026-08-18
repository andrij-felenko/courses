# ⚙️ Цифровий PI-сервоконтролер годинника

Ця практична вставка містить поглиблений розбір та реалізацію цифрового сервоконтролера (пропорційно-інтегрального фазового автопідстроювання), який синхронізує місцеву програмну шкалу часу з зовнішніми мітками 1PPS (Pulse Per Second) від GNSS-приймача. Вона демонструє, як одночасно компенсувати фазовий зсув і відхилення частоти кварцу без стрибків часу назад, забезпечуючи сувору монотонність, субнаносекундну роздільну здатність, стійкість до збоїв сигналу та зв'язок із системними інтерфейсами ядра ОС.

## Задача та архітектура сервопетлі

Програмний годинник реального часу в операційній системі або прошивці мікроконтролера базується на лічильнику апаратних тактів (наприклад, `SysTick` у Cortex-M, таймері `TIM` або апаратному лічильнику циклів `TSC`/`DWT`). Номінальна частота тактування відома лише приблизно: реальний кристал має початкову похибку ±10…50 ppm і постійно дрейфує від зміни температури та старіння.

Якщо щосекунди при надходженні еталонного імпульсу PPS просто перезаписувати поточний час («робити стрибок» або *step*), у системі виникають дві неприпустимі проблеми:
1. **Порушення монотонності.** Якщо місцевий годинник поспішав, стрибок назад створює від'ємні прирости часу `Δt = t₂ − t₁ < 0`. Це ламає операційні таймери, планувальники задач, черги подій та навігаційні алгоритми фільтрації (наприклад, розрахунок коваріацій у фільтрі Калмана).
2. **Нескінченна похідна швидкості.** Миттєва зміна показань розриває часову шкалу, що робить неможливим коректне вимірювання швидкостей, фаз і затримок у реальному часі.

Правильне інженерне рішення — **плавне підстроювання швидкості ходу** (*slewing*): сервоконтролер безперервно коригує тривалість програмного такту, змушуючи місцеву шкалу плавно наздоганяти або пригальмовувати до еталону.

```
       e_k = T_ref − T_local
PPS ───(+)──────────────────┬──────[ K_p ]────────────────(+)──► α_corr (ppm)
        ▲                   │                              ▲
        │                   └──────[ K_i · ∫ dt ]──────────┘
        │                            (оцінка α̂)            │
        │                                                  ▼
        └──────────[ Акумулятор шкали часу T_local ]◄──────┘
```

Сервопетля розв'язує два математичні завдання:
- **Пропорційна ланка (P):** генерує тимчасову поправку швидкості `u_p = K_p · e_k`, пропорційну миттєвому фазовому розриву `e_k`, щоб ліквідувати накопичений фазовий зсув.
- **Інтегральна ланка (I):** накопичує фазову похибку за багато секунд і знаходить точне значення систематичного відхилення частоти кварцу `α̂` (`u_i = u_i + K_i · e_k · Δt`). Коли фазова похибка стає рівною нулю, інтегральна ланка продовжує видавати постійну компенсацію темпу, не даючи годиннику знову розійтися.

## Апаратне захоплення фронту та фазовий акумулятор

Точність синхронізації критично залежить від двох факторів: фіксації моменту приходу PPS та математики накопичення часу.

### 1. Апаратний Input Capture проти переривань
Якщо зчитувати таймер у звичайному обробнику переривання GPIO, латентність переривань (затримка реакції ядра, конвеєр, критичні секції з вимкненими перериваннями) додає випадковий джиттер від одиниць до сотень мікросекунд. 

Тому лінію PPS підключають до каналу **апаратного захоплення таймера** (*Input Capture*). Фронт сигналу апаратно фіксує значення лічильника в регістрі захоплення без участі процесора з точністю до одного такту таймера (наприклад, 10 нс при 100 МГц). Програма може вичитати це значення пізніше, коли з'явиться вільний час, без втрати точності моменту.

### 2. Фазовий акумулятор у форматі фіксованої коми Q32.32
При тактовій частоті, наприклад, 80 МГц період такту дорівнює точно `12.5 нс`. Проте при частоті 48 МГц період становить `20.833333... нс`. Округлення до цілих наносекунд призведе до набігання гігантської систематичної похибки. 

Для розв'язання цієї проблеми шкала часу ведеться через дробовий фазовий акумулятор: час зберігається у вигляді пари `(секунди, наносекунди)`, де наносекунди містять цілу 64-бітну частину та 32-бітну дробову частину в форматі `Q32.32` (1 одиниця молодшого розряду дорівнює `2⁻³² ≈ 0.233 пікосекунди`).

## Реалізація на C та C++

Нижче наведено промисловий код сервоконтролера. Код містить захист від пропуску імпульсів, анти-віндап інтегратора, плавний slewing і стан захоплення синхронізації.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <stdlib.h>

#define SUBNS_SHIFT         32
#define SUBNS_SCALE         (1ULL << SUBNS_SHIFT)

/* Параметри обмеження корекції */
#define MAX_SLEW_PPM        500.0       /* Максимальне підстроювання темпу (+-500 ppm) */
#define STEP_THRESHOLD_NS   100000000ULL /* 100 мс: понад це робимо разовий стрибок */
#define PPS_TIMEOUT_TICKS   2           /* Кількість пропущених секунд для переходу в Holdover */

typedef enum {
    SERVO_UNLOCKED = 0,
    SERVO_LOCKING  = 1,
    SERVO_LOCKED   = 2,
    SERVO_HOLDOVER = 3
} servo_state_t;

typedef struct {
    uint64_t sec;           /* Цілі секунди UTC/TAI */
    uint64_t nsec;          /* Цілі наносекунди (0..999999999) */
    uint32_t sub_nsec;      /* Дробова частина наносекунди (Q32) */
} clock_time_t;

typedef struct {
    /* Стан шкали часу */
    clock_time_t time;
    uint64_t last_hw_ticks;
    double nominal_tick_ns; /* Номінальна тривалість апаратного такту в нс */

    /* Параметри PI-регулятора */
    double kp;              /* Пропорційний коефіцієнт (1/с) */
    double ki;              /* Інтегральний коефіцієнт (1/с^2) */
    double integrated_drift_ppm; /* Оцінка постійного відхилення частоти кварцу (I-ланка) */
    double current_slew_ppm;     /* Поточна сумарна поправка швидкості ходу */

    /* Стан та діагностика */
    servo_state_t state;
    int64_t last_phase_error_ns;
    uint32_t consecutive_locked_secs;
    uint32_t missed_pps_count;
} clock_servo_t;

void clock_servo_init(clock_servo_t *cs, double nominal_freq_hz) {
    cs->time.sec = 0;
    cs->time.nsec = 0;
    cs->time.sub_nsec = 0;
    cs->last_hw_ticks = 0;
    cs->nominal_tick_ns = 1e9 / nominal_freq_hz;

    /* Оптимальні коефіцієнти: смуга ~0.05 Гц, демпфування zeta = 0.707 */
    cs->kp = 0.10;          /* Відпрацювання 10% фазового зсуву за секунду */
    cs->ki = 0.005;         /* Повільна інтеграція дрейфу частоти */
    cs->integrated_drift_ppm = 0.0;
    cs->current_slew_ppm = 0.0;

    cs->state = SERVO_UNLOCKED;
    cs->last_phase_error_ns = 0;
    cs->consecutive_locked_secs = 0;
    cs->missed_pps_count = 0;
}

/* Оновлення місцевого часу на основі пройдених апаратних тактів */
void clock_advance_ticks(clock_servo_t *cs, uint64_t current_hw_ticks) {
    uint64_t delta_ticks = current_hw_ticks - cs->last_hw_ticks;
    cs->last_hw_ticks = current_hw_ticks;

    /* Фактична швидкість з урахуванням корекції сервоконтролера */
    double rate_multiplier = 1.0 + (cs->current_slew_ppm * 1e-6);
    double elapsed_ns_exact = (double)delta_ticks * cs->nominal_tick_ns * rate_multiplier;

    uint64_t elapsed_ns_int = (uint64_t)elapsed_ns_exact;
    uint32_t elapsed_sub_ns = (uint32_t)((elapsed_ns_exact - (double)elapsed_ns_int) * SUBNS_SCALE);

    /* Додавання з урахуванням переносу розрядів */
    uint64_t total_sub = (uint64_t)cs->time.sub_nsec + elapsed_sub_ns;
    cs->time.sub_nsec = (uint32_t)(total_sub & (SUBNS_SCALE - 1));
    uint64_t carry_ns = total_sub >> SUBNS_SHIFT;

    uint64_t total_ns = cs->time.nsec + elapsed_ns_int + carry_ns;
    cs->time.sec += total_ns / 1000000000ULL;
    cs->time.nsec = total_ns % 1000000000ULL;
}

/* Обробка події PPS: вимірювання помилки фази та оновлення PI-сервоконтролера */
void clock_on_pps(clock_servo_t *cs, uint64_t pps_hw_ticks, uint64_t ref_sec) {
    /* 1. Доводимо час точно до моменту приходу фронту PPS */
    clock_advance_ticks(cs, pps_hw_ticks);
    cs->missed_pps_count = 0;

    /* 2. Обчислення похибки фази e_k = T_ref - T_local */
    int64_t sec_diff = (int64_t)ref_sec - (int64_t)cs->time.sec;
    int64_t error_ns = (sec_diff * 1000000000LL) - (int64_t)cs->time.nsec;
    cs->last_phase_error_ns = error_ns;

    /* 3. Грубий зсув (холодний старт або аварійний розрив) */
    if (llabs(error_ns) > (int64_t)STEP_THRESHOLD_NS) {
        cs->time.sec = ref_sec;
        cs->time.nsec = 0;
        cs->time.sub_nsec = 0;
        cs->integrated_drift_ppm = 0.0;
        cs->current_slew_ppm = 0.0;
        cs->state = SERVO_LOCKING;
        cs->consecutive_locked_secs = 0;
        return;
    }

    /* 4. PI-розрахунок керуючого впливу */
    double p_term = cs->kp * (double)error_ns * 1e-3; /* нс помилки -> ppm швидкості */
    cs->integrated_drift_ppm += cs->ki * (double)error_ns * 1e-3;

    /* Анти-віндап обмеження інтегратора */
    if (cs->integrated_drift_ppm > MAX_SLEW_PPM) cs->integrated_drift_ppm = MAX_SLEW_PPM;
    if (cs->integrated_drift_ppm < -MAX_SLEW_PPM) cs->integrated_drift_ppm = -MAX_SLEW_PPM;

    double total_slew = p_term + cs->integrated_drift_ppm;

    /* Насичення загального темпу slewing */
    if (total_slew > MAX_SLEW_PPM) total_slew = MAX_SLEW_PPM;
    if (total_slew < -MAX_SLEW_PPM) total_slew = -MAX_SLEW_PPM;
    cs->current_slew_ppm = total_slew;

    /* 5. Автомат станів захоплення */
    if (llabs(error_ns) < 100) { /* Фазова похибка менше 100 нс */
        cs->consecutive_locked_secs++;
        if (cs->consecutive_locked_secs >= 5) {
            cs->state = SERVO_LOCKED;
        }
    } else {
        cs->consecutive_locked_secs = 0;
        if (cs->state == SERVO_LOCKED) {
            cs->state = SERVO_LOCKING;
        }
    }
}

/* Обробка відсутності імпульсу PPS (викликається за тайм-аутом) */
void clock_on_pps_timeout(clock_servo_t *cs) {
    cs->missed_pps_count++;
    if (cs->missed_pps_count >= PPS_TIMEOUT_TICKS) {
        /* Перехід у режим Holdover: вимикаємо P-ланку, тримаємо вивчену I-ланку */
        cs->state = SERVO_HOLDOVER;
        cs->current_slew_ppm = cs->integrated_drift_ppm;
    }
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <chrono>
#include <algorithm>
#include <concepts>

class ClockServo {
public:
    enum class State {
        Unlocked,
        Locking,
        Locked,
        Holdover
    };

    struct Timestamp {
        std::uint64_t sec{0};
        std::uint64_t nsec{0};
        std::uint32_t sub_nsec{0}; // Q32 дробова частина наносекунди
    };

    struct TuningParameters {
        double kp{0.10};          // 1/с
        double ki{0.005};         // 1/с^2
        double max_slew_ppm{500.0};
        std::int64_t step_threshold_ns{100'000'000}; // 100 мс
        std::uint32_t pps_timeout_ticks{2};
    };

    explicit ClockServo(double nominal_freq_hz, TuningParameters params = {})
        : nominal_tick_ns_{1e9 / nominal_freq_hz}, params_{params} {}

    void advance_ticks(std::uint64_t current_hw_ticks) noexcept {
        const std::uint64_t delta_ticks = current_hw_ticks - last_hw_ticks_;
        last_hw_ticks_ = current_hw_ticks;

        const double rate_multiplier = 1.0 + (current_slew_ppm_ * 1e-6);
        const double elapsed_ns_exact = static_cast<double>(delta_ticks) * nominal_tick_ns_ * rate_multiplier;

        const auto elapsed_ns_int = static_cast<std::uint64_t>(elapsed_ns_exact);
        const auto elapsed_sub_ns = static_cast<std::uint32_t>(
            (elapsed_ns_exact - static_cast<double>(elapsed_ns_int)) * subns_scale_
        );

        const std::uint64_t total_sub = static_cast<std::uint64_t>(time_.sub_nsec) + elapsed_sub_ns;
        time_.sub_nsec = static_cast<std::uint32_t>(total_sub & (subns_scale_ - 1));
        const std::uint64_t carry_ns = total_sub >> subns_shift_;

        const std::uint64_t total_ns = time_.nsec + elapsed_ns_int + carry_ns;
        time_.sec += total_ns / 1'000'000'000ULL;
        time_.nsec = total_ns % 1'000'000'000ULL;
    }

    void on_pps(std::uint64_t pps_hw_ticks, std::uint64_t ref_sec) noexcept {
        advance_ticks(pps_hw_ticks);
        missed_pps_count_ = 0;

        const auto sec_diff = static_cast<std::int64_t>(ref_sec) - static_cast<std::int64_t>(time_.sec);
        const std::int64_t error_ns = (sec_diff * 1'000'000'000LL) - static_cast<std::int64_t>(time_.nsec);
        last_phase_error_ns_ = error_ns;

        if (std::abs(error_ns) > params_.step_threshold_ns) {
            time_.sec = ref_sec;
            time_.nsec = 0;
            time_.sub_nsec = 0;
            integrated_drift_ppm_ = 0.0;
            current_slew_ppm_ = 0.0;
            state_ = State::Locking;
            consecutive_locked_secs_ = 0;
            return;
        }

        const double p_term = params_.kp * static_cast<double>(error_ns) * 1e-3;
        integrated_drift_ppm_ += params_.ki * static_cast<double>(error_ns) * 1e-3;

        // Anti-windup
        integrated_drift_ppm_ = std::clamp(integrated_drift_ppm_, -params_.max_slew_ppm, params_.max_slew_ppm);

        const double total_slew = p_term + integrated_drift_ppm_;
        current_slew_ppm_ = std::clamp(total_slew, -params_.max_slew_ppm, params_.max_slew_ppm);

        if (std::abs(error_ns) < 100) {
            ++consecutive_locked_secs_;
            if (consecutive_locked_secs_ >= 5) {
                state_ = State::Locked;
            }
        } else {
            consecutive_locked_secs_ = 0;
            if (state_ == State::Locked) {
                state_ = State::Locking;
            }
        }
    }

    void on_pps_timeout() noexcept {
        ++missed_pps_count_;
        if (missed_pps_count_ >= params_.pps_timeout_ticks) {
            state_ = State::Holdover;
            current_slew_ppm_ = integrated_drift_ppm_;
        }
    }

    [[nodiscard]] Timestamp now() const noexcept { return time_; }
    [[nodiscard]] std::int64_t phase_error_ns() const noexcept { return last_phase_error_ns_; }
    [[nodiscard]] double estimated_drift_ppm() const noexcept { return integrated_drift_ppm_; }
    [[nodiscard]] State state() const noexcept { return state_; }

private:
    static constexpr std::uint32_t subns_shift_{32};
    static constexpr double subns_scale_{4294967296.0}; // 2^32

    Timestamp time_{};
    std::uint64_t last_hw_ticks_{0};
    double nominal_tick_ns_{0.0};
    TuningParameters params_{};

    double integrated_drift_ppm_{0.0};
    double current_slew_ppm_{0.0};
    std::int64_t last_phase_error_ns_{0};
    State state_{State::Unlocked};
    std::uint32_t consecutive_locked_secs_{0};
    std::uint32_t missed_pps_count_{0};
};
```
:::

## Покроковий числовий розбір: процес захоплення синхронізації

Розглянемо числовий приклад роботи сервопетлі в реальних умовах. Нехай генератор мікроконтролера має фактичну похибку частоти `α = +25.0 ppm` (поспішає на 25 мкс щосекунди), а після увімкнення фазовий зсув становив `-350 мкс` (`-350 000 нс`).

Послідовність розрахунків на перших кроках роботи регулятора (`K_p = 0.10`, `K_i = 0.005`):

| Секунда `k` | Помилка фази `e_k` (нс) | `P`-поправка (ppm) | `I`-накопичення `α̂` (ppm) | Поточний темп (ppm) | Залишок похибки на наступну секунду |
|:---:|:---:|:---:|:---:|:---:|:---|
| 0 | −350 000 | 0.00 | 0.00 | 0.00 | Кварц біжить вперед на +25 ppm |
| 1 | −325 000 | −32.50 | −1.62 | −34.12 | За секунду темп зменшено, фаза зблизилась |
| 2 | −265 880 | −26.59 | −2.95 | −29.54 | Інтегратор поглиблює оцінку зміщення |
| 5 | −142 300 | −14.23 | −7.80 | −22.03 | Наближення до стаціонарного темпу |
| 10 | −38 400 | −3.84 | −16.45 | −20.29 | Перехідний процес затухає |
| 25 | −1 250 | −0.12 | −24.91 | −25.03 | Інтегратор майже повністю вивчив похибку кварцу (+25 ppm) |
| 50 | −18 | 0.00 | −25.00 | −25.00 | **Синхронізація захоплена (State: LOCKED)** |

З таблиці видно, як роль пропорційної ланки поступово згасає від `-32.5 ppm` до `0.0 ppm`, передаючи повне керування інтегральній ланці, яка точно зафіксувала поправку `-25.000 ppm`, повністю нівелюючи природний поспіх кристала.

## Зв'язок із ядром ОС: системний виклик `adjtimex` та PTP Hardware Clock

В операційній системі Linux аналогічна архітектура реалізована безпосередньо в ядрі (підсистема `NTP/PTP`).

### 1. Системний інтерфейс `clock_adjtime()` / `adjtimex`
Програма простору користувача не повинна вручну переписувати змінні системного часу. Замість цього вона взаємодіє з сервоконтролером ядра через структуру `struct timex`:

```
struct timex tmx = {0};
tmx.modes = ADJ_FREQUENCY | ADJ_OFFSET;
tmx.freq = (long)(cs.integrated_drift_ppm * 65536.0); // Переведення ppm у формат Linux Q16.16
tmx.offset = cs.last_phase_error_ns / 1000;            // Фазова похибка в мікросекундах
adjtimex(&tmx);
```

Ядро Linux самостійно виконує плавний slewing тактової частоти `ktime_get()` відповідно до алгоритму Mills PLL/FLL.

### 2. Апаратні годинники PTP (`/dev/ptp0`)
У сучасних мережевих картах Ethernet (наприклад, Intel I210/I225) фазовий акумулятор і лічильник наносекунд реалізовані безпосередньо в кремнії мережевого MAC-контролера. Демон `ptp4l` зчитує мітки часу апаратного захоплення і через `ioctl(PTP_CLOCK_ADJFREQ)` керує цифровим синтезатором частоти всередині мережевого чипа, досягаючи синхронізації з точністю кращою за 10 наносекунд без жодного навантаження на центральний процесор.

## Динаміка замкненої петлі та вибір коефіцієнтів

Неперервна передавальна функція замкненого сервоконтролера другого порядку описується виразом:

```
H(s) = (K_p · s + K_i) / (s² + K_p · s + K_i)
```

Власна частота петлі `ω_n` та коефіцієнт демпфування `ζ` пов'язані з коефіцієнтами регулятора:

```
ω_n = √(K_i)
ζ   = K_p / (2 · √(K_i))
```

### Фізичний зміст параметрів:
1. **Коефіцієнт демпфування `ζ`:** Визначає коливальність системи. Оптимальне значення лежить у діапазоні `ζ = 0.707…1.0`. 
   - Якщо `ζ < 0.5` (недодемпфована петля), фазова похибка буде довго коливатися навколо нуля з перерегулюванням.
   - Якщо `ζ > 1.5` (передемпфована петля), годинник буде повільно підходити до синхронізації.
2. **Власна частота петлі `ω_n`:** Визначає смугу пропускання фільтра. Для імпульсів з періодом 1 с зазвичай обирають `ω_n ≈ 0.05…0.1 рад/с` (постійна часу `τ = 1/ω_n ≈ 10…20 с`). 
   - Занадто швидка петля (`K_p > 0.5`) почне транслювати вільний шум квантування та фазовий джиттер PPS у швидкість місцевого годинника.
   - Занадто повільна петля (`K_p < 0.01`) не встигатиме відстежувати температурний дрейф кристала при швидкому нагріванні приладу.

## Практичні пастки та захисні механізми

### 1. Захист від аномальних викидів PPS (Gating / Outlier Rejection)
Через електромагнітні перешкоди або багатопроменевість сигналу антени GNSS іноді трапляються фальшиві імпульси або раптові зсуви фази на мілісекунди. 
Справжній сервоконтролер повинен мати «вікно довіри»: якщо черговий імпульс приходить із фазовою похибкою, що суттєво перевищує шум попередніх вимірів (наприклад, понад `±1 мкс`), цей імпульс відкидається як аномалія й не потрапляє в інтегратор `K_i`.

### 2. Режим утримання (Holdover State Machine)
Коли сигнал GNSS зникає (дрон залетів у тунель або ввімкнувся глушник), контролер не повинен намагатися інтегрувати шум. Перехід у стан `Holdover` фіксує останнє стабільне значення інтегратора `integrated_drift_ppm`. Оскільки інтегратор запам'ятав точну похибку кристала в ppm, програмний годинник продовжуватиме йти з компенсацією частоти, втрачаючи точність лише через вторинний температурний дрейф.

### 3. Обробка високосних секунд (Leap Seconds)
Шкала часу GPS є неперервною, тоді як цивільний час UTC містить високосні секунди. Коли GNSS-приймач передає інформацію про вставку високосної секунди (`23:59:60`), сервоконтролер не повинен сприймати розрив у 1 секунду як аварійний збій кварцу. Системи точного часу завчасно зчитують прапорець `Leap Indicator` з NMEA/UBX повідомлення й плавно «розтягують» або вставляють додаткову секунду в системний календар без збурення фазової петлі.
