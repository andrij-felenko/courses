#include <math.h>
#include <stdbool.h>

// Сталі підгінки кривих IPC-2221 (площа — у квадратних мілах, I — A, dT — °C).
#define IPC_B   0.44
#define IPC_C   0.725
#define IPC_K_EXTERNAL  0.048   // доріжка на зовнішньому шарі (обдувається)
#define IPC_K_INTERNAL  0.024   // доріжка на внутрішньому шарі (похована)

// Перевідні множники між системами одиниць.
#define MM_PER_MIL        0.0254          // 1 мил = 0.0254 мм
#define MIL_PER_OZ        1.378           // товщина 1 oz міді у мілах
#define COPPER_RHO_OHM_M  1.724e-8        // питомий опір міді при ~25 °C, Ом·м

// Мінімальна ширина доріжки (мм) під заданий струм і перегрів за IPC-2221.
//   current_a   — струм, А
//   delta_t_c   — допустимий перегрів над довкіллям, °C
//   copper_oz   — вага міді, унції на кв. фут (0.5, 1, 2 ...)
//   external    — true: зовнішній шар; false: внутрішній
// Повертає ширину в міліметрах, або -1.0 при некоректних аргументах.
double ipc2221_trace_width_mm(double current_a, double delta_t_c,
                              double copper_oz, bool external)
{
    if (current_a <= 0.0 || delta_t_c <= 0.0 || copper_oz <= 0.0)
        return -1.0;                       // безглузді вхідні — не вгадуємо

    double k = external ? IPC_K_EXTERNAL : IPC_K_INTERNAL;

    // Обернена формула: A = ( I / (k · dT^b) )^(1/c), площа у кв. мілах.
    double area_mils2 = pow(current_a / (k * pow(delta_t_c, IPC_B)), 1.0 / IPC_C);

    // Товщина міді у мілах -> ширина = площа / товщина (теж у мілах).
    double thickness_mils = copper_oz * MIL_PER_OZ;
    double width_mils = area_mils2 / thickness_mils;

    return width_mils * MM_PER_MIL;        // у міліметри для людини
}
