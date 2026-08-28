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
