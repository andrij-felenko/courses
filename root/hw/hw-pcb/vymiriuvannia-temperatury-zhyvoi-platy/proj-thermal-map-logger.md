# ⚙️ Модуль збору багатоточкових температурних профілів та розрахунку теплових градієнтів плати

Цей практичний модуль реалізує низькорівневу систему збору багатоточкових теплових профілів, радіометричної корекції неконтактних вимірів, оцінки внутрішньої температури напівпровідникових переходів `T_J` та чисельного розрахунку двовимірних просторових градієнтів температури `∇T` працюючої друкованої плати для завчасного виявлення теплових перевантажень і механічних напружень до настання апаратного збою.

Під час оживлення, налагодження та тривалих кліматичних випробувань електронних модулів із високою питомою густиною розсіюваної потужності — таких як багатофазні синхронні понижувальні перетворювачі DC-DC, силові мости керування безколекторними двигунами, ультракомпактні GaN-каскади та високопродуктивні обчислювальні процесори чи FPGA — виділення тепла зосереджується на мікроскопічних ділянках напівпровідникових кристалів площею від кількох квадратних міліметрів до кількох квадратних сантиметрів. Одночасна наявність сильно нагрітих силових ключів та відносно холодних масивів пасивних компонентів або роз'ємів створює на друкованій платі складне, динамічно змінюване двовимірне температурне поле.

Контроль лише однієї «найгарячішої точки» за допомогою портативного мультиметра чи невідкаліброваного пірометра принципово не здатен дати повної картини надійності виробу. По-перше, локальний перегрів кристала може розвиватися за частки секунди, випереджаючи нагрів зовнішнього корпусу мікросхеми. По-друге, різкий просторовий перепад температур між сусідніми ділянками плати генерує термомеханічні напруження зрізу в паяних з'єднаннях через суттєву розбіжність коефіцієнтів теплового розширення матеріалів. Даний програмно-апаратний модуль поєднує прямі виміри від масиву мікротермопар, цифрових шинних сенсорів та радіометричних тепловізійних каналів в єдину аналітичну систему реального часу.

## Метрологічні основи та математичні алгоритми аналізу теплового поля

Надійна система теплового профілювання працює з фізичними величинами, отриманими з різних фізичних джерел, кожне з яких має власні систематичні похибки, нелінійності та динамічні затримки.

### Поліноміальне перетворення термопар типу K за міжнародним стандартом NIST ITS-90

Термопара типу K (термоелектрична пара зі сплавів хромелю та алюмелю) є основним інструментом контактного вимірювання високих і динамічних температур на платах завдяки широкому діапазону (від -200 °C до +1350 °C), стійкості до окиснення та малій теплоємності мініатюрного спаю. Фізичний принцип термопари базується на термоелектричному ефекті Зеебека: у замкненому колі з двох різнорідних металів виникає термо-ЕРС, пропорційна різниці температур між гарячим спаєм (на платі) та холодним спаєм (на клемах вимірювального приладу).

Середня чутливість термопари типу K становить близько 41 мкВ/°C при кімнатній температурі. Проте коефіцієнт Зеебека має виражену нелінійність: при нагріванні від 0 °C до 500 °C він змінюється від 39.5 до 42.8 мкВ/°C. Використання простого лінійного масштабування призводить до неприпустимої систематичної похибки у 4–7 °C, що є критичним для перевірки теплових запасів напівпровідників.

Для досягнення прецизійної точності (похибка менше 0.1 °C) алгоритм реалізує стандартну компенсацію холодного спаю (Cold Junction Compensation, CJC) та повне поліноміальне наближення дев'ятого степеня за стандартом NIST ITS-90. Розрахунок складається з двох етапів:

1. Вимірювання температури опорного холодного спаю `T_cjc` за допомогою прецизійного напівпровідникового або платинового датчика, розташованого безпосередньо на ізотермічному клемнику вимірювального модуля, та розрахунок еквівалентної термо-ЕРС `V_cjc`:

```
V_cjc = S_cjc · T_cjc                                  [наближення ЕРС холодного спаю]
```

2. Додавання виміряної аналого-цифровим перетворювачем різниці потенціалів `V_th` та напруги `V_cjc` для отримання повної термо-ЕРС `V_total` відносно віртуального нуля 0 °C, після чого обчислюється поліном NIST:

```
V_total = V_th + V_cjc                                 [сумарна термо-ЕРС відносно 0 °C]
T_hot = d_0 + d_1·V + d_2·V² + d_3·V³ + ... + d_9·V⁹   [поліном 9-го степеня NIST ITS-90]
```

де значення коефіцієнтів `d_1` .. `d_9` строго фіксовані міжнародним стандартом для кожного діапазону температур.

### Радіометрична корекція випромінювання за законом Стефана–Больцмана

Безконтактні оптичні засоби (тепловізори довгохвильового інфрачервоного діапазону LWIR 8–14 мкм, пірометри) реєструють сумарний потік електромагнітного випромінювання `W_tot`, який потрапляє на чутливий елемент мікроболометра. Відповідно до закону випромінювання Стефана–Больцмана, густина власного теплового потоку ідеального чорного тіла пропорційна четвертому степеню його абсолютної термодинамічної температури: `W = σ · T⁴`, де `σ = 5.670374 · 10⁻⁸ Вт/(м²·К⁴)`.

Реальні конструкційні матеріали друкованої плати є сірими або селективними випромінювачами з коефіцієнтом випромінювання `ε` в діапазоні від 0 до 1. Поверхня з коефіцієнтом випромінювання `ε` не лише випромінює власне тепло з послабленням `ε · σ · T_obj⁴`, але й відбиває зовнішнє інфрачервоне випромінювання навколишнього середовища з часткою `(1 - ε)`:

```
W_tot = ε · σ · (T_obj)⁴ + (1 - ε) · σ · (T_refl)⁴      [сумарне випромінювання на датчику]
```

де `T_refl` — температура навколишніх поверхонь і освітлювальних приладів, випромінювання яких падає на плату та відбивається в об'єктив.

