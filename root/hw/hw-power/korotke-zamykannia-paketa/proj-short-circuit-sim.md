# ⚙️ Чисельна симуляція перехідного процесу КЗ та розрахунок руйнування компонентів

Перехідний процес під час короткого замикання батарейного пакета описується нелінійною динамічною системою, де одночасно взаємодіють електромагнітна індуктивність монтажного контуру, температурне зростання електричного опору провідників, локальний тепловий розігрів напівпровідникового кристала MOSFET та час реакції апаратної відсічки BMS.

Ця симуляція моделює поведінку 16S літій-іонного батарейного пакета (60 В) під час прямого металевого короткого замикання (опір перемички 1 мОм), чисельно інтегруючи диференціальне рівняння струму за методом Ейлера з малим фіксованим кроком `dt = 0.1 мкс`. Вона відстежує накопичення інтегралу Джоуля `I²t`, миттєву потужність втрат на ключах BMS, температуру p-n переходу `T_junction` та розраховує амплітуду індуктивного сплеску напруги `V_spike` на стоку під час розмикання.

## Задача та фізична модель

Електричне коло описується рівнянням Кірхгофа для контуру з послідовною індуктивністю та змінним активним опором:

```
L_loop · (di / dt) + R_total(T) · i(t) = U_ocv
```

де:
- `U_ocv` — напруга розімкненого кола батареї (67.2 В для повністю зарядженого пакета 16S);
- `L_loop` — сумарна паразитна індуктивність дротів, шин, внутрішньої конструкції комірок та струмовимірювального шунта (типово 300–800 нГн);
- `R_total(T)` — сума активних опорів: внутрішній опір комірок `R_cells`, нікелевих шин `R_bus(T)`, шунта BMS `R_shunt` та активного опору відкритого/закриваючогося каналу польових транзисторів `R_dson(T_j)`.

### Особливості імпульсного теплового балансу кристала

У стаціонарному режимі температура транзистора визначається тепловим опором перехід-корпус `R_th_jc` (°C/Вт). Проте для імпульсів тривалістю менше 1 мілісекунди теплота фізично не встигає дійти до мідної підкладки корпусу чи радіатора — нагрівається виключно сам тонкий кремнієвий шар товщиною 50–100 мкм.

В адіабатичному наближенні зміна температури кристала описується формулою:

```
dT_j = (P_loss(t) / C_th_die) · dt = (i(t)² · R_dson(T_j) / C_th_die) · dt
```

де `C_th_die` — ефективна теплоємність активної зони кристала кремнію (Дж/°C).

### Фізика індуктивного сплеску при вимкненні

Під час форсованого закриття затворів похідна струму стає від'ємною (`di/dt < 0`), породжуючи ЕРС самоіндукції, що складається з напругою батареї:

```
V_ds_peak = U_ocv + L_loop · |di / dt|_turnoff
```

Якщо швидкість вимкнення занадто висока, амплітуда `V_ds_peak` перевищує напругу лавинного пробою транзистора `V_(BR)DSS`, руйнуючи кристал перенапругою.

## Чисельна дискретизація та стабільність

Рівняння струму є типовим представником жорстких диференціальних рівнянь (англ. *stiff ODE*), оскільки часова стала закриття затвора `toff` (1–5 мкс) значно менша за електромагнітну сталу контуру `L / R` (10–30 мкс). Для забезпечення числової стійкості без виникнення паразитної осциляції крок інтегрування `dt` повинен задовольняти умову Куранта-Фрідріхса:

```
dt << min(L_loop / R_total, mosfet_toff)
```

Вибір `dt = 0.1 мкс` (100 нс) гарантує високу точність розрахунку напруги сплеску та інтегралу `I²t`.

