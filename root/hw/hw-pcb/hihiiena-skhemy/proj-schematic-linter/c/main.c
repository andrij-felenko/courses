#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>

#define MAX_NAME_LEN    32
#define MAX_PINS        64
#define MAX_COMPONENTS  32
#define MAX_NETS        32
#define MAX_JUNCTIONS   32
#define MAX_ISSUES      64

typedef enum {
    SEVERITY_INFO,
    SEVERITY_WARNING,
    SEVERITY_ERROR
} IssueSeverity;

typedef enum {
    PIN_INPUT,
    PIN_OUTPUT,
    PIN_OPEN_DRAIN,
    PIN_POWER_IN,
    PIN_POWER_OUT,
    PIN_PASSIVE
} PinType;

typedef struct {
    char name[MAX_NAME_LEN];
    PinType type;
    int parent_comp_idx;
    int net_idx;
} Pin;

typedef struct {
    char refdes[MAX_NAME_LEN];
    char value_raw[MAX_NAME_LEN];
    double value_numeric;
    double voltage_rating;
    bool is_dnp;
    int pin_indices[16];
    int pin_count;
} Component;

typedef struct {
    char name[MAX_NAME_LEN];
    int pin_indices[MAX_PINS];
    int pin_count;
    double operating_voltage;
    bool is_power_rail;
} Net;

typedef struct {
    double x;
    double y;
    int connected_wires_count;
    char sheet[MAX_NAME_LEN];
} Junction;

typedef struct {
    IssueSeverity severity;
    char rule_code[16];
    char message[128];
} LintIssue;

typedef struct {
    Component components[MAX_COMPONENTS];
    int comp_count;
    Pin pins[MAX_PINS];
    int pin_count;
    Net nets[MAX_NETS];
    int net_count;
    Junction junctions[MAX_JUNCTIONS];
    int junction_count;
    LintIssue issues[MAX_ISSUES];
    int issue_count;
} SchematicDesign;

void init_design(SchematicDesign *d) {
    memset(d, 0, sizeof(SchematicDesign));
}

void add_issue(SchematicDesign *d, IssueSeverity sev, const char *code, const char *msg) {
    if (d->issue_count >= MAX_ISSUES) return;
    LintIssue *iss = &d->issues[d->issue_count++];
    iss->severity = sev;
    strncpy(iss->rule_code, code, sizeof(iss->rule_code) - 1);
    strncpy(iss->message, msg, sizeof(iss->message) - 1);
}

int add_component(SchematicDesign *d, const char *refdes, const char *val, double volt_rating) {
    if (d->comp_count >= MAX_COMPONENTS) return -1;
    int idx = d->comp_count++;
    Component *c = &d->components[idx];
    strncpy(c->refdes, refdes, MAX_NAME_LEN - 1);
    strncpy(c->value_raw, val, MAX_NAME_LEN - 1);
    c->voltage_rating = volt_rating;
    c->is_dnp = false;
    c->pin_count = 0;
    return idx;
}

int add_net(SchematicDesign *d, const char *name, double op_voltage, bool is_pwr) {
    if (d->net_count >= MAX_NETS) return -1;
    int idx = d->net_count++;
    Net *n = &d->nets[idx];
    strncpy(n->name, name, MAX_NAME_LEN - 1);
    n->operating_voltage = op_voltage;
    n->is_power_rail = is_pwr;
    n->pin_count = 0;
    return idx;
}

void connect_pin(SchematicDesign *d, int comp_idx, const char *pin_name, PinType type, int net_idx) {
    if (d->pin_count >= MAX_PINS || comp_idx < 0 || net_idx < 0) return;
    int p_idx = d->pin_count++;
    Pin *p = &d->pins[p_idx];
    strncpy(p->name, pin_name, MAX_NAME_LEN - 1);
    p->type = type;
    p->parent_comp_idx = comp_idx;
    p->net_idx = net_idx;

    Component *c = &d->components[comp_idx];
    c->pin_indices[c->pin_count++] = p_idx;

    Net *n = &d->nets[net_idx];
    n->pin_indices[n->pin_count++] = p_idx;
}

