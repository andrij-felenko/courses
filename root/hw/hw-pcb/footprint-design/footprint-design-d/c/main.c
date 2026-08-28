#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Структура для перевірки параметрів контактної площадки за IPC-7351 */
typedef struct {
    double pitch_mm;           /* Крок виводів компонента */
    double pad_width_mm;       /* Ширина мідної площадки X */
    double pad_length_mm;      /* Довжина мідної площадки Y */
    double mask_expansion_mm;  /* Розширення вікна паяльної маски на сторону */
    double min_mask_dam_mm;    /* Технологічний мінімум містка маски фабрики */
} FootprintCheckParams;

/* Результат валідації посадкового місця */
typedef struct {
    double actual_mask_dam_mm;
    bool is_dam_sufficient;
    bool is_nsmd_recommended;
} FootprintCheckResult;

FootprintCheckResult validate_footprint_geometry(const FootprintCheckParams *p) {
    FootprintCheckResult res;
    
    /* Розрахунок фактичного просвіту між сусідніми вікнами маски */
    double copper_clearance = p->pitch_mm - p->pad_width_mm;
    res.actual_mask_dam_mm = copper_clearance - (2.0 * p->mask_expansion_mm);
    
    /* Перевірка достатності полімерного містка маски */
    res.is_dam_sufficient = (res.actual_mask_dam_mm >= p->min_mask_dam_mm);
    
    /* Для дрібного кроку (<= 0.5 мм) рекомендовано конфігурацію NSMD */
    res.is_nsmd_recommended = (p->pitch_mm <= 0.50);
    
    return res;
}

int main(void) {
    /* Перевірка QFP з кроком 0.5 мм та розширенням маски 0.05 мм */
    FootprintCheckParams qfp = {
        .pitch_mm = 0.50,
        .pad_width_mm = 0.28,
        .pad_length_mm = 1.20,
        .mask_expansion_mm = 0.05,
        .min_mask_dam_mm = 0.075
    };
    
    FootprintCheckResult r = validate_footprint_geometry(&qfp);
    
    printf("Фактичний місток маски: %.3f мм (Норма >= %.3f мм): %s\n",
           r.actual_mask_dam_mm, qfp.min_mask_dam_mm,
           r.is_dam_sufficient ? "ПРОЙДЕНО" : "ПОМИЛКА: ЗАМИКАННЯ");
    printf("Тип площадки: %s\n",
           r.is_nsmd_recommended ? "Рекомендовано NSMD" : "Допустимо SMD");
           
    return 0;
}