Якщо оптичний прилад налаштовано на усереднений коефіцієнт за замовчуванням (наприклад, `ε_cam = 0.95`), а вимірювання проводиться на відкритому металевому майданчику з низькою випромінювальною здатністю (паяний меніск із чистого припою SAC305 має `ε ≈ 0.08`, а полірована мідь `ε ≈ 0.04`), прилад зареєструє уявну температуру `T_apparent`, яка на 90–95% складатиметься з відбиття фону.

Програмний модуль виконує зворотне радіометричне перетворення, відновлюючи істинну термодинамічну температуру об'єкта `T_true`:

```
T_true = [ ( (T_apparent)⁴ - (1 - ε) · (T_refl)⁴ ) / ε ]^(1/4)  [радіометрична температура]
```

Для виключення невизначеності на досліджувану плату наносяться опорні мікромаркери з точно відомою випромінювальною здатністю (високотемпературний каптоновий скотч із `ε = 0.96` або матова чорна поліімідна фарба). Зіставивши покази камери на маркері та прилеглій ділянці, алгоритм автоматично калібрує фонову температуру `T_refl` і коригує теплову карту.

### Чисельний розрахунок просторових градієнтів температури та оцінка термомеханічних ризиків

Матеріали, з яких складається змонтована друкована плата, мають кардинально різні коефіцієнти лінійного теплового розширення (Coefficient of Thermal Expansion, CTE):

* Кремній напівпровідникового кристала: `CTE_Si ≈ 2.6 ppm/K` (10⁻⁶ 1/°C).
* Мідні провідники та полігони: `CTE_Cu ≈ 16.5–17.0 ppm/K`.
* Безсвинцевий припій SAC305 (Sn96.5Ag3.0Cu0.5): `CTE_solder ≈ 21.5–23.0 ppm/K`.
* Склотекстоліт FR-4: у площині шарів `CTE_xy ≈ 13–17 ppm/K`, перпендикулярно шарам `CTE_z ≈ 50–70 ppm/K`.

Коли на платі виникає крутий локальний градієнт температури (наприклад, кристал силового MOSFET нагрітий до 115 °C, а плата на відстані 5 мм від нього має температуру 45 °C), сусідні ділянки матеріалу розширюються з різною швидкістю. Виникає деформація згину та зсуву, що концентрується на контактних майданчиках і кутових паяних кульках мікросхем у корпусах BGA, QFN та WLCSP. При циклічному нагріванні та охолодженні ці напруження спричиняють втомне розтріскування безсвинцевого припою та розрив мідних перехідних отворів (microvias).

Для контролю цього явища модуль будує топологічну двовимірну сітку вимірювань і розраховує вектор просторового градієнта температури `∇T = (∂T/∂x, ∂T/∂y)` у кожному вузлі. На прямокутній сітці з кроком `Δx` та `Δy` частинні похідні апроксимуються центральними скінченними різницями другого порядку точності:

```
∂T/∂x ≈ (T(x + Δx, y) - T(x - Δx, y)) / (2 · Δx)        [швидкість зміни температури по X]
∂T/∂y ≈ (T(x, y + Δy) - T(x, y - Δy)) / (2 · Δy)        [швидкість зміни температури по Y]
|grad T| = sqrt( (∂T/∂x)² + (∂T/∂y)² )                  [модуль просторового градієнта]
```

Для крайових вузлів застосовуються спрямовані різниці першого порядку. Якщо розрахований модуль градієнта перевищує критичну межу (для стандартних промислових плат `1.5 °C/мм = 15 °C/см`), система фіксує попередження `WARN_GRADIENT`.

### Обробка сигналів резистивних давачів температури (RTD Pt100/Pt1000 та NTC)

Окрім термопар, система підтримує роботу з платиновими термоопорами (RTD) та напівпровідниковими терморезисторами (NTC), які монтуються у критичних вузлах для тривалого моніторингу:

1. **Платинові сенсори Pt100 / Pt1000:** мають практично лінійну залежність опору від температури, яка в діапазоні від 0 °C до +200 °C описується рівнянням Каллендара–Ван Дюзена:

```
R(T) = R_0 · (1 + A·T + B·T²)                          [рівняння Каллендара–Ван Дюзена]
```

де `R_0 = 100 Ом` (для Pt100) або `1000 Ом` (для Pt1000), `A = 3.9083 · 10⁻³ °C⁻¹`, `B = -5.775 · 10⁻⁷ °C⁻²`. Для усунення впливу опору вимірювальних дротів використовується 4-провідне підключення Кельвіна.

2. **Терморезистори з від'ємним ТКО (NTC):** використовуються для локального контролю завдяки високій чутливості (-3...-5 %/°C). Нелінійний опір апроксимується рівнянням Стейнхарта–Харта третього порядку:

```
1 / T_K = A_sh + B_sh · ln(R) + C_sh · (ln(R))³        [рівняння Стейнхарта–Харта]
```

де `T_K` — абсолютна температура в Кельвінах, а коефіцієнти `A_sh`, `B_sh`, `C_sh` визначаються калібруванням за трьома реперними температурними точками.

### Оцінка температури напівпровідникового кристала `T_J` за методикою JEDEC JESD51

Безпосередній монтаж контактного датчика всередину герметичного корпусу мікросхеми під час випробувань серійного зразка фізично неможливий. Вимірюваній величині доступна лише температура зовнішньої поверхні кришки `T_C` (Top Case) або температура плати на відстані 1 мм від виводів компонента `T_B` (Board).

Згідно зі стандартом JEDEC JESD51-2A, використання класичного теплового опору `θ_JA` (junction-to-ambient) для розрахунку температури кристала на реальній користувацькій платі дає хибні результати, оскільки `θ_JA` визначається на стандартизованій тестовій 4-шаровій платі фіксованого розміру (76.2 × 114.3 мм) у закритому боксі без сторонніх джерел тепла.

