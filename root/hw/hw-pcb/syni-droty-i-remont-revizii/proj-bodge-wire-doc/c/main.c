#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

#define MAX_STEPS 64
#define MAX_STR_LEN 64
#define PI 3.14159265358979323846
#define RHO_COPPER 1.72e-8

typedef enum {
    WIRE_AWG30 = 0,
    WIRE_AWG32,
    WIRE_AWG34,
    WIRE_AWG36,
    WIRE_AWG38,
    WIRE_COUNT
} WireGauge;

typedef struct {
    WireGauge gauge;
    const char *name;
    double diameter_mm;
    double max_current_a;
    double r_per_meter;
} WireSpec;

static const WireSpec WIRE_TABLE[WIRE_COUNT] = {
    {WIRE_AWG30, "AWG 30 (0.25mm Kynar)", 0.254, 0.85, 0.338},
    {WIRE_AWG32, "AWG 32 (0.20mm PTFE)",  0.203, 0.55, 0.531},
    {WIRE_AWG34, "AWG 34 (0.16mm Enamel)",0.160, 0.35, 0.855},
    {WIRE_AWG36, "AWG 36 (0.12mm Enamel)",0.127, 0.20, 1.360},
    {WIRE_AWG38, "AWG 38 (0.10mm Enamel)",0.101, 0.12, 2.130}
};

typedef enum {
    STEP_CUT = 0,
    STEP_JUMPER,
    STEP_PIN_LIFT,
    STEP_COMP_ADD
} StepType;

typedef enum {
    DOMAIN_POWER = 0,
    DOMAIN_SLOW_DIGITAL,
    DOMAIN_FAST_DIGITAL,
    DOMAIN_ANALOG
} SignalDomain;

typedef struct {
    StepType type;
    char id[16];
    char net_name[MAX_STR_LEN];
    SignalDomain domain;
    char loc_from[MAX_STR_LEN];
    char loc_to[MAX_STR_LEN];
    WireGauge wire;
    double length_mm;
    double height_above_gnd_mm;
    double current_ma;
    double nominal_voltage_v;
    char comp_val[32];
    char notes[MAX_STR_LEN];
} EcoStep;

typedef struct {
    char project_name[MAX_STR_LEN];
    char pcb_revision_from[16];
    char pcb_revision_to[16];
    EcoStep steps[MAX_STEPS];
    size_t step_count;
} EcoProject;

typedef struct {
    int errors;
    int warnings;
    double total_wire_len_mm[WIRE_COUNT];
    int total_cuts;
    int total_jumpers;
    int total_pin_lifts;
    int total_comps;
} ValidationReport;

void eco_project_init(EcoProject *proj, const char *name, const char *rev_from, const char *rev_to) {
    if (!proj) return;
    strncpy(proj->project_name, name, MAX_STR_LEN - 1);
    proj->project_name[MAX_STR_LEN - 1] = '\0';
    strncpy(proj->pcb_revision_from, rev_from, 15);
    proj->pcb_revision_from[15] = '\0';
    strncpy(proj->pcb_revision_to, rev_to, 15);
    proj->pcb_revision_to[15] = '\0';
    proj->step_count = 0;
}

bool eco_add_cut(EcoProject *proj, const char *id, const char *net, const char *loc, const char *notes) {
    if (!proj || proj->step_count >= MAX_STEPS) return false;
    EcoStep *s = &proj->steps[proj->step_count++];
    s->type = STEP_CUT;
    strncpy(s->id, id, 15);
    strncpy(s->net_name, net, MAX_STR_LEN - 1);
    strncpy(s->loc_from, loc, MAX_STR_LEN - 1);
    s->loc_to[0] = '\0';
    strncpy(s->notes, notes, MAX_STR_LEN - 1);
    return true;
}

bool eco_add_jumper(EcoProject *proj, const char *id, const char *net, SignalDomain domain,
                    const char *from, const char *to, WireGauge wire, double len_mm,
                    double h_gnd_mm, double current_ma, double v_nom, const char *notes) {
    if (!proj || proj->step_count >= MAX_STEPS) return false;
    EcoStep *s = &proj->steps[proj->step_count++];
    s->type = STEP_JUMPER;
    strncpy(s->id, id, 15);
    strncpy(s->net_name, net, MAX_STR_LEN - 1);
    s->domain = domain;
    strncpy(s->loc_from, from, MAX_STR_LEN - 1);
    strncpy(s->loc_to, to, MAX_STR_LEN - 1);
    s->wire = wire;
    s->length_mm = len_mm;
    s->height_above_gnd_mm = h_gnd_mm;
    s->current_ma = current_ma;
    s->nominal_voltage_v = v_nom;
    strncpy(s->notes, notes, MAX_STR_LEN - 1);
    return true;
}

