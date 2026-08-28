// Смуга на виході високоомного джерела, що навантажене ємністю кабелю.
// f_3dB = 1 / (2*pi*R*C). Ведений екран ділить ефективну C на коефіцієнт буфера.
#include <math.h>

float bandwidth_hz(float r_source_ohm, float c_eff_farad) {
    return 1.0f / (2.0f * 3.14159265f * r_source_ohm * c_eff_farad);
}

int main(void) {
    float R = 1.0e9f;          // вихідний опір давача, Ом
    float C_cable = 100e-12f;  // ємність метра кабелю, Ф

    float f_plain  = bandwidth_hz(R, C_cable);          // екран на землі
    float f_driven = bandwidth_hz(R, C_cable / 1000.0f);// ведений екран

    // f_plain  = 1 / (2*pi*1e9*100e-12)  ≈ 1.6 Гц    — кабель убив смугу
    // f_driven = 1 / (2*pi*1e9*0.1e-12)  ≈ 1.6 кГц   — у 1000 разів ширше
    (void)f_plain; (void)f_driven;
    return 0;
}
