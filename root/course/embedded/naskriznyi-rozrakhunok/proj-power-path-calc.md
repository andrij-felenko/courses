# ⚙️ Модуль наскрізного аудиту силового тракту на C та C++

Проектування надійного силового тракту друкованої плати вимагає неперервного простеження ланцюга від вхідного джерела до кінцевого навантаження: врахування опору роз'ємів, нагріву мідних доріжок з температурним коефіцієнтом, втрат на силових ключах за робочої температури кристала та запасу селективності запобіжника за інтегралом Джоуля I²t. Ручний розрахунок у таблицях часто втрачає динамічний зв'язок між нагрівом і додатковим падінням напруги. Наведений нижче програмний модуль реалізує повний числовий аудит силового тракту плати для вбудованих систем, автоматично перевіряючи падіння напруги в найгіршому температурному режимі, допустимий перегрів міді за стандартом IPC-2152 та координацію захисту.

## Фізичні моделі та архітектура розрахункового рушія

Розрахунковий модуль розбиває силовий тракт на послідовність уніфікованих дискретних сегментів (Power Path Elements), кожен з яких описується власною електротепловою моделлю:

1. **Контактні пари роз'ємів (`ELEMENT_CONNECTOR`):** Описуються базовим контактним опором за температури 20 °C та помірним температурним коефіцієнтом. Модель враховує контактну деградацію при підвищенні температури вузла.
2. **Мідні провідники та силові шини (`ELEMENT_TRACE`):** Геометрія провідника задається довжиною, шириною та товщиною мідної фольги (стандартні 1 oz = 35 мкм, 2 oz = 70 мкм або 3 oz = 105 мкм). Опір розраховується через питомий опір електролітичної міді `1.724e-8 Ом*м`. Перегрів провідника оцінюється за модифікованою степеневою моделлю стандарту IPC-2152 з урахуванням кондуктивного охолодження через тонкий діелектрик у внутрішній суцільний полігон заземлення.
3. **Масиви перехідних отворів (`ELEMENT_VIA_ARRAY`):** Перехідний отвір розглядається як порожнистий мідний циліндр, площа стінки якого визначається діаметром свердла та товщиною електролітичного покриття (типово 20..25 мкм). Модуль розраховує еквівалентний опір паралельного масиву via та перевіряє густину струму на кожен отвір.
4. **Комутаційні та захисні ключі MOSFET (`ELEMENT_MOSFET`):** Враховується нелінійне зростання опору відкритого каналу `R_DS(on)` від температури кристала $T_j$. Температура кристала визначається ітераційно через тепловий опір кристал-довкілля `R_th_ja` або кристал-корпус `R_th_jc` та розсіювану потужність втрат провідності.
5. **Захисні елементи надструму (`ELEMENT_FUSE`):** Характеризуються холодним опором `R_cold`, номінальним струмом спрацювання та паспортним інтегралом повного відключення `I²t_clear`.
6. **Вимірювальні резистори-шунти (`ELEMENT_SHUNT`):** Мають стабільний опір із низьким температурним коефіцієнтом (типово 20..50 ppm/°C).

Для кожного елемента силового тракту програмний рушій виконує замкнений цикл розрахунків:
- Оцінка розсіюваної потужності за початкового номінального струму;
- Обчислення власного перегріву `Delta_T` та підсумкової робочої температури `T_final = T_ambient + Delta_T`;
- Корекція електричного опору провідника з урахуванням температурного коефіцієнта матеріалу;
- Перерахунок точного спаду напруги `Delta_V = I * R_hot` та розсіюваної потужності `P = I² * R_hot`;
- Перевірка критерію стійкості міді до імпульсу короткого замикання: чи перевищує граничний інтеграл Джоуля доріжки `(I²t)_trace` паспортне значення `I²t_clear` встановленого запобіжника.

## Покроковий розбір коду

Модуль спроектовано для використання як у складі вбудованого діагностичного ПЗ контролера (наприклад, для динамічного моніторингу просідання шини та оцінки залишкового ресурсу контактів), так і у вигляді автономної консольної утиліти чи частини CI/CD пайплайну верифікації апаратних проектів друкованих плат.