Для точного інженерного розрахунку на робочій платі стандарт запроваджує параметри теплової характеризації: `Ψ_JT` (Psi-JT, відносно верхньої точки корпусу) та `Ψ_JB` (Psi-JB, відносно площадки плати). Формула розрахунку істинної температури кристала `T_J` має вигляд:

```
T_J = T_C + Ψ_JT · P_diss                               [розрахунок через верх корпусу]
T_J = T_B + Ψ_JB · P_diss                               [розрахунок через площадку плати]
```

де `P_diss` — миттєва потужність теплових втрат компонента у ватах, яка обчислюється як добуток виміряного струму на падіння напруги або розраховується з ККД силового каскаду. Оскільки через верхню кришку корпусу пластикових корпусів QFN/DFN із нижнім металевим тепловідводом виходить лише 2–8% сумарного теплового потоку, величина `Ψ_JT` є дуже малою (зазвичай 0.5–2.0 °C/Вт). Це забезпечує високу точність відновлення `T_J` навіть за помірних похибок визначення `P_diss`.

### Цифрова фільтрація імпульсних завад комутації

Під час роботи потужних імпульсних стабілізаторів напруги на платі виникають швидкі перехідні процеси з фронтами `dU/dt > 20 В/нс` та `dI/dt > 5 А/нс`. Ці комутаційні завади індукують високі синфазні та диференціальні напруги у довгих провідниках термопар. 

Для захисту від фальшивих спрацьовувань модуль реалізує комбіновану фільтрацію:
* **Апаратне придушення:** диференціальний RC-фільтр низьких частот на вході АЦП (`R = 100 Ом`, `C_diff = 100 нФ`, `C_cm = 10 нФ`) із частотою зрізу близько 8 кГц.
* **Програмна фільтрація:** рекурсивний експоненційний фільтр ковзного середнього (IIR першого порядку) з коефіцієнтом згладжування `α = 0.2` та медіанне вікно на 5 відліків для відсікання одиночних імпульсних викидів.

### Методика покрокового проведення теплового стрес-тесту

Процес верифікації теплового режиму на робочій платі за допомогою розробленого модуля виконується за чотири послідовні етапи:

* **Етап 1: Ізотермічне базове калібрування.** За відсутності силового живлення плата витримується у термокамері за кімнатної температури протягом 15 хвилин. Перевіряється узгодженість усіх каналів (розбіжність показів термопар, цифрових датчиків та RTD не повинна перевищувати ±0.3 °C). Проводиться калібрування опорного значення `T_refl` для тепловізійного тракту.
* **Етап 2: Ступеневе навантаження.** Подається 25%, 50%, 75% та 100% номінального струму навантаження з інтервалом фіксації даних кожні 5 хвилин. Модуль фіксує динаміку росту температури та обчислює теплову постійну часу `τ_th` для кожного силового компонента.
* **Етап 3: Фіксація квазістаціонарного теплового поля.** Після виходу на плато теплової рівноваги (коли `dT/dt < 0.1 °C/хв` протягом 10 хвилин) модуль розраховує підсумкову матрицю градієнтів `∇T` та формує карту зон ризику за стандартом IPC-9701.
* **Етап 4: Стрес-тест із відмовою охолодження.** Імітується аварійна зупинка вентилятора примусового охолодження. Модуль веде безперервний моніторинг швидкості наростання температури `dT/dt`. При перевищенні порогу 5.0 °C/с або досягненні критичної температури кристала `T_J = 125 °C` система формує сигнал аварійного відключення силового живлення (Power Good / Shutdown).

## Програмна реалізація системи збору та аналізу

Нижче наведено дві повнофункціональні реалізації алгоритму: низькорівневий драйвер мовою C99 для систем реального часу та вбудованих мікроконтролерів без динамічної пам'яті, а також об'єктно-орієнтований аналітичний модуль мовою C++20 із суворою типізацією, семантикою переміщення та обробкою даних у стилі `constexpr`.

