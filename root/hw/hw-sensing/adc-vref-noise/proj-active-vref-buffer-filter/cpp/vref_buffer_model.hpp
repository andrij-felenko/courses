#pragma once

#include <cmath>
#include <vector>
#include <string>
#include <iostream>
#include <iomanip>

namespace sensing {

/**
 * @brief Модель параметрів прецизійного операційного підсилювача
 */
class OpAmpModel {
public:
    double gbw_hz;          // Добуток підсилення на смугу (Gain Bandwidth Product), Гц
    double aol_db;          // Підсилення розімкненої петлі на постійному струмі, дБ
    double r_out_open_ohm;  // Внутрішній розімкнений вихідний опір ОП, Ом
    double slew_rate_v_us;  // Швидкість наростання вихідної напруги, В/мкс

    OpAmpModel(double gbw, double aol, double r_out, double sr)
        : gbw_hz(gbw), aol_db(aol), r_out_open_ohm(r_out), slew_rate_v_us(sr) {}

    [[nodiscard]] double dominant_pole_hz() const noexcept {
        double aol_linear = std::pow(10.0, aol_db / 20.0);
        return gbw_hz / aol_linear;
    }
};

/**
 * @brief Схемотехнічні параметри петлі з in-loop компенсацією
 */
class InLoopCompensation {
public:
    double r_iso_ohm;   // Ізолюючий резистор між виходом ОП і ємністю, Ом
    double r_f_ohm;     // Резистор зворотного зв'язку DC, Ом
    double c_f_f;       // Конденсатор швидкого високочастотного зворотного зв'язку, Ф
    double c_load_f;    // Накопичувальна навантажувальна ємність VREF, Ф

    InLoopCompensation(double r_iso, double r_f, double c_f, double c_load)
        : r_iso_ohm(r_iso), r_f_ohm(r_f), c_f_f(c_f), c_load_f(c_load) {}

    [[nodiscard]] bool is_stable() const noexcept {
        // Умова компенсації затримки фази: C_f >= C_load * (R_iso / R_f)
        return c_f_f >= (c_load_f * (r_iso_ohm / r_f_ohm));
    }

    [[nodiscard]] double compensation_ratio() const noexcept {
        return c_f_f / (c_load_f * (r_iso_ohm / r_f_ohm));
    }
};

/**
 * @brief Результат числової симуляції перехідного процесу
 */
struct SimulationResult {
    double time_step_s;
    std::vector<double> time_points;
    std::vector<double> vref_voltages;
    double max_voltage_drop_v;
    double final_settling_error_v;
    double error_in_lsb;
    bool meets_half_lsb_spec;
};

/**
 * @brief Симулятор перехідного процесу відновлення напруги VREF після імпульсу CDAC
 */
class VrefBufferSimulator {
private:
    OpAmpModel opamp_;
    InLoopCompensation comp_;
    double vref_nominal_v_;
    int adc_bits_;

public:
    VrefBufferSimulator(const OpAmpModel& opamp, const InLoopCompensation& comp,
                        double vref_nominal, int bits)
        : opamp_(opamp), comp_(comp), vref_nominal_v_(vref_nominal), adc_bits_(bits) {}

    [[nodiscard]] double lsb_voltage() const noexcept {
        return vref_nominal_v_ / std::pow(2.0, adc_bits_);
    }

    /**
     * @brief Числова симуляція відновлення заряду на комутованій ємності CDAC
     * @param charge_pulse_c Заряд, спожитий матрицею CDAC під час перемикання (Кл)
     * @param settling_time_s Тривалість такту порозрядного зрівноваження (с)
     * @param num_steps Кількість кроків дискретизації за часом
     */
    SimulationResult simulate_step_response(double charge_pulse_c,
                                           double settling_time_s,
                                           size_t num_steps = 1000) const {
        SimulationResult result;
        result.time_step_s = settling_time_s / static_cast<double>(num_steps);
        result.time_points.reserve(num_steps);
        result.vref_voltages.reserve(num_steps);

        // Миттєвий стрибок просідання напруги на виводі VREF: delta_V = Q / C_load
        double delta_v_initial = charge_pulse_c / comp_.c_load_f;
        result.max_voltage_drop_v = delta_v_initial;

        double v_vref = vref_nominal_v_ - delta_v_initial;
        double v_opamp_out = vref_nominal_v_;
        double dt = result.time_step_s;

        // Еквівалентна стала часу відновлення петлі ОП
        double r_effective = comp_.r_iso_ohm + (opamp_.r_out_open_ohm / (1.0 + opamp_.gbw_hz * 2.0 * M_PI * dt));
        double tau_vref = r_effective * comp_.c_load_f;

        for (size_t step = 0; step < num_steps; ++step) {
            double current_time = static_cast<double>(step) * dt;
            result.time_points.push_back(current_time);
            result.vref_voltages.push_back(v_vref);

            // Оновлення напруги виходу підсилювача з урахуванням швидкості наростання
            double target_out = vref_nominal_v_ + (vref_nominal_v_ - v_vref) * (comp_.r_f_ohm / comp_.r_iso_ohm);
            double dv_max = opamp_.slew_rate_v_us * 1.0e6 * dt;
            double dv = target_out - v_opamp_out;
            if (std::abs(dv) > dv_max) {
                dv = (dv > 0) ? dv_max : -dv_max;
            }
            v_opamp_out += dv;

            // Експоненційне відновлення потенціалу на навантажувальному конденсаторі
            double d_vref = (v_opamp_out - v_vref) * (dt / tau_vref);
            v_vref += d_vref;
        }

        result.final_settling_error_v = std::abs(vref_nominal_v_ - v_vref);
        double lsb = lsb_voltage();
        result.error_in_lsb = result.final_settling_error_v / lsb;
        result.meets_half_lsb_spec = (result.error_in_lsb < 0.5);

        return result;
    }
};

} // namespace sensing