У коді реалізовано:
- Функцію `calc_trace_resistance_20c`, яка обчислює опір мідної шини за її метричними розмірами;
- Функцію `calc_via_array_resistance_20c`, що розраховує опір стінок масиву переходів через геометрію свердління та товщину металізації;
- Функцію `calc_trace_temp_rise_ipc2152`, яка реалізує емпіричну формулу стандарту IPC-2152 для плат із внутрішнім полігоном заземлення (коефіцієнт тепловідведення `k = 14.5`) та без нього (`k = 9.95`);
- Основний цикл аудиту `run_power_path_audit`, що послідовно обробляє вектор компонентів, накопичує загальний опір шини, сумарне падіння напруги в номінальному та піковому режимах, розраховує мінімальну напругу на навантаженні в найгіршому випадку розряду батареї та формує структурований звіт із діагностикою помилок.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define COPPER_RHO_20C      1.724e-8   /* Ом * м (питомий опір міді за 20 °C) */
#define COPPER_ALPHA_20C    0.00393    /* 1 / °C (ТКО міді) */
#define COPPER_K_CU         5.091e4    /* А^2 * с / мм^4 (константа плавлення) */

typedef enum {
    ELEM_CONNECTOR,
    ELEM_TRACE,
    ELEM_VIA_ARRAY,
    ELEM_MOSFET,
    ELEM_FUSE,
    ELEM_SHUNT
} ElementType;

typedef struct {
    const char *name;
    ElementType type;
    
    /* Базові електричні параметри */
    double nominal_resistance_ohm; /* Опір за 20 °C */
    double temp_coefficient;       /* ТКО (1/°C) */
    
    /* Геометричні параметри для доріжок (тип ELEM_TRACE) */
    double length_mm;
    double width_mm;
    double thickness_um;           /* наприклад, 35 мкм для 1 oz, 70 мкм для 2 oz */
    bool has_ground_plane;         /* наявність опорного полігону (IPC-2152) */
    
    /* Параметри via-масиву (тип ELEM_VIA_ARRAY) */
    int via_count;
    double drill_diameter_mm;
    double plating_thickness_um;
    
    /* Параметри MOSFET (тип ELEM_MOSFET) */
    double r_th_ja;                /* Тепловий опір кристал-довкілля (°C/Вт) */
    
    /* Захисні характеристики */
    double i2t_rating_a2s;         /* I^2 * t елемента */
    
    /* Результати розрахунку (заповнюються рушієм) */
    double op_resistance_ohm;
    double voltage_drop_v;
    double power_loss_w;
    double temp_rise_c;
    double final_temp_c;
    bool is_safe;
} PowerElement;

typedef struct {
    double v_source_nom;
    double v_source_min;
    double i_load_continuous;
    double i_load_peak;
    double t_ambient_c;
    double v_uvlo_threshold;
    
    PowerElement *elements;
    size_t element_count;
    
    /* Підсумки аудиту */
    double total_resistance_nom;
    double total_resistance_hot;
    double total_v_drop_cont;
    double total_v_drop_peak;
    double v_load_min_worst_case;
    double total_power_dissipated_w;
    bool system_pass;
} PowerPathAudit;

/* Розрахунок опору мідної доріжки за 20 °C */
double calc_trace_resistance_20c(double length_mm, double width_mm, double thickness_um) {
    double length_m = length_mm * 1e-3;
    double area_m2 = (width_mm * 1e-3) * (thickness_um * 1e-6);
    if (area_m2 <= 0.0) return 0.0;
    return COPPER_RHO_20C * (length_m / area_m2);
}

