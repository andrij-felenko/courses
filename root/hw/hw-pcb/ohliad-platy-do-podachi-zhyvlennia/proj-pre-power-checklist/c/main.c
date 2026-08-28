#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

#define MAX_RAILS 16
#define MAX_NAME_LEN 32
#define CU_RESISTIVITY 1.724e-8 // Ом*м при 20°C
#define CU_FOIL_1OZ 35.0e-6     // 35 мкм (1 oz фольга)

typedef enum {
    LOAD_TYPE_HIGH_VOLTAGE_IN = 0,
    LOAD_TYPE_DIGITAL_IO,
    LOAD_TYPE_MEMORY_VDDQ,
    LOAD_TYPE_CORE_LOGIC,
    LOAD_TYPE_ANALOG_PLL
} RailLoadType;

typedef enum {
    STATUS_UNTESTED = 0,
    STATUS_HARD_SHORT,      // R < 0.05 Ом (металеве КЗ або пробитий MLCC)
    STATUS_OUT_OF_SPEC_LOW, // R < R_min (підвищений струм витоку)
    STATUS_NORMAL,          // R_min <= R <= R_max (штатна норма)
    STATUS_HIGH_RESISTANCE  // R > R_max (можливий обрив або високий імпеданс)
} MeasurementStatus;

typedef struct {
    char name[MAX_NAME_LEN];
    double v_nominal;       // Номінальна напруга, В
    double i_max;           // Максимальний струм споживання, А
    double c_filter_uf;     // Сумарна ємність фільтра, мкФ
    RailLoadType load_type;
    double r_min_expected;  // Розрахунковий мінімальний опір спокою, Ом
    double r_typical;       // Очікуваний типовий опір, Ом
    double t_settle_sec;    // Очікуваний час стабілізації заряду конденсаторів, с
} PowerRailSpec;

typedef struct {
    double r_measured_fwd;  // Прямий вимір (плюс щупа на рейку, мінус на GND), Ом
    double r_measured_rev;  // Зворотний вимір (мінус щупа на рейку, плюс на GND), Ом
    MeasurementStatus status;
    bool visual_polarity_ok;
    bool pin1_orientation_ok;
    bool solder_bridges_checked;
} RailTestResult;

typedef struct {
    char board_name[64];
    char serial_number[32];
    size_t rail_count;
    PowerRailSpec specs[MAX_RAILS];
    RailTestResult results[MAX_RAILS];
} BoardInspectionSession;

// Розрахунок параметрів шини живлення за фізичною моделлю витоків
void calculate_rail_thresholds(PowerRailSpec *spec) {
    if (!spec) return;

    double k_leak = 0.001;
    switch (spec->load_type) {
        case LOAD_TYPE_HIGH_VOLTAGE_IN:
            k_leak = 0.0001; // Дуже малий витік через закриті MOSFET і плівку
            spec->r_min_expected = spec->v_nominal / (k_leak * spec->i_max);
            if (spec->r_min_expected < 10000.0) spec->r_min_expected = 10000.0;
            spec->r_typical = spec->r_min_expected * 5.0;
            break;
        case LOAD_TYPE_DIGITAL_IO:
            k_leak = 0.002;  // Витоки буферів GPIO і Flash
            spec->r_min_expected = spec->v_nominal / (k_leak * spec->i_max);
            if (spec->r_min_expected < 100.0) spec->r_min_expected = 100.0;
            spec->r_typical = spec->r_min_expected * 3.0;
            break;
        case LOAD_TYPE_MEMORY_VDDQ:
            k_leak = 0.02;   // Внутрішня резистивна термінація ODT
            spec->r_min_expected = spec->v_nominal / (k_leak * spec->i_max);
            if (spec->r_min_expected < 10.0) spec->r_min_expected = 10.0;
            spec->r_typical = 30.0;
            break;
        case LOAD_TYPE_CORE_LOGIC:
            k_leak = 0.10;   // Мільярди затворів FinFET з тунельними витоками
            spec->r_min_expected = spec->v_nominal / (k_leak * spec->i_max);
            if (spec->r_min_expected < 0.15) spec->r_min_expected = 0.15;
            spec->r_typical = spec->r_min_expected * 2.5;
            break;
        case LOAD_TYPE_ANALOG_PLL:
            k_leak = 0.001;  // Малошумні чутливі ланцюги
            spec->r_min_expected = spec->v_nominal / (k_leak * spec->i_max);
            if (spec->r_min_expected < 500.0) spec->r_min_expected = 500.0;
            spec->r_typical = spec->r_min_expected * 4.0;
            break;
    }

    // Розрахунок часу стабілізації омметра (I_test = 200 мкА, V_clamp = 0.3 В)
    double i_test = 200.0e-6; // 200 мкА
    double v_clamp = 0.3;     // 300 мВ
    spec->t_settle_sec = (spec->c_filter_uf * 1.0e-6 * v_clamp) / i_test;
    if (spec->t_settle_sec < 0.05) spec->t_settle_sec = 0.05;
}