bool eco_add_pin_lift(EcoProject *proj, const char *id, const char *net, const char *ic_pin, const char *notes) {
    if (!proj || proj->step_count >= MAX_STEPS) return false;
    EcoStep *s = &proj->steps[proj->step_count++];
    s->type = STEP_PIN_LIFT;
    strncpy(s->id, id, 15);
    strncpy(s->net_name, net, MAX_STR_LEN - 1);
    strncpy(s->loc_from, ic_pin, MAX_STR_LEN - 1);
    s->loc_to[0] = '\0';
    strncpy(s->notes, notes, MAX_STR_LEN - 1);
    return true;
}

bool eco_add_comp(EcoProject *proj, const char *id, const char *net, const char *comp_val,
                  const char *from, const char *to, const char *notes) {
    if (!proj || proj->step_count >= MAX_STEPS) return false;
    EcoStep *s = &proj->steps[proj->step_count++];
    s->type = STEP_COMP_ADD;
    strncpy(s->id, id, 15);
    strncpy(s->net_name, net, MAX_STR_LEN - 1);
    strncpy(s->comp_val, comp_val, 31);
    strncpy(s->loc_from, from, MAX_STR_LEN - 1);
    strncpy(s->loc_to, to, MAX_STR_LEN - 1);
    strncpy(s->notes, notes, MAX_STR_LEN - 1);
    return true;
}

double calc_loop_inductance_nh(double len_mm, double wire_dia_mm, double h_gnd_mm) {
    if (wire_dia_mm <= 0.0 || h_gnd_mm <= 0.0 || len_mm <= 0.0) return 0.0;
    double ratio = (4.0 * h_gnd_mm) / wire_dia_mm;
    if (ratio <= 1.0) ratio = 1.05;
    double l_per_meter = 2.0e-7 * log(ratio);
    return (l_per_meter * (len_mm / 1000.0)) * 1.0e9;
}

ValidationReport eco_validate_and_analyze(const EcoProject *proj) {
    ValidationReport rep;
    memset(&rep, 0, sizeof(rep));
    if (!proj) return rep;

    for (size_t i = 0; i < proj->step_count; ++i) {
        const EcoStep *s = &proj->steps[i];
        switch (s->type) {
            case STEP_CUT:
                rep.total_cuts++;
                break;
            case STEP_PIN_LIFT:
                rep.total_pin_lifts++;
                break;
            case STEP_COMP_ADD:
                rep.total_comps++;
                break;
            case STEP_JUMPER: {
                rep.total_jumpers++;
                if (s->wire < WIRE_COUNT) {
                    rep.total_wire_len_mm[s->wire] += s->length_mm;
                    const WireSpec *ws = &WIRE_TABLE[s->wire];
                    double current_a = s->current_ma / 1000.0;

                    if (current_a > ws->max_current_a) {
                        rep.errors++;
                        printf("[ERROR] %s: Струм %.2fA перевищує ліміт %.2fA для %s!\n",
                               s->id, current_a, ws->max_current_a, ws->name);
                    }

                    if (s->nominal_voltage_v > 0.0) {
                        double r_total = ws->r_per_meter * (s->length_mm / 1000.0);
                        double v_drop = current_a * r_total;
                        double drop_pct = (v_drop / s->nominal_voltage_v) * 100.0;
                        if (drop_pct > 2.0) {
                            rep.warnings++;
                            printf("[WARN] %s: Падіння напруги %.1f%% (%.3fV) на сітці %s > 2.0%%\n",
                                   s->id, drop_pct, v_drop, s->net_name);
                        }
                    }

                    if (s->domain == DOMAIN_FAST_DIGITAL && s->height_above_gnd_mm > 1.0) {
                        double l_nh = calc_loop_inductance_nh(s->length_mm, ws->diameter_mm, s->height_above_gnd_mm);
                        rep.warnings++;
                        printf("[WARN] %s: Швидкісна сітка %s має високу індуктивність контуру %.1fnH (h=%.1fmm)!\n",
                               s->id, s->net_name, l_nh, s->height_above_gnd_mm);
                    }
                }
                break;
            }
        }
    }
    return rep;
}

