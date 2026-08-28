# ⚙️ Аудит параметрів за даташитом перед виробництвом

Схемотехнічний аудит документації на компоненти — це систематична інженерна верифікація числових параметрів схеми за найгіршим випадком *(worst-case circuit analysis)* до трасування друкованої плати та запуску монтажу. Помилка у виборі номіналу через ігнорування зміщення постійною напругою, перегрів кристала чи неузгодженість логічних рівнів виявляються або під час першого диму в лабораторії, або у вигляді плаваючих збоїв у клієнта. Цей практикум містить алгоритм та програмний інструмент розрахунку критичних параметрів надійності: запасів завадостійкості, теплового навантаження кристала та ефективної ємності розв'язки.

## Задача аудиту

Перед затвердженням принципової схеми вузла на мікроконтролері з цифровою шиною та автономним живленням необхідно автоматизовано перевірити три ключові інженерні критерії:

1. **Запас завадостійкості цифрових рівнів** *(DC Noise Margins)* між виходом передавача та входом приймача:
   - Для високого логічного рівня: `N_MH = V_OH,min - V_IH,min`.
   - Для низького логічного рівня: `N_ML = V_IL,max - V_OL,max`.
   - Критерій: обидва запаси мають бути строго більшими за мінімально допустимий поріг завад у пристрої (зазвичай не менше 0.2–0.4 В). Недостатній запас призводить до того, що комутаційні шуми шини живлення або наведення від сусідніх сигнальних ліній спотворюють передачу даних.

2. **Ефективна ємність керамічного конденсатора** *(Effective MLCC Capacitance)*:
   - Зниження номіналу через зміщення постійною робочою напругою (DC-bias derating), виробничий допуск (tolerance) та температурне відхилення (temperature coefficient).
   - Критерій: ефективна ємність на робочій напрузі шини живлення `V_DD` має перевищувати мінімальну вимогу даташита на стабілізатор або вивід живлення мікроконтролера:
   ```
   C_effective = C_nominal · (1 - Tolerance) · k_DC_bias · k_temp
   ```
   Якщо ефективна ємність падає нижче критичної межі, лінійний стабілізатор або імпульсний перетворювач втрачає стійкість петлі зворотного зв'язку, генеруючи високочастотні пульсації на шині живлення.

