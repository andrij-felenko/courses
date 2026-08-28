#include <stdio.h>
#include <math.h>

int main(void) {
    const double fc  = 50.0e3;     // бажана частота зрізу, Гц
    const double pm_goal = 60.0;   // бажаний запас фази, градуси
    const double ph_plant = -65.0; // фаза силовоі частини на fc, градуси
    const double gm  = 1.2e-3;     // крутість підсилювача похибки, А/В
    const double A   = 8.0;        // робочий виграш компенсатора, рази

    // 1. скільки фази має докинути пара нуль-полюс над −90° інтегратора
    //    boost = запас_ціль − фаза_силовоі − 90°
    double boost = pm_goal - ph_plant - 90.0;
    printf("boost = %.1f deg\n", boost);               // 35.0

    // 2. коефіцієнт K із потрібного підйому
    double K = tan((45.0 + boost/2.0) * M_PI/180.0);
    printf("K = %.3f\n", K);                            // ~1.921

    // 3. нуль і полюс — симетрично навколо fc (fc — їхній геом. центр)
    double f_zero = fc / K;
    double f_pole = fc * K;
    printf("f_нуль  = %.0f Hz\n", f_zero);              // ~26030
    printf("f_полюс = %.0f Hz\n", f_pole);              // ~96040

    // 4. номінали для OTA-схеми (послідовна ланка R2+C1 від COMP на землю,
    //    плюс малий C2 паралельно на полюс):
    double R2 = A / gm;                                 // виграш gm·R2 = A  →  R2, Ом
    double C1 = 1.0 / (2.0*M_PI*R2*f_zero);             // нуль,  Ф
    double C2 = 1.0 / (2.0*M_PI*R2*f_pole);             // полюс, Ф
    printf("R2 = %.0f Ohm\n", R2);                      // ~6667
    printf("C1 = %.0f pF\n", C1*1e12);                  // ~918
    printf("C2 = %.0f pF\n", C2*1e12);                  // ~249
    return 0;
}
