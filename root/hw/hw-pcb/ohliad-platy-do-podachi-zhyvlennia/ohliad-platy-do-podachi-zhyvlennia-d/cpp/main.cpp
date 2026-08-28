#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <format>
#include <algorithm>

namespace pcb {

enum class RailCategory {
    HighVoltage,
    DigitalIo,
    MemoryVddq,
    CoreLogic,
    AnalogVdda
};

struct RailDescriptor {
    std::string name;
    double v_nom{0.0};
    double i_max{0.0};
    double c_uf{0.0};
    RailCategory cat{RailCategory::DigitalIo};
    double r_min_limit{0.0};

    RailDescriptor(std::string_view n, double v, double i, double c, RailCategory category)
        : name(n), v_nom(v), i_max(i), c_uf(c), cat(category) {
        double k_leak = 0.001;
        switch (cat) {
            case RailCategory::HighVoltage: k_leak = 0.0001; break;
            case RailCategory::DigitalIo:   k_leak = 0.002;  break;
            case RailCategory::MemoryVddq:  k_leak = 0.02;   break;
            case RailCategory::CoreLogic:   k_leak = 0.10;   break;
            case RailCategory::AnalogVdda:  k_leak = 0.001;  break;
        }
        r_min_limit = v_nom / (k_leak * i_max);
        if (cat == RailCategory::HighVoltage) r_min_limit = std::max(r_min_limit, 10000.0);
        if (cat == RailCategory::CoreLogic)   r_min_limit = std::max(r_min_limit, 0.15);
    }
};

struct RailMeasurement {
    double r_fwd{0.0};
    double r_rev{0.0};
    bool is_hard_short{false};
    bool is_within_spec{false};

    RailMeasurement(const RailDescriptor& desc, double fwd, double rev)
        : r_fwd(fwd), r_rev(rev) {
        is_hard_short = (r_fwd < 0.05 || r_rev < 0.05);
        is_within_spec = (!is_hard_short && r_fwd >= desc.r_min_limit);
    }
};

} // namespace pcb

int main() {
    using namespace pcb;

    std::vector<RailDescriptor> rails = {
        {"V_IN_12V",  12.0, 3.0,  220.0, RailCategory::HighVoltage},
        {"V_IO_3V3",   3.3, 2.0,  150.0, RailCategory::DigitalIo},
        {"VDDQ_1V2",   1.2, 5.0,  680.0, RailCategory::MemoryVddq},
        {"VCORE_0V9",  0.9, 20.0, 1500.0, RailCategory::CoreLogic}
    };

    std::vector<RailMeasurement> results = {
        {rails[0], 48000.0, 52000.0},
        {rails[1],  2100.0,  2300.0},
        {rails[2],    34.0,    38.0},
        {rails[3],     0.78,    0.82} // 0.78 Ом - норма для ядра FPGA!
    };

    std::cout << "ПЕРЕВІРКА РЕЙОК ЖИВЛЕННЯ ПЕРЕД ВВІМКНЕННЯМ:\n";
    for (size_t i = 0; i < rails.size(); ++i) {
        std::cout << std::format("Рейка {:<10}: V_nom={:>4.1f}В, Поріг={:>7.2f} Ом, Вимір={:>7.2f} Ом -> {}\n",
                                 rails[i].name, rails[i].v_nom, rails[i].r_min_limit, results[i].r_fwd,
                                 results[i].is_within_spec ? "НОРМА (PASS)" : "АВАРІЯ / КЗ (FAIL)");
    }
    return 0;
}