## Реалізація симулятора

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double v_ocv;            /* Напруга холостого ходу пакета, В */
    double l_loop;           /* Паразитна індуктивність контуру, Гн */
    double r_cells;          /* Внутрішній опір комірок, Ом */
    double r_bus_base;       /* Базовий опір шин та дротів за 20 °C, Ом */
    double r_dson_base;      /* Опір каналу всіх паралельних MOSFET за 25 °C, Ом */
    double r_shunt;          /* Опір струмовимірювального шунта, Ом */
    double r_fault;          /* Опір перемички КЗ, Ом */
    double i2t_fuse_rating;  /* Номінальний I²t розплавлення запобіжника, А²·с */
    double i2t_pcb_rating;   /* Граничний I²t доріжки друкованої плати, А²·с */
    double scp_delay_sec;    /* Затримка апаратного компаратора BMS, с */
    double mosfet_toff_sec;  /* Час спаду струму затвора при вимкненні, с */
    double c_th_die;         /* Теплоємність кристала кремнію MOSFET, Дж/°C */
    double t_j_max;          /* Максимально допустима температура кристала, °C */
} PackSimConfig;

typedef struct {
    double time_sec;
    double current;
    double i2t_accumulated;
    double t_junction;
    double v_ds_peak;
    bool fuse_blown;
    bool pcb_damaged;
    bool mosfet_destroyed;
    bool bms_tripped;
} SimResult;

SimResult run_short_circuit_simulation(const PackSimConfig *cfg, double dt, double t_max) {
    SimResult res = {
        .time_sec = 0.0,
        .current = 0.0,
        .i2t_accumulated = 0.0,
        .t_junction = 25.0,
        .v_ds_peak = cfg->v_ocv,
        .fuse_blown = false,
        .pcb_damaged = false,
        .mosfet_destroyed = false,
        .bms_tripped = false
    };

    double current = 0.0;
    double t = 0.0;
    bool bms_opening = false;
    double bms_open_progress = 0.0;

    while (t < t_max) {
        /* Температурний дрейф опору міді/нікелю та каналу MOSFET */
        double r_dson = cfg->r_dson_base * (1.0 + 0.005 * (res.t_junction - 25.0));
        double r_bus = cfg->r_bus_base * (1.0 + 0.00393 * (res.t_junction - 25.0));
        double r_active_dson = r_dson;

        /* Моделювання переходу в режим відсічки затвора */
        if (bms_opening) {
            bms_open_progress += dt / cfg->mosfet_toff_sec;
            if (bms_open_progress >= 1.0) {
                bms_open_progress = 1.0;
            }
            /* Зростання опору каналу при закритті ключа */
            r_active_dson = r_dson / (1.0 - 0.999 * bms_open_progress);
        }

        double r_total = cfg->r_cells + r_bus + r_active_dson + cfg->r_shunt + cfg->r_fault;

        /* Диференціальне рівняння di/dt = (V_ocv - i * R_total) / L */
        double di_dt = (cfg->v_ocv - current * r_total) / cfg->l_loop;
        current += di_dt * dt;
        if (current < 0.0) {
            current = 0.0;
        }

        /* Накопичення інтегралу Джоуля */
        res.i2t_accumulated += (current * current) * dt;

        /* Тепловий баланс кристала MOSFET */
        double p_loss_die = (current * current) * r_active_dson;
        res.t_junction += (p_loss_die / cfg->c_th_die) * dt;

        /* Перевірка критеріїв руйнування */
        if (res.t_junction >= cfg->t_j_max && !res.mosfet_destroyed) {
            res.mosfet_destroyed = true;
        }

        if (res.i2t_accumulated >= cfg->i2t_pcb_rating && !res.pcb_damaged) {
            res.pcb_damaged = true;
        }

        if (res.i2t_accumulated >= cfg->i2t_fuse_rating && !res.fuse_blown) {
            res.fuse_blown = true;
            break;
        }

        /* Спрацьовування апаратного захисту BMS */
        if (t >= cfg->scp_delay_sec && !res.bms_tripped && !bms_opening) {
            bms_opening = true;
            res.bms_tripped = true;
        }

        /* Фіксація індуктивного сплеску напруги під час вимкнення */
        if (bms_opening && di_dt < 0.0) {
            double v_spike = cfg->v_ocv + cfg->l_loop * fabs(di_dt);
            if (v_spike > res.v_ds_peak) {
                res.v_ds_peak = v_spike;
            }
        }

        if (bms_opening && bms_open_progress >= 1.0 && current < 1.0) {
            break;
        }

        t += dt;
    }

    res.time_sec = t;
    res.current = current;
    return res;
}