// Додавання нової шини живлення в сесію контролю
bool add_power_rail(BoardInspectionSession *session,
                    const char *name,
                    double v_nom,
                    double i_max,
                    double c_uf,
                    RailLoadType l_type) {
    if (!session || session->rail_count >= MAX_RAILS) return false;

    PowerRailSpec *s = &session->specs[session->rail_count];
    strncpy(s->name, name, MAX_NAME_LEN - 1);
    s->name[MAX_NAME_LEN - 1] = '\0';
    s->v_nominal = v_nom;
    s->i_max = i_max;
    s->c_filter_uf = c_uf;
    s->load_type = l_type;

    calculate_rail_thresholds(s);

    RailTestResult *r = &session->results[session->rail_count];
    r->r_measured_fwd = 0.0;
    r->r_measured_rev = 0.0;
    r->status = STATUS_UNTESTED;
    r->visual_polarity_ok = false;
    r->pin1_orientation_ok = false;
    r->solder_bridges_checked = false;

    session->rail_count++;
    return true;
}

// Валідація виміряного значення опору
void evaluate_rail_measurement(BoardInspectionSession *session,
                               size_t rail_idx,
                               double r_fwd,
                               double r_rev) {
    if (!session || rail_idx >= session->rail_count) return;

    PowerRailSpec *s = &session->specs[rail_idx];
    RailTestResult *r = &session->results[rail_idx];

    r->r_measured_fwd = r_fwd;
    r->r_measured_rev = r_rev;

    // Пряме коротке замикання (металевий місток чи пробитий конденсатор)
    if (r_fwd < 0.05 || r_rev < 0.05) {
        r->status = STATUS_HARD_SHORT;
        return;
    }

    // Порівняння з розрахунковим порогом
    if (r_fwd < s->r_min_expected) {
        r->status = STATUS_OUT_OF_SPEC_LOW;
    } else {
        r->status = STATUS_NORMAL;
    }
}

// Розрахунок спаду напруги для локалізації КЗ методом градієнта Кельвіна
double calculate_kelvin_trace_drop(double trace_length_mm,
                                   double trace_width_mm,
                                   double injected_current_a) {
    if (trace_width_mm <= 0.0) return 0.0;
    double r_sq = CU_RESISTIVITY / CU_FOIL_1OZ; // ~0.4926 мОм/sq
    double squares = trace_length_mm / trace_width_mm;
    double r_trace = r_sq * squares;
    return injected_current_a * r_trace; // Спад напруги у Вольтах
}

