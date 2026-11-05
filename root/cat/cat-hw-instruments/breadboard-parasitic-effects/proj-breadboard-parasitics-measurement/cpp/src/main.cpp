#include "oscilloscope_trace.hpp"
#include "breadboard_parasitics_analyzer.hpp"

#include <cmath>
#include <iomanip>
#include <iostream>
#include <random>
#include <string>

/**
 * @brief Генерація змодельованої осцилограми перехідного процесу заряджання ємності через опір (RC-ланцюг).
 *
 * Модель сигналу: v(t) = v_start + (v_final - v_start) * (1 - exp(-(t - t_step) / tau)) + шум
 */
static OscilloscopeTrace generateRcStepTrace(double v_start,
                                             double v_final,
                                             double r_ohm,
                                             double c_total_f,
                                             double step_time_s,
                                             double duration_s,
                                             double sample_interval_s,
                                             std::mt19937& rng) {
    OscilloscopeTrace trace;
    const double tau = r_ohm * c_total_f;
    std::normal_distribution<double> noise_dist(0.0, 0.003); // Невеликий шум АЦП (3 мВ СКО)

    for (double t = 0.0; t <= duration_s; t += sample_interval_s) {
        double v = v_start;
        if (t >= step_time_s) {
            const double dt = t - step_time_s;
            v = v_start + (v_final - v_start) * (1.0 - std::exp(-dt / tau));
        }
        v += noise_dist(rng);
        trace.addSample(t, v);
    }

    return trace;
}

/**
 * @brief Генерація змодельованої осцилограми падіння напруги на контакті під час імпульсу навантаження.
 *
 * Модель сигналу: у стані спокою напруга V_supply, під час імпульсу струму I_load
 * напруга просідає на величину Delta_V = I_load * R_contact.
 */
static OscilloscopeTrace generateLoadPulseTrace(double v_supply,
                                                double r_contact_ohm,
                                                double i_load_a,
                                                double pulse_start_s,
                                                double pulse_duration_s,
                                                double duration_s,
                                                double sample_interval_s,
                                                std::mt19937& rng) {
    OscilloscopeTrace trace;
    const double pulse_end_s = pulse_start_s + pulse_duration_s;
    const double v_drop = i_load_a * r_contact_ohm;
    std::normal_distribution<double> noise_dist(0.0, 0.002); // Шум вимірювання 2 мВ

    for (double t = 0.0; t <= duration_s; t += sample_interval_s) {
        double v = v_supply;
        if (t >= pulse_start_s && t <= pulse_end_s) {
            v = v_supply - v_drop;
        }
        v += noise_dist(rng);
        trace.addSample(t, v);
    }

    return trace;
}

/**
 * @brief Форматоване виведення результатів діагностичного звіту в консоль.
 */
static void printReport(const std::string& title, const ParasiticReport& rep) {
    std::cout << "======================================================================\n";
    std::cout << "  " << title << "\n";
    std::cout << "======================================================================\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "  Час наростання фронту (t_r 10%-90%):    " << std::setw(8) << rep.rise_time_ns << " нс\n";
    std::cout << "  Повна виміряна ємність (C_total):        " << std::setw(8) << rep.total_capacitance_pf << " пФ\n";
    std::cout << "  Паразитна міжрейкова ємність (C_par):    " << std::setw(8) << rep.parasitic_capacitance_pf << " пФ\n";
    std::cout << "  Гранична частота зрізу RC (f_-3dB):      " << std::setw(8) << rep.cutoff_frequency_mhz << " МГц\n";
    std::cout << "  Падіння напруги під навантаженням:       " << std::setw(8) << rep.voltage_drop_mv << " мВ\n";
    std::cout << "  Контактний перехідний опір (R_cont):     " << std::setw(8) << rep.contact_resistance_mohm << " мОм\n";
    std::cout << "  Стан пружинного затискача:               " << contactHealthToString(rep.health) << "\n";
    std::cout << "----------------------------------------------------------------------\n";
    std::cout << "  Інженерний висновок:\n  " << rep.notes << "\n";
    std::cout << "======================================================================\n\n";
}

