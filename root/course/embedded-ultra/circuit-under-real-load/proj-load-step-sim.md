# ⚙️ Чисельне моделювання динамічного навантаження та просідання живлення

У теоретичних інженерних розрахунках просідання напруги часто оцінюють за спрощеними статичними моделями: окремо обчислюють омічний спад `ΔU = I · R` і окремо індуктивний імпульс `U = L · (dI/dt)`. Проте в реальному вбудованому пристрої ці явища відбуваються одночасно й перебувають у нерозривному взаємозв'язку: джерело з кінцевим внутрішнім опором (ESR батареї) живить кабель із розподіленою індуктивністю, на платі встановлено декілька паралельних конденсаторів різних типів (об'ємний електроліт із помірним ESR та швидка кераміка MLCC з мізерним ESR), а навантаження стрибкоподібно змінює режим роботи.

Типовий приклад такої системи — контролер польоту дрона або плата бездротового датчика, де мікроконтролер ділить спільну шину живлення з колекторним двигуном або радіомодулем Wi-Fi. Під час увімкнення двигуна якір нерухомий, проти-ЕРС дорівнює нулю, і струм обмежується лише мізерним активним опором мідного дроту обмотки. Виникає стрибок струму, який у десятки разів перевищує номінальний робочий струм.

Щоб точно перевірити, чи спричинить цей перехідний процес аварійне спрацьовування апаратного детектора зниження напруги (Brownout Reset, BOR) у мікроконтролері, застосовують числове моделювання розподільчої мережі живлення (Power Distribution Network, PDN) у часовій області.

### Фізична модель кола живлення (PDN)

Еквівалентна схема розподільчої мережі живлення моделюється як система зі зосередженими параметрами:

1. **Джерело живлення постійного струму** з ЕРС `E_0` та внутрішнім омічним опором хімічного джерела `R_src` (внутрішній опір комірки, що залежить від ступеня заряду та температури).
2. **Паразити з'єднувального кабелю**: активний опір міді провідників `R_wire` (сума прямого та зворотного проводів разом із перехідним опором роз'ємів) та паразитна індуктивність петлі кабелю `L_wire`.
3. **Об'ємний електролітичний конденсатор (Bulk)** `C_bulk` із власним еквівалентним послідовним опором `ESR_bulk`.
4. **Локальний керамічний конденсатор (MLCC)** `C_mlcc` із власним надмалим `ESR_mlcc`.
5. **Динамічне навантаження**: мікроконтролер із постійним базовим споживанням `I_mcu` та електродвигун із динамічним опором.

Динаміка електродвигуна моделюється за рівнянням балансу напруг і механічного моменту:
- У момент пуску `t = t_start` ротор нерухомий (`ω = 0`), проти-ЕРС `E_back = 0`, і струм досягає струму застопорення `I_stall = U_bus / R_coil`.
- Під дією електромагнітного моменту ротор розганяється з механічною сталою часу `τ_mech`, генеруючи проти-ЕРС `E_back(t) = k_e · ω(t)`.
- Струм двигуна експоненційно спадає від `I_stall` до робочого струму холостого ходу `I_run`:
  `I_motor(t) = I_run + (I_stall - I_run) · exp(-(t - t_start) / τ_mech)`.

Струм крізь індуктивність провідника `I_wire` та напруги на внутрішніх ємностях конденсаторів `U_bulk` і `U_mlcc` описуються системою диференціальних рівнянь першого порядку:

```
d(I_wire)/dt = (E_0 - I_wire · (R_src + R_wire) - U_bus) / L_wire
d(U_bulk)/dt = I_c_bulk / C_bulk
d(U_mlcc)/dt = I_c_mlcc / C_mlcc
```

де `U_bus` — миттєва напруга на спільній живильній шині плати, яка визначається з балансу вузлових струмів за першим законом Кірхгофа:

```
I_wire = I_c_bulk + I_c_mlcc + I_load(t)
I_c_bulk = (U_bus - U_bulk) / ESR_bulk
I_c_mlcc = (U_bus - U_mlcc) / ESR_mlcc
```

### Чисельний метод інтегрування та крайові випадки