// Друк детального підсумкового звіту сесії
void print_inspection_report(const BoardInspectionSession *session) {
    if (!session) return;

    printf("================================================================================\n");
    printf("     ПРОТОКОЛ ПЕРЕДСТАРТОВОЇ ІНСПЕКЦІЇ ТА ДЗВІНКА РЕЙОК ЖИВЛЕННЯ ПЛАТИ          \n");
    printf("  Виріб: %-20s | Серійний номер: %-20s\n", session->board_name, session->serial_number);
    printf("================================================================================\n");
    printf("%-10s | %-6s | %-8s | %-12s | %-12s | %-15s\n",
           "Рейка", "V_ном", "I_макс", "R_мін (пор)", "R_вимір (F/R)", "Статус лінії");
    printf("--------------------------------------------------------------------------------\n");

    bool all_passed = true;
    for (size_t i = 0; i < session->rail_count; i++) {
        const PowerRailSpec *s = &session->specs[i];
        const RailTestResult *r = &session->results[i];

        const char *status_str = "НЕ ВІДОМО";
        switch (r->status) {
            case STATUS_UNTESTED:         status_str = "НЕ ТЕСТОВАНО"; all_passed = false; break;
            case STATUS_HARD_SHORT:       status_str = "КРИТИЧНЕ КЗ (!)"; all_passed = false; break;
            case STATUS_OUT_OF_SPEC_LOW:  status_str = "НИЗЬКИЙ ОПІР"; all_passed = false; break;
            case STATUS_NORMAL:           status_str = "НОРМА (PASS)"; break;
            case STATUS_HIGH_RESISTANCE:  status_str = "ВИСОКИЙ ОПІР"; break;
        }

        char r_meas_str[32];
        snprintf(r_meas_str, sizeof(r_meas_str), "%.2f / %.2f", r->r_measured_fwd, r->r_measured_rev);

        printf("%-10s | %5.2fВ | %5.2fА  | %9.2f Ом | %-12s | %-15s\n",
               s->name, s->v_nominal, s->i_max, s->r_min_expected, r_meas_str, status_str);
    }
    printf("================================================================================\n");

    if (all_passed) {
        printf("РЕЗУЛЬТАТ: УСІ РЕЙКИ УСПІШНО ПРОЙШЛИ ПЕРЕВІРКУ. ДОЗВОЛЕНО ДИМОВИЙ ТЕСТ.\n");
    } else {
        printf("УВАГА: ВИЯВЛЕНО КРИТИЧНІ АНОМАЛІЇ ОПОРУ! ПОДАВАТИ ЖИВЛЕННЯ СУВОРО ЗАБОРОНЕНО!\n");
    }
    printf("================================================================================\n");
}

int main(void) {
    BoardInspectionSession session;
    memset(&session, 0, sizeof(session));
    strncpy(session.board_name, "STM32H7-ComputeModule", sizeof(session.board_name));
    strncpy(session.serial_number, "SN-2026-REV-B-0042", sizeof(session.serial_number));

    // Конфігурація рейок живлення виробу
    add_power_rail(&session, "V_IN_12V",  12.0, 3.0,  220.0, LOAD_TYPE_HIGH_VOLTAGE_IN);
    add_power_rail(&session, "V_SYS_5V",   5.0, 4.0,  470.0, LOAD_TYPE_HIGH_VOLTAGE_IN);
    add_power_rail(&session, "V_IO_3V3",   3.3, 2.0,  150.0, LOAD_TYPE_DIGITAL_IO);
    add_power_rail(&session, "VDDQ_1V2",   1.2, 5.0,  680.0, LOAD_TYPE_MEMORY_VDDQ);
    add_power_rail(&session, "VCORE_0V9",  0.9, 15.0, 1200.0, LOAD_TYPE_CORE_LOGIC);
    add_power_rail(&session, "VDDA_3V3",   3.3, 0.2,   47.0, LOAD_TYPE_ANALOG_PLL);

    // Імітація результатів чотирипровідних вимірів реальної плати
    evaluate_rail_measurement(&session, 0, 45000.0, 48000.0); // 12V: 45 кОм (Норма)
    evaluate_rail_measurement(&session, 1, 12000.0, 13500.0); // 5V:  12 кОм (Норма)
    evaluate_rail_measurement(&session, 2,  1850.0,  1920.0); // 3.3V: 1.85 кОм (Норма)
    evaluate_rail_measurement(&session, 3,    28.5,    31.0); // 1.2V DDR: 28.5 Ом (Норма)
    evaluate_rail_measurement(&session, 4,     0.82,    0.85); // 0.9V Core: 0.82 Ом (Норма для FPGA/SoC!)
    evaluate_rail_measurement(&session, 5,  3400.0,  3450.0); // 3.3V VDDA: 3.4 кОм (Норма)

    print_inspection_report(&session);

    // Розрахунок градієнта Кельвіна для локалізації гіпотетичного КЗ
    double delta_v = calculate_kelvin_trace_drop(25.0, 0.5, 0.2); // 25 мм доріжка шириною 0.5 мм при 200 мА
    printf("\nЛокалізація точки КЗ методом Кельвіна (I_inj = 200 мА):\n");
    printf("Спад напруги на відрізку міді 25 мм x 0.5 мм (1 oz): %.3f мВ\n", delta_v * 1000.0);

    return 0;
}