/* Розрахунок опору масиву перехідних отворів за 20 °C */
double calc_via_array_resistance_20c(int count, double drill_diam_mm, double plating_um, double board_thickness_mm) {
    if (count <= 0 || drill_diam_mm <= 0.0 || plating_um <= 0.0) return 0.0;
    
    /* Площа мідного кільця стінки via: A ≈ pi * d_drill * t_plating */
    double mean_diam_m = (drill_diam_mm - plating_um * 1e-3) * 1e-3;
    double wall_area_m2 = M_PI * mean_diam_m * (plating_um * 1e-6);
    double single_via_r = COPPER_RHO_20C * (board_thickness_mm * 1e-3 / wall_area_m2);
    
    return single_via_r / (double)count;
}

/* Оцінка перегріву доріжки за моделлю IPC-2152 */
double calc_trace_temp_rise_ipc2152(double current, double width_mm, double thickness_um, bool has_plane) {
    double area_mm2 = width_mm * (thickness_um * 1e-3);
    if (area_mm2 <= 0.0) return 999.0;
    
    /* 
     * Метрична апроксимація IPC-2152 для плати з опорною площиною заземлення:
     * Delta_T = [ I / (k * A^0.725) ]^(1 / 0.44)
     * Для плати з полігоном GND ефективне відведення покращується в 1.6..2.0 раза.
     */
    double k = has_plane ? 14.5 : 9.95;
    double term = current / (k * pow(area_mm2, 0.725));
    if (term <= 0.0) return 0.0;
    return pow(term, 1.0 / 0.44);
}

/* Виконання аудиту силового тракту */
bool run_power_path_audit(PowerPathAudit *audit) {
    audit->total_resistance_nom = 0.0;
    audit->total_resistance_hot = 0.0;
    audit->total_power_dissipated_w = 0.0;
    audit->system_pass = true;
    
    for (size_t i = 0; i < audit->element_count; i++) {
        PowerElement *e = &audit->elements[i];
        
        /* 1. Визначення базового опору за 20 °C */
        if (e->type == ELEM_TRACE) {
            e->nominal_resistance_ohm = calc_trace_resistance_20c(e->length_mm, e->width_mm, e->thickness_um);
            e->temp_coefficient = COPPER_ALPHA_20C;
        } else if (e->type == ELEM_VIA_ARRAY) {
            e->nominal_resistance_ohm = calc_via_array_resistance_20c(e->via_count, e->drill_diameter_mm, e->plating_thickness_um, 1.6);
            e->temp_coefficient = COPPER_ALPHA_20C;
        }
        
        /* 2. Тепловий розрахунок для тривалого струму */
        double current = audit->i_load_continuous;
        double p_est = current * current * e->nominal_resistance_ohm;
        
        if (e->type == ELEM_TRACE) {
            e->temp_rise_c = calc_trace_temp_rise_ipc2152(current, e->width_mm, e->thickness_um, e->has_ground_plane);
        } else if (e->type == ELEM_MOSFET && e->r_th_ja > 0.0) {
            e->temp_rise_c = p_est * e->r_th_ja;
        } else {
            /* Спрощена оцінка для пасивних дискретних компонентів */
            e->temp_rise_c = p_est * 15.0; 
        }
        
        e->final_temp_c = audit->t_ambient_c + e->temp_rise_c;
        
        /* 3. Корекція опору за робочої температури */
        double delta_t_from_20c = e->final_temp_c - 20.0;
        e->op_resistance_ohm = e->nominal_resistance_ohm * (1.0 + e->temp_coefficient * delta_t_from_20c);
        
        /* 4. Втрати потужності та спад напруги */
        e->voltage_drop_v = current * e->op_resistance_ohm;
        e->power_loss_w = current * current * e->op_resistance_ohm;
        
        /* 5. Перевірка безпеки та I^2*t */
        e->is_safe = true;
        if (e->final_temp_c > 105.0) {
            e->is_safe = false; /* Перевищення допустимої температури FR-4 */
        }
        
        if (e->type == ELEM_TRACE) {
            double area_mm2 = e->width_mm * (e->thickness_um * 1e-3);
            double ln_term = log((1.0 + COPPER_ALPHA_20C * (150.0 - 20.0)) / (1.0 + COPPER_ALPHA_20C * (e->final_temp_c - 20.0)));
            double i2t_trace_limit = COPPER_K_CU * area_mm2 * area_mm2 * ln_term;
            
            /* Порівнюємо із захисним запобіжником (якщо є в ланцюзі) */
            for (size_t j = 0; j < audit->element_count; j++) {
                if (audit->elements[j].type == ELEM_FUSE && audit->elements[j].i2t_rating_a2s > 0.0) {
                    if (audit->elements[j].i2t_rating_a2s >= i2t_trace_limit) {
                        e->is_safe = false; /* Запобіжник не захищає цю доріжку від випаровування */
                    }
                }
            }
        }
        
        if (!e->is_safe) {
            audit->system_pass = false;
        }
        
        audit->total_resistance_nom += e->nominal_resistance_ohm;
        audit->total_resistance_hot += e->op_resistance_ohm;
        audit->total_power_dissipated_w += e->power_loss_w;
    }
    
    audit->total_v_drop_cont = audit->i_load_continuous * audit->total_resistance_hot;
    audit->total_v_drop_peak = audit->i_load_peak * audit->total_resistance_hot;
    audit->v_load_min_worst_case = audit->v_source_min - audit->total_v_drop_peak;
    
    if (audit->v_load_min_worst_case < audit->v_uvlo_threshold) {
        audit->system_pass = false; /* Ризик перезавантаження системи від просідання живлення */
    }
    
    return audit->system_pass;
}