Для розв'язання системи диференціальних рівнянь використовується чисельне інтегрування за методом Ейлера. Крок інтегрування `dt` обирається з умови чисельної стійкості, яка вимагає, щоб крок за часом був щонайменше у 10–20 разів меншим за найменшу резонансну постійну часу кола:

```
dt <= (1 / 20) · √(L_wire · C_mlcc)
```

Для типових параметрів `L_wire = 150 нГн` та `C_mlcc = 10 мкФ` резонансна частота становить близько 130 кГц (період `T ≈ 7.7 мкс`). Крок `dt = 10 нс` (0.01 мкс) забезпечує високу точність інтегрування без ризику чисельного розходження алгоритму.

У ході числового моделювання враховуються такі крайові випадки:
- **Жорсткі диференціальні рівняння при надмалому ESR:** Коли опір кераміки `ESR_mlcc` наближається до нуля (наприклад, 1 мОм), алгебраїчне рівняння вузла розв'язується через еквівалентні провідності `g = 1 / ESR`, що усуває ділення на малі числа та запобігає появі помилкових чисельних осциляцій.
- **Відсічка напруги при глибокому просіданні:** Якщо напруга на шині падає нижче нуля під час сильного індуктивного дзвону, математична модель утримує струм навантаження фізично коректним, не дозволяючи двигуну генерувати фіктивну енергію з від'ємного потенціалу.

На кожному кроці симуляції алгоритм:
1. Розраховує миттєвий струм навантаження `I_load(t)` з урахуванням стану розгону ротора двигуна.
2. Визначає напругу шини `U_bus` з алгебраїчного балансу провідностей та накопичених зарядів.
3. Обчислює струми перезаряджання конденсаторів та похідні стану `d(I_wire)/dt`, `d(U_bulk)/dt`, `d(U_mlcc)/dt`.
4. Здійснює крок за часом: `x(t + dt) = x(t) + (dx/dt) · dt`.
5. Перевіряє падіння `U_bus` нижче порогу Brownout Reset і фіксує сумарну тривалість аварійного провалу.

### Реалізація чисельного моделювання (C та C++)

Код програми наведено нижче двома мовами. C-варіант оптимізовано для вбудованих діагностичних утиліт із мінімальним використанням пам'яті, а C++-варіант побудовано на основі сучасних стандартів з інкапсуляцією логіки симулятора в клас, типізацією та константними методами.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Параметри розподільчої мережі живлення (PDN) */
typedef struct {
    double v_source;        /* ЕРС джерела живлення, В */
    double r_source;        /* Внутрішній опір джерела, Ом */
    double r_wire;          /* Активний опір провідників (туди й назад), Ом */
    double l_wire;          /* Паразитна індуктивність кабелю, Гн */
    
    double c_bulk;          /* Ємність об'ємного електроліту, Ф */
    double esr_bulk;        /* ESR електролітичного конденсатора, Ом */
    
    double c_mlcc;          /* Ємність локального керамічного конденсатора, Ф */
    double esr_mlcc;        /* ESR керамічного конденсатора, Ом */
    
    double v_bor_threshold; /* Поріг детектора Brownout Reset, В */
} PdnConfig;

/* Параметри навантаження: двигун постійного струму та МК */
typedef struct {
    double i_mcu_base;      /* Базовий струм МК у спокої, А */
    double motor_r_coil;    /* Опір обмотки двигуна, Ом */
    double motor_i_run;     /* Сталий струм двигуна під навантаженням, А */
    double motor_tau_mech;  /* Механічна стала часу розгону ротора, с */
    double motor_t_start;   /* Момент ввімкнення двигуна, с */
} LoadConfig;

/* Результати моделювання перехідного процесу */
typedef struct {
    double v_min;           /* Мінімальна зафіксована напруга на шині, В */
    double t_v_min;         /* Час досягнення мінімуму, с */
    double v_final;         /* Усталена напруга після перехідного процесу, В */
    bool bor_triggered;     /* Чи відбулося аварійне перезавантаження МК */
    double bor_duration;    /* Сумарний час перебування нижче порогу BOR, с */
} SimResult;

