#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Структура комплексного числа для C
typedef struct {
    double real;
    double imag;
} Complex;

static inline Complex c_add(Complex a, Complex b) {
    return (Complex){ a.real + b.real, a.imag + b.imag };
}

static inline Complex c_sub(Complex a, Complex b) {
    return (Complex){ a.real - b.real, a.imag - b.imag };
}

static inline Complex c_mul(Complex a, Complex b) {
    return (Complex){ a.real * b.real - a.imag * b.imag, a.real * b.imag + a.imag * b.real };
}

static inline Complex c_div(Complex a, Complex b) {
    double denom = b.real * b.real + b.imag * b.imag;
    return (Complex){ (a.real * b.real + a.imag * b.imag) / denom,
                      (a.imag * b.real - a.real * b.imag) / denom };
}

static inline double c_abs(Complex a) {
    return sqrt(a.real * a.real + a.imag * a.imag);
}

static inline double c_arg(Complex a) {
    return atan2(a.imag, a.real);
}

static inline Complex c_exp(Complex a) {
    double r = exp(a.real);
    return (Complex){ r * cos(a.imag), r * sin(a.imag) };
}

typedef struct {
    double z0;
    double frequency_hz;
    double length_m;
    double velocity_factor;
    double attenuation_db_m;
} LineParams;

typedef struct {
    Complex gamma_load;
    double gamma_mag;
    double gamma_phase_deg;
    double vswr;
    double return_loss_db;
    double power_transmitted_pct;
    double power_reflected_pct;
    Complex gamma_input;
    Complex z_input;
} ReflectionResult;

bool calculate_reflection(Complex z_load, const LineParams* line, ReflectionResult* out) {
    if (!line || !out || line->z0 <= 0.0 || line->frequency_hz <= 0.0 || 
        line->velocity_factor <= 0.0 || line->velocity_factor > 1.0 || line->length_m < 0.0) {
        return false;
    }

    const double c0 = 299792458.0;
    double v_phase = c0 * line->velocity_factor;
    double wavelength = v_phase / line->frequency_hz;
    double beta = 2.0 * M_PI / wavelength;
    double alpha_np_m = line->attenuation_db_m / 8.685889638;

    // Γ_L = (Z_L - Z0) / (Z_L + Z0)
    Complex z0_c = { line->z0, 0.0 };
    Complex num = c_sub(z_load, z0_c);
    Complex den = c_add(z_load, z0_c);
    out->gamma_load = c_div(num, den);

    out->gamma_mag = c_abs(out->gamma_load);
    out->gamma_phase_deg = c_arg(out->gamma_load) * 180.0 / M_PI;

    out->vswr = (out->gamma_mag >= 0.99999) ? 999.99 : (1.0 + out->gamma_mag) / (1.0 - out->gamma_mag);
    out->return_loss_db = (out->gamma_mag < 1e-12) ? 240.0 : -20.0 * log10(out->gamma_mag);
    out->power_reflected_pct = out->gamma_mag * out->gamma_mag * 100.0;
    out->power_transmitted_pct = (1.0 - out->gamma_mag * out->gamma_mag) * 100.0;

    // Γ(l) = Γ_L * exp(-2*alpha*l - j*2*beta*l)
    Complex gamma_prop = { -2.0 * alpha_np_m * line->length_m, -2.0 * beta * line->length_m };
    out->gamma_input = c_mul(out->gamma_load, c_exp(gamma_prop));

    // Z_in = Z0 * (1 + Γ_in) / (1 - Γ_in)
    Complex one = { 1.0, 0.0 };
    Complex z_in_num = c_mul(z0_c, c_add(one, out->gamma_input));
    Complex z_in_den = c_sub(one, out->gamma_input);
    out->z_input = c_div(z_in_num, z_in_den);

    return true;
}

int main(void) {
    Complex z_load = { 75.0, 25.0 };
    LineParams line = {
        .z0 = 50.0,
        .frequency_hz = 2.4e9,
        .length_m = 0.05,
        .velocity_factor = 0.60,
        .attenuation_db_m = 1.5
    };

    ReflectionResult res;
    if (!calculate_reflection(z_load, &line, &res)) {
        printf("Помилка вхідних параметрів\n");
        return 1;
    }

    printf("=== C РЕЗУЛЬТАТИ ===\n");
    printf("Γ_L = %.4f + j(%.4f)\n", res.gamma_load.real, res.gamma_load.imag);
    printf("|Γ| = %.4f, Фаза = %.2f deg\n", res.gamma_mag, res.gamma_phase_deg);
    printf("VSWR = %.2f : 1, Return Loss = %.2f dB\n", res.vswr, res.return_loss_db);
    printf("Передано потужності = %.2f %%\n", res.power_transmitted_pct);
    printf("Z_in = %.2f + j(%.2f) Ом\n", res.z_input.real, res.z_input.imag);

    return 0;
}
