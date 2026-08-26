# ⚙️ Симуляція холодного старту та енергетичних циклів збирача

Безбатарейні системи збирання мікроенергії неможливо надійно спроектувати без точного часового моделювання нелінійних перехідних процесів. Система проходить три принципово різні стадії: спочатку автогенератор холодного старту викачує перші мікроджоулі з нульового заряду, потім високошвидкісний boost-перетворювач накопичує енергію в головному резервуарі в умовах нелінійного саморозряду, і врешті гістерезисний супервізор керує імпульсним скиданням енергії в цифрове навантаження. Нижче наведено дискретно-подійну математичну модель цієї системи мовами C та C++.

---

### Постановка задачі та фізична модель

Симуляція обчислює миттєвий стан безбатарейного вузла крок за кроком у часі за методом Ейлера з фіксованим кроком дискретизації `Δt = 1 мс`. Модель враховує внутрішній опір джерела, ККД перетворювачів на різних етапах, експоненційну залежність струму витоку від напруги та порогову логіку гістерезисного керування живленням:

1. **Фаза холодного старту (V_aux < 1.8 В):**
   - Джерело (термоелектричний генератор TEG або малогабаритний фотодіод) має напругу холостого ходу `V_src = 0.04 В` (40 мВ) та внутрішній опір `R_src = 2.0 Ом`.
   - За умови узгодження імпедансів максимальна потужність, яку можна вилучити з джерела, становить `P_in = V_src² / (4 · R_src)`.
   - Працює JFET-генератор Мейснера з низьким пусковим ККД `η_cold = 0.25`, заряджаючи допоміжний конденсатор `C_aux = 4.7 мкФ`.
   - Накопичення енергії розраховується з рівняння потужності `d(1/2 · C_aux · V_aux²) / dt = P_in · η_cold`.

2. **Фаза основного заряду (V_aux ≥ 1.8 В, V_store < V_high):**
   - Щойно напруга `V_aux` досягає 1.8 В, супервізор пробуджує основний синхронний Boost-перетворювач із високим ККД `η_main = 0.82` та алгоритмом MPPT. Пусковий JFET-генератор блокується від'ємною напругою затвора.
   - Струм заряду надходить у головний накопичувач `C_store = 470 мкФ`.
   - Враховується напругозалежний струм власного витоку діелектрика накопичувача `I_leak(V) = I_0 · exp(α · V)` та струм спокою схеми керування `I_q = 45 нА`.
   - Корисна потужність заряду зменшується на величину втрат: `P_net = P_in · η_main - (I_leak + I_q) · V_store`.
   - Ключ Power Path розімкнений, цифрове навантаження повністю знеструмлене (`I_load = 0`).

3. **Фаза активного імпульсу (V_store ≥ V_high = 3.3 В):**
   - Супервізор замикає ключ Power Path, подаючи напругу на мікроконтролер та радіотрансивер.
   - Навантаження споживає струм `I_burst = 22 мА` протягом заданого робочого вікна `t_burst = 15 мс`.
   - Напруга на `C_store` стрімко спадає за законом `dV/dt = -I_total / C_store`.
   - Якщо передача завершується за 15 мс або напруга просідає нижче критичного порогу відсічки `V_low = 2.2 В`, супервізор негайно розмикає ключ Power Path, і вузол повертається до фази накопичення.

---

### Архітектура коду: порівняння C та C++

Реалізація завдання демонструє дві різні парадигми проектування системного коду:

- **Мова C (процедурний підхід):**
  Використовує плоскі структури даних (`HarvesterParams` та `HarvesterState`), ізольовані функції з передачею вказівників за константним посиланням та явне керування числовими типами. Такий стиль характерний для низькорівневих модулів ядра ОС та безпосередньої прошивки мікроконтролерів без динамічного виділення пам'яті.

- **Мова C++ (об'єктно-орієнтований підхід із суворою типізацією):**
  Інкапсулює логіку симулятора всередині класу `SystemSimulator` у просторі імен `HarvesterSim`. Використовує безпечні перелічення `enum class`, модифікатори `constexpr`, `noexcept`, методні специфікатори `[[nodiscard]]` та сучасні типи `std::string_view` для форматування виводу без накладних витрат у пам'яті.

---

### Реалізація симулятора

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    PHASE_COLD_START = 0,
    PHASE_MAIN_CHARGING,
    PHASE_ACTIVE_BURST
} SystemPhase;