:::tabs
@tab C99
```c
/**
 * @file thermal_logger.c
 * @brief Модуль збору багатоточкових температурних профілів та аналізу градієнтів PCB.
 * Стандарт: C99. Повна відсутність динамічного виділення пам'яті (MISRA C compliant).
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define THERMAL_MAX_CHANNELS      16
#define THERMAL_GRID_ROWS         4
#define THERMAL_GRID_COLS         4
#define THERMAL_HISTORY_DEPTH     8

#define THERMAL_SAFE_GRADIENT_MAX 1.5f  /* 1.5 °C/мм = 15.0 °C/см — поріг механічного ризику */
#define THERMAL_MAX_RISE_RATE     5.0f  /* 5.0 °C/с — поріг теплової втечі або КЗ */

/** @brief Тип вимірювального датчика каналу */
typedef enum {
    SENSOR_TYPE_THERMOCOUPLE_K   = 0,
    SENSOR_TYPE_DIGITAL_IC       = 1,
    SENSOR_TYPE_LWIR_RADIOMETRIC = 2
} sensor_type_t;

/** @brief Прапорці стану та попереджень теплової системи */
typedef enum {
    THERMAL_STAT_OK               = 0,
    THERMAL_STAT_WARN_HOTSPOT     = (1 << 0),
    THERMAL_STAT_WARN_GRADIENT    = (1 << 1),
    THERMAL_STAT_WARN_RUNAWAY     = (1 << 2),
    THERMAL_STAT_ERR_SENSOR_FAULT = (1 << 3)
} thermal_status_flags_t;

/** @brief Конфігурація та поточний стан вимірювального каналу */
typedef struct {
    uint8_t channel_id;
    char name[24];
    sensor_type_t type;
    float pos_x_mm;
    float pos_y_mm;
    float emissivity;         /* Коефіцієнт випромінювання поверхні (0.02 .. 1.00) */
    float psi_jt;             /* JEDEC JESD51 параметр Psi-JT (°C/Вт) */
    float p_diss_w;           /* Потужність втрат у компоненті (Вт) */
    float t_crit_c;           /* Гранична температура напівпровідникового кристала */
    float current_temp_c;     /* Виміряна температура поверхні */
    float junction_temp_c;    /* Розрахована температура кристала T_J */
    float rate_of_rise_cps;   /* Перша похідна нагріву dT/dt (°C/с) */
    float history[THERMAL_HISTORY_DEPTH];
    uint8_t history_idx;
    bool is_active;
    bool fault_detected;
} thermal_channel_t;

/** @brief Контекст теплового моніторингу друкованої плати */
typedef struct {
    thermal_channel_t channels[THERMAL_MAX_CHANNELS];
    size_t channel_count;
    float ambient_temp_c;
    float reflected_temp_c;   /* Опорна температура для радіометрії Стефана-Больцмана */
    float max_board_temp_c;
    float max_junction_temp_c;
    float max_gradient_c_per_mm;
    uint32_t status_flags;
    uint32_t sample_index;
    float temp_grid[THERMAL_GRID_ROWS][THERMAL_GRID_COLS];
    float grid_pitch_x_mm;
    float grid_pitch_y_mm;
} thermal_monitor_t;

/**
 * @brief Прецизійне поліноміальне наближення NIST ITS-90 для термопари типу K.
 * @param v_mv Сумарна термо-ЕРС у мілівольтах відносно віртуального нуля 0 °C.
 * @return Розрахована температура гарячого спаю в °C.
 */
static float thermocouple_k_nist_eval(float v_mv) {
    /* Коефіцієнти NIST ITS-90 для діапазону 0 °C .. 500 °C */
    static const double d[10] = {
        0.0,
        2.508355e1,
        7.860106e-2,
        -2.503131e-1,
        8.315270e-2,
        -1.228034e-2,
        9.804036e-4,
        -4.413030e-5,
        1.057734e-6,
        -1.052755e-8
    };

    if (v_mv < -6.0f || v_mv > 55.0f) {
        return -999.0f; /* Обрив кола або некоректний вхідний сигнал */
    }

    double temp = 0.0;
    double v_pow = 1.0;
    for (int i = 1; i < 10; ++i) {
        v_pow *= (double)v_mv;
        temp += d[i] * v_pow;
    }
    return (float)temp;
}

/**
 * @brief Оцінка ЕРС холодного спаю для компенсації CJC.
 * @param t_cjc_c Температура клемного блоку в °C.
 * @return Термо-ЕРС у мілівольтах.
 */
static float thermocouple_k_cjc_emf(float t_cjc_c) {
    const float seebeck_nominal = 0.0405f; /* мВ/°C для діапазону 15..45 °C */
    return t_cjc_c * seebeck_nominal;
}

/**
 * @brief Радіометрична корекція оптичних показів за законом Стефана-Больцмана.
 * @param t_app_c Уявна температура з матриці тепловізора (°C).
 * @param emissivity Коефіцієнт випромінювання тестової зони.
 * @param t_refl_c Температура навколишніх відбиваючих об'єктів (°C).
 * @return Істинна відновлена температура поверхні (°C).
 */
static float radiometric_stefan_boltzmann_correct(float t_app_c, float emissivity, float t_refl_c) {
    if (emissivity < 0.02f) {
        emissivity = 0.02f;
    }

    float t_app_k = t_app_c + 273.15f;
    float t_refl_k = t_refl_c + 273.15f;

    float w_app = powf(t_app_k, 4.0f);
    float w_refl = powf(t_refl_k, 4.0f);

    float w_obj = (w_app - (1.0f - emissivity) * w_refl) / emissivity;
    if (w_obj <= 0.0f) {
        return t_refl_c;
    }

    return powf(w_obj, 0.25f) - 273.15f;
}

/**
 * @brief Ініціалізація структури теплового моніторингу.
 */
void thermal_monitor_init(thermal_monitor_t *mon, float ambient_c, float grid_dx_mm, float grid_dy_mm) {
    if (!mon) return;
    memset(mon, 0, sizeof(thermal_monitor_t));
    mon->ambient_temp_c = ambient_c;
    mon->reflected_temp_c = ambient_c;
    mon->grid_pitch_x_mm = grid_dx_mm;
    mon->grid_pitch_y_mm = grid_dy_mm;
}

/**
 * @brief Реєстрація нового каналу вимірювання на платі.
 */
bool thermal_monitor_add_channel(thermal_monitor_t *mon, const thermal_channel_t *ch) {
    if (!mon || !ch || mon->channel_count >= THERMAL_MAX_CHANNELS) {
        return false;
    }
    mon->channels[mon->channel_count] = *ch;
    mon->channels[mon->channel_count].channel_id = (uint8_t)mon->channel_count;
    mon->channels[mon->channel_count].is_active = true;
    mon->channel_count++;
    return true;
}

/**
 * @brief Обробка одного такту вимірювань для вказаного каналу.
 */
void thermal_monitor_process_sample(thermal_monitor_t *mon, size_t idx, float raw_val, float dt_sec) {
    if (!mon || idx >= mon->channel_count) return;
    thermal_channel_t *ch = &mon->channels[idx];
    if (!ch->is_active) return;

    float computed_t = 0.0f;

    switch (ch->type) {
        case SENSOR_TYPE_THERMOCOUPLE_K: {
            float v_cjc = thermocouple_k_cjc_emf(mon->ambient_temp_c);
            float v_total = raw_val + v_cjc;
            computed_t = thermocouple_k_nist_eval(v_total);
            if (computed_t < -100.0f) {
                ch->fault_detected = true;
                return;
            }
            break;
        }
        case SENSOR_TYPE_LWIR_RADIOMETRIC: {
            computed_t = radiometric_stefan_boltzmann_correct(raw_val, ch->emissivity, mon->reflected_temp_c);
            break;
        }
        case SENSOR_TYPE_DIGITAL_IC:
        default: {
            computed_t = raw_val;
            break;
        }
    }

    /* Оцінка похідної dT/dt через ковзне вікно */
    if (dt_sec > 0.001f && ch->current_temp_c > 0.0f) {
        ch->rate_of_rise_cps = (computed_t - ch->current_temp_c) / dt_sec;
    }

    ch->current_temp_c = computed_t;
    ch->history[ch->history_idx] = computed_t;
    ch->history_idx = (uint8_t)((ch->history_idx + 1) % THERMAL_HISTORY_DEPTH);

    /* Розрахунок кристала T_J за JESD51 */
    ch->junction_temp_c = ch->current_temp_c + (ch->psi_jt * ch->p_diss_w);
}

/**
 * @brief Оновлення просторового розподілу та чисельне диференціювання градієнтів.
 */
void thermal_monitor_compute_field(thermal_monitor_t *mon) {
    if (!mon) return;

    mon->status_flags = THERMAL_STAT_OK;
    mon->max_board_temp_c = -273.15f;
    mon->max_junction_temp_c = -273.15f;
    mon->max_gradient_c_per_mm = 0.0f;

    /* Скидання вузлів сітки до фонового значення */
    for (int r = 0; r < THERMAL_GRID_ROWS; ++r) {
        for (int c = 0; c < THERMAL_GRID_COLS; ++c) {
            mon->temp_grid[r][c] = mon->ambient_temp_c;
        }
    }

    /* Інтерполяція точок на топологічну сітку */
    for (size_t i = 0; i < mon->channel_count; ++i) {
        const thermal_channel_t *ch = &mon->channels[i];
        if (!ch->is_active || ch->fault_detected) continue;

        if (ch->current_temp_c > mon->max_board_temp_c) {
            mon->max_board_temp_c = ch->current_temp_c;
        }
        if (ch->junction_temp_c > mon->max_junction_temp_c) {
            mon->max_junction_temp_c = ch->junction_temp_c;
        }

        if (ch->junction_temp_c >= ch->t_crit_c) {
            mon->status_flags |= THERMAL_STAT_WARN_HOTSPOT;
        }
        if (ch->rate_of_rise_cps >= THERMAL_MAX_RISE_RATE) {
            mon->status_flags |= THERMAL_STAT_WARN_RUNAWAY;
        }

        int col = (int)(ch->pos_x_mm / mon->grid_pitch_x_mm);
        int row = (int)(ch->pos_y_mm / mon->grid_pitch_y_mm);
        if (row >= 0 && row < THERMAL_GRID_ROWS && col >= 0 && col < THERMAL_GRID_COLS) {
            mon->temp_grid[row][col] = ch->current_temp_c;
        }
    }

    /* Чисельний розрахунок градієнта |grad T| методом центральних різниць */
    for (int r = 0; r < THERMAL_GRID_ROWS; ++r) {
        for (int c = 0; c < THERMAL_GRID_COLS; ++c) {
            float dt_dx = 0.0f;
            float dt_dy = 0.0f;

            if (c > 0 && c < THERMAL_GRID_COLS - 1) {
                dt_dx = (mon->temp_grid[r][c + 1] - mon->temp_grid[r][c - 1]) / (2.0f * mon->grid_pitch_x_mm);
            } else if (c == 0 && THERMAL_GRID_COLS > 1) {
                dt_dx = (mon->temp_grid[r][1] - mon->temp_grid[r][0]) / mon->grid_pitch_x_mm;
            }

            if (r > 0 && r < THERMAL_GRID_ROWS - 1) {
                dt_dy = (mon->temp_grid[r + 1][c] - mon->temp_grid[r - 1][c]) / (2.0f * mon->grid_pitch_y_mm);
            } else if (r == 0 && THERMAL_GRID_ROWS > 1) {
                dt_dy = (mon->temp_grid[1][c] - mon->temp_grid[0][c]) / mon->grid_pitch_y_mm;
            }

            float grad = sqrtf(dt_dx * dt_dx + dt_dy * dt_dy);
            if (grad > mon->max_gradient_c_per_mm) {
                mon->max_gradient_c_per_mm = grad;
            }
        }
    }

    if (mon->max_gradient_c_per_mm >= THERMAL_SAFE_GRADIENT_MAX) {
        mon->status_flags |= THERMAL_STAT_WARN_GRADIENT;
    }

    mon->sample_index++;
}

/**
 * @brief Форматоване виведення телеметрії теплового стану плати.
 */
void thermal_monitor_print_summary(const thermal_monitor_t *mon) {
    if (!mon) return;

    printf("\n=== ПРОТОКОЛ ТЕПЛОВОГО МОНІТОРИНГУ ПЛАТИ [#%u] ===\n", (unsigned int)mon->sample_index);
    printf("Фон: %.1f °C | Макс T_Board: %.1f °C | Макс T_Junction: %.1f °C\n",
           mon->ambient_temp_c, mon->max_board_temp_c, mon->max_junction_temp_c);
    printf("Піковий просторовий градієнт: %.2f °C/мм (%.1f °C/см)\n",
           mon->max_gradient_c_per_mm, mon->max_gradient_c_per_mm * 10.0f);

    printf("Стан системи: [%s%s%s%s]\n",
           (mon->status_flags == 0) ? " НОРМА " : "",
           (mon->status_flags & THERMAL_STAT_WARN_HOTSPOT) ? " [ПЕРЕГРІВ КРИСТАЛА] " : "",
           (mon->status_flags & THERMAL_STAT_WARN_GRADIENT) ? " [НЕБЕЗПЕЧНИЙ ГРАДІЄНТ] " : "",
           (mon->status_flags & THERMAL_STAT_WARN_RUNAWAY) ? " [ТЕПЛОВИЙ РОЗГІН dT/dt] " : "");

    printf("--------------------------------------------------------------------------------\n");
    printf("ID | Контрольна точка     | Тип  | T_поверхні | T_Кристала | Швидк.dT/dt | Втрати P\n");
    printf("---+----------------------+------+------------+------------+-------------+---------\n");

    for (size_t i = 0; i < mon->channel_count; ++i) {
        const thermal_channel_t *ch = &mon->channels[i];
        const char *t_desc = (ch->type == SENSOR_TYPE_THERMOCOUPLE_K) ? "Терм.K" :
                             (ch->type == SENSOR_TYPE_LWIR_RADIOMETRIC) ? "LWIR  " : "Цифр. ";

        printf("%02u | %-20s | %s | %7.1f °C  | %8.1f °C  | %+6.2f °C/s | %4.2f Вт %s\n",
               (unsigned int)ch->channel_id, ch->name, t_desc,
               ch->current_temp_c, ch->junction_temp_c, ch->rate_of_rise_cps, ch->p_diss_w,
               (ch->junction_temp_c >= ch->t_crit_c) ? "(!)" : "   ");
    }
    printf("--------------------------------------------------------------------------------\n");
}
```
@tab C++20
```cpp
/**
 * @file thermal_logger.hpp
 * @brief Об'єктно-орієнтований аналітичний модуль теплового профілювання плати.
 * Стандарт: C++20 (strong typing, constexpr математика, std::span, std::expected).
 */

#pragma once

#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <string>
#include <string_view>
#include <cmath>
#include <algorithm>
#include <expected>
#include <iomanip>
#include <numbers>

namespace pcb_thermal {

enum class SensorType : uint8_t {
    ThermocoupleK,
    DigitalIC,
    LwirRadiometric
};

enum class ThermalAlert : uint32_t {
    None         = 0,
    HotspotWarn  = 1 << 0,
    GradientWarn = 1 << 1,
    RunawayWarn  = 1 << 2,
    SensorFault  = 1 << 3
};

[[nodiscard]] constexpr ThermalAlert operator|(ThermalAlert a, ThermalAlert b) noexcept {
    return static_cast<ThermalAlert>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

[[nodiscard]] constexpr bool has_flag(ThermalAlert flags, ThermalAlert mask) noexcept {
    return (static_cast<uint32_t>(flags) & static_cast<uint32_t>(mask)) != 0;
}

struct Point2D {
    float x_mm{0.0f};
    float y_mm{0.0f};
};

struct ChannelConfig {
    uint8_t id{0};
    std::string name;
    SensorType type{SensorType::DigitalIC};
    Point2D pos;
    float emissivity{0.95f};       ///< Випромінювальна здатність поверхні
    float psi_jt{1.2f};            ///< Параметр JESD51 Psi-JT (°C/Вт)
    float power_dissipation_w{0.0f}; ///< Потужність втрат компонента (Вт)
    float critical_temp_c{125.0f}; ///< Гранична температура кристала
};

struct ChannelState {
    float measured_temp_c{25.0f};
    float junction_temp_c{25.0f};
    float rate_of_rise_cps{0.0f};
    bool is_valid{true};
};

class NistPolynomialK {
public:
    /// Коефіцієнти NIST ITS-90 для діапазону 0 .. 500 °C
    static constexpr std::array<double, 10> kCoeffs = {
        0.0,
        2.508355e1,
        7.860106e-2,
        -2.503131e-1,
        8.315270e-2,
        -1.228034e-2,
        9.804036e-4,
        -4.413030e-5,
        1.057734e-6,
        -1.052755e-8
    };

    [[nodiscard]] static constexpr float voltage_to_temperature(float v_mv) noexcept {
        if (v_mv < -6.0f || v_mv > 55.0f) {
            return -999.0f;
        }
        double temp = 0.0;
        double v_pow = 1.0;
        for (size_t i = 1; i < kCoeffs.size(); ++i) {
            v_pow *= static_cast<double>(v_mv);
            temp += kCoeffs[i] * v_pow;
        }
        return static_cast<float>(temp);
    }

    [[nodiscard]] static constexpr float cold_junction_emf(float t_cjc_c) noexcept {
        constexpr float seebeck_k = 0.0405f; // мВ/°C
        return t_cjc_c * seebeck_k;
    }
};

class RadiometryEngine {
public:
    [[nodiscard]] static float correct_emissivity(float t_apparent_c, float emissivity, float t_refl_c) noexcept {
        const float eps = std::max(emissivity, 0.02f);
        const float t_app_k = t_apparent_c + 273.15f;
        const float t_refl_k = t_refl_c + 273.15f;

        const float w_app = std::pow(t_app_k, 4.0f);
        const float w_refl = std::pow(t_refl_k, 4.0f);

        const float w_obj = (w_app - (1.0f - eps) * w_refl) / eps;
        if (w_obj <= 0.0f) {
            return t_refl_c;
        }
        return std::pow(w_obj, 0.25f) - 273.15f;
    }
};

template <size_t Rows = 4, size_t Cols = 4>
class ThermalProfiler {
public:
    explicit ThermalProfiler(float ambient_c = 25.0f, float pitch_x = 10.0f, float pitch_y = 10.0f)
        : ambient_temp_c_(ambient_c), reflected_temp_c_(ambient_c),
          grid_pitch_x_mm_(pitch_x), grid_pitch_y_mm_(pitch_y) {}

    bool register_channel(const ChannelConfig& config) {
        if (configs_.size() >= 32) return false;
        configs_.push_back(config);
        states_.push_back(ChannelState{.measured_temp_c = ambient_temp_c_, .junction_temp_c = ambient_temp_c_});
        return true;
    }

    void update_measurement(size_t index, float raw_reading, float dt_seconds) noexcept {
        if (index >= configs_.size()) return;

        const auto& cfg = configs_[index];
        auto& st = states_[index];

        float computed_t = 0.0f;

        switch (cfg.type) {
            case SensorType::ThermocoupleK: {
                const float v_cjc = NistPolynomialK::cold_junction_emf(ambient_temp_c_);
                const float v_total = raw_reading + v_cjc;
                computed_t = NistPolynomialK::voltage_to_temperature(v_total);
                if (computed_t < -100.0f) {
                    st.is_valid = false;
                    return;
                }
                break;
            }
            case SensorType::LwirRadiometric: {
                computed_t = RadiometryEngine::correct_emissivity(raw_reading, cfg.emissivity, reflected_temp_c_);
                break;
            }
            case SensorType::DigitalIC:
            default: {
                computed_t = raw_reading;
                break;
            }
        }

        if (dt_seconds > 0.001f) {
            st.rate_of_rise_cps = (computed_t - st.measured_temp_c) / dt_seconds;
        }
        st.measured_temp_c = computed_t;
        st.junction_temp_c = computed_t + (cfg.psi_jt * cfg.power_dissipation_w);
        st.is_valid = true;
    }

    void evaluate_thermal_field() noexcept {
        alert_flags_ = ThermalAlert::None;
        max_board_temp_c_ = -273.15f;
        max_junction_temp_c_ = -273.15f;
        max_gradient_c_per_mm_ = 0.0f;

        for (auto& row : grid_) {
            row.fill(ambient_temp_c_);
        }

        for (size_t i = 0; i < configs_.size(); ++i) {
            const auto& cfg = configs_[i];
            const auto& st = states_[i];
            if (!st.is_valid) continue;

            max_board_temp_c_ = std::max(max_board_temp_c_, st.measured_temp_c);
            max_junction_temp_c_ = std::max(max_junction_temp_c_, st.junction_temp_c);

            if (st.junction_temp_c >= cfg.critical_temp_c) {
                alert_flags_ = alert_flags_ | ThermalAlert::HotspotWarn;
            }
            if (st.rate_of_rise_cps >= 5.0f) {
                alert_flags_ = alert_flags_ | ThermalAlert::RunawayWarn;
            }

            const int col = static_cast<int>(cfg.pos.x_mm / grid_pitch_x_mm_);
            const int row = static_cast<int>(cfg.pos.y_mm / grid_pitch_y_mm_);
            if (row >= 0 && row < static_cast<int>(Rows) && col >= 0 && col < static_cast<int>(Cols)) {
                grid_[row][col] = st.measured_temp_c;
            }
        }

        for (size_t r = 0; r < Rows; ++r) {
            for (size_t c = 0; c < Cols; ++c) {
                float dt_dx = 0.0f;
                float dt_dy = 0.0f;

                if (c > 0 && c < Cols - 1) {
                    dt_dx = (grid_[r][c + 1] - grid_[r][c - 1]) / (2.0f * grid_pitch_x_mm_);
                } else if (c == 0 && Cols > 1) {
                    dt_dx = (grid_[r][1] - grid_[r][0]) / grid_pitch_x_mm_;
                }

                if (r > 0 && r < Rows - 1) {
                    dt_dy = (grid_[r + 1][c] - grid_[r - 1][c]) / (2.0f * grid_pitch_y_mm_);
                } else if (r == 0 && Rows > 1) {
                    dt_dy = (grid_[1][c] - grid_[0][c]) / grid_pitch_y_mm_;
                }

                const float grad_mag = std::sqrt(dt_dx * dt_dx + dt_dy * dt_dy);
                max_gradient_c_per_mm_ = std::max(max_gradient_c_per_mm_, grad_mag);
            }
        }

        if (max_gradient_c_per_mm_ >= 1.5f) {
            alert_flags_ = alert_flags_ | ThermalAlert::GradientWarn;
        }

        sample_count_++;
    }

    void print_telemetry() const {
        std::cout << "\n=== [C++20] ТЕЛЕМЕТРІЯ ТЕПЛОВОГО ПОЛЯ PCB [# " << sample_count_ << "] ===\n"
                  << std::fixed << std::setprecision(1)
                  << "Фон T_amb: " << ambient_temp_c_ << " °C | "
                  << "Макс T_board: " << max_board_temp_c_ << " °C | "
                  << "Макс T_Junction: " << max_junction_temp_c_ << " °C\n"
                  << "Макс просторовий градієнт: " << std::setprecision(2)
                  << max_gradient_c_per_mm_ << " °C/мм (" << max_gradient_c_per_mm_ * 10.0f << " °C/см)\n"
                  << "Тривожні прапорці: " << static_cast<uint32_t>(alert_flags_) << "\n"
                  << "--------------------------------------------------------------------------------\n"
                  << "ID | Назва вузла         | T_вимір  | T_Junction | dT/dt    | Потужність\n"
                  << "---+---------------------+----------+------------+----------+-----------\n";

        for (size_t i = 0; i < configs_.size(); ++i) {
            const auto& cfg = configs_[i];
            const auto& st = states_[i];

            std::cout << std::setw(2) << std::setfill('0') << static_cast<int>(cfg.id) << " | "
                      << std::setfill(' ') << std::left << std::setw(19) << cfg.name << " | "
                      << std::right << std::fixed << std::setprecision(1)
                      << std::setw(6) << st.measured_temp_c << " °C | "
                      << std::setw(7) << st.junction_temp_c << " °C  | "
                      << std::showpos << std::setw(5) << st.rate_of_rise_cps << " °C/s | "
                      << std::noshowpos << std::setw(4) << cfg.power_dissipation_w << " Вт "
                      << ((st.junction_temp_c >= cfg.critical_temp_c) ? "(!)" : "   ") << "\n";
        }
        std::cout << "--------------------------------------------------------------------------------\n";
    }

private:
    float ambient_temp_c_{25.0f};
    float reflected_temp_c_{25.0f};
    float grid_pitch_x_mm_{10.0f};
    float grid_pitch_y_mm_{10.0f};
    float max_board_temp_c_{25.0f};
    float max_junction_temp_c_{25.0f};
    float max_gradient_c_per_mm_{0.0f};
    ThermalAlert alert_flags_{ThermalAlert::None};
    uint32_t sample_count_{0};

    std::vector<ChannelConfig> configs_;
    std::vector<ChannelState> states_;
    std::array<std::array<float, Cols>, Rows> grid_{};
};

} // namespace pcb_thermal
```
:::

