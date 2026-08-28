// Падіння напруги (В) на доріжці заданих розмірів при заданому струмі.
//   width_mm   — ширина, мм
//   length_mm  — довжина, мм
//   copper_oz  — вага міді, унції
//   current_a  — струм, А
// Повертає падіння у вольтах, або -1.0 при некоректних аргументах.
double trace_voltage_drop_v(double width_mm, double length_mm,
                            double copper_oz, double current_a)
{
    if (width_mm <= 0.0 || length_mm <= 0.0 ||
        copper_oz <= 0.0 || current_a < 0.0)
        return -1.0;

    // Усе в метри: переріз A = ширина · товщина.
    double thickness_m = copper_oz * MIL_PER_OZ * MM_PER_MIL * 1e-3;  // oz->мил->мм->м
    double width_m  = width_mm  * 1e-3;
    double length_m = length_mm * 1e-3;
    double area_m2  = width_m * thickness_m;

    double resistance_ohm = COPPER_RHO_OHM_M * length_m / area_m2;
    return current_a * resistance_ohm;     // U = I · R
}
