#include <iostream>
#include <vector>
#include <cmath>
#include <complex>
#include <random>
#include <numeric>
#include <iomanip>
#include <algorithm>

constexpr double PI = 3.14159265358979323846;
constexpr double CS_FREQ = 9192631770.0; // Фундаментальна частота Цезію-133 (Гц)

// Квантова фізична модель Рамзі
class RamseyPhysics {
public:
    RamseyPhysics(double pulse_duration_tau, double drift_time_T, size_t atom_count)
        : tau_(pulse_duration_tau), T_(drift_time_T), N_atoms_(atom_count), rng_(42) {}

    // Обчислення точної квантовомеханічної ймовірності переходу P_ge
    double compute_probability(double frequency_detuning_hz) const {
        double delta = 2.0 * PI * frequency_detuning_hz; // Розбудова в рад/с
        double omega_rabi = PI / (2.0 * tau_);          // Умова pi/2 імпульсу
        double omega_eff = std::sqrt(omega_rabi * omega_rabi + delta * delta);

        double sin_pulse = std::sin(omega_eff * tau_ / 2.0);
        double cos_pulse = std::cos(omega_eff * tau_ / 2.0);

        // Формула Рамзі з урахуванням тривалості імпульсів tau та дрейфу T
        double term1 = cos_pulse * std::cos(delta * T_ / 2.0);
        double term2 = (delta / omega_eff) * sin_pulse * std::sin(delta * T_ / 2.0);
        double bracket = term1 - term2;

        double p_rabi = 4.0 * (omega_rabi * omega_rabi / (omega_eff * omega_eff)) * (sin_pulse * sin_pulse);
        double p_ramsey = p_rabi * (bracket * bracket);

        return std::clamp(p_ramsey, 0.0, 1.0);
    }

    // Симуляція вимірювання флуоресценції з урахуванням квантового дробового шуму
    double measure_transition_fraction(double frequency_detuning_hz) {
        double p_true = compute_probability(frequency_detuning_hz);
        std::normal_distribution<double> shot_noise(0.0, std::sqrt(p_true * (1.0 - p_true) / N_atoms_));
        double measured_p = p_true + shot_noise(rng_);
        return std::clamp(measured_p, 0.0, 1.0);
    }

    double get_drift_time() const { return T_; }

private:
    double tau_;
    double T_;
    size_t N_atoms_;
    std::mt19937_64 rng_;
};

// Цифровий PID-серворегулятор частоти
class FrequencyServoPID {
public:
    FrequencyServoPID(double Kp, double Ki, double Kd)
        : Kp_(Kp), Ki_(Ki), Kd_(Kd), integral_(0.0), prev_error_(0.0) {}

    double update(double error, double dt) {
        integral_ += error * dt;
        double derivative = (error - prev_error_) / dt;
        prev_error_ = error;
        return Kp_ * error + Ki_ * integral_ + Kd_ * derivative;
    }

    void reset() {
        integral_ = 0.0;
        prev_error_ = 0.0;
    }

private:
    double Kp_, Ki_, Kd_;
    double integral_;
    double prev_error_;
};

// Обчислювач двовибіркової девіації Аллана sigma_y(tau)
class AllanDeviationCalculator {
public:
    static std::vector<std::pair<double, double>> compute(const std::vector<double>& y_series, double sampling_dt) {
        std::vector<std::pair<double, double>> result;
        size_t N = y_series.size();

        // Обчислюємо девіацію для різних інтервалів усереднення tau = m * dt
        for (size_t m = 1; m <= N / 4; m *= 2) {
            double tau = m * sampling_dt;
            size_t K = N / m;
            std::vector<double> bar_y(K, 0.0);

            for (size_t i = 0; i < K; ++i) {
                double sum = 0.0;
                for (size_t j = 0; j < m; ++j) {
                    sum += y_series[i * m + j];
                }
                bar_y[i] = sum / static_cast<double>(m);
            }

            double sum_sq_diff = 0.0;
            for (size_t i = 0; i < K - 1; ++i) {
                double diff = bar_y[i + 1] - bar_y[i];
                sum_sq_diff += diff * diff;
            }

            double sigma_sq = sum_sq_diff / (2.0 * static_cast<double>(K - 1));
            result.emplace_back(tau, std::sqrt(sigma_sq));
        }

        return result;
    }
};

int main() {
    std::cout << "=== Симуляція цезієвого атомного годинника та сервоконтуру ===" << std::endl;

    // Фізичні параметри фонтана: tau = 10 мс, T = 0.5 с, N = 10^6 атомів
    RamseyPhysics clock_physics(0.010, 0.500, 1000000);
    FrequencyServoPID pid(0.4, 0.1, 0.01);

    double vcxo_frequency = CS_FREQ + 0.15; // Початкове відхилення генератора +0.15 Гц
    double dt = 1.0;                        // Цикл вимірювання = 1 секунда
    size_t total_steps = 1000;              // 1000 секунд роботи

    std::vector<double> relative_freq_history;
    relative_freq_history.reserve(total_steps);

    // Модуляційний зсув для квадратного розгортання частоти (Lock-in modulation)
    double mod_offset = 1.0 / (4.0 * clock_physics.get_drift_time()); // +/- 0.5 Гц

    for (size_t step = 0; step < total_steps; ++step) {
        // Крок 1: Вимірювання ймовірності на лівому схилі розбудови (f - mod_offset)
        double p_left = clock_physics.measure_transition_fraction(vcxo_frequency - CS_FREQ - mod_offset);

        // Крок 2: Вимірювання ймовірності на правому схилі розбудови (f + mod_offset)
        double p_right = clock_physics.measure_transition_fraction(vcxo_frequency - CS_FREQ + mod_offset);

        // Крок 3: Сигнал похибки дискримінатора
        double error_signal = p_right - p_left;

        // Крок 4: Обчислення корекції частоти PID-регулятором
        double freq_correction = pid.update(error_signal, dt);
        vcxo_frequency -= freq_correction;

        // Збереження відносного відхилення частоти y(t) = (f - f0) / f0
        double y_val = (vcxo_frequency - CS_FREQ) / CS_FREQ;
        relative_freq_history.push_back(y_val);

        if (step % 200 == 0 || step == total_steps - 1) {
            std::cout << "Крок " << std::setw(4) << step 
                      << " | Частота: " << std::fixed << std::setprecision(6) << vcxo_frequency << " Гц"
                      << " | Похибка y(t): " << std::scientific << std::setprecision(3) << y_val << std::endl;
        }
    }

    // Крок 5: Обчислення девіації Аллана
    std::cout << "\n=== Обчислення девіації Аллана sigma_y(tau) ===" << std::endl;
    auto adev_results = AllanDeviationCalculator::compute(relative_freq_history, dt);

    for (const auto& [tau, adev] : adev_results) {
        std::cout << "tau = " << std::setw(4) << static_cast<int>(tau) << " с | sigma_y(tau) = " 
                  << std::scientific << std::setprecision(3) << adev << std::endl;
    }

    return 0;
}