void add_junction(SchematicDesign *d, double x, double y, int wires, const char *sheet) {
    if (d->junction_count >= MAX_JUNCTIONS) return;
    Junction *j = &d->junctions[d->junction_count++];
    j->x = x;
    j->y = y;
    j->connected_wires_count = wires;
    strncpy(j->sheet, sheet, MAX_NAME_LEN - 1);
}

// ── ПЕРЕВІРКА 1: Детекція 4-сторонніх перехресть ─────────────────────────────
void check_4way_junctions(SchematicDesign *d) {
    for (int i = 0; i < d->junction_count; ++i) {
        Junction *j = &d->junctions[i];
        if (j->connected_wires_count >= 4) {
            char buf[128];
            snprintf(buf, sizeof(buf), "4-сторонній вузол на аркуші '%s' (X=%.1f, Y=%.1f). Замініть на зміщені Т-вузли!",
                     j->sheet, j->x, j->y);
            add_issue(d, SEVERITY_ERROR, "HYG-01-4WAY", buf);
        }
    }
}

// ── ПЕРЕВІРКА 2: Конфлікти драйверів та плаваючі входи ──────────────────────
void check_net_drivers(SchematicDesign *d) {
    for (int i = 0; i < d->net_count; ++i) {
        Net *n = &d->nets[i];
        int drivers_out = 0;
        int drivers_od = 0;
        int inputs_count = 0;
        int passives_count = 0;

        for (int p = 0; p < n->pin_count; ++p) {
            Pin *pin = &d->pins[n->pin_indices[p]];
            if (pin->type == PIN_OUTPUT || pin->type == PIN_POWER_OUT) drivers_out++;
            else if (pin->type == PIN_OPEN_DRAIN) drivers_od++;
            else if (pin->type == PIN_INPUT || pin->type == PIN_POWER_IN) inputs_count++;
            else if (pin->type == PIN_PASSIVE) passives_count++;
        }

        // Конфлікт виходів: більше 1 активного виходу без Open-Drain
        if (drivers_out > 1) {
            char buf[128];
            snprintf(buf, sizeof(buf), "Ланцюг '%s' має %d активних виходів Output. Коротке замикання драйверів!",
                     n->name, drivers_out);
            add_issue(d, SEVERITY_ERROR, "ERC-02-COLLISION", buf);
        }

        // Плаваючий вхід: є входи, але немає жодного драйвера і жодного пасивного компонента (підтяжки)
        if (inputs_count > 0 && drivers_out == 0 && drivers_od == 0 && passives_count == 0 && !n->is_power_rail) {
            char buf[128];
            snprintf(buf, sizeof(buf), "Ланцюг '%s' має %d входів, але не має джерела сигналу або підтяжки (Floating Input).",
                     n->name, inputs_count);
            add_issue(d, SEVERITY_WARNING, "ERC-03-FLOATING", buf);
        }

        // Поодинока висяча мітка (Single-pin net)
        if (n->pin_count == 1 && !n->is_power_rail) {
            char buf[128];
            snprintf(buf, sizeof(buf), "Ланцюг '%s' підключений лише до одного виводу. Можлива одруківка в мітці!",
                     n->name);
            add_issue(d, SEVERITY_WARNING, "HYG-04-SINGLEPIN", buf);
        }
    }
}

// ── ПЕРЕВІРКА 3: Запас напруги та синтаксис номіналів ────────────────────────
void check_components_hygiene(SchematicDesign *d) {
    for (int i = 0; i < d->comp_count; ++i) {
        Component *c = &d->components[i];
        if (c->is_dnp) continue;

        // Перевірка конденсаторів на DC-bias запас напруги
        if (c->refdes[0] == 'C') {
            for (int p = 0; p < c->pin_count; ++p) {
                Net *n = &d->nets[d->pins[c->pin_indices[p]].net_idx];
                if (n->is_power_rail && n->operating_voltage > 0.0) {
                    if (c->voltage_rating <= 0.0) {
                        char buf[128];
                        snprintf(buf, sizeof(buf), "Конденсатор %s (%s) на шині %.1fV не має вказаної робочої напруги!",
                                 c->refdes, c->value_raw, n->operating_voltage);
                        add_issue(d, SEVERITY_ERROR, "HYG-05-NOVOLD", buf);
                    } else if (c->voltage_rating < n->operating_voltage * 1.5) {
                        char buf[128];
                        snprintf(buf, sizeof(buf), "Конденсатор %s (номінал %.0fV) на шині %.1fV має недостатній запас напруги (<1.5x). Ризик DC-bias деградації ємності!",
                                 c->refdes, c->voltage_rating, n->operating_voltage);
                        add_issue(d, SEVERITY_WARNING, "HYG-06-DERATING", buf);
                    }
                }
            }
        }

        // Перевірка інженерного форматування (небезпечна крапка замість R-S-H)
        if (strchr(c->value_raw, '.') != NULL) {
            char buf[128];
            snprintf(buf, sizeof(buf), "Компонент %s: Номінал '%s' містить крапку. Рекомендовано синтаксис IEC (напр. '4k7', '0R1').",
                     c->refdes, c->value_raw);
            add_issue(d, SEVERITY_INFO, "HYG-07-DOTVALUE", buf);
        }
    }
}