## Інженерний аналіз та апаратні пастки теплових вимірів

Практичне застосування системи на стенді оживлення друкованих плат вимагає суворого дотримання метрологічних правил монтажу сенсорів та калібрування вимірювальних трактів.

### Пастка 1: Тепловідвідний ефект товстих провідників термопари (Thermal Sinking)

Якщо для контролю мініатюрного поверхневого компонента (наприклад, польового транзистора в корпусі DFN 3×3 мм або стабілізатора SOT-23) застосувати стандартну промислову термопару з провідниками калібру AWG 24 (діаметр жили 0.51 мм), виникає виражений ефект теплового стоку (Fin Effect). Металеві жили термопари мають високу теплопровідність і відводять значний тепловий потік від крихітної кришки корпусу у навколишнє повітря. 

В результаті виміряна температура виявляється заниженою на 12–25 °C відносно істинного значення. Для достовірних вимірів на SMD-платах обов'язково використовують виключно ультратонкі мікротермопари калібру AWG 36 (діаметр 0.127 мм) або AWG 40 (діаметр 0.08 мм) із приклеюванням кінчика спаю мікрокраплею теплопровідного епоксидного клею або цианоакрилату поверх шару високоефективної термопасти.

### Пастка 2: Помилки випромінювання на блискучих менісках припою та відкритій міді