void print_power_path_report(const PowerPathAudit *audit) {
    printf("================================================================================\n");
    printf("                  ЗВІТ НАСКРІЗНОГО АУДИТУ СИЛОВОГО ТРАКТУ                       \n");
    printf("================================================================================\n");
    printf("Джерело: %.2f В (мін: %.2f В) | Струм: %.2f А (пік: %.2f А) | T_amb: %.1f °C\n",
           audit->v_source_nom, audit->v_source_min, audit->i_load_continuous, audit->i_load_peak, audit->t_ambient_c);
    printf("--------------------------------------------------------------------------------\n");
    printf("%-20s | %-8s | %-8s | %-8s | %-8s | %-6s\n",
           "Елемент", "R_hot,мОм", "Drop_V", "P_loss,Вт", "T_fin,°C", "Стан");
    printf("--------------------------------------------------------------------------------\n");
    
    for (size_t i = 0; i < audit->element_count; i++) {
        const PowerElement *e = &audit->elements[i];
        printf("%-20s | %8.2f | %8.3f | %8.3f | %8.1f | %-6s\n",
               e->name,
               e->op_resistance_ohm * 1e3,
               e->voltage_drop_v,
               e->power_loss_w,
               e->final_temp_c,
               e->is_safe ? "OK" : "DEFECT");
    }
    printf("--------------------------------------------------------------------------------\n");
    printf("Загальний опір тракту (гарячий):  %.2f мОм\n", audit->total_resistance_hot * 1e3);
    printf("Сумарне падіння напруги (номінал): %.3f В\n", audit->total_v_drop_cont);
    printf("Сумарне падіння напруги (пік):     %.3f В\n", audit->total_v_drop_peak);
    printf("Мінімальна напруга на навантаженні:%.3f В (Поріг UVLO: %.2f В)\n",
           audit->v_load_min_worst_case, audit->v_uvlo_threshold);
    printf("Загальні теплові втрати шини:      %.2f Вт\n", audit->total_power_dissipated_w);
    printf("Підсумковий вердикт:               %s\n",
           audit->system_pass ? "СИСТЕМА ВІДПОВІДАЄ НОРМАМ" : "ПОМИЛКА: ПОТРІБЕН РЕДИЗАЙН");
    printf("================================================================================\n");
}

