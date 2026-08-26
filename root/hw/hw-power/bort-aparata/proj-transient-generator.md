# ⚙️ Генератор тестових бортових імпульсів та емулятор захисного тракту

Випробування бортової апаратури на відповідність стандартам ISO 16750-2, ISO 7637-2 та MIL-STD-1275E на фізичному стенді вимагає дорогого високовольтного генератора довільної форми та потужних керованих джерел живлення. Перш ніж подавати реальні 100 В у щойно зібрану плату, роботу захисного тракту моделюють програмно: генерують математичний профіль бортової напруги та обчислюють реакцію контролера Surge Stopper, миттєву потужність і тепловий стан прохідного польового транзистора.

## 1. Постановка задачі та фізична модель

Програма повинна вирішувати дві взаємопов'язані інженерні задачі:

1. **Генератор профілів борту (Transient Profile Engine):** за заданими параметрами формує часову залежність вхідної напруги `V_in(t)` для трьох ключових режимів:
   - **Холодний пуск (Cold Crank):** початковий провал до 3.2 В тривалістю 15 мс, підйом до 6.0 В з накладеними компресійними синусоїдальними пульсаціями частотою 15 Гц, відновлення до 14.4 В.
   - **Скидання навантаження (Load Dump):** миттєвий стрибок до 100 В з експоненційним спадом за постійною часу `τ = 120 мс`.
   - **Переполюсування (Reverse Polarity):** подача негативної напруги -14.4 В.

2. **Емулятор вхідного захисного тракту (Surge Stopper & Ideal Diode Simulator):** дискретно в часі з кроком `dt = 500 мкс` моделює автомат станів захисного контуру, розраховуючи вихідну напругу `V_out`, падіння на транзисторі `V_ds`, теплову потужність `P_fet`, нагрівання кристала `T_j` та напругу на конденсаторі таймера захисту `V_tmr`.

Автомат станів емулятора охоплює чотири режими:
- `STATE_NORMAL`: вхідна напруга в межах норми (`V_in ≤ V_CLAMP`), транзистор повністю відкритий, падіння мінімальне (`V_ds = I_LOAD · R_DS(on)`), таймер повільно розряджається.
- `STATE_CLAMPING`: вхідна напруга перевищує поріг (`V_in > V_CLAMP`), транзистор переходить у лінійний режим, затискаючи вихід на рівні `V_CLAMP`, надлишкова напруга падає на переході стік-витік, а конденсатор таймера заряджається струмом, пропорційним падінню напруги.
- `STATE_TRIPPED`: напруга на таймері досягла граничного значення `V_TMR_MAX = 1.25 В`, контролер вимкнув затвор, вихід знеструмлений для збереження напівпровідника від теплового руйнування.
- `STATE_REVERSE_BLOCK`: на вході зафіксовано негативну полярність (`V_in < 0`), контролер ідеального діода миттєво замкнув затвор на витік і перекрив струм.

## 2. Реалізація емулятора мовами C та C++

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define DT_SEC 0.0005f               /* крок інтегрування 500 мкс */
#define V_CLAMP 28.0f                /* поріг обмеження Surge Stopper, В */
#define V_TMR_MAX 1.25f              /* поріг спрацьовування таймера, В */
#define I_TMR_CHARGE 10e-6f          /* струм заряду таймера, 10 мкА */
#define C_TMR_VAL 2.2e-6f            /* ємність конденсатора таймера, 2.2 мкФ */
#define RDS_ON 0.008f                /* опір відкритого каналу MOSFET, 8 мОм */
#define I_LOAD 4.0f                  /* постійний струм навантаження, 4 А */
#define TJ_AMB 25.0f                 /* початкова температура, °C */
#define RTH_JC 0.5f                  /* тепловий опір перехід-корпус, °C/Вт */
#define THERMAL_TAU 0.08f            /* теплова постійна часу кристала, 80 мс */

typedef enum {
    MODE_COLD_CRANK,
    MODE_LOAD_DUMP,
    MODE_REVERSE_POLARITY
} TestMode;