int main(void) {
    PackSimConfig cfg = {
        .v_ocv = 67.2,                  /* 16S Li-ion (4.2 В на комірку) */
        .l_loop = 600e-9,               /* 600 нГн індуктивність */
        .r_cells = 0.030,               /* 30 мОм пакет */
        .r_bus_base = 0.010,            /* 10 мОм шини */
        .r_dson_base = 0.002,           /* 2 мОм ключі BMS */
        .r_shunt = 0.001,               /* 1 мОм шунт */
        .r_fault = 0.001,               /* 1 мОм коротке замикання */
        .i2t_fuse_rating = 1200.0,      /* 1200 А²·с DC запобіжник */
        .i2t_pcb_rating = 2200.0,       /* 2200 А²·с доріжки плати */
        .scp_delay_sec = 25e-6,         /* 25 мкс реакція BMS SCP */
        .mosfet_toff_sec = 5e-6,        /* 5 мкс час закриття затвора */
        .c_th_die = 0.35,               /* 0.35 Дж/°C теплоємність кристалів */
        .t_j_max = 175.0                /* 175 °C межа кремнію */
    };

    SimResult r = run_short_circuit_simulation(&cfg, 0.1e-6, 500e-6);

    printf("=== РЕЗУЛЬТАТИ СИМУЛЯЦІЇ КЗ БАТАРЕЇ 16S (67.2 В) ===\n");
    printf("Час процесу:          %.2f мкс\n", r.time_sec * 1e6);
    printf("Накопичений I²t:      %.1f А²·с\n", r.i2t_accumulated);
    printf("Температура MOSFET:   %.1f °C\n", r.t_junction);
    printf("Піковий викид V_ds:   %.1f В\n", r.v_ds_peak);
    printf("BMS відсічка:         %s\n", r.bms_tripped ? "СПРАЦЮВАЛА" : "НІ");
    printf("Стан MOSFET:          %s\n", r.mosfet_destroyed ? "ПРОБИТО (ТЕПЛОВИЙ ВИБУХ)" : "ВЦІЛІЛИ");
    printf("Стан запобіжника:     %s\n", r.fuse_blown ? "ПЕРЕГОРІВ" : "ЦІЛИЙ");
    printf("Стан плати (PCB):     %s\n", r.pcb_damaged ? "ЗГОРІЛА" : "ВЦІЛІЛА");

    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <string_view>

struct PackSimConfig {
    double v_ocv{67.2};              // Напруга холостого ходу пакета, В
    double l_loop{600e-9};           // Паразитна індуктивність контуру, Гн
    double r_cells{0.030};           // Внутрішній опір комірок, Ом
    double r_bus_base{0.010};        // Базовий опір шин та дротів за 20 °C, Ом
    double r_dson_base{0.002};       // Опір каналу всіх паралельних MOSFET за 25 °C, Ом
    double r_shunt{0.001};           // Опір струмовимірювального шунта, Ом
    double r_fault{0.001};           // Опір перемички КЗ, Ом
    double i2t_fuse_rating{1200.0};  // Номінальний I²t розплавлення запобіжника, А²·с
    double i2t_pcb_rating{2200.0};   // Граничний I²t доріжки друкованої плати, А²·с
    double scp_delay_sec{25e-6};     // Затримка апаратного компаратора BMS, с
    double mosfet_toff_sec{5e-6};    // Час спаду струму затвора при вимкненні, с
    double c_th_die{0.35};           // Теплоємність кристала кремнію MOSFET, Дж/°C
    double t_j_max{175.0};           // Максимально допустима температура кристала, °C
};

struct SimResult {
    double time_sec{0.0};
    double current{0.0};
    double i2t_accumulated{0.0};
    double t_junction{25.0};
    double v_ds_peak{0.0};
    bool fuse_blown{false};
    bool pcb_damaged{false};
    bool mosfet_destroyed{false};
    bool bms_tripped{false};
};

class BatteryShortCircuitSimulator {
public:
    explicit constexpr BatteryShortCircuitSimulator(PackSimConfig config) noexcept
        : cfg_{config} {}

    [[nodiscard]] SimResult simulate(double dt = 0.1e-6, double t_max = 500e-6) const noexcept {
        SimResult res{};
        res.v_ds_peak = cfg_.v_ocv;

        double current = 0.0;
        double t = 0.0;
        bool bms_opening = false;
        double bms_open_progress = 0.0;

        while (t < t_max) {
            const double r_dson = cfg_.r_dson_base * (1.0 + 0.005 * (res.t_junction - 25.0));
            const double r_bus = cfg_.r_bus_base * (1.0 + 0.00393 * (res.t_junction - 25.0));
            double r_active_dson = r_dson;

            if (bms_opening) {
                bms_open_progress += dt / cfg_.mosfet_toff_sec;
                if (bms_open_progress >= 1.0) {
                    bms_open_progress = 1.0;
                }
                r_active_dson = r_dson / (1.0 - 0.999 * bms_open_progress);
            }

            const double r_total = cfg_.r_cells + r_bus + r_active_dson + cfg_.r_shunt + cfg_.r_fault;
            const double di_dt = (cfg_.v_ocv - current * r_total) / cfg_.l_loop;

            current += di_dt * dt;
            if (current < 0.0) {
                current = 0.0;
            }

            res.i2t_accumulated += (current * current) * dt;

            const double p_loss_die = (current * current) * r_active_dson;
            res.t_junction += (p_loss_die / cfg_.c_th_die) * dt;

            if (res.t_junction >= cfg_.t_j_max && !res.mosfet_destroyed) {
                res.mosfet_destroyed = true;
            }

            if (res.i2t_accumulated >= cfg_.i2t_pcb_rating && !res.pcb_damaged) {
                res.pcb_damaged = true;
            }

            if (res.i2t_accumulated >= cfg_.i2t_fuse_rating && !res.fuse_blown) {
                res.fuse_blown = true;
                break;
            }

            if (t >= cfg_.scp_delay_sec && !res.bms_tripped && !bms_opening) {
                bms_opening = true;
                res.bms_tripped = true;
            }

            if (bms_opening && di_dt < 0.0) {
                const double v_spike = cfg_.v_ocv + cfg_.l_loop * std::abs(di_dt);
                if (v_spike > res.v_ds_peak) {
                    res.v_ds_peak = v_spike;
                }
            }

            if (bms_opening && bms_open_progress >= 1.0 && current < 1.0) {
                break;
            }

            t += dt;
        }

        res.time_sec = t;
        res.current = current;
        return res;
    }

private:
    PackSimConfig cfg_;
};

int main() {
    constexpr PackSimConfig config{};
    const BatteryShortCircuitSimulator sim{config};
    const SimResult r = sim.simulate();

    std::cout << "=== РЕЗУЛЬТАТИ СИМУЛЯЦІЇ КЗ БАТАРЕЇ 16S (67.2 В) ===\n"
              << std::fixed << std::setprecision(2)
              << "Час процесу:          " << (r.time_sec * 1e6) << " мкс\n"
              << "Накопичений I²t:      " << r.i2t_accumulated << " А²·с\n"
              << "Температура MOSFET:   " << r.t_junction << " °C\n"
              << "Піковий викид V_ds:   " << r.v_ds_peak << " В\n"
              << "BMS відсічка:         " << (r.bms_tripped ? "СПРАЦЮВАЛА" : "НІ") << '\n'
              << "Стан MOSFET:          " << (r.mosfet_destroyed ? "ПРОБИТО (ТЕПЛОВИЙ ВИБУХ)" : "ВЦІЛІЛИ") << '\n'
              << "Стан запобіжника:     " << (r.fuse_blown ? "ПЕРЕГОРІВ" : "ЦІЛИЙ") << '\n'
              << "Стан плати (PCB):     " << (r.pcb_damaged ? "ЗГОРІЛА" : "ВЦІЛІЛА") << '\n';

    return 0;
}
```
:::

## Методика лабораторної верифікації моделі

Щоб перевірити розрахункові параметри симуляції на практиці без руйнування дорогого силового обладнання, застосовують випробувальний стенд зі зниженою напругою та імпульсним комутатором:

1. **Вимірювання паразитної індуктивності монтажу `L_loop`:**
   Батарейний пакет без хімічних комірок (замінений мідними перемичками) підключають до генератора імпульсів через калібрований плівковий конденсатор відомої ємності `C_test`. За частотою виникнення резонансних затухаючих коливань контуру `f_res` визначають точну індуктивність:

```
L_loop = 1 / (4 · π² · f_res² · C_test)
```

2. **Реєстрація аварійного струму:**
   Звичайні струмові кліщі Холла мають занадто вузьку смугу пропускання (типово до 100 кГц) і насичуються за швидких перехідних процесів. Для коректного захоплення фронту наростання струму `di/dt` застосовують **пояс Роговського** зі смугою від 20 МГц або низькоіндуктивний коаксіальний шунт (CVR — Coaxial Current Viewing Resistor) із власною індуктивністю менше 0.1 нГн.

## Інженерні пастки при відсічці КЗ

1. **Ефект Міллера та самовільне відкриття MOSFET при закритті:**
   Коли драйвер швидко тягне затвор униз, на стоку стрімко зростає напруга `dV_ds / dt`. Через прохідну ємність сток-затвор `C_gd` (ємність Міллера) в коло затвора впорскується струм зміщення:

```
i_gate = C_gd · (dV_ds / dt)
```

   Якщо опір розряду затвора в драйвері завеликий (наприклад, понад 5–10 Ом), цей струм створює на затворі падіння напруги, що піднімає потенціал вище порогової напруги відкриття `V_th` (2–4 В). Транзистор самовільно підвідкривається і заходить у лінійний режим активного нагріву за максимального струму КЗ, що призводить до миттєвого теплового вибуху кристала.

2. **Руйнівний сплеск `V_ds` від індуктивності `L_loop`:**
   Чим швидше BMS закриває транзистор (`toff` < 1 мкс), тим вища похідна `|di/dt|` і тим вища амплітуда перенапруги `V = L · |di/dt|`. Для 60 В пакета індуктивний сплеск легко перевищує 200–300 В, пробиваючи 80-вольтові або 100-вольтові MOSFET. Правильне інженерне рішення — **двоступеневе кероване закриття (Soft Turn-Off)** у комбінації з потужними двонаправленими TVS-діодами (супресорами) паралельно силовим ключам.

3. **Нерівномірний розподіл струму між паралельними ключами:**
   Коли у силовому каскаді встановлено 4–8 паралельних MOSFET, під час закриття транзистори з дещо меншою пороговою напругою `V_th` закриваються останніми. Увесь струм КЗ (понад 1000 А) на останні 500 нс концентрується в одному кристалі, викликаючи його локальне перегорання, після чого ланцюгово пробиває решту ключів. Для запобігання цьому затвори кожного транзистора розв'язують окремими симетричними резисторами.

4. **Вплив деградації комірок (Aging / SOH) на небезпеку КЗ:**
   З часом, у міру старіння акумуляторів, їхній внутрішній опір `R_cells` зростає у 2–3 рази. Парадоксально, але це призводить до **зменшення пікового струму КЗ**, що може зіграти злий жарт із захистом: струм може не досягти апаратного порогу спрацьовування швидкодіючого захисту SCP, і батарея перейде в тривалий режим глибокого перевантаження (OCP). При цьому всередині самої зношеної комірки виділяється значно більша частка енергії (`I² · R_cell`), що прискорює закипання електроліту та термічний розгін у деградованому сепараторі.