Спроба оцінити температуру паяних з'єднань силових транзисторів за допомогою невідкаліброваного тепловізора призводить до критичних помилок. Чистий безсвинцевий припій SAC305 після оплавлення має коефіцієнт теплового випромінювання `ε ≈ 0.08`. Це означає, що 92% інфрачервоного потоку, що потрапляє в об'єктив камери від паяного шва, є відбиттям навколишніх предметів: стельових світильників, настільних ламп або тіла оператора.

Якщо температура припою становить реальні 95 °C, а кімнатні світильники нагріті до 30 °C, тепловізор із налаштуванням `ε = 0.95` покаже оманливі 35 °C. Інженер робить хибний висновок про нормальний тепловий режим, тоді як напівпровідниковий кристал всередині корпусу перебуває на межі незворотної деградації. Для усунення цієї помилки на всі контрольні металеві поверхні обов'язково наклеюють шматочки матової поліімідної стрічки (Kapton) або наносять калібрувальне матове графітове покриття з відомим `ε = 0.95–0.96`.

### Пастка 3: Гальванічні зв'язки та паразитні контури заземлення через термопари

При контактному вимірюванні на відкритих тепловідвідних майданчиках компонентів (наприклад, стоку польового транзистора первинної обмотки, який перебуває під імпульсною напругою 48 В із фронтами `dU/dt > 50 В/нс`) відкритий металевий спай термопари закорочує високовольтний вузол на вимірювальний тракт АЦП або спільну шину заземлення осцилографа. Це викликає миттєве вигорання вхідних каскадів перетворювача CJC (MAX31855/MCP9600) та створює потужні електромагнітні наводки, що повністю спотворюють результати вимірювань. 