int main() {
    std::cout << "\n";
    std::cout << "======================================================================\n";
    std::cout << "   ДІАГНОСТИКА ПАРАЗИТНИХ ЕФЕКТІВ БЕЗПАЯЛЬНИХ МАКЕТНИХ ПЛАТ (C++)\n";
    std::cout << "   Визначення міжрейкової ємності та контактного опору за осцилограмами\n";
    std::cout << "======================================================================\n\n";

    // Налаштування вимірювального стенда:
    // - Тестовий резистор: R_test = 10 кОм (10000 Ом) для створення вимірюваного RC-перехідного процесу
    // - Власна вхідна ємність щупа осцилографа: C_probe = 12.0 пФ (стандартний пасивний щуп 10X)
    // - Тестовий струм навантаження для імпульсного заміру опору: I_test = 0.5 А
    TestBenchConfig bench_cfg;
    bench_cfg.test_resistance_ohm = 10000.0;
    bench_cfg.probe_capacitance_f = 12.0e-12;
    bench_cfg.test_load_current_a = 0.5;

    std::cout << "Параметри вимірювального стенда:\n";
    std::cout << " - Опір тестового резистора (R_test):    " << bench_cfg.test_resistance_ohm << " Ом\n";
    std::cout << " - Власна ємність щупа (C_probe 10X):     " << (bench_cfg.probe_capacitance_f * 1.0e12) << " пФ\n";
    std::cout << " - Струм імпульсного навантаження:       " << bench_cfg.test_load_current_a << " А\n\n";

    BreadboardParasiticsAnalyzer analyzer(bench_cfg);

    // Ініціалізація фіксованого генератора випадкових чисел для повторюваності шуму
    std::mt19937 rng(42);

    // --------------------------------------------------------------------------------
    // Сценарій 1: Нова якісна макетна плата (фосфориста бронза, крок 2.54 мм)
    // Очікувані фізичні параметри:
    // - Міжрейкова паразитна ємність C_par ≈ 2.2 пФ -> Разом зі щупом C_total ≈ 14.2 пФ
    // - Контактний опір R_cont ≈ 32 мОм -> Падіння при 0.5 А складе ~16 мВ
    // --------------------------------------------------------------------------------
    const double expected_c_par_1 = 2.2e-12;
    const double expected_c_total_1 = expected_c_par_1 + bench_cfg.probe_capacitance_f;
    const double expected_r_cont_1 = 0.032; // 32 мОм

    // Генерація оцифрованих осцилограм (дискретизація 1 нс для фронту, 0.5 мкс для навантаження)
    OscilloscopeTrace step_trace_1 = generateRcStepTrace(
        0.0, 3.3, bench_cfg.test_resistance_ohm, expected_c_total_1,
        100.0e-9, 1200.0e-9, 1.0e-9, rng
    );
    step_trace_1.filterOutliers();

    OscilloscopeTrace load_trace_1 = generateLoadPulseTrace(
        5.0, expected_r_cont_1, bench_cfg.test_load_current_a,
        10.0e-6, 20.0e-6, 50.0e-6, 0.5e-6, rng
    );
    load_trace_1.filterOutliers();

    // Запуск аналізу
    ParasiticReport report_1 = analyzer.analyze(step_trace_1, load_trace_1);
    printReport("ЗРАЗОК 1: Нова якісна безпаяльна макетна плата", report_1);

    // --------------------------------------------------------------------------------
    // Сценарій 2: Зношена / окислена дешева макетна плата
    // Очікувані фізичні параметри:
    // - Збільшена міжрейкова ємність C_par ≈ 4.8 пФ (забруднення, залишкова паста, зсув шин)
    // - Деградований контактний опір R_cont ≈ 380 мОм (втома пружинних пелюсток, окислення)
    // --------------------------------------------------------------------------------
    const double expected_c_par_2 = 4.8e-12;
    const double expected_c_total_2 = expected_c_par_2 + bench_cfg.probe_capacitance_f;
    const double expected_r_cont_2 = 0.380; // 380 мОм

    OscilloscopeTrace step_trace_2 = generateRcStepTrace(
        0.0, 3.3, bench_cfg.test_resistance_ohm, expected_c_total_2,
        100.0e-9, 1500.0e-9, 1.0e-9, rng
    );
    step_trace_2.filterOutliers();

    OscilloscopeTrace load_trace_2 = generateLoadPulseTrace(
        5.0, expected_r_cont_2, bench_cfg.test_load_current_a,
        10.0e-6, 20.0e-6, 50.0e-6, 0.5e-6, rng
    );
    load_trace_2.filterOutliers();

    ParasiticReport report_2 = analyzer.analyze(step_trace_2, load_trace_2);
    printReport("ЗРАЗОК 2: Зношена / окислена макетна плата (дефектні затискачі)", report_2);

    // --------------------------------------------------------------------------------
    // Підсумкові інженерні висновки для макетування начорно
    // --------------------------------------------------------------------------------
    std::cout << "ПРАКТИЧНІ РЕКОМЕНДАЦІЇ ДЛЯ ІНЖЕНЕРА-РОЗРОБНИКА:\n";
    std::cout << "1. Компенсація щупа осцилографа є критичною: ємність щупа 10X (~12 пФ)\n";
    std::cout << "   у 4-6 разів перевищує власну ємність контактів макетки (1-3 пФ).\n";
    std::cout << "2. Контактний опір > 200 мОм створює неприпустиме просідання шин живлення\n";
    std::cout << "   (Delta_V = I * R) при комутації мікроконтролерів і Wi-Fi/BLE передавачів.\n";
    std::cout << "3. Обов'язково встановлюйте керамічні блокувальні конденсатори 100 нФ\n";
    std::cout << "   безпосередньо біля виводів живлення кожної мікросхеми на макеті.\n\n";

    return 0;
}