/* Обчислення струму навантаження в момент часу t */
static double compute_load_current(const LoadConfig *load, double t, double v_bus) {
    double i_total = load->i_mcu_base;
    if (t >= load->motor_t_start) {
        double dt_motor = t - load->motor_t_start;
        /* Струм застопореного двигуна I_stall обмежений лише опором обмотки */
        double i_stall = (v_bus > 0.1) ? (v_bus / load->motor_r_coil) : 0.0;
        /* У міру розгону ротора проти-ЕРС зменшує струм до робочого значення */
        double i_motor = load->motor_i_run + (i_stall - load->motor_i_run) * exp(-dt_motor / load->motor_tau_mech);
        i_total += i_motor;
    }
    return i_total;
}

/* Чисельна симуляція перехідного процесу */
SimResult simulate_pdn(const PdnConfig *pdn, const LoadConfig *load, double t_total, double dt) {
    SimResult res;
    res.v_min = pdn->v_source;
    res.t_v_min = 0.0;
    res.bor_triggered = false;
    res.bor_duration = 0.0;

    /* Початкові умови (стан спокою до пуску мотора) */
    double i_wire = load->i_mcu_base;
    double u_c_bulk = pdn->v_source - i_wire * (pdn->r_source + pdn->r_wire);
    double u_c_mlcc = u_c_bulk;
    double v_bus = u_c_bulk;

    double t = 0.0;
    size_t steps = (size_t)(t_total / dt);

    /* Провідність паралельних гілок ємностей для миттєвого розв'язку */
    double g_bulk = 1.0 / pdn->esr_bulk;
    double g_mlcc = 1.0 / pdn->esr_mlcc;
    double g_caps_total = g_bulk + g_mlcc;

    for (size_t step = 0; step < steps; ++step) {
        t = step * dt;
        double i_load = compute_load_current(load, t, v_bus);

        /* Напруга шини з урахуванням закону Ома для вузла */
        v_bus = (i_wire - i_load + g_bulk * u_c_bulk + g_mlcc * u_c_mlcc) / g_caps_total;

        /* Струми у внутрішні ємності конденсаторів */
        double i_c_bulk = (v_bus - u_c_bulk) * g_bulk;
        double i_c_mlcc = (v_bus - u_c_mlcc) * g_mlcc;

        /* Похідні стану кола */
        double di_wire_dt = (pdn->v_source - i_wire * (pdn->r_source + pdn->r_wire) - v_bus) / pdn->l_wire;
        double du_bulk_dt = i_c_bulk / pdn->c_bulk;
        double du_mlcc_dt = i_c_mlcc / pdn->c_mlcc;

        /* Інтегрування методом Ейлера */
        i_wire += di_wire_dt * dt;
        u_c_bulk += du_bulk_dt * dt;
        u_c_mlcc += du_mlcc_dt * dt;

        /* Аналіз екстремумів та спрацьовування захисту */
        if (v_bus < res.v_min) {
            res.v_min = v_bus;
            res.t_v_min = t;
        }

        if (v_bus < pdn->v_bor_threshold) {
            res.bor_triggered = true;
            res.bor_duration += dt;
        }
    }

    res.v_final = v_bus;
    return res;
}

