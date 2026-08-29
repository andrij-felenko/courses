#include "loading.hpp"
#include "verification.hpp"

#include <array>
#include <format>
#include <iostream>
#include <string_view>

// Стенд із розділу: дільник 5.00 В на двох резисторах 1.00 МОм,
// виміряний трьома приладами різного класу, і шина живлення
// з прецизійним шунтом 1.00 Ом у розриві.
namespace {

struct Meter {
    std::string_view name;
    double r_meter;
};

constexpr std::array kMeters{
    Meter{"кишеньковий мультиметр", 1.0e6},
    Meter{"лабораторний мультиметр", 10.0e6},
    Meter{"буфер на польовому вході", 10.0e9}
};

constexpr std::size_t kLabMeter = 1;  // саме його показ піде в протокол

// Значення стенда живлення.
constexpr double kSupply = 5.000;   // виставлено на блоці живлення
constexpr double kShuntDrop = 0.0475;  // мілівольтметр на шунті 1.00 Ом
constexpr double kPinVoltage = 4.886;  // виміряно просто на виводі V_CC чипа
constexpr double kShunt = 1.00;
constexpr int kContacts = 4;  // дві клеми макетки плюс дві перемички

struct DividerSurvey {
    double lab_reading{};
    double lab_restored{};
};

}  // namespace

int main()
{
    const auto node = bench::divider(kSupply, 1.0e6, 1.0e6);
    if (!node) {
        std::cerr << "дільник: " << bench::describe(node.error()) << '\n';
        return 1;
    }
    std::cout << std::format("Вузол дільника: U_th = {:.5f} В, R_th = {:.0f} Ом\n\n",
                             node->u_th, node->r_th);

    DividerSurvey survey;
    for (std::size_t i = 0; i < kMeters.size(); ++i) {
        const auto& meter = kMeters[i];

        const auto direct = bench::reading_of(*node, meter.r_meter);
        if (!direct) {
            std::cerr << meter.name << ": " << bench::describe(direct.error()) << '\n';
            return 1;
        }

        // Обернений хід: за самим лише показом приладу відновлюємо U_th —
        // це і є та корекція, яку роблять руками над журналом.
        const auto restored =
            bench::restore_open_circuit(direct->u_meas, node->r_th, meter.r_meter);
        if (!restored) {
            std::cerr << meter.name << ": " << bench::describe(restored.error()) << '\n';
            return 1;
        }

        std::cout << bench::align_left(meter.name, 26)
                  << std::format("R_m = {:>8.3g} МОм   показ {:.4f} В   "
                                 "δ = {:+6.2f} %   R_m/R_th = {:>8.1f}   {}\n",
                                 meter.r_meter / 1.0e6, direct->u_meas,
                                 direct->error_pct, direct->ratio,
                                 bench::to_string(bench::rule_of_hundred(direct->ratio)))
                  << std::format("{:26}  відновлена U_th = {:.5f} В\n", "", restored->u_true);

        if (i == kLabMeter) {
            survey.lab_reading = direct->u_meas;
            survey.lab_restored = restored->u_true;
        }
    }

    const auto rail =
        bench::contact_resistance(kSupply, kShuntDrop, kPinVoltage, kShunt, kContacts);
    if (!rail) {
        std::cerr << "шина живлення: " << bench::describe(rail.error()) << '\n';
        return 1;
    }

    const auto rail_verdict = bench::contact_verdict(rail->per_contact);
    std::cout << std::format("\nСтрум гілки за шунтом:    {:8.2f} мА\n"
                             "Просідання шини до чипа:  {:8.1f} мВ\n"
                             "Опір шляху живлення:      {:8.3f} Ом на {} контакти\n"
                             "Опір одного контакту:     {:8.3f} Ом   {}\n\n",
                             rail->current * 1000.0, rail->drop * 1000.0,
                             rail->path, kContacts,
                             rail->per_contact, bench::to_string(rail_verdict));

    bench::VerificationLog log;
    log.add("Живлення на виводі V_CC чипа", "В", kSupply, kPinVoltage, 2.0);
    log.add("Середня точка, сирий показ 10 МОм", "В", node->u_th, survey.lab_reading, 1.0);
    log.add("Середня точка після корекції", "В", node->u_th, survey.lab_restored, 1.0);
    log.add("Струм гілки за шунтом", "мА", 45.0, rail->current * 1000.0, 10.0);
    log.note(rail_verdict);

    log.render(std::cout);
    std::cout << std::format("\nЗагальний вердикт вузла: {}\n", bench::to_string(log.overall()));

    // Ненульовий код повернення дає скриптові стенда підставу зупинити прогін.
    return log.overall() == bench::Verdict::Fail ? 1 : 0;
}