void eco_print_runsheet_markdown(const EcoProject *proj, const ValidationReport *rep) {
    if (!proj) return;
    printf("\n# Технологічна карта доопрацювання ECO: %s\n", proj->project_name);
    printf("**Перехід ревізій:** %s -> %s\n\n", proj->pcb_revision_from, proj->pcb_revision_to);

    printf("## 1. Специфікація матеріалів модифікації (BOM)\n\n");
    printf("| Матеріал / Калібр | Загальна довжина / Кількість | Призначення |\n");
    printf("|---|---|---|\n");
    for (int w = 0; w < WIRE_COUNT; ++w) {
        if (rep->total_wire_len_mm[w] > 0.0) {
            printf("| %s | %.1f мм (%.1f см) | Монтажні перемички |\n",
                   WIRE_TABLE[w].name, rep->total_wire_len_mm[w], rep->total_wire_len_mm[w] / 10.0);
        }
    }
    printf("| УФ-маска рідка | %d точок герметизації | Захист різів і фіксація |\n",
           rep->total_cuts + rep->total_jumpers * 2);
    printf("| Каптоновий скотч | За потребою | Тимчасове утримання трас |\n\n");

    printf("## 2. Покрокова інструкція монтажника (Rework Run-Sheet)\n\n");
    printf("| Крок | Дія | Локація / Від | Куди | Параметри / Провід | Примітки |\n");
    printf("|---|---|---|---|---|---|\n");

    for (size_t i = 0; i < proj->step_count; ++i) {
        const EcoStep *s = &proj->steps[i];
        switch (s->type) {
            case STEP_CUT:
                printf("| %s | **CUT (Різ)** | %s | — | IPC-7721 V-Cut 1.0mm | %s |\n",
                       s->id, s->loc_from, s->notes);
                break;
            case STEP_PIN_LIFT:
                printf("| %s | **PIN LIFT** | %s | — | Відгин ніжки 30° | %s |\n",
                       s->id, s->loc_from, s->notes);
                break;
            case STEP_COMP_ADD:
                printf("| %s | **COMP ADD** | %s | %s | %s (Tombstone) | %s |\n",
                       s->id, s->loc_from, s->loc_to, s->comp_val, s->notes);
                break;
            case STEP_JUMPER: {
                const WireSpec *ws = &WIRE_TABLE[s->wire];
                printf("| %s | **JUMPER** | %s | %s | %s, L=%.0fмм | %s |\n",
                       s->id, s->loc_from, s->loc_to, ws->name, s->length_mm, s->notes);
                break;
            }
        }
    }

    printf("\n## 3. Чекліст контролю та верифікації ВТК\n\n");
    for (size_t i = 0; i < proj->step_count; ++i) {
        const EcoStep *s = &proj->steps[i];
        if (s->type == STEP_CUT) {
            printf("- [ ] **%s**: Перевірити опір ізоляції розрізу на %s (R > 10 МОм, КЗ на GND відсутнє).\n",
                   s->id, s->loc_from);
        } else if (s->type == STEP_JUMPER) {
            printf("- [ ] **%s**: Продзвонити ланцюг %s (%s -> %s), R < 0.5 Ом, фіксація УФ-маскою.\n",
                   s->id, s->net_name, s->loc_from, s->loc_to);
        } else if (s->type == STEP_COMP_ADD) {
            printf("- [ ] **%s**: Контроль номіналу %s між %s та %s під мікроскопом.\n",
                   s->id, s->comp_val, s->loc_from, s->loc_to);
        }
    }
}

int main(void) {
    EcoProject proj;
    eco_project_init(&proj, "IoT Sensor Hub Telemetry Node", "Rev A", "Rev A.1");

    eco_add_cut(&proj, "CUT-01", "UART1_TX", "U3.Pin4 (L1 Trace near R12)", "Подвійний V-кут, розрив TX");
    eco_add_cut(&proj, "CUT-02", "UART1_RX", "U3.Pin5 (L1 Trace near R13)", "Подвійний V-кут, розрив RX");
    eco_add_pin_lift(&proj, "LIFT-01", "MCU_NRST", "U1.Pin7 (NRST)", "Підняти вивід для додавання підтяжки");

    eco_add_comp(&proj, "ADD-R1", "MCU_NRST_PU", "10k 0402", "U1.Pin7", "C12.Pad1 (3.3V)", "Підтягуючий резистор");

    eco_add_jumper(&proj, "JUMP-01", "UART1_SWAP_TX", DOMAIN_SLOW_DIGITAL,
                   "U3.Pin4", "U1.Pin12 (MCU_RX)", WIRE_AWG34, 35.0, 0.3, 15.0, 3.3, "Фіксація до плати маскою");
    eco_add_jumper(&proj, "JUMP-02", "UART1_SWAP_RX", DOMAIN_SLOW_DIGITAL,
                   "U3.Pin5", "U1.Pin11 (MCU_TX)", WIRE_AWG34, 35.0, 0.3, 15.0, 3.3, "Фіксація до плати маскою");
    eco_add_jumper(&proj, "JUMP-03", "VCC_RADIO_3V3", DOMAIN_POWER,
                   "C5.Pad1 (+3.3V)", "U8.Pin1 (VCC_RF)", WIRE_AWG30, 80.0, 0.2, 450.0, 3.3, "Силове живлення RF");
    eco_add_jumper(&proj, "JUMP-04", "SPI_CLK_FAST", DOMAIN_FAST_DIGITAL,
                   "U1.Pin24", "U4.Pin6", WIRE_AWG36, 45.0, 8.0, 20.0, 3.3, "Помилка монтажу: піднятий у повітря");

    printf("=== ВАЛІДАЦІЯ ТА РОЗРАХУНОК ECO ===\n");
    ValidationReport rep = eco_validate_and_analyze(&proj);
    printf("Валідацію завершено: помилок = %d, попереджень = %d\n", rep.errors, rep.warnings);

    eco_print_runsheet_markdown(&proj, &rep);
    return 0;
}