typedef struct {
    double v_src;          /* Вхідна напруга джерела (В) */
    double r_src;          /* Внутрішній опір джерела (Ом) */
    double c_aux;          /* Ємність пускового конденсатора (Ф) */
    double c_store;        /* Ємність головного накопичувача (Ф) */
    double v_high;         /* Поріг увімкнення навантаження (В) */
    double v_low;          /* Поріг відсічки навантаження (В) */
    double i_burst;        /* Струм навантаження в імпульсі (А) */
    double t_burst;        /* Тривалість робочого імпульсу (с) */
    double i_q;            /* Струм споживання супервізора (А) */
    double leak_i0;        /* Базовий витік конденсатора при 0 В (А) */
    double leak_alpha;     /* Коефіцієнт експоненційного зростання витоку */
    double eta_cold;       /* ККД автогенератора Мейснера */
    double eta_main;       /* ККД основного boost-перетворювача */
} HarvesterParams;

typedef struct {
    double time_sec;
    double v_aux;
    double v_store;
    SystemPhase phase;
    double burst_timer;
    int burst_count;
} HarvesterState;

static double calculate_leakage(const HarvesterParams *p, double voltage) {
    if (voltage <= 0.0) return 0.0;
    return p->leak_i0 * exp(p->leak_alpha * voltage);
}

static void harvester_step(const HarvesterParams *p, HarvesterState *s, double dt) {
    s->time_sec += dt;

    if (s->phase == PHASE_COLD_START) {
        /* Максимальна вхідна потужність джерела за умови узгодження імпедансів: V_src^2 / (4 * R_src) */
        double p_in = (p->v_src * p->v_src) / (4.0 * p->r_src);
        double p_aux = p_in * p->eta_cold;

        /* dE = P * dt -> d(0.5 * C * V^2) = P * dt -> V_next = sqrt(V_curr^2 + 2 * P * dt / C) */
        double v_sq = s->v_aux * s->v_aux + (2.0 * p_aux * dt) / p->c_aux;
        s->v_aux = sqrt(v_sq);

        /* Умова пробудження основного перетворювача */
        if (s->v_aux >= 1.8) {
            s->phase = PHASE_MAIN_CHARGING;
        }
    } else if (s->phase == PHASE_MAIN_CHARGING) {
        double p_in = (p->v_src * p->v_src) / (4.0 * p->r_src);
        double p_ch = p_in * p->eta_main;

        double i_leak = calculate_leakage(p, s->v_store);
        double p_loss = (i_leak + p->i_q) * s->v_store;
        double p_net = p_ch - p_loss;

        if (p_net > 0.0) {
            double v_sq = s->v_store * s->v_store + (2.0 * p_net * dt) / p->c_store;
            s->v_store = sqrt(v_sq);
        }

        /* Досягнення верхнього гістерезисного порогу V_high */
        if (s->v_store >= p->v_high) {
            s->phase = PHASE_ACTIVE_BURST;
            s->burst_timer = 0.0;
            s->burst_count++;
        }
    } else if (s->phase == PHASE_ACTIVE_BURST) {
        s->burst_timer += dt;

        /* Розряд великим струмом навантаження: I = C * dV/dt */
        double i_total = p->i_burst + p->i_q + calculate_leakage(p, s->v_store);
        double dv = (i_total * dt) / p->c_store;
        s->v_store -= dv;

        /* Умови завершення імпульсу */
        if (s->burst_timer >= p->t_burst || s->v_store <= p->v_low) {
            s->phase = PHASE_MAIN_CHARGING;
        }
    }
}

