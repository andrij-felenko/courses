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
