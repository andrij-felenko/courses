#include "breadboard_parasitics_analyzer.hpp"

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <sstream>
#include <stdexcept>

// Математична константа ln(9) для розрахунку перехідного процесу 10%-90% у колі 1-го порядку:
// v(t) = V_max * (1 - exp(-t/tau)); t_10 = -tau * ln(0.9); t_90 = -tau * ln(0.1);
// t_r = t_90 - t_10 = tau * ln(9) ≈ 2.197224577 * tau
inline constexpr double LN_9 = 2.1972245773362196;
inline constexpr double TWO_PI = 6.2831853071795865;

BreadboardParasiticsAnalyzer::BreadboardParasiticsAnalyzer(const TestBenchConfig& config)
    : config_(config) {
    if (config_.test_resistance_ohm <= 0.0) {
        throw std::invalid_argument("Опір тестового резистора повинен бути додатним.");
    }
    if (config_.probe_capacitance_f < 0.0) {
        throw std::invalid_argument("Ємність щупа не може бути від'ємною.");
    }
    if (config_.test_load_current_a <= 0.0) {
        throw std::invalid_argument("Тестовий струм навантаження повинен бути додатним.");
    }
}

const TestBenchConfig& BreadboardParasiticsAnalyzer::config() const noexcept {
    return config_;
}

void BreadboardParasiticsAnalyzer::setConfig(const TestBenchConfig& config) noexcept {
    config_ = config;
}

double BreadboardParasiticsAnalyzer::calculateTotalCapacitance(double rise_time_s) const {
    if (rise_time_s <= 0.0) {
        return 0.0;
    }
    // C_total = t_r / (ln(9) * R_test)
    return rise_time_s / (LN_9 * config_.test_resistance_ohm);
}

double BreadboardParasiticsAnalyzer::calculateParasiticCapacitance(double rise_time_s) const {
    const double c_total = calculateTotalCapacitance(rise_time_s);
    // Віднімаємо відому власну ємність вимірювального щупа (компенсація нуля вимірювального стенда)
    const double c_parasitic = c_total - config_.probe_capacitance_f;
    return std::max(0.0, c_parasitic);
}

double BreadboardParasiticsAnalyzer::calculateContactResistance(double voltage_drop_v) const {
    if (voltage_drop_v <= 0.0 || config_.test_load_current_a <= 0.0) {
        return 0.0;
    }
    // R_cont = Delta_V / I_load
    return voltage_drop_v / config_.test_load_current_a;
}

double BreadboardParasiticsAnalyzer::calculateCutoffFrequency(double capacitance_f) const {
    if (capacitance_f <= 1.0e-15 || config_.test_resistance_ohm <= 0.0) {
        return 0.0;
    }
    // f_-3dB = 1 / (2 * pi * R * C)
    return 1.0 / (TWO_PI * config_.test_resistance_ohm * capacitance_f);
}

ContactHealth BreadboardParasiticsAnalyzer::assessContactHealth(double contact_resistance_ohm) const noexcept {
    // Критерії оцінки контактних затискачів безпаяльних макетних плат:
    // < 50 мОм: новий пружинний контакт із фосфористої бронзи
    // 50..200 мОм: прийнятний робочий контакт (допустиме поверхневе окиснення)
    // > 200 мОм: зношений, ослаблений або сильно окислений затискач
    if (contact_resistance_ohm < 0.050) {
        return ContactHealth::New;
    }
    if (contact_resistance_ohm <= 0.200) {
        return ContactHealth::Acceptable;
    }
    return ContactHealth::Degraded;
}

double BreadboardParasiticsAnalyzer::extractContactVoltageDrop(const OscilloscopeTrace& load_trace) const {
    const auto& samples = load_trace.samples();
    if (samples.size() < 4) {
        return 0.0;
    }

    // Визначаємо напругу холостого ходу V_idle (початок осцилограми без струму)
    // та мінімальну стабільну напругу під час протікання імпульсу навантаження V_loaded
    const std::size_t init_count = std::max<std::size_t>(2, samples.size() / 10);
    double v_idle_sum = 0.0;
    for (std::size_t i = 0; i < init_count; ++i) {
        v_idle_sum += samples[i].voltage_v;
    }
    const double v_idle = v_idle_sum / static_cast<double>(init_count);

    double v_min = v_idle;
    for (const auto& pt : samples) {
        if (pt.voltage_v < v_min) {
            v_min = pt.voltage_v;
        }
    }

    const double drop = v_idle - v_min;
    return std::max(0.0, drop);
}

ParasiticReport BreadboardParasiticsAnalyzer::analyze(const OscilloscopeTrace& step_trace,
                                                      double contact_voltage_drop_v) const {
    ParasiticReport report;

    // 1. Аналіз перехідного процесу наростання напруги
    const auto rise_time_opt = step_trace.calculateRiseTime(0.10, 0.90);
    const double rise_time_s = rise_time_opt.value_or(0.0);
    report.rise_time_ns = rise_time_s * 1.0e9;

    // 2. Обчислення ємнісних параметрів
    const double c_total_f = calculateTotalCapacitance(rise_time_s);
    const double c_par_f = calculateParasiticCapacitance(rise_time_s);
    report.total_capacitance_pf = c_total_f * 1.0e12;
    report.parasitic_capacitance_pf = c_par_f * 1.0e12;

    // 3. Розрахунок граничної частоти зрізу RC-ланцюга
    const double cutoff_hz = calculateCutoffFrequency(c_par_f);
    report.cutoff_frequency_mhz = cutoff_hz / 1.0e6;

    // 4. Обчислення контактного опору
    report.voltage_drop_mv = contact_voltage_drop_v * 1000.0;
    const double r_cont_ohm = calculateContactResistance(contact_voltage_drop_v);
    report.contact_resistance_mohm = r_cont_ohm * 1000.0;
    report.health = assessContactHealth(r_cont_ohm);

    // 5. Формування інженерних висновків та рекомендацій
    std::ostringstream oss;
    oss << "Стан контактної групи: " << contactHealthToString(report.health) << ". ";

    if (report.health == ContactHealth::New) {
        oss << "Низький опір контакту (<50 мОм), придатний для живлення з пульсаціями струму до 1 А. ";
    } else if (report.health == ContactHealth::Acceptable) {
        oss << "Опір у межах робочої норми. Рекомендовано обмежити тривалий струм до 0.5 А. ";
    } else {
        oss << "УВАГА: контакт деградований (>200 мОм)! Ризик просідання VCC та локального нагріву. ";
    }

    if (report.parasitic_capacitance_pf <= 3.0) {
        oss << "Паразитна ємність рейок у типових межах (1-3 пФ). "
            << "Макет придатний для I2C (до 400 кГц) та помірних SPI шин (до 10 МГц).";
    } else {
        oss << "Підвищена міжрейкова ємність ("
            << std::fixed << std::setprecision(1) << report.parasitic_capacitance_pf
            << " пФ). Можливі завали фронтів та ємнісні перехресні завади (crosstalk).";
    }

    report.notes = oss.str();
    return report;
}

ParasiticReport BreadboardParasiticsAnalyzer::analyze(const OscilloscopeTrace& step_trace,
                                                      const OscilloscopeTrace& load_trace) const {
    const double drop_v = extractContactVoltageDrop(load_trace);
    return analyze(step_trace, drop_v);
}