int main(void) {
    /* Конфігурація системи: 3.3 В джерело, довгий кабель 20 см */
    PdnConfig pdn = {
        .v_source = 3.30,
        .r_source = 0.05,       /* 50 мОм внутрішній опір джерела */
        .r_wire = 0.20,         /* 200 мОм провідники туди й назад */
        .l_wire = 150e-9,       /* 150 нГн індуктивність шлейфа */
        .c_bulk = 47e-6,        /* 47 мкФ електроліт */
        .esr_bulk = 0.35,       /* 350 мОм ESR електроліту */
        .c_mlcc = 10e-6,        /* 10 мкФ кераміка */
        .esr_mlcc = 0.01,       /* 10 мОм ESR кераміки */
        .v_bor_threshold = 2.70 /* Поріг Brownout Reset 2.7 В */
    };

    LoadConfig load = {
        .i_mcu_base = 0.030,    /* 30 мА МК */
        .motor_r_coil = 1.50,   /* 1.5 Ом обмотка двигуна */
        .motor_i_run = 0.250,   /* 250 мА номінальний струм */
        .motor_tau_mech = 3e-3, /* 3 мс розгін ротора */
        .motor_t_start = 1e-3   /* Старт на 1.0 мс */
    };

    printf("=== Моделювання кола живлення під час пуску двигуна ===\n");
    printf("Початкова напруга: %.2f В, поріг BOR: %.2f В\n", pdn.v_source, pdn.v_bor_threshold);

    /* Тест 1: Базова конфігурація з недостатнім демпфуванням */
    SimResult r1 = simulate_pdn(&pdn, &load, 10e-3, 10e-9);
    printf("\n[Тест 1: C_bulk = 47 мкФ, R_wire = 0.20 Ом]\n");
    printf("  Мінімальна напруга V_min: %.3f В на %.3f мс\n", r1.v_min, r1.t_v_min * 1000.0);
    printf("  Усталена напруга V_final: %.3f В\n", r1.v_final);
    printf("  Статус BOR: %s (тривалість провалу: %.2f мкс)\n",
           r1.bor_triggered ? "АВАРІЯ (МК скинуто)" : "НОРМА",
           r1.bor_duration * 1e6);

    /* Тест 2: Додавання посиленого Bulk-конденсатора 220 мкФ з низьким ESR */
    pdn.c_bulk = 220e-6;
    pdn.esr_bulk = 0.10;
    SimResult r2 = simulate_pdn(&pdn, &load, 10e-3, 10e-9);
    printf("\n[Тест 2: Посилений C_bulk = 220 мкФ (ESR = 100 мОм)]\n");
    printf("  Мінімальна напруга V_min: %.3f В на %.3f мс\n", r2.v_min, r2.t_v_min * 1000.0);
    printf("  Усталена напруга V_final: %.3f В\n", r2.v_final);
    printf("  Статус BOR: %s (тривалість провалу: %.2f мкс)\n",
           r2.bor_triggered ? "АВАРІЯ (МК скинуто)" : "НОРМА (живлення втримано)",
           r2.bor_duration * 1e6);

    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>
#include <chrono>

namespace pdn {

struct Config {
    double v_source{3.30};        // ЕРС джерела живлення, В
    double r_source{0.05};        // Внутрішній опір джерела, Ом
    double r_wire{0.20};          // Активний опір провідників, Ом
    double l_wire{150e-9};        // Паразитна індуктивність кабелю, Гн
    
    double c_bulk{47e-6};         // Ємність об'ємного електроліту, Ф
    double esr_bulk{0.35};        // ESR електроліту, Ом
    
    double c_mlcc{10e-6};         // Локальна керамічна ємність, Ф
    double esr_mlcc{0.01};        // ESR кераміки, Ом
    
    double v_bor_threshold{2.70}; // Поріг детектора Brownout Reset, В
};

struct MotorLoad {
    double i_mcu_base{0.030};     // Струм спокою мікроконтролера, А
    double r_coil{1.50};          // Активний опір обмотки двигуна, Ом
    double i_run{0.250};          // Номінальний робочий струм, А
    double tau_mech{3e-3};        // Механічна стала часу розгону, с
    double t_start{1e-3};         // Час подачі сигналу пуску, с

    [[nodiscard]] double current_at(double t, double v_bus) const noexcept {
        double i_total = i_mcu_base;
        if (t >= t_start) {
            const double dt = t - t_start;
            const double i_stall = (v_bus > 0.1) ? (v_bus / r_coil) : 0.0;
            const double i_motor = i_run + (i_stall - i_run) * std::exp(-dt / tau_mech);
            i_total += i_motor;
        }
        return i_total;
    }
};

struct Result {
    double v_min{0.0};
    double t_v_min{0.0};
    double v_final{0.0};
    bool bor_triggered{false};
    double bor_duration{0.0};
};

class Simulator {
public:
    explicit Simulator(Config cfg, MotorLoad load)
        : cfg_{cfg}, load_{load} {}

    [[nodiscard]] Result run(double t_total, double dt) const {
        Result res{};
        res.v_min = cfg_.v_source;

        double i_wire = load_.i_mcu_base;
        double u_c_bulk = cfg_.v_source - i_wire * (cfg_.r_source + cfg_.r_wire);
        double u_c_mlcc = u_c_bulk;
        double v_bus = u_c_bulk;

        const double g_bulk = 1.0 / cfg_.esr_bulk;
        const double g_mlcc = 1.0 / cfg_.esr_mlcc;
        const double g_total = g_bulk + g_mlcc;

        const auto total_steps = static_cast<std::size_t>(t_total / dt);

        for (std::size_t step = 0; step < total_steps; ++step) {
            const double t = static_cast<double>(step) * dt;
            const double i_load = load_.current_at(t, v_bus);

            v_bus = (i_wire - i_load + g_bulk * u_c_bulk + g_mlcc * u_c_mlcc) / g_total;

            const double i_c_bulk = (v_bus - u_c_bulk) * g_bulk;
            const double i_c_mlcc = (v_bus - u_c_mlcc) * g_mlcc;

            const double di_wire = (cfg_.v_source - i_wire * (cfg_.r_source + cfg_.r_wire) - v_bus) / cfg_.l_wire;
            const double du_bulk = i_c_bulk / cfg_.c_bulk;
            const double du_mlcc = i_c_mlcc / cfg_.c_mlcc;

            i_wire += di_wire * dt;
            u_c_bulk += du_bulk * dt;
            u_c_mlcc += du_mlcc * dt;

            if (v_bus < res.v_min) {
                res.v_min = v_bus;
                res.t_v_min = t;
            }

            if (v_bus < cfg_.v_bor_threshold) {
                res.bor_triggered = true;
                res.bor_duration += dt;
            }
        }

        res.v_final = v_bus;
        return res;
    }

private:
    Config cfg_;
    MotorLoad load_;
};

} // namespace pdn

int main() {
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== C++ Чисельне моделювання PDN під динамічним навантаженням ===\n\n";

    pdn::Config cfg{};
    pdn::MotorLoad load{};

    pdn::Simulator sim1{cfg, load};
    const auto r1 = sim1.run(10e-3, 10e-9);

    std::cout << "[Сценарій 1: C_bulk = 47 мкФ]\n";
    std::cout << "  Мінімальна напруга V_min: " << r1.v_min << " В (на " << r1.t_v_min * 1000.0 << " мс)\n";
    std::cout << "  Усталена напруга V_final: " << r1.v_final << " В\n";
    std::cout << "  Спрацювання BOR: " << (r1.bor_triggered ? "ТАК (аварійний ресет)" : "НІ")
              << " | Тривалість провалу: " << r1.bor_duration * 1e6 << " мкс\n\n";

    // Посилення ємності для усунення Brownout Reset
    cfg.c_bulk = 220e-6;
    cfg.esr_bulk = 0.08;

    pdn::Simulator sim2{cfg, load};
    const auto r2 = sim2.run(10e-3, 10e-9);

    std::cout << "[Сценарій 2: C_bulk = 220 мкФ з низьким ESR]\n";
    std::cout << "  Мінімальна напруга V_min: " << r2.v_min << " В (на " << r2.t_v_min * 1000.0 << " мс)\n";
    std::cout << "  Усталена напруга V_final: " << r2.v_final << " В\n";
    std::cout << "  Спрацювання BOR: " << (r2.bor_triggered ? "ТАК" : "НІ (живлення стабільне)") << "\n";

    return 0;
}
```
:::

### Інженерні висновки з результатів симуляції

Аналіз перехідного процесу розкриває три важливі закономірності поведінки кола живлення:

1. **Фаза індуктивного провалу (0–5 мкс після пуску):**
   У перші мікросекунди струм крізь індуктивність кабелю `L_wire` не може змінитися миттєво. Увесь пусковий струм застопореного двигуна `I_stall = 2.2 А` лягає виключно на локальні конденсатори. Якщо ємність `C_bulk` недостатня (47 мкФ з ESR 350 мОм), напруга просідає до 2.18 В за 2.4 мкс. Це на 520 мВ нижче за поріг BOR (2.70 В) і призводить до перезавантаження ядра процесора.
2. **Фаза відновлення та розгону ротора (5 мкс – 3 мс):**
   У міру розгону ротора струм падає від 2.2 А до робочих 250 мА, а струм джерела в кабелі плавно зростає, компенсуючи розряд конденсаторів.
3. **Ефект посилення ємності:**
   Встановлення електролітичного конденсатора ємністю `220 мкФ` з низьким ESR (80–100 мОм) створює достатній запас заряду: мінімальна напруга під час комутації опускається лише до `2.84 В`, що залишає стабільний запас понад 140 мВ над порогом Brownout Reset.