void run_all_linter_checks(SchematicDesign *d) {
    check_4way_junctions(d);
    check_net_drivers(d);
    check_components_hygiene(d);
}

void print_linter_report(const SchematicDesign *d) {
    printf("====================================================================\n");
    printf("                  ЗВІТ СХЕМНОГО ЛІНТЕРА (C99)                       \n");
    printf("====================================================================\n");
    printf("Проаналізовано: %d компонентів, %d ланцюгів, %d вузлів.\n\n",
           d->comp_count, d->net_count, d->junction_count);

    if (d->issue_count == 0) {
        printf("[OK] Усі перевірки пройдено успішно. Дефектів не виявлено.\n");
        return;
    }

    for (int i = 0; i < d->issue_count; ++i) {
        const LintIssue *iss = &d->issues[i];
        const char *sev_str = "INFO";
        if (iss->severity == SEVERITY_WARNING) sev_str = "ПОПЕРЕДЖЕННЯ";
        else if (iss->severity == SEVERITY_ERROR) sev_str = "ПОМИЛКА";

        printf("[%s] [%s] %s\n", sev_str, iss->rule_code, iss->message);
    }
    printf("====================================================================\n");
    printf("Разом знайдено зауважень: %d\n", d->issue_count);
}

int main(void) {
    SchematicDesign design;
    init_design(&design);

    // Створюємо ланцюги живлення та сигналів
    int net_vcc12 = add_net(&design, "+12V", 12.0, true);
    int net_gnd   = add_net(&design, "GND", 0.0, true);
    int net_miso  = add_net(&design, "SPI_MISO", 3.3, false);
    int net_alert = add_net(&design, "IRQ_ALERT", 3.3, false);
    int net_typo  = add_net(&design, "SENSOR_DAT0", 3.3, false);

    // Додаємо компоненти
    int c1 = add_component(&design, "C101", "10u", 16.0); // 16V на лінії 12V -> Derating warning
    connect_pin(&design, c1, "1", PIN_PASSIVE, net_vcc12);
    connect_pin(&design, c1, "2", PIN_PASSIVE, net_gnd);

    int r1 = add_component(&design, "R101", "4.7k", 0.0); // Крапка в номіналі -> Info warning
    connect_pin(&design, r1, "1", PIN_PASSIVE, net_vcc12);
    connect_pin(&design, r1, "2", PIN_PASSIVE, net_miso);

    int u1 = add_component(&design, "U1", "STM32F4", 0.0);
    connect_pin(&design, u1, "PA6", PIN_OUTPUT, net_miso); // Вихід 1 на MISO
    connect_pin(&design, u1, "PB0", PIN_INPUT, net_alert); // Плаваючий вхід ALERT

    int u2 = add_component(&design, "U2", "ADC_DRIVER", 0.0);
    connect_pin(&design, u2, "SDO", PIN_OUTPUT, net_miso); // Вихід 2 на MISO -> Driver collision!
    connect_pin(&design, u2, "DATA", PIN_OUTPUT, net_typo); // Єдиний пін на net_typo -> Single pin warning!

    // Додаємо заборонений 4-сторонній вузол
    add_junction(&design, 125.0, 80.0, 4, "Power_Sheet.kicad_sch");

    // Запуск аудиту
    run_all_linter_checks(&design);
    print_linter_report(&design);

    return 0;
}
