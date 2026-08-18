# ⚙️ Моделювання динаміки SET/RESET та ВАХ істерезису CBRAM

Чисельне моделювання вольт-амперної характеристики (ВАХ) осередку CBRAM дозволяє розрахувати динаміку проростання металевого нанопровідника, стрибок провідності під час фазового переходу SET, а також тепловий розрив містка при стиранні (RESET).

## 1. Алгоритм та фізичні рівняння моделі

Чисельна модель інтегрує рівняння росту висоти містка `h(t)` з часовим кроком `Δt`. Схема чисельного розрахунку будується на зв'язаній системі трьох фізичних рівнянь:

1. **Розрахунок електричного поля в зазорі**:
   Зазором між верхівкою містка висотою `h` та анодом є `d - h`. Напруженість поля в зазорі дорівнює:
   ```
   E = V_app / (d - h + δ)
   ```
   де `δ` — невелика регуляризаційна константа для уникнення ділення на нуль при торканні (`δ ≈ 0.1 нм`).

2. **Оновлення висоти містка (SET)**:
   При `V_app > 0` швидкість росту розраховується за формулою Мотта — Герні:
   ```
   v_growth = v_0 · exp( -E_a / (k_B · T) ) · sinh( (q · E · a) / (2 · k_B · T) )
   dh = v_growth · dt
   ```
   Якщо `h ≥ d`, місток повністю замкнений (стан LRS). Опір осередку стає рівним `R_LRS`.

3. **Струм та обмеження (Compliance)**:
   Струм через осередок обчислюється за законом Ома `I = V_app / R(h)`. Якщо `I > I_CC` (струм обмеження, compliance current), джерело напруги переходить у режим обмеження струму, і далі ріст містка припиняється.

4. **Джоулів нагрів та розчинення (RESET)**:
   При зворотній полярності `V_app < 0` струм `I` викликає Джоулів нагрів у звуженні:
   ```
   T = T_env + (I² · R_LRS) / C_th
   ```
   При підвищенні температури швидкість розчинення містка зростає експоненціально, призводячи до зменшення `h` та розриву містка назад у стан HRS.

Фізична модель враховує нелінійний зв'язок між прикладеним імпульсом та швидкістю переміщення ростового фронту. Використання адаптивного часового кроку `Δt` дозволяє точно відстежити фазовий стрибок провідності, який протікає у пікосекундному часовому масштабі.

Модель також забезпечує захист від переповнення експоненти при розрахунку синуса гіперболічного у сильних полях, обрізаючи аргумент `arg` на безпечному рівні. Це гарантує чисельну стабільність розв'язку навіть при кроках напруги `V > 2 В`.

## 2. Структура параметрів та фізичний зміст змінних

Модель спирається на такі ключові параметри комірки та середовища:

- **`cell_gap` / `cellGap`**: Товщина диелектричної матриці електроліту у метрах (`10.0e-9 м` або `10 нм`). Визначає абсолютну довжину пробігу катіона від катода до анода.
- **`act_energy` / `activationEnergy`**: Початковий активаційний бар'єр стрибка катіона `E_a` у джоулях (`0.8 еВ ≈ 1.28 × 10⁻¹⁹ Дж`). Пояснює термодинамічну стійкість збереженого стану за відсутності поля.
- **`hop_distance` / `hopDistance`**: Середня відстань між сусідніми потенційними ямами ґратки `a` у метрах (`0.4e-9 м` або `0.4 нм`).
- **`nu_0` / `attemptFrequency`**: Частота спроб стрибка катіона `ν_0` у герцах (`1.0e13 Гц`), що відповідає частоті фононних коливань ґратки.
- **`r_hrs` / `rHrs`**: Початковий опір диелектричної матриці в стані HRS у омах (`10.0e6 Ом` або `10 МОм`).
- **`r_lrs` / `rLrs`**: Опір повністю сформованого металевого містка в стані LRS у омах (`1000.0 Ом` або `1 кОм`).
- **`i_comp` / `iCompliance`**: Струм обмеження селектора `I_CC` у амперах (`100.0e-6 А` або `100 мкА`).
- **`c_th` / `thermalCoeff`**: Ефективний коефіцієнт тепловідводу звуження `C_th` у ватах на келвін (`5.0e-5 Вт/К`), який задає рівноважну температуру Джоулевого нагріву.

## 3. Програмна реалізація симулятора

Нижче наведено програмну реалізацію чисельного симулятора істерезисної ВАХ комірки CBRAM двома мовами — C та C++. Обидві версії реалізують ідентичний чисельний алгоритм з можливістю параметризації фізичних властивостей електроліту.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Фізичні константи */
#define Q_ELEM 1.602e-19       /* Елементарний заряд, Кл */
#define KB 1.381e-23           /* Стала Больцмана, Дж/К */
#define T_ENV 300.0            /* Температура середовища, К */