3. **Температура напівпровідникового переходу** *(Junction Temperature, T_J)*:
   - Розрахунок за температурою довкілля `T_A`, розсіюваною потужністю `P_D` та тепловим опором перехід-середовище `θ_JA`:
   ```
   T_J = T_A + P_D · θ_JA
   ```
   - Критерій: `T_J` не повинен перевищувати рекомендований максимум `T_J,rec` (з обов'язковим урахуванням запасу дератингу не менше 20–25 °C до межі Absolute Maximum Ratings).

4. **Перевірка сумарного навантаження шини живлення** (`I_VDD_total`):
   - Порівняння суми вихідних струмів усіх одночасно активних виводів GPIO зі встановленою межею струму металізації кристала в розділі Absolute Maximum Ratings.

5. **Узгодження навантажувальної ємності кварцового резонатора** (`C_L`):
   - Розрахунок номіналу зовнішніх конденсаторів обв'язки кварцу `C_1` та `C_2` з урахуванням паразитної ємності монтажу друкованої плати `C_stray` (зазвичай 3–5 пФ):
   ```
   C_1 = C_2 = 2 · (C_L - C_stray)
   ```
   Невідповідність номіналу зміщує резонансну частоту генератора та може зірвати генерацію за низьких температур.

## Алгоритм перевірки

Алгоритм приймає структуровані паспортні дані компонентів, витягнуті з таблиць *Absolute Maximum Ratings*, *Recommended Operating Conditions* та *Electrical Characteristics*, виконує покроковий розрахунок найгіршого випадку та формує структурований звіт про придатність схемного рішення.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>

/* Структура паспортних логічних рівнів */
typedef struct {
    float v_oh_min; /* Мінімальна вихідна напруга лог. 1 (В) */
    float v_ol_max; /* Максимальна вихідна напруга лог. 0 (В) */
    float v_ih_min; /* Мінімальна вхідна напруга розпізнавання лог. 1 (В) */
    float v_il_max; /* Максимальна вхідна напруга розпізнавання лог. 0 (В) */
} LogicLevels;

/* Структура параметрів конденсатора розв'язки */
typedef struct {
    float nominal_uf;   /* Номінальна ємність (мкФ) */
    float tolerance_pct;/* Виробничий допуск (±%) */
    float dc_bias_derat;/* Коефіцієнт залишкової ємності під робочою напругою (0.0 .. 1.0) */
    float temp_derat;   /* Температурний коефіцієнт ємності (0.0 .. 1.0) */
    float min_req_uf;   /* Мінімально необхідна ємність за даташитом чипа (мкФ) */
} DecouplingCap;

/* Структура теплових параметрів чіпа */
typedef struct {
    float ambient_temp_c; /* Максимальна робоча температура середовища (°C) */
    float power_watts;    /* Розсіювана потужність (Вт) */
    float theta_ja;       /* Тепловий опір перехід-середовище (°C/Вт) */
    float tj_max_abs;     /* Гранична температура кристала за Absolute Maximum (°C) */
} ThermalProfile;

/* Структура струмового бюджету виводів */
typedef struct {
    float pin_current_ma;   /* Струм одного навантаженого виводу (мА) */
    int   active_pins_count;/* Кількість одночасно навантажених виводів */
    float core_current_ma;  /* Власне споживання ядра чипа (мА) */
    float max_vdd_limit_ma; /* Граничний струм шини VDD за даташитом (мА) */
} GpioCurrentBudget;

/* Перевірка логічних рівнів */
bool audit_logic_margins(const LogicLevels *tx, const LogicLevels *rx, float min_margin) {
    float nm_high = tx->v_oh_min - rx->v_ih_min;
    float nm_low  = rx->v_il_max - tx->v_ol_max;

    printf("[Аудит логіки] N_MH: %.2f В, N_ML: %.2f В (вимога >= %.2f В)\n",
           nm_high, nm_low, min_margin);

    if (nm_high < min_margin || nm_low < min_margin) {
        printf("  [ПОМИЛКА] Недостатній запас завадостійкості! Ризик збоїв зв'язку.\n");
        return false;
    }
    printf("  [OK] Логічні рівні сумісні з надійним запасом.\n");
    return true;
}

/* Перевірка ємності розв'язки з урахуванням DC-bias */
bool audit_decoupling(const DecouplingCap *cap) {
    float worst_case_nominal = cap->nominal_uf * (1.0f - (cap->tolerance_pct / 100.0f));
    float effective_c = worst_case_nominal * cap->dc_bias_derat * cap->temp_derat;

    printf("[Аудит розв'язки] Номінал: %.1f мкФ -> Ефективна ємність під напругою: %.2f мкФ (потрібно >= %.2f мкФ)\n",
           cap->nominal_uf, effective_c, cap->min_req_uf);

    if (effective_c < cap->min_req_uf) {
        printf("  [ПОМИЛКА] Реальна ємність впала нижче порогу стабільності чіпа!\n");
        return false;
    }
    printf("  [OK] Ефективна ємність відповідає вимогам даташита.\n");
    return true;
}

/* Перевірка теплового режиму кристала */
bool audit_thermal(const ThermalProfile *th, float safety_margin_c) {
    float tj_calculated = th->ambient_temp_c + (th->power_watts * th->theta_ja);
    float tj_allowed_limit = th->tj_max_abs - safety_margin_c;

    printf("[Аудит тепла] Розрахункова Tj: %.1f °C (Abs Max: %.1f °C, ліміт з запасом: %.1f °C)\n",
           tj_calculated, th->tj_max_abs, tj_allowed_limit);

    if (tj_calculated > tj_allowed_limit) {
        printf("  [ПОМИЛКА] Перегрів кристала! Ризик теплового пробою або деградації.\n");
        return false;
    }
    printf("  [OK] Температура кристала в межах інженерного запасу.\n");
    return true;
}

/* Перевірка струмового навантаження шини живлення */
bool audit_gpio_budget(const GpioCurrentBudget *budget) {
    float total_current = budget->core_current_ma + (budget->pin_current_ma * budget->active_pins_count);

    printf("[Аудит шини VDD] Розрахунковий струм: %.1f мА (ліміт даташита: %.1f мА)\n",
           total_current, budget->max_vdd_limit_ma);

    if (total_current > budget->max_vdd_limit_ma) {
        printf("  [ПОМИЛКА] Перевищено граничний струм металізації шини живлення кристала!\n");
        return false;
    }
    printf("  [OK] Сумарний струм шини живлення в безпечних межах.\n");
    return true;
}

int main(void) {
    /* Тест 1: 3.3 В вихід MCU керує входом 5 В трансивера */
    LogicLevels tx_mcu = { .v_oh_min = 2.9f, .v_ol_max = 0.4f, .v_ih_min = 2.3f, .v_il_max = 0.8f };
    LogicLevels rx_bus = { .v_oh_min = 4.2f, .v_ol_max = 0.5f, .v_ih_min = 3.5f, .v_il_max = 1.5f };

    /* Тест 2: Кераміка 10 мкФ 0402 X5R під напругою 3.3 В (залишається лише 32% ємності) */
    DecouplingCap ldo_cap = {
        .nominal_uf = 10.0f,
        .tolerance_pct = 20.0f,
        .dc_bias_derat = 0.32f,
        .temp_derat = 0.90f,
        .min_req_uf = 4.7f
    };

    /* Тест 3: LDO регулятор у корпусі SOT-23 на струмі 150 мА при перепаді 5V -> 3.3V */
    ThermalProfile ldo_thermal = {
        .ambient_temp_c = 55.0f,
        .power_watts = (5.0f - 3.3f) * 0.150f, /* 0.255 Вт */
        .theta_ja = 220.0f,
        .tj_max_abs = 125.0f
    };

    /* Тест 4: 12 світлодіодів по 15 мА на виводах MCU з лімітом VDD 150 мА */
    GpioCurrentBudget mcu_gpio = {
        .pin_current_ma = 15.0f,
        .active_pins_count = 12,
        .core_current_ma = 35.0f,
        .max_vdd_limit_ma = 150.0f
    };

    printf("=== АУДИТ ДАТАШИТА ТА СХЕМОТЕХНІЧНОГО РІШЕННЯ ===\n\n");
    audit_logic_margins(&tx_mcu, &rx_bus, 0.3f);
    printf("\n");
    audit_decoupling(&ldo_cap);
    printf("\n");
    audit_thermal(&ldo_thermal, 25.0f);
    printf("\n");
    audit_gpio_budget(&mcu_gpio);

    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <format>
#include <expected>

struct LogicLevels {
    float v_oh_min; /* Мінімальна вихідна напруга лог. 1 (В) */
    float v_ol_max; /* Максимальна вихідна напруга лог. 0 (В) */
    float v_ih_min; /* Мінімальна вхідна напруга розпізнавання лог. 1 (В) */
    float v_il_max; /* Максимальна вхідна напруга розпізнавання лог. 0 (В) */
};

struct DecouplingCap {
    float nominal_uf;   /* Номінальна ємність (мкФ) */
    float tolerance_pct;/* Виробничий допуск (±%) */
    float dc_bias_derat;/* Коефіцієнт залишкової ємності під напругою (0.0 .. 1.0) */
    float temp_derat;   /* Температурний коефіцієнт ємності (0.0 .. 1.0) */
    float min_req_uf;   /* Мінімально необхідна ємність за даташитом (мкФ) */
};

struct ThermalProfile {
    float ambient_temp_c; /* Робоча температура середовища (°C) */
    float power_watts;    /* Розсіювана потужність (Вт) */
    float theta_ja;       /* Тепловий опір перехід-середовище (°C/Вт) */
    float tj_max_abs;     /* Гранична температура кристала Abs Max (°C) */
};

struct GpioCurrentBudget {
    float pin_current_ma;   /* Струм одного навантаженого виводу (мА) */
    int   active_pins_count;/* Кількість одночасно навантажених виводів */
    float core_current_ma;  /* Власне споживання ядра чипа (мА) */
    float max_vdd_limit_ma; /* Граничний струм шини VDD за даташитом (мА) */
};

class ComponentAuditor {
public:
    static std::expected<void, std::string_view> check_logic_margins(
        const LogicLevels& tx, const LogicLevels& rx, float min_margin
    ) {
        float nm_high = tx.v_oh_min - rx.v_ih_min;
        float nm_low  = rx.v_il_max - tx.v_ol_max;

        std::cout << "[Аудит логіки] N_MH: " << nm_high << " В, N_ML: " << nm_low
                  << " В (вимога >= " << min_margin << " В)\n";

        if (nm_high < min_margin || nm_low < min_margin) {
            return std::unexpected("Недостатній запас завадостійкості логічних рівнів!");
        }
        return {};
    }

    static std::expected<void, std::string_view> check_decoupling(const DecouplingCap& cap) {
        float worst_case_nominal = cap.nominal_uf * (1.0f - (cap.tolerance_pct / 100.0f));
        float effective_c = worst_case_nominal * cap.dc_bias_derat * cap.temp_derat;

        std::cout << "[Аудит розв'язки] Номінал: " << cap.nominal_uf
                  << " мкФ -> Ефективна: " << effective_c
                  << " мкФ (потрібно >= " << cap.min_req_uf << " мкФ)\n";

        if (effective_c < cap.min_req_uf) {
            return std::unexpected("Ефективна ємність нижча за паспортний поріг стабільності!");
        }
        return {};
    }

    static std::expected<void, std::string_view> check_thermal(
        const ThermalProfile& th, float safety_margin_c
    ) {
        float tj_calculated = th.ambient_temp_c + (th.power_watts * th.theta_ja);
        float tj_allowed_limit = th.tj_max_abs - safety_margin_c;

        std::cout << "[Аудит тепла] Розрахункова Tj: " << tj_calculated
                  << " °C (ліміт з запасом: " << tj_allowed_limit << " °C)\n";

        if (tj_calculated > tj_allowed_limit) {
            return std::unexpected("Перегрів напівпровідникового переходу!");
        }
        return {};
    }

    static std::expected<void, std::string_view> check_gpio_budget(const GpioCurrentBudget& budget) {
        float total_current = budget.core_current_ma + (budget.pin_current_ma * budget.active_pins_count);

        std::cout << "[Аудит шини VDD] Розрахунковий струм: " << total_current
                  << " мА (ліміт даташита: " << budget.max_vdd_limit_ma << " мА)\n";

        if (total_current > budget.max_vdd_limit_ma) {
            return std::unexpected("Перевищено граничний струм металізації шини живлення кристала!");
        }
        return {};
    }
};

int main() {
    LogicLevels tx_mcu{ .v_oh_min = 2.9f, .v_ol_max = 0.4f, .v_ih_min = 2.3f, .v_il_max = 0.8f };
    LogicLevels rx_bus{ .v_oh_min = 4.2f, .v_ol_max = 0.5f, .v_ih_min = 3.5f, .v_il_max = 1.5f };

    DecouplingCap ldo_cap{
        .nominal_uf = 10.0f,
        .tolerance_pct = 20.0f,
        .dc_bias_derat = 0.32f,
        .temp_derat = 0.90f,
        .min_req_uf = 4.7f
    };

    ThermalProfile ldo_thermal{
        .ambient_temp_c = 55.0f,
        .power_watts = (5.0f - 3.3f) * 0.150f,
        .theta_ja = 220.0f,
        .tj_max_abs = 125.0f
    };

    GpioCurrentBudget mcu_gpio{
        .pin_current_ma = 15.0f,
        .active_pins_count = 12,
        .core_current_ma = 35.0f,
        .max_vdd_limit_ma = 150.0f
    };

    std::cout << "=== АУДИТ ДАТАШИТА ТА СХЕМОТЕХНІЧНОГО РІШЕННЯ ===\n\n";

    if (auto res = ComponentAuditor::check_logic_margins(tx_mcu, rx_bus, 0.3f); !res) {
        std::cout << "  [ПОМИЛКА] " << res.error() << "\n";
    } else {
        std::cout << "  [OK] Логічні рівні валідні.\n";
    }

    std::cout << "\n";
    if (auto res = ComponentAuditor::check_decoupling(ldo_cap); !res) {
        std::cout << "  [ПОМИЛКА] " << res.error() << "\n";
    } else {
        std::cout << "  [OK] Ємність розв'язки валідна.\n";
    }

    std::cout << "\n";
    if (auto res = ComponentAuditor::check_thermal(ldo_thermal, 25.0f); !res) {
        std::cout << "  [ПОМИЛКА] " << res.error() << "\n";
    } else {
        std::cout << "  [OK] Тепловий режим кристала в нормі.\n";
    }

    std::cout << "\n";
    if (auto res = ComponentAuditor::check_gpio_budget(mcu_gpio); !res) {
        std::cout << "  [ПОМИЛКА] " << res.error() << "\n";
    } else {
        std::cout << "  [OK] Навантаження шини живлення в нормі.\n";
    }

    return 0;
}
```
:::

## Типові підводні камені аудиту

1. **Неправильне припущення про сумісність 3.3 В виходу з 5 В входом**:
   - Мікроконтролер з живленням 3.3 В гарантує `V_OH,min = 2.9 В`.
   - Мікросхема логіки 5 В серії CMOS (наприклад, 74HC або класичний 5 В трансивер) вимагає на вході `V_IH,min = 0.7 · V_CC = 3.5 В`.
   - Запас `N_MH = 2.9 - 3.5 = -0.6 В` (від'ємний). Вхід потрапляє в заборонену зону, спричиняючи втрату пакетів або хаотичні спрацьовування. Потрібен транслятор рівнів або мікросхема з TTL-сумісним входом (серія 74HCT, де `V_IH,min = 2.0 В`).

2. **Недооцінка падіння ємності кераміки в малих корпусах**:
   - Конденсатор 10 мкФ типорозміру 0402 з діелектриком X5R під номінальною напругою 3.3 В має коефіцієнт дератингу близько 0.32, а з урахуванням допуску 20% та нагріву дає лише:
   ```
   10 мкФ · 0.80 · 0.32 · 0.90 = 2.30 мкФ
   ```
   - Якщо LDO-стабілізатор вимагає мінімум 4.7 мкФ для стійкості петлі зворотного зв'язку, схема самозбуджується і генерує високочастотну генерацію з просіданням вихідної напруги. Рішення — застосування більшого типорозміру (0805 чи 1206) або діелектрика X7R із вищою номінальною напругою (наприклад, на 25 В замість 6.3 В).

3. **Тепловий пробій лінійного стабілізатора у компактному корпусі**:
   - Корпус SOT-23-5 має тепловий опір `θ_JA ≈ 220 °C/Вт` на стандартній двошаровій платі.
   - За потужності розсіювання 0.255 Вт кристал нагрівається на `0.255 · 220 = 56.1 °C` вище температури середовища. За температури всередині закритого корпусу пристрою `T_A = 55 °C` температура кристала досягає `111.1 °C`, що небезпечно близько до `T_J,max = 125 °C` і не залишає обов'язкового 25-градусного запасу надійності.

4. **Паразитне живлення знеструмлених мікросхем через захисні діоди (Phantom Powering)**:
   - Якщо мікроконтролер вимикає живлення зовнішнього давача для економії батареї за допомогою польового транзистора в колі VDD, але залишає активними лінії зв'язку SPI (MOSI, SCK, CS на рівні 3.3 В), струм тече з виходів мікроконтролера через верхній вхідний захисний діод давача в його знеструмлену шину живлення.
   - Давач продовжує споживати струм через сигнальні лінії (до 5–15 мА), перегріваючи вхідний каскад і зводячи нанівець економію енергії у режимі сну.
   - Рішення аудиту: перед зняттям живлення з периферійного чипа всі підключені виводи мікроконтролера програмно перемикаються у стан високого імпедансу (High-Z / Input Floating) або на логічний нуль.

5. **Зрив генерації кварцового резонатора через помилку в ємності навантаження**:
   - Паспортна навантажувальна ємність кварцу `C_L` (наприклад, 12 пФ) — це не номінал конденсаторів на схемі. Вона задає послідовну ємність двох плечей плюс паразитна ємність трас:
   ```
   C_L = (C_1 · C_2) / (C_1 + C_2) + C_stray
   ```
   - За типової ємності трас `C_stray = 4 пФ` правильний номінал конденсаторів розраховується як `C_1 = C_2 = 2 · (12 - 4) = 16 пФ`.
   - Встановлення конденсаторів 12 пФ зміщує еквівалентну ємність до `12/2 + 4 = 10 пФ`, що викликає додатний зсув частоти генератора (до +50..+100 ppm) і може призвести до зриву старту генератора під час охолодження пристрою нижче 0 °C.