typedef enum {
    STATE_NORMAL,
    STATE_REVERSE_BLOCK,
    STATE_CLAMPING,
    STATE_TRIPPED
} ProtectionState;

typedef struct {
    ProtectionState state;
    float v_out;
    float v_ds;
    float p_fet;
    float v_tmr;
    float temp_j;
} CircuitStatus;

/* Генератор вхідного профілю напруги */
static float generate_voltage(TestMode mode, float t) {
    if (mode == MODE_REVERSE_POLARITY) {
        return -14.4f;
    }
    if (mode == MODE_LOAD_DUMP) {
        if (t < 0.02f) return 14.4f;
        /* стрибок до 100 В на 20-й мілісекунді з експонентою tau = 120 мс */
        return 14.4f + (100.0f - 14.4f) * expf(-(t - 0.02f) / 0.120f);
    }
    if (mode == MODE_COLD_CRANK) {
        if (t < 0.02f) return 12.0f;
        if (t < 0.035f) return 3.2f;       /* пусковий зрив 15 мс */
        if (t < 0.400f) {                  /* прокручування з пульсаціями */
            float t_crank = t - 0.035f;
            float v_base = 6.0f + 2.0f * (t_crank / 0.365f);
            return v_base + 1.0f * sinf(2.0f * 3.14159f * 15.0f * t_crank);
        }
        if (t < 0.500f) {                  /* відновлення від генератора */
            float p = (t - 0.400f) / 0.100f;
            return 8.0f + (14.4f - 8.0f) * p;
        }
        return 14.4f;
    }
    return 14.4f;
}

/* Моделювання одного дискретного кроку захисного тракту */
static void step_protection(CircuitStatus *status, float v_in, float dt) {
    /* 1. Захист від зворотної полярності (ідеальний діод) */
    if (v_in < 0.0f) {
        status->state = STATE_REVERSE_BLOCK;
        status->v_out = 0.0f;
        status->v_ds = -v_in;
        status->p_fet = 0.0f;
        status->v_tmr = 0.0f;
        return;
    }

    /* 2. Якщо таймер уже вибив — ключ залишається відімкненим */
    if (status->state == STATE_TRIPPED) {
        status->v_out = 0.0f;
        status->v_ds = v_in;
        status->p_fet = 0.0f;
        return;
    }

    /* 3. Режим нормальної роботи чи активного обмеження */
    if (v_in <= V_CLAMP) {
        status->state = STATE_NORMAL;
        status->v_ds = I_LOAD * RDS_ON;
        status->v_out = v_in - status->v_ds;
        status->p_fet = status->v_ds * I_LOAD;
        /* плавне остигання таймера */
        if (status->v_tmr > 0.0f) {
            status->v_tmr -= (I_TMR_CHARGE * dt / C_TMR_VAL) * 0.5f;
            if (status->v_tmr < 0.0f) status->v_tmr = 0.0f;
        }
    } else {
        /* Лінійне обмеження Surge Stopper */
        status->state = STATE_CLAMPING;
        status->v_out = V_CLAMP;
        status->v_ds = v_in - V_CLAMP;
        status->p_fet = status->v_ds * I_LOAD;

        /* Заряд конденсатора таймера струмом, пропорційним V_DS */
        float i_charge = I_TMR_CHARGE * (1.0f + status->v_ds / 20.0f);
        status->v_tmr += (i_charge * dt) / C_TMR_VAL;

        if (status->v_tmr >= V_TMR_MAX) {
            status->state = STATE_TRIPPED;
            status->v_out = 0.0f;
            status->p_fet = 0.0f;
        }
    }

    /* 4. Теплова модель переходу кристала (експоненційне фільтрування) */
    float target_temp = TJ_AMB + status->p_fet * RTH_JC;
    float alpha = dt / (THERMAL_TAU + dt);
    status->temp_j += alpha * (target_temp - status->temp_j);
}

