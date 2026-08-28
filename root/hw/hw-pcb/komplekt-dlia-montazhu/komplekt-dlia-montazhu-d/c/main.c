#include <stdbool.h>
#include <stdint.h>

typedef enum {
    SOLDER_POWDER_TYPE_3 = 3,
    SOLDER_POWDER_TYPE_4 = 4,
    SOLDER_POWDER_TYPE_5 = 5,
    SOLDER_POWDER_TYPE_6 = 6
} solder_powder_type_t;

typedef struct {
    double foil_thickness_um;
    solder_powder_type_t powder;
} stencil_spec_t;

typedef struct {
    double aspect_ratio;
    double area_ratio;
    bool is_aspect_valid;
    bool is_area_valid;
    bool is_powder_valid;
    bool overall_pass;
} stencil_check_result_t;

static inline double max_powder_diameter_um(solder_powder_type_t type) {
    switch (type) {
        case SOLDER_POWDER_TYPE_3: return 45.0;
        case SOLDER_POWDER_TYPE_4: return 38.0;
        case SOLDER_POWDER_TYPE_5: return 25.0;
        case SOLDER_POWDER_TYPE_6: return 15.0;
        default:                   return 45.0;
    }
}

stencil_check_result_t stencil_check_rect_aperture(const stencil_spec_t* spec,
                                                   double width_um,
                                                   double length_um) {
    stencil_check_result_t res;
    const double t = spec->foil_thickness_um;
    const double d_max = max_powder_diameter_um(spec->powder);

    res.aspect_ratio = width_um / t;
    res.area_ratio = (width_um * length_um) / (2.0 * (width_um + length_um) * t);

    res.is_aspect_valid = (res.aspect_ratio >= 1.50);
    res.is_area_valid = (res.area_ratio >= 0.66);
    res.is_powder_valid = (width_um >= 5.0 * d_max);

    res.overall_pass = res.is_aspect_valid && res.is_area_valid && res.is_powder_valid;
    return res;
}

stencil_check_result_t stencil_check_circle_aperture(const stencil_spec_t* spec,
                                                     double diameter_um) {
    stencil_check_result_t res;
    const double t = spec->foil_thickness_um;
    const double d_max = max_powder_diameter_um(spec->powder);

    res.aspect_ratio = diameter_um / t;
    res.area_ratio = diameter_um / (4.0 * t);

    res.is_aspect_valid = (res.aspect_ratio >= 1.50);
    res.is_area_valid = (res.area_ratio >= 0.66);
    res.is_powder_valid = (diameter_um >= 5.0 * d_max);

    res.overall_pass = res.is_aspect_valid && res.is_area_valid && res.is_powder_valid;
    return res;
}