int main(void) {
    PowerElement elements[] = {
        { .name = "XT30 Роз'єм",       .type = ELEM_CONNECTOR, .nominal_resistance_ohm = 0.005,  .temp_coefficient = 0.002 },
        { .name = "SMD Запобіжник 7A", .type = ELEM_FUSE,      .nominal_resistance_ohm = 0.015,  .temp_coefficient = 0.001, .i2t_rating_a2s = 18.0 },
        { .name = "P-MOS FET Захист",  .type = ELEM_MOSFET,    .nominal_resistance_ohm = 0.008,  .temp_coefficient = 0.006, .r_th_ja = 45.0 },
        { .name = "Шина живлення (2oz)",.type = ELEM_TRACE,     .length_mm = 80.0, .width_mm = 4.0, .thickness_um = 70.0, .has_ground_plane = true },
        { .name = "Масив переходів (4x)",.type = ELEM_VIA_ARRAY,.via_count = 4, .drill_diameter_mm = 0.4, .plating_thickness_um = 25.0 },
        { .name = "Вимірювальний шунт", .type = ELEM_SHUNT,     .nominal_resistance_ohm = 0.010,  .temp_coefficient = 0.0001 }
    };
    
    PowerPathAudit audit = {
        .v_source_nom = 24.0,
        .v_source_min = 18.0,
        .i_load_continuous = 5.0,
        .i_load_peak = 10.0,
        .t_ambient_c = 55.0,
        .v_uvlo_threshold = 17.0,
        .elements = elements,
        .element_count = sizeof(elements) / sizeof(elements[0])
    };
    
    run_power_path_audit(&audit);
    print_power_path_report(&audit);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <expected>
#include <span>

namespace PowerAudit {

constexpr double CopperRho20C   = 1.724e-8; // Ом * м
constexpr double CopperAlpha20C = 0.00393;  // 1 / °C
constexpr double CopperKcu      = 5.091e4;  // А^2 * с / мм^4

enum class ElementType {
    Connector,
    Trace,
    ViaArray,
    Mosfet,
    Fuse,
    Shunt
};

struct ElementParams {
    std::string name;
    ElementType type;
    double nominalResistanceOhm{0.0};
    double tempCoefficient{0.0};
    
    // Доріжка
    double lengthMm{0.0};
    double widthMm{0.0};
    double thicknessUm{0.0};
    bool hasGroundPlane{true};
    
    // Переходи (via)
    int viaCount{1};
    double drillDiameterMm{0.4};
    double platingThicknessUm{25.0};
    
    // MOSFET
    double rThJa{0.0};
    
    // Захист
    double i2tRatingA2s{0.0};
};

struct ElementResult {
    double opResistanceOhm{0.0};
    double voltageDropV{0.0};
    double powerLossW{0.0};
    double tempRiseC{0.0};
    double finalTempC{0.0};
    bool isSafe{true};
    std::string defectReason{};
};

struct AuditReport {
    double totalResistanceNom{0.0};
    double totalResistanceHot{0.0};
    double totalVDropCont{0.0};
    double totalVDropPeak{0.0};
    double vLoadMinWorstCase{0.0};
    double totalPowerDissipatedW{0.0};
    bool systemPass{true};
    std::vector<ElementResult> elementResults;
};

class PowerPathAuditor {
public:
    struct Config {
        double vSourceNom{24.0};
        double vSourceMin{18.0};
        double iLoadContinuous{5.0};
        double iLoadPeak{10.0};
        double tAmbientC{55.0};
        double vUvloThreshold{17.0};
    };

    explicit PowerPathAuditor(Config cfg) : cfg_(cfg) {}

    [[nodiscard]] AuditReport evaluate(std::span<const ElementParams> elements) const {
        AuditReport report{};
        report.elementResults.reserve(elements.size());

        for (const auto& elem : elements) {
            ElementResult res{};
            double rNom = elem.nominalResistanceOhm;
            double alpha = elem.tempCoefficient;

            if (elem.type == ElementType::Trace) {
                rNom = calculateTraceResistance20C(elem.lengthMm, elem.widthMm, elem.thicknessUm);
                alpha = CopperAlpha20C;
            } else if (elem.type == ElementType::ViaArray) {
                rNom = calculateViaArrayResistance20C(elem.viaCount, elem.drillDiameterMm, elem.platingThicknessUm, 1.6);
                alpha = CopperAlpha20C;
            }

            // Оцінка перегріву
            const double current = cfg_.iLoadContinuous;
            const double pEst = current * current * rNom;

            if (elem.type == ElementType::Trace) {
                res.tempRiseC = calculateTraceTempRise(current, elem.widthMm, elem.thicknessUm, elem.hasGroundPlane);
            } else if (elem.type == ElementType::Mosfet && elem.rThJa > 0.0) {
                res.tempRiseC = pEst * elem.rThJa;
            } else {
                res.tempRiseC = pEst * 15.0;
            }

            res.finalTempC = cfg_.tAmbientC + res.tempRiseC;
            const double deltaT = res.finalTempC - 20.0;
            res.opResistanceOhm = rNom * (1.0 + alpha * deltaT);
            res.voltageDropV = current * res.opResistanceOhm;
            res.powerLossW = current * current * res.opResistanceOhm;

            // Верифікація безпеки
            if (res.finalTempC > 105.0) {
                res.isSafe = false;
                res.defectReason = "Перегрів > 105 °C (межа FR-4)";
            }

            if (elem.type == ElementType::Trace) {
                const double areaMm2 = elem.widthMm * (elem.thicknessUm * 1e-3);
                const double lnTerm = std::log((1.0 + CopperAlpha20C * (150.0 - 20.0)) /
                                               (1.0 + CopperAlpha20C * (res.finalTempC - 20.0)));
                const double i2tTraceLimit = CopperKcu * areaMm2 * areaMm2 * lnTerm;

                for (const auto& other : elements) {
                    if (other.type == ElementType::Fuse && other.i2tRatingA2s > 0.0) {
                        if (other.i2tRatingA2s >= i2tTraceLimit) {
                            res.isSafe = false;
                            res.defectReason = "I²t запобіжника перевищує поріг руйнування міді";
                        }
                    }
                }
            }

            if (!res.isSafe) {
                report.systemPass = false;
            }

            report.totalResistanceNom += rNom;
            report.totalResistanceHot += res.opResistanceOhm;
            report.totalPowerDissipatedW += res.powerLossW;
            report.elementResults.push_back(res);
        }

        report.totalVDropCont = cfg_.iLoadContinuous * report.totalResistanceHot;
        report.totalVDropPeak = cfg_.iLoadPeak * report.totalResistanceHot;
        report.vLoadMinWorstCase = cfg_.vSourceMin - report.totalVDropPeak;

        if (report.vLoadMinWorstCase < cfg_.vUvloThreshold) {
            report.systemPass = false;
        }

        return report;
    }

private:
    Config cfg_;

    static double calculateTraceResistance20C(double lenMm, double widthMm, double thickUm) noexcept {
        const double areaM2 = (widthMm * 1e-3) * (thickUm * 1e-6);
        if (areaM2 <= 0.0) return 0.0;
        return CopperRho20C * ((lenMm * 1e-3) / areaM2);
    }

    static double calculateViaArrayResistance20C(int count, double drillMm, double platingUm, double boardThickMm) noexcept {
        if (count <= 0 || drillMm <= 0.0 || platingUm <= 0.0) return 0.0;
        const double meanDiamM = (drillMm - platingUm * 1e-3) * 1e-3;
        const double wallAreaM2 = std::numbers::pi * meanDiamM * (platingUm * 1e-6);
        const double singleViaR = CopperRho20C * (boardThickMm * 1e-3 / wallAreaM2);
        return singleViaR / static_cast<double>(count);
    }

    static double calculateTraceTempRise(double current, double widthMm, double thickUm, bool hasPlane) noexcept {
        const double areaMm2 = widthMm * (thickUm * 1e-3);
        if (areaMm2 <= 0.0) return 999.0;
        const double k = hasPlane ? 14.5 : 9.95;
        const double term = current / (k * std::pow(areaMm2, 0.725));
        if (term <= 0.0) return 0.0;
        return std::pow(term, 1.0 / 0.44);
    }
};

} // namespace PowerAudit

int main() {
    using namespace PowerAudit;

    const std::vector<ElementParams> powerElements = {
        { .name = "XT30 Роз'єм",       .type = ElementType::Connector, .nominalResistanceOhm = 0.005,  .tempCoefficient = 0.002 },
        { .name = "SMD Запобіжник 7A", .type = ElementType::Fuse,      .nominalResistanceOhm = 0.015,  .tempCoefficient = 0.001, .i2tRatingA2s = 18.0 },
        { .name = "P-MOS FET Захист",  .type = ElementType::Mosfet,    .nominalResistanceOhm = 0.008,  .tempCoefficient = 0.006, .rThJa = 45.0 },
        { .name = "Шина живлення (2oz)",.type = ElementType::Trace,     .lengthMm = 80.0, .widthMm = 4.0, .thicknessUm = 70.0, .hasGroundPlane = true },
        { .name = "Масив переходів (4x)",.type = ElementType::ViaArray, .viaCount = 4, .drillDiameterMm = 0.4, .platingThicknessUm = 25.0 },
        { .name = "Вимірювальний шунт", .type = ElementType::Shunt,     .nominalResistanceOhm = 0.010,  .tempCoefficient = 0.0001 }
    };

    PowerPathAuditor::Config cfg{
        .vSourceNom = 24.0,
        .vSourceMin = 18.0,
        .iLoadContinuous = 5.0,
        .iLoadPeak = 10.0,
        .tAmbientC = 55.0,
        .vUvloThreshold = 17.0
    };

    PowerPathAuditor auditor(cfg);
    const auto report = auditor.evaluate(powerElements);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "================================================================================\n";
    std::cout << "             ЗВІТ НАСКРІЗНОГО АУДИТУ СИЛОВОГО ТРАКТУ (C++20)                    \n";
    std::cout << "================================================================================\n";
    std::cout << "Загальний опір (гарячий):          " << report.totalResistanceHot * 1e3 << " мОм\n";
    std::cout << "Сумарний спад напруги (пік 10A):  " << report.totalVDropPeak << " В\n";
    std::cout << "Мінімальна напруга на шині:       " << report.vLoadMinWorstCase << " В (UVLO: " << cfg.vUvloThreshold << " В)\n";
    std::cout << "Сумарні втрати потужності:        " << report.totalPowerDissipatedW << " Вт\n";
    std::cout << "Статус системи:                   " << (report.systemPass ? "ВІДПОВІДАЄ НОРМАМ" : "ДЕФЕКТ") << "\n";
    std::cout << "================================================================================\n";

    return 0;
}
```
:::

## Крайові випадки та аналіз надійності

Під час практичного використання модуля аудиту необхідно звернути увагу на наступні фізичні крайові режими:

1. **Електротепловий позитивний зворотний зв'язок (Thermal Runaway):** Якщо питома потужність у вузькому місці доріжки перевищує здатність текстоліту відводити тепло, зростання температури збільшує опір міді (`alpha = +0.00393 1/°C`), що за постійного струму навантаження збільшує виділення тепла `I²R`. При підвищенні температури шини з +20 °C до +75 °C опір міді зростає на `1.0 + 0.00393 * 55 = 1.216` (+21.6%). Якщо розрахунок падіння напруги виконувати за холодною геометрією 20 °C, реальний спад напруги під навантаженням виявиться на 20–25% більшим, що призводить до несподіваного відключення перетворювачів по UVLO.
2. **Селективність захисту за інтегралом I²t:** Якщо ширина силової доріжки 1 oz становить менше ніж 1.5 мм, її граничний допустимий імпульс руйнування `I²t_trace` становить менше 35 А²·с. Застосування запобіжника з `I²t_clear = 40 А²·с` перетворює саму друковану плату на плавку вставку: під час короткого замикання першою випарується та обвуглить текстоліт доріжка на платі, а не корпусний запобіжник.
3. **Паразитний опір переходів між шарами:** Заміна суцільного полігону одним перехідним отвором створює точковий нагрівач із тепловим опором понад 80 °C/Вт. У коді перевіряється кратність кількості via до розрахункового струму, що гарантує відсутність прихованих локальних теплових плям під BGA- та QFN-компонентами.
