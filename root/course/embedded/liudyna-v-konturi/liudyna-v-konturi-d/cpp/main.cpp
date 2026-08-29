#include <array>
#include <exception>
#include <format>
#include <iostream>

#include "pio.hpp"
#include "simulation.hpp"

int main() {
    using hitl::ControlMode;
    using hitl::Scenario;

    static constexpr std::array kScenarios = {
        Scenario{"Rate, лаг 50 мс — прямий аналоговий лінк", ControlMode::Rate,
                 0.050f},
        Scenario{"Rate, лаг 250 мс — цифровий HD-лінк", ControlMode::Rate, 0.250f},
        Scenario{"Rate, лаг 120 мс сталий", ControlMode::Rate, 0.120f},
        Scenario{"Rate, лаг 120 мс з розкидом +-80 мс", ControlMode::Rate, 0.120f,
                 0.080f},
        Scenario{"Rate, той самий розкид, але з буфером джитера", ControlMode::Rate,
                 0.120f, 0.080f, true},
        Scenario{"Rate, 250 мс + бортове пригнічення PIO", ControlMode::Rate, 0.250f,
                 0.0f, false, true},
        Scenario{"Rate, 250 мс + предиктивний маркер HUD", ControlMode::Rate, 0.250f,
                 0.0f, false, false, true},
        Scenario{"Rate, 250 мс + Expo 0.6 на пульті", ControlMode::Rate, 0.250f,
                 0.0f, false, false, false, 0.6f},
        Scenario{"Angle, 250 мс — швидкий контур перенесено на борт",
                 ControlMode::Angle, 0.250f},
    };

    try {
        std::cout << "=== Людина в контурі: бюджет фази й розкачка оператором ===\n\n";
        std::cout << "Аналітична межа лагу tau_crit = PM_0 / omega_c:\n";
        std::cout << std::format(
            "  FPV-дрон (omega_c = 5.0 рад/с, PM_0 = 65 град): {:.0f} мс\n",
            hitl::CriticalDelay(65.0f, 5.0f) * 1000.0f);
        std::cout << std::format(
            "  ровер    (omega_c = 1.5 рад/с, PM_0 = 60 град): {:.0f} мс\n\n",
            hitl::CriticalDelay(60.0f, 1.5f) * 1000.0f);

        for (const Scenario& sc : kScenarios) {
            std::cout << std::format("--- {}\n", sc.name);
            const hitl::Report r = hitl::Run(sc, std::cout);

            std::cout << std::format(
                "    K_p = {:.2f} | T_L = {:.2f} c | tau_чиста = {:.0f} мс | "
                "PM_0 = {:.0f} град -> PM = {:.0f} град | запас лінка = {:.0f} мс\n",
                r.pilot_gain, r.pilot_lead, r.pure_delay * 1000.0f,
                r.phase_margin0_deg, r.phase_margin_deg, r.link_budget * 1000.0f);
            std::cout << std::format(
                "    коливання {:.2f} Гц, амплітуда {:.1f} град, наростання x{:.2f}, "
                "кореляція стік/гіро {:+.2f}\n",
                r.osc_freq_hz, r.osc_amp_deg, r.osc_growth, r.stick_gyro_corr);
            std::cout << std::format(
                "    насичення моторів {:.0f}% кроків, застигань кадру {}\n",
                r.saturation * 100.0f, r.video_freezes);
            std::cout << std::format("    -> {} (макс. нахил {:.1f} град)\n\n",
                                     r.pio ? "РОЗКАЧКА ОПЕРАТОРОМ (PIO)"
                                           : "контур стійкий",
                                     r.max_angle_deg);
        }
    } catch (const std::exception& e) {
        std::cerr << "модель зібрати не вдалося: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
