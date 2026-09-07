#include "lcr_meter.hpp"
#include <numbers>
#include <algorithm>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

LCRMeter::LCRMeter(double test_frequency_hz) {
    set_frequency(test_frequency_hz);
    reset_calibration();
}

void LCRMeter::set_frequency(double test_frequency_hz) {
    frequency_hz_ = (test_frequency_hz > 0.0) ? test_frequency_hz : 1000.0;
    omega_ = 2.0 * M_PI * frequency_hz_;
}

void LCRMeter::reset_calibration() noexcept {
    z_short_ = {0.0, 0.0};
    y_open_ = {0.0, 0.0};
    has_open_cal_ = false;
    has_short_cal_ = false;
}

void LCRMeter::calibrate_open(const std::complex<double>& z_open_raw) {
    /* Паразитний адмітанс розімкнених щупів Y_open = 1 / Z_open */
    if (std::abs(z_open_raw) > 1e-9) {
        y_open_ = 1.0 / z_open_raw;
        has_open_cal_ = true;
    }
}

void LCRMeter::calibrate_short(const std::complex<double>& z_short_raw) {
    /* Паразитний залишковий опір замкнених контактів Z_short */
    z_short_ = z_short_raw;
    has_short_cal_ = true;
}

MeasurementResult LCRMeter::measure(const std::complex<double>& z_raw) const {
    MeasurementResult res{};
    res.z_raw = z_raw;

    /*
     * Повна формула векторної компенсації паразитних ланцюгів:
     *                 Z_raw - Z_short
     * Z_DUT = -------------------------------
     *          1 - (Z_raw - Z_short) * Y_open
     */
    std::complex<double> z_diff = z_raw - z_short_;
    std::complex<double> denominator = 1.0 - z_diff * y_open_;

    if (std::abs(denominator) > 1e-12) {
        res.z_corrected = z_diff / denominator;
    } else {
        res.z_corrected = z_diff;
    }

    // Послідовна еквівалентна схема (Series Model: Z = Rs + j*Xs)
    res.r_series = res.z_corrected.real();
    res.x_series = res.z_corrected.imag();
    res.phase_deg = std::arg(res.z_corrected) * (180.0 / M_PI);

    // Розрахунок реактивних компонентів Ls та Cs
    if (res.x_series < -1e-9) {
        // Ємнісний характер імпедансу: X = -1 / (omega * Cs)  =>  Cs = -1 / (omega * X)
        res.c_series = -1.0 / (omega_ * res.x_series);
        res.l_series = 0.0;
    } else if (res.x_series > 1e-9) {
        // Індуктивний характер імпедансу: X = omega * Ls  =>  Ls = X / omega
        res.l_series = res.x_series / omega_;
        res.c_series = 0.0;
    } else {
        res.c_series = 0.0;
        res.l_series = 0.0;
    }

    // Розрахунок добротності (Q) та тангенса кута втрат (D)
    double abs_r = std::abs(res.r_series);
    double abs_x = std::abs(res.x_series);

    if (abs_r > 1e-9) {
        res.quality_factor = abs_x / abs_r;
    } else {
        res.quality_factor = 1e6;
    }

    if (abs_x > 1e-9) {
        res.dissipation_factor = abs_r / abs_x;
    } else {
        res.dissipation_factor = 1e6;
    }

    // Паралельна еквівалентна схема (Parallel Model: Y = 1/Rp + j*B)
    std::complex<double> y_dut = (std::abs(res.z_corrected) > 1e-12) ? (1.0 / res.z_corrected) : 0.0;
    double g_parallel = y_dut.real(); // 1 / Rp
    double b_parallel = y_dut.imag(); // Сусцептанс B

    res.r_parallel = (g_parallel > 1e-15) ? (1.0 / g_parallel) : 1e12;

    if (b_parallel > 1e-12) {
        // Паралельна ємність Cp = B / omega
        res.c_parallel = b_parallel / omega_;
        res.l_parallel = 0.0;
    } else if (b_parallel < -1e-12) {
        // Паралельна індуктивність Lp = -1 / (omega * B)
        res.l_parallel = -1.0 / (omega_ * b_parallel);
        res.c_parallel = 0.0;
    } else {
        res.c_parallel = 0.0;
        res.l_parallel = 0.0;
    }

    return res;
}
