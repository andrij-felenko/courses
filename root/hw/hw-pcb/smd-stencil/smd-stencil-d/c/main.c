#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    APERTURE_RECTANGLE,
    APERTURE_CIRCLE
} ApertureShape;

typedef struct {
    ApertureShape shape;
    double width_mm;      /* Ширина або діаметр для кола */
    double length_mm;     /* Довжина (для прямокутника) */
    double foil_thick_mm; /* Товщина фольги трафарету T */
    bool has_nano_coating;/* Наявність гідрофобного нанопокриття */
} StencilAperture;

typedef struct {
    double area_ratio;
    double aspect_ratio;
    double expected_transfer_eff; /* Очікуваний коефіцієнт передачі 0.0 - 1.0 */
    bool is_ipc_ar_valid;
    bool is_ipc_as_valid;
} ValidationResult;

ValidationResult validate_aperture(const StencilAperture* ap) {
    ValidationResult res;
    double w = ap->width_mm;
    double l = ap->length_mm;
    double t = ap->foil_thick_mm;

    if (ap->shape == APERTURE_CIRCLE) {
        /* Для круглої апертури AR = D / (4 * T) */
        res.area_ratio = w / (4.0 * t);
        res.aspect_ratio = w / t;
    } else {
        /* Для прямокутної апертури AR = (W * L) / (2 * (W + L) * T) */
        double a_pad = w * l;
        double a_walls = 2.0 * (w + l) * t;
        res.area_ratio = a_pad / a_walls;
        res.aspect_ratio = (w < l ? w : l) / t;
    }

    double ar_limit = ap->has_nano_coating ? 0.55 : 0.66;
    res.is_ipc_ar_valid = (res.area_ratio >= ar_limit);
    res.is_ipc_as_valid = (res.aspect_ratio >= 1.50);

    /* Моделювання сигмоїди Transfer Efficiency за моделлю IPC */
    double k = ap->has_nano_coating ? 14.0 : 11.0;
    double ar0 = ap->has_nano_coating ? 0.45 : 0.55;
    res.expected_transfer_eff = 0.95 / (1.0 + exp(-k * (res.area_ratio - ar0)));

    return res;
}

int main(void) {
    /* Аналіз виводу QFN 0.4 мм: W = 0.20 мм, L = 0.80 мм, Фольга T = 0.12 мм */
    StencilAperture qfn_lead = {
        .shape = APERTURE_RECTANGLE,
        .width_mm = 0.20,
        .length_mm = 0.80,
        .foil_thick_mm = 0.12,
        .has_nano_coating = true
    };

    ValidationResult r = validate_aperture(&qfn_lead);
    printf("Аналіз апертури QFN 0.4mm (Фольга 120 мкм, Нанопокриття):\n");
    printf("  Area Ratio:   %.3f (Норма >= %.2f) -> %s\n", 
           r.area_ratio, qfn_lead.has_nano_coating ? 0.55 : 0.66, 
           r.is_ipc_ar_valid ? "PASS" : "FAIL");
    printf("  Aspect Ratio: %.3f (Норма >= 1.50) -> %s\n", 
           r.aspect_ratio, r.is_ipc_as_valid ? "PASS" : "FAIL");
    printf("  Очікуваний Transfer Efficiency: %.1f%%\n", r.expected_transfer_eff * 100.0);

    return 0;
}