Для вимірювань на вузлах, що перебувають під електричним потенціалом, спай термопари обов'язково електрично ізолюють тонкою плівкою каптонового скотчу завтовшки 25 мкм із нанесенням шару діелектричної теплопровідної пасти (на основі нітриду алюмінію AlN або оксиду цинку ZnO), або використовують гальванічно розв'язані вимірювальні модулі з оптичною ізоляцією каналів.

### Пастка 4: Термомеханічний відрив спаю термопари при нагріванні

Під час тривалого нагріву плати від кімнатної температури до +100 °C різниця коефіцієнтів теплового розширення мідних провідників термопари та матеріалу корпусу мікросхеми створює механічне зусилля зсуву. Якщо термопара зафіксована нееластичним компаундом або слабо натягнутим скотчем, спай мікроскопічно відривається від поверхні, утворюючи повітряний зазор усього в 10–20 мкм. Оскільки теплопровідність нерухомого повітря становить лише 0.026 Вт/(м·К), покази датчика падають на 20–40 °C нижче реальної температури компонента. 

Для усунення цієї пастки провідники термопари обов'язково фіксують із формуванням компенсаційної петлі (S-вигину) перед точкою контакту, що знімає механічне напруження розширення, а приклеювання виконують термостійким еластичним силіконовим клеєм або двокомпонентним епоксидом із мінеральним наповнювачем.

