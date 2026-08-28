// Допустимий струм (А) для доріжки заданої ширини й товщини за IPC-2221.
//   width_mm    — ширина доріжки, мм
//   delta_t_c   — допустимий перегрів, °C
//   copper_oz   — вага міді, унції
//   external    — true: зовнішній шар; false: внутрішній
// Повертає струм в амперах, або -1.0 при некоректних аргументах.
double ipc2221_trace_current_a(double width_mm, double delta_t_c,
                               double copper_oz, bool external)
{
    if (width_mm <= 0.0 || delta_t_c <= 0.0 || copper_oz <= 0.0)
        return -1.0;

    double k = external ? IPC_K_EXTERNAL : IPC_K_INTERNAL;

    // Переріз у кв. мілах = ширина(мил) · товщина(мил).
    double width_mils = width_mm / MM_PER_MIL;
    double thickness_mils = copper_oz * MIL_PER_OZ;
    double area_mils2 = width_mils * thickness_mils;

    // Пряма формула: I = k · dT^b · A^c.
    return k * pow(delta_t_c, IPC_B) * pow(area_mils2, IPC_C);
}