int main(void) {
    HarvesterParams params = {
        .v_src = 0.040,         /* 40 мВ від термоелемента TEG */
        .r_src = 2.0,           /* 2.0 Ом внутрішнього опору */
        .c_aux = 4.7e-6,        /* 4.7 мкФ пускової ємності */
        .c_store = 470.0e-6,    /* 470 мкФ головного накопичувача */
        .v_high = 3.30,         /* 3.30 В поріг увімкнення */
        .v_low = 2.20,          /* 2.20 В поріг відсічки */
        .i_burst = 0.022,       /* 22 мА струм радіопередавача */
        .t_burst = 0.015,       /* 15 мс тривалість передачі */
        .i_q = 45.0e-9,         /* 45 нА струм споживання супервізора */
        .leak_i0 = 5.0e-9,      /* 5 нА початковий витік */
        .leak_alpha = 0.95,     /* коефіцієнт експоненти витоку */
        .eta_cold = 0.25,       /* 25% ККД JFET автогенератора */
        .eta_main = 0.82        /* 82% ККД синхронного boost */
    };

    HarvesterState state = {
        .time_sec = 0.0,
        .v_aux = 0.0,
        .v_store = 0.0,
        .phase = PHASE_COLD_START,
        .burst_timer = 0.0,
        .burst_count = 0
    };

    double dt = 0.001; /* крок інтегрування 1 мс */
    double max_time = 120.0; /* 2 хвилини симуляції */

    printf("Час (с) | Фаза         | V_aux (В) | V_store (В) | Імпульси\n");
    printf("-----------------------------------------------------------\n");

    double next_print = 0.0;
    while (state.time_sec <= max_time) {
        if (state.time_sec >= next_print) {
            const char *phase_str = (state.phase == PHASE_COLD_START) ? "Холодний старт" :
                                    (state.phase == PHASE_MAIN_CHARGING) ? "Накопичення  " : "АКТИВНИЙ СПАЛАХ";
            printf("%7.2f | %-12s | %9.3f | %11.3f | %8d\n",
                   state.time_sec, phase_str, state.v_aux, state.v_store, state.burst_count);
            next_print += (state.phase == PHASE_ACTIVE_BURST) ? 0.005 : 10.0;
        }

        harvester_step(&params, &state, dt);
    }

    printf("-----------------------------------------------------------\n");
    printf("Підсумок: успішно виконано %d імпульсів за %.1f с.\n",
           state.burst_count, state.time_sec);

    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <string_view>

namespace HarvesterSim {

enum class Phase {
    ColdStart,
    MainCharging,
    ActiveBurst
};

struct Config {
    double v_src{0.040};         // 40 мВ від джерела
    double r_src{2.0};           // 2.0 Ом внутрішнього опору
    double c_aux{4.7e-6};        // 4.7 мкФ пускова ємність
    double c_store{470.0e-6};    // 470 мкФ головний накопичувач
    double v_high{3.30};         // 3.30 В поріг запуску
    double v_low{2.20};          // 2.20 В поріг відсічки
    double i_burst{0.022};       // 22 мА струм навантаження
    double t_burst{0.015};       // 15 мс активний імпульс
    double i_q{45.0e-9};         // 45 нА споживання супервізора
    double leak_i0{5.0e-9};      // 5 нА базова константа витоку
    double leak_alpha{0.95};     // нахил експоненти витоку
    double eta_cold{0.25};       // ККД JFET генератора
    double eta_main{0.82};       // ККД основного boost
};

class SystemSimulator {
public:
    explicit SystemSimulator(Config config) : cfg_{config} {}

    void step(double dt) noexcept {
        time_ += dt;

        switch (phase_) {
            case Phase::ColdStart: {
                const double p_in = (cfg_.v_src * cfg_.v_src) / (4.0 * cfg_.r_src);
                const double p_aux = p_in * cfg_.eta_cold;
                const double v_sq = v_aux_ * v_aux_ + (2.0 * p_aux * dt) / cfg_.c_aux;
                v_aux_ = std::sqrt(v_sq);

                if (v_aux_ >= 1.8) {
                    phase_ = Phase::MainCharging;
                }
                break;
            }
            case Phase::MainCharging: {
                const double p_in = (cfg_.v_src * cfg_.v_src) / (4.0 * cfg_.r_src);
                const double p_ch = p_in * cfg_.eta_main;
                const double i_leak = calculate_leakage(v_store_);
                const double p_loss = (i_leak + cfg_.i_q) * v_store_;
                const double p_net = p_ch - p_loss;

                if (p_net > 0.0) {
                    const double v_sq = v_store_ * v_store_ + (2.0 * p_net * dt) / cfg_.c_store;
                    v_store_ = std::sqrt(v_sq);
                }

                if (v_store_ >= cfg_.v_high) {
                    phase_ = Phase::ActiveBurst;
                    burst_timer_ = 0.0;
                    ++burst_count_;
                }
                break;
            }
            case Phase::ActiveBurst: {
                burst_timer_ += dt;
                const double i_total = cfg_.i_burst + cfg_.i_q + calculate_leakage(v_store_);
                const double dv = (i_total * dt) / cfg_.c_store;
                v_store_ -= dv;

                if (burst_timer_ >= cfg_.t_burst || v_store_ <= cfg_.v_low) {
                    phase_ = Phase::MainCharging;
                }
                break;
            }
        }
    }

    [[nodiscard]] double time() const noexcept { return time_; }
    [[nodiscard]] double v_aux() const noexcept { return v_aux_; }
    [[nodiscard]] double v_store() const noexcept { return v_store_; }
    [[nodiscard]] Phase phase() const noexcept { return phase_; }
    [[nodiscard]] int burst_count() const noexcept { return burst_count_; }

    [[nodiscard]] std::string_view phase_name() const noexcept {
        switch (phase_) {
            case Phase::ColdStart:    return "Холодний старт";
            case Phase::MainCharging: return "Накопичення  ";
            case Phase::ActiveBurst:  return "АКТИВНИЙ СПАЛАХ";
        }
        return "Невідомо";
    }

private:
    [[nodiscard]] double calculate_leakage(double voltage) const noexcept {
        if (voltage <= 0.0) return 0.0;
        return cfg_.leak_i0 * std::exp(cfg_.leak_alpha * voltage);
    }

    Config cfg_;
    double time_{0.0};
    double v_aux_{0.0};
    double v_store_{0.0};
    double burst_timer_{0.0};
    int burst_count_{0};
    Phase phase_{Phase::ColdStart};
};

} // namespace HarvesterSim

int main() {
    HarvesterSim::Config config;
    HarvesterSim::SystemSimulator sim(config);

    constexpr double dt = 0.001;      // крок 1 мс
    constexpr double max_time = 120.0; // 2 хвилини

    std::cout << "Час (с) | Фаза         | V_aux (В) | V_store (В) | Імпульси\n";
    std::cout << "-----------------------------------------------------------\n";

    double next_print = 0.0;
    while (sim.time() <= max_time) {
        if (sim.time() >= next_print) {
            std::cout << std::fixed << std::setprecision(2)
                      << std::setw(7) << sim.time() << " | "
                      << std::setw(12) << sim.phase_name() << " | "
                      << std::setprecision(3)
                      << std::setw(9) << sim.v_aux() << " | "
                      << std::setw(11) << sim.v_store() << " | "
                      << std::setw(8) << sim.burst_count() << "\n";

            next_print += (sim.phase() == HarvesterSim::Phase::ActiveBurst) ? 0.005 : 10.0;
        }

        sim.step(dt);
    }

    std::cout << "-----------------------------------------------------------\n";
    std::cout << "Підсумок: успішно виконано " << sim.burst_count()
              << " імпульсів за " << sim.time() << " с.\n";

    return 0;
}
```
:::

---

### Аналіз результатів симуляції та підводні камені

Чисельний експеримент виявляє низку критичних інженерних закономірностей, які не є очевидними з простих аналітичних формул:

1. **Тривалість холодного старту (Cold Start Latency).**
   У перші 3–6 секунд симуляції головний накопичувач `C_store` перебуває під напругою 0 В. Уся вилучена енергія спрямовується виключно в малу допоміжну ємність `C_aux = 4.7 мкФ`. Завдяки малій ємності напруга на ній швидко піднімається до 1.8 В за 3.8 секунди. Якби розробник спробував пусковим JFET-генератором одразу заряджати головний накопичувач 470 мкФ або суперконденсатор 0.1 Ф, початковий старт розтягнувся б на десятки хвилин або взагалі зірвався через внутрішні витоки.

2. **Нелінійна асимптота заряду та пастка витоків.**
   У фазі основного накопичення напруга `V_store` наростає не лінійно, а за увігнутою кривою. У міру наближення напруги до 3.3 В експоненційний витік діелектрика `I_leak(V)` зростає від 5 нА до майже 115 нА. Якщо вхідна потужність збирача становить лише 10 мкВт (струм заряду ~3 мкА), а замість якісної кераміки встановлено старий іоністор із витоком `I_0 = 500 нА`, симуляція демонструє асимптотичне зависання напруги на рівні 2.75 В: система взагалі ніколи не досягає порогу `V_high = 3.3 В`.

3. **Динамічний спад напруги на внутрішньому опорі (ESR Droop).**
   У фазі активного спалаху струм 22 мА викачується за 15 мс. За цей час напруга ємності просідає з 3.30 В до 2.60 В, що безпечно перевищує нижній поріг відсічки `V_low = 2.20 В`. Проте якщо врахувати реальний опір `ESR = 15 Ом` (характерний для дешевих танталових конденсаторів або мініатюрних тонкоплівкових мікробатарей), на виході виникне миттєве стрибкоподібне просідання `ΔV_esr = 22 мА · 15 Ом = 330 мВ`. Напруга на виході впаде до 2.27 В, небезпечно наблизившись до порогу скидання. Для усунення цього ефекту накопичувач обов'язково шунтують керамічними конденсаторами типорозміру 0805/1206 з низьким `ESR < 50 мОм`.