### Пастка 5: Вплив примусової конвекції на відкриті контактні датчики

При проведенні випробувань у системах із примусовим повітряним охолодженням вентилятори створюють турбулентні повітряні потоки зі швидкістю 1.5–5.0 м/с. Якщо кінчик термопари не занурений у теплопровідну краплю повністю або виступає над корпусом компонента, набігаючий потік холодного повітря інтенсивно охолоджує зовнішню частину спаю. 

У результаті термопара вимірює не температуру поверхні мікросхеми, а проміжну рівноважну точку між компонентом і холодним повітряним потоком (похибка заниження досягає 15–30%). Кожен контактний датчик у продувних корпусах повинен бути повністю закритий теплоізолюючим ковпачком зі спіненого силікону або захищений шаром поліімідного скотчу, що екранує спай від прямого повітряного обдування.

### Пастка 6: Теплова інерція датчиків під час коротких імпульсних навантажень

Під час імпульсних випробувань (наприклад, пусковий струм мотора або короткочасне блокування ротора тривалістю 100–500 мс) теплова потужність у кристалі польового транзистора підскакує в десятки разів. Власна теплова постійна часу спаю термопари AWG 36 становить близько 50–150 мс, а тепловий шлях від кристала крізь пластиковий корпус до датчика додає затримку у 200–800 мс. 

Спроба зареєструвати пікову температуру імпульсу контактним датчиком покаже лише згладжений низькоамплітудний сплеск. Для дослідження швидкоплинних перехідних теплових процесів (Transient Thermal Surge) обов'язково застосовують високошвидкісні радіометричні LWIR-камери з частотою кадрів 50–200 Гц або вимірюють падіння напруги на внутрішньому паразитному p-n переході діода транзистора (методика V_f body diode sensing), яка фіксує істинну температуру переходу з мікросекундною реакцією.
