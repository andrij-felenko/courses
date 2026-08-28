#include <math.h>
#include <stdbool.h>

// Сталі підгінки кривих IPC-2221 (переріз — у кв. мілах, I — A, dT — °C).
#define IPC_B   0.44
#define IPC_C   0.725
#define IPC_K_EXTERNAL  0.048   // мідь на зовнішньому шарі (обдувається)
#define IPC_K_INTERNAL  0.024   // мідь на внутрішньому шарі (похована)

#define MM_PER_MIL   0.0254     // 1 мил = 0.0254 мм
#define MIL_PER_OZ   1.378      // товщина 1 oz міді у мілах
#define PI_          3.14159265358979

// Пряма формула IPC-2221: струм (А), який дасть переріз area_mils2 при перегріві dT.
static double ipc2221_current(double area_mils2, double delta_t_c, double k)
{
    return k * pow(delta_t_c, IPC_B) * pow(area_mils2, IPC_C);
}