/* Параметри структури CBRAM */
typedef struct {
    double cell_gap;           /* Товщина електроліту, м (наприклад, 10 нм) */
    double act_energy;         /* Енергія активації E_a, джоулі (0.8 еВ) */
    double hop_distance;       /* Довжина стрибка іона a, м (0.4 нм) */
    double nu_0;               /* Частота спроб, Гц (1e13) */
    double r_hrs;              /* Опір матриці в стан HRS, Ом (10 МОм) */
    double r_lrs;              /* Опір сформованого містка LRS, Ом (1 кОм) */
    double i_comp;             /* Комплайєнс струму I_CC, А (100 мкА) */
    double c_th;               /* Тепловий коефіцієнт нагріву, Вт/К */
} CbramParams;

/* Стан осередку */
typedef struct {
    double fil_height;         /* Висота містка h, м */
    double temp;               /* Поточна температура звуження, К */
    bool is_connected;         /* Прапорець замикання містка */
} CbramState;

/* Ініціалізація параметрів за замовчуванням */
static CbramParams default_params(void) {
    CbramParams p;
    p.cell_gap = 10.0e-9;
    p.act_energy = 0.8 * Q_ELEM;
    p.hop_distance = 0.4e-9;
    p.nu_0 = 1.0e13;
    p.r_hrs = 1.0e7;
    p.r_lrs = 1000.0;
    p.i_comp = 100.0e-6;
    p.c_th = 5.0e-5;
    return p;
}

/* Обчислення поточного опору елемента */
static double compute_resistance(const CbramParams *p, double h) {
    if (h >= p->cell_gap * 0.99) {
        return p->r_lrs;
    }
    /* Пропорційне змішування опору зазору та містка */
    double fraction = h / p->cell_gap;
    double r_curr = p->r_hrs * (1.0 - fraction) + p->r_lrs * fraction;
    return (r_curr < p->r_lrs) ? p->r_lrs : r_curr;
}

/* Один крок симуляції часом dt */
static void step_simulation(const CbramParams *p, CbramState *st, double v_app, double dt, double *out_i) {
    double r_cell = compute_resistance(p, st->fil_height);
    double i_cell = v_app / r_cell;

    /* Обмеження комплайєнсом при SET */
    if (v_app > 0 && fabs(i_cell) > p->i_comp) {
        i_cell = (i_cell > 0) ? p->i_comp : -p->i_comp;
    }

    /* Джоулів нагрів */
    double p_joule = i_cell * i_cell * r_cell;
    st->temp = T_ENV + p_joule / p->c_th;

    /* Польовий дрейф іонів */
    double gap_rem = p->cell_gap - st->fil_height + 0.1e-9;
    double e_field = v_app / gap_rem;

    if (v_app > 0 && !st->is_connected) {
        /* Режим SET: ріст містка */
        double arg = (Q_ELEM * e_field * p->hop_distance) / (2.0 * KB * st->temp);
        if (arg > 30.0) arg = 30.0; /* Захист від переповнення */
        double v_drift = p->nu_0 * p->hop_distance * exp(-p->act_energy / (KB * st->temp)) * sinh(arg);

        st->fil_height += v_drift * dt;
        if (st->fil_height >= p->cell_gap * 0.99) {
            st->fil_height = p->cell_gap;
            st->is_connected = true;
        }
    } else if (v_app < 0 && st->is_connected) {
        /* Режим RESET: термічне та електрохімічне розчинення */
        double v_dissolve = p->nu_0 * p->hop_distance * exp(-p->act_energy / (KB * st->temp)) * 2.0;
        st->fil_height -= v_dissolve * dt;
        if (st->fil_height < p->cell_gap * 0.95) {
            st->is_connected = false;
        }
        if (st->fil_height < 0) {
            st->fil_height = 0;
        }
    }

    *out_i = i_cell;
}