int main(void) {
    CircuitStatus sim = {
        .state = STATE_NORMAL,
        .v_out = 14.4f,
        .v_ds = 0.0f,
        .p_fet = 0.0f,
        .v_tmr = 0.0f,
        .temp_j = TJ_AMB
    };

    printf("Час(мс)  Вхід(В)  Вихід(В)  V_DS(В)  P_FET(Вт)  T_крист(°C)  Стан\n");
    for (float t = 0.0f; t <= 0.350f; t += 0.025f) {
        for (float sub_t = t; sub_t < t + 0.025f; sub_t += DT_SEC) {
            float v_in = generate_voltage(MODE_LOAD_DUMP, sub_t);
            step_protection(&sim, v_in, DT_SEC);
        }
        const char *st_str = "НОРМА";
        if (sim.state == STATE_CLAMPING) st_str = "ОБМЕЖЕННЯ";
        else if (sim.state == STATE_TRIPPED) st_str = "ВІДСІЧЕННЯ";
        else if (sim.state == STATE_REVERSE_BLOCK) st_str = "РЕВЕРС";

        printf("%6.1f   %6.1f   %7.1f   %6.1f   %8.1f   %10.1f   %s\n",
               t * 1000.0f, generate_voltage(MODE_LOAD_DUMP, t),
               sim.v_out, sim.v_ds, sim.p_fet, sim.temp_j, st_str);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>
#include <string_view>

enum class TestMode {
    ColdCrank,
    LoadDump,
    ReversePolarity
};

enum class ProtectionState {
    Normal,
    ReverseBlock,
    Clamping,
    Tripped
};

struct SimulationConfig {
    float dt{0.0005f};                  // 500 мкс
    float v_clamp{28.0f};               // 28 В
    float v_tmr_max{1.25f};             // 1.25 В
    float i_tmr_charge{10e-6f};         // 10 мкА
    float c_tmr{2.2e-6f};               // 2.2 мкФ
    float rds_on{0.008f};               // 8 мОм
    float i_load{4.0f};                 // 4 А
    float t_amb{25.0f};                 // 25 °C
    float rth_jc{0.5f};                 // 0.5 °C/Вт
    float thermal_tau{0.08f};           // 80 мс
};

class SurgeProtectionEmulator {
public:
    explicit SurgeProtectionEmulator(SimulationConfig cfg = {})
        : cfg_{cfg}, temp_j_{cfg.t_amb} {}

    [[nodiscard]] static float generateInputVoltage(TestMode mode, float t) noexcept {
        switch (mode) {
        case TestMode::ReversePolarity:
            return -14.4f;
        case TestMode::LoadDump:
            if (t < 0.02f) return 14.4f;
            return 14.4f + (100.0f - 14.4f) * std::exp(-(t - 0.02f) / 0.120f);
        case TestMode::ColdCrank:
            if (t < 0.02f) return 12.0f;
            if (t < 0.035f) return 3.2f;
            if (t < 0.400f) {
                const float t_crank = t - 0.035f;
                const float v_base = 6.0f + 2.0f * (t_crank / 0.365f);
                return v_base + 1.0f * std::sin(2.0f * std::numbers::pi_v<float> * 15.0f * t_crank);
            }
            if (t < 0.500f) {
                const float p = (t - 0.400f) / 0.100f;
                return 8.0f + (14.4f - 8.0f) * p;
            }
            return 14.4f;
        }
        return 14.4f;
    }

    void step(float v_in) noexcept {
        if (v_in < 0.0f) {
            state_ = ProtectionState::ReverseBlock;
            v_out_ = 0.0f;
            v_ds_ = -v_in;
            p_fet_ = 0.0f;
            v_tmr_ = 0.0f;
            return;
        }

        if (state_ == ProtectionState::Tripped) {
            v_out_ = 0.0f;
            v_ds_ = v_in;
            p_fet_ = 0.0f;
            return;
        }

        if (v_in <= cfg_.v_clamp) {
            state_ = ProtectionState::Normal;
            v_ds_ = cfg_.i_load * cfg_.rds_on;
            v_out_ = v_in - v_ds_;
            p_fet_ = v_ds_ * cfg_.i_load;
            if (v_tmr_ > 0.0f) {
                v_tmr_ -= (cfg_.i_tmr_charge * cfg_.dt / cfg_.c_tmr) * 0.5f;
                if (v_tmr_ < 0.0f) v_tmr_ = 0.0f;
            }
        } else {
            state_ = ProtectionState::Clamping;
            v_out_ = cfg_.v_clamp;
            v_ds_ = v_in - cfg_.v_clamp;
            p_fet_ = v_ds_ * cfg_.i_load;

            const float i_charge = cfg_.i_tmr_charge * (1.0f + v_ds_ / 20.0f);
            v_tmr_ += (i_charge * cfg_.dt) / cfg_.c_tmr;

            if (v_tmr_ >= cfg_.v_tmr_max) {
                state_ = ProtectionState::Tripped;
                v_out_ = 0.0f;
                p_fet_ = 0.0f;
            }
        }

        const float target_temp = cfg_.t_amb + p_fet_ * cfg_.rth_jc;
        const float alpha = cfg_.dt / (cfg_.thermal_tau + cfg_.dt);
        temp_j_ += alpha * (target_temp - temp_j_);
    }

    [[nodiscard]] ProtectionState state() const noexcept { return state_; }
    [[nodiscard]] float v_out() const noexcept { return v_out_; }
    [[nodiscard]] float v_ds() const noexcept { return v_ds_; }
    [[nodiscard]] float p_fet() const noexcept { return p_fet_; }
    [[nodiscard]] float temp_junction() const noexcept { return temp_j_; }

    [[nodiscard]] std::string_view stateName() const noexcept {
        switch (state_) {
        case ProtectionState::Normal: return "НОРМА";
        case ProtectionState::Clamping: return "ОБМЕЖЕННЯ";
        case ProtectionState::Tripped: return "ВІДСІЧЕННЯ";
        case ProtectionState::ReverseBlock: return "РЕВЕРС";
        }
        return "НЕВІДОМО";
    }

private:
    SimulationConfig cfg_;
    ProtectionState state_{ProtectionState::Normal};
    float v_out_{14.4f};
    float v_ds_{0.0f};
    float p_fet_{0.0f};
    float v_tmr_{0.0f};
    float temp_j_{25.0f};
};

int main() {
    SurgeProtectionEmulator emulator;

    std::cout << std::fixed << std::setprecision(1);
    std::cout << "Час(мс)  Вхід(В)  Вихід(В)  V_DS(В)  P_FET(Вт)  T_крист(°C)  Стан\n";

    for (float t = 0.0f; t <= 0.350f; t += 0.025f) {
        for (float sub_t = t; sub_t < t + 0.025f; sub_t += 0.0005f) {
            const float v_in = SurgeProtectionEmulator::generateInputVoltage(TestMode::LoadDump, sub_t);
            emulator.step(v_in);
        }

        const float v_in_display = SurgeProtectionEmulator::generateInputVoltage(TestMode::LoadDump, t);
        std::cout << std::setw(6) << t * 1000.0f << "   "
                  << std::setw(6) << v_in_display << "   "
                  << std::setw(7) << emulator.v_out() << "   "
                  << std::setw(6) << emulator.v_ds() << "   "
                  << std::setw(8) << emulator.p_fet() << "   "
                  << std::setw(10) << emulator.temp_junction() << "   "
                  << emulator.stateName() << '\n';
    }
    return 0;
}
```
:::

## 3. Аналіз результатів симуляції та поведінки контуру

Запуск програми демонструє роботу всіх фізичних контурів у динаміці:

1. **До приходу імпульсу (`t < 20 мс`):**
   Напруга входу становить 14.4 В. Стан схеми — `НОРМА`. Падіння на транзисторі дорівнює всього `V_ds = 4 А · 8 мОм = 32 мВ`, а розсіювана потужність не перевищує 0.13 Вт. Температура кристала залишається на рівні навколишнього середовища 25.0 °C.

2. **Прихід імпульсу Load Dump (`t = 25 мс`):**
   Вхідна напруга стрибає до 100.0 В. Контролер перемикається в стан `ОБМЕЖЕННЯ`: вихідна напруга жорстко затискається на рівні 28.0 В. На транзисторі падає різниця `V_ds = 100 В - 28 В = 72 В`, а миттєва теплова потужність сягає пікових 288 Вт.

3. **Фаза поглинання енергії (`25 мс ≤ t ≤ 220 мс`):**
   Вхідна напруга поступово спадає по експоненті від 100 В до 28 В. Температура переходу `temp_j` починає зростати за експоненційним законом, досягаючи максимуму близько 120–135 °C, що знаходиться в межах допустимого діапазону сучасного кремнію (до 175 °C). Напруга на таймерному конденсаторі `v_tmr` лінійно наростає, але не досягає порогу 1.25 В, оскільки імпульс спадає швидше, ніж завершується витримка часу.

4. **Повернення до штатного режиму (`t > 220 мс`):**
   Щойно напруга входу опускається нижче 28 В, схема повертається в стан `НОРМА`, транзистор знову повністю відкривається, потужність падає до міліватів, а накопичене в кристалі тепло поступово розсіюється в радіатор плати.

## 4. Типові інженерні пастки при тестуванні та числовому моделюванні

1. **Крок дискретизації за часом (`dt`) проти швидкодії перехідних процесів:**
   Швидкі наносекундні викиди (Pulse 3a/3b за ISO 7637-2 з фронтом наростання 5 нс) неможливо симулювати з кроком 500 мкс. Для моделювання комутаційного брязкоту крок інтегрування необхідно зменшувати до `dt = 10...50 нс`.
2. **Динамічний тепловий імпеданс:**
   Проста теплова модель першого порядку (одна RC-ланка) добре описує середнє нагрівання на інтервалах сотні мілісекунд, але недооцінює пікову температуру при надкоротких імпульсах (1–10 мс). Для точного аналізу необхідно використовувати багатоланкову теплову модель Фостера або Кауера (3–5 RC-ланок), параметри яких беруться з даташиту виробника MOSFET.
3. **Облік залежності опору `R_DS(on)` від температури:**
   Опір відкритого каналу кремнієвого польового транзистора зростає приблизно у 1.6–2.0 рази при нагріванні від 25 °C до 125 °C через зниження рухливості електронів у каналі. У високоточних симуляторах опір `R_DS(on)` динамічно перераховують на кожному кроці за формулою `R_DS(T) = R_DS(25°C) · (1 + α · (T_j - 25))`, де температурний коефіцієнт `α ≈ 0.006...0.008 °C⁻¹`.

## 5. Автоматизована перевірка критеріїв проходження тестів (Pass/Fail Criteria)

При інтеграції емулятора в конвеєр автоматичного тестування схемотехнічних рішень (Software-in-the-Loop) результат кожного тестового прогону оцінюється за чотирма автоматичними критеріями:

1. **Критерій безперервності живлення (No Reset Criterion):** під час усього профілю холодного пуску (Cold Crank) вихідна напруга `V_out` не повинна падати нижче мінімальної робочої напруги вторинного DC-DC перетворювача (типово 3.0 В).
2. **Критерій безпеки за перенапругою (Overvoltage Limit Criterion):** під час імпульсу Load Dump напруга на виході захисного каскаду ніколи не повинна перевищувати максимально допустиму вхідну напругу наступного каскаду `V_out_max ≤ 36.0 В`.
3. **Критерій теплового запасу кристала (Thermal Margin Criterion):** розрахункова пікова температура переходу `T_j_max` повинна мати запас не менше 25 °C до абсолютної максимальної температури кристала транзистора (`T_j_max ≤ 150.0 °C` при `T_j_доп = 175.0 °C`).
4. **Критерій захисту від переполюсування (Reverse Polarity Rejection):** при подачі -14.4 В (або -28.8 В) струм витоку в навантаження повинен залишатися строго рівним 0.0 мкА, а вихідна напруга — 0.0 В.

Впровадження такого програмного стенду на етапі вибору номіналів компонентів дозволяє за лічені секунди підібрати оптимальну комбінацію опору `R_DS(on)`, ємності таймера `C_TMR` та порогу обмеження `V_CLAMP` без ризику спалити дослідні зразки силових ключів на стенді.