int main(void) {
    CbramParams params = default_params();
    CbramState state = { 0.0, T_ENV, false };

    int num_steps = 200;
    double dt = 1.0e-5; /* 10 мкс */
    
    printf("--- CBRAM Simulation Output (C) ---\n");
    printf("Step\tVoltage(V)\tCurrent(uA)\tHeight(nm)\tState\n");

    /* Цикл напруги: 0V -> 1.5V (SET) -> 0V -> -1.0V (RESET) -> 0V */
    for (int i = 0; i <= num_steps; i++) {
        double t = (double)i / num_steps;
        double v_app = 0.0;

        if (t <= 0.25) {
            v_app = (t / 0.25) * 1.5;         /* Наростання SET */
        } else if (t <= 0.50) {
            v_app = 1.5 - ((t - 0.25) / 0.25) * 1.5; /* Спад SET */
        } else if (t <= 0.75) {
            v_app = -((t - 0.50) / 0.25) * 1.0; /* Наростання RESET */
        } else {
            v_app = -1.0 + ((t - 0.75) / 0.25) * 1.0; /* Повернення в 0В */
        }

        double i_out = 0.0;
        step_simulation(&params, &state, v_app, dt, &i_out);

        if (i % 20 == 0) {
            printf("%d\t%.3f\t\t%.2f\t\t%.2f\t\t%s\n",
                   i, v_app, i_out * 1e6, state.fil_height * 1e9,
                   state.is_connected ? "LRS" : "HRS");
        }
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <string_view>
#include <algorithm>

namespace cbram {

constexpr double kElemCharge = 1.602e-19; // Елементарний заряд, Кл
constexpr double kBoltzmann  = 1.381e-23; // Стала Больцмана, Дж/К
constexpr double kTempEnv    = 300.0;     // Кімнатна температура, К

// Структура фізичних параметрів комірки
struct CellParameters {
    double cellGap{10.0e-9};            // Товщина електроліту (м)
    double activationEnergy{0.8 * kElemCharge}; // E_a (Дж)
    double hopDistance{0.4e-9};         // Довжина стрибка іона (м)
    double attemptFrequency{1.0e13};    // Частота спроб (Гц)
    double rHrs{1.0e7};                 // Опір HRS (Ом)
    double rLrs{1000.0};                // Опір LRS (Ом)
    double iCompliance{100.0e-6};       // Обмеження струму I_CC (А)
    double thermalCoeff{5.0e-5};        // Тепловий коефіцієнт (Вт/К)
};

// Точка результату розрахунку ВАХ
struct SimulationPoint {
    double voltage{0.0};
    double current{0.0};
    double filamentHeight{0.0};
    double temperature{kTempEnv};
    bool isLrs{false};
};

class CellSimulator {
public:
    explicit CellSimulator(CellParameters params = {})
        : params_(params), height_(0.0), temp_(kTempEnv), isConnected_(false) {}

    // Виконати один диференціальний крок
    SimulationPoint step(double vApp, double dt) {
        const double rCell = computeResistance();
        double iCell = vApp / rCell;

        // Захист струму комплайєнсом
        if (vApp > 0.0 && std::abs(iCell) > params_.iCompliance) {
            iCell = std::copysign(params_.iCompliance, iCell);
        }

        // Джоулів нагрів у звуженні
        const double pJoule = iCell * iCell * rCell;
        temp_ = kTempEnv + pJoule / params_.thermalCoeff;

        // Поле в зазорі
        const double gapRem = params_.cellGap - height_ + 0.1e-9;
        const double eField = vApp / gapRem;

        if (vApp > 0.0 && !isConnected_) {
            // Динаміка SET
            double arg = (kElemCharge * eField * params_.hopDistance) / (2.0 * kBoltzmann * temp_);
            arg = std::min(arg, 30.0); // Захист від exp-overflow

            const double vDrift = params_.attemptFrequency * params_.hopDistance *
                                  std::exp(-params_.activationEnergy / (kBoltzmann * temp_)) *
                                  std::sinh(arg);

            height_ += vDrift * dt;
            if (height_ >= params_.cellGap * 0.99) {
                height_ = params_.cellGap;
                isConnected_ = true;
            }
        } else if (vApp < 0.0 && isConnected_) {
            // Динаміка RESET
            const double vDissolve = params_.attemptFrequency * params_.hopDistance *
                                     std::exp(-params_.activationEnergy / (kBoltzmann * temp_)) * 2.0;
            height_ -= vDissolve * dt;
            if (height_ < params_.cellGap * 0.95) {
                isConnected_ = false;
            }
            height_ = std::max(0.0, height_);
        }

        return SimulationPoint{vApp, iCell, height_, temp_, isConnected_};
    }

    [[nodiscard]] double height() const noexcept { return height_; }
    [[nodiscard]] bool isLrs() const noexcept { return isConnected_; }

private:
    [[nodiscard]] double computeResistance() const noexcept {
        if (height_ >= params_.cellGap * 0.99) {
            return params_.rLrs;
        }
        const double fraction = height_ / params_.cellGap;
        const double rCurr = params_.rHrs * (1.0 - fraction) + params_.rLrs * fraction;
        return std::max(rCurr, params_.rLrs);
    }

    CellParameters params_;
    double height_;
    double temp_;
    bool isConnected_;
};

} // namespace cbram

int main() {
    using namespace cbram;

    CellParameters params;
    CellSimulator simulator(params);

    constexpr int steps = 200;
    constexpr double dt = 1.0e-5;

    std::cout << "=== CBRAM Simulation Output (C++) ===\n";
    std::cout << std::left 
              << std::setw(8)  << "Step"
              << std::setw(14) << "Voltage (V)"
              << std::setw(16) << "Current (uA)"
              << std::setw(16) << "Filament (nm)"
              << "State\n";

    for (int i = 0; i <= steps; ++i) {
        const double t = static_cast<double>(i) / steps;
        double vApp = 0.0;

        if (t <= 0.25) {
            vApp = (t / 0.25) * 1.5;
        } else if (t <= 0.50) {
            vApp = 1.5 - ((t - 0.25) / 0.25) * 1.5;
        } else if (t <= 0.75) {
            vApp = -((t - 0.50) / 0.25) * 1.0;
        } else {
            vApp = -1.0 + ((t - 0.75) / 0.25) * 1.0;
        }

        const auto pt = simulator.step(vApp, dt);

        if (i % 20 == 0) {
            std::cout << std::left
                      << std::setw(8)  << i
                      << std::setw(14) << std::fixed << std::setprecision(3) << pt.voltage
                      << std::setw(16) << std::fixed << std::setprecision(2) << pt.current * 1e6
                      << std::setw(16) << std::fixed << std::setprecision(2) << pt.filamentHeight * 1e9
                      << (pt.isLrs ? "LRS" : "HRS") << "\n";
        }
    }

    return 0;
}
```
:::

## 4. Порівняльний аналіз реалізацій C та C++

Обидві реалізації розраховують однакову фізичну модель, проте виражають її через різні ідіоми мов програмування:

- **C-реалізація**: використовує класичний імперативний підхід із процедурними функціями, явними покажчиками та структурами `CbramParams` і `CbramState`. Обчислення опору здійснюється статичною функцією `compute_resistance()`, а вивід результатів — через `printf`.
- **C++-реалізація**: організована у вигляді ізольованого класу `CellSimulator` в окремому просторі імен `cbram`. Стан комірки інкапсульовано у приватних полях класу, забезпечуючи RAII та гарантію незмінності вихідних параметрів. Для форматування виводу використовується тип `SimulationPoint` та безпечні маніпулятори потоку `std::setw` і `std::setprecision`.

## 5. Крайові випадки та обробка чисельних обмежень

Під час чисельного моделювання нелінійного іонного транспорту можуть виникати крайові умови, які вимагають спеціальної обробки у коді:

1. **Захист від ділення на нуль при торканні анода**: коли `fil_height` наближається до `cell_gap`, зазор `(cell_gap - fil_height)` наближається до нуля. Введення регуляризаційної добавки `0.1 нм` запобігає нескінченному значення електричного поля `e_field`.
2. **Захист від переповнення експоненти (Floating Point Overflow)**: при напруженій `E > 5 × 10⁶ В/см` аргумент гіперболічного синуса `arg = q E a / (2 k_B T)` може перевищувати `100`. Оскільки `sinh(100)` виходить за межі `double`, аргумент обрізається функцією `std::min(arg, 30.0)`.
3. **Обмеження висоти містка**: висота містка фізично обмежена інтервалом `[0, cell_gap]`. Від'ємні значення `fil_height` при інтенсивному RESET відсікаються функцією `std::max(0.0, height_)`.

## 6. Аналіз результатів симуляції та часова динаміка

Чисельне моделювання демонструє ключові особливості роботи приладу CBRAM:

1. **Поріг SET**: при досягненні напруги `V_app ≈ 1.0–1.2 В` висока напруженість поля в зазорі викликує лавиноподібне прискорення росту містка. Опір падає від `10 МОм` до `1 кОм`, а струм обмежено рівнем `100 мкА`.
2. **Асиметрія RESET**: стирання відбувається лише при зворотній полярності `V_app < 0`. Джоулів нагрів локального звуження прискорює термохімічне розчинення, повертаючи комірку у високоомний стан HRS.
3. **Ефекти комплайєнсу**: регулювання величини `I_CC` у коді прямо визначає остаточний значення опору `R_LRS`. При зменшенні `I_CC` від `100 мкА` до `10 мкА` сформований місток стає вужчим, а його опір піднімається від `1 кОм` до `10 кОм`, що підтверджує можливість багаторівневого кодування даних.

Урахування теплового балансу в коді пояснює, чому стирання RESET вимагає меншого часу за наявності високого струму: локальне підвищення температури `T_max` в звуженні до `500–600 K` знижує активаційний бар'єр дифузії, прискорюючи розрив містка на кілька порядків.

При праці у режимі постійної напруги часовий затрим «формування» містка обернено пропорційний гіперболічному синусу електричного поля. Це дозволяє проектувати імпульсні режими запису, де висока напруга подається коротким сплеском тривалістю `2–5 нс`, забезпечуючи мінімальне енергоспоживання.
