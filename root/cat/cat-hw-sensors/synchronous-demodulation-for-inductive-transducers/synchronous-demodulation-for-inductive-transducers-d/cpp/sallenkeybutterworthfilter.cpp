#include <cmath>
#include <iostream>

class SallenKeyButterworthFilter {
public:
    struct ComponentValues {
        double r1_ohms;
        double r2_ohms;
        double c1_farads;
        double c2_farads;
        double cutoff_freq_hz;
        double quality_factor;
    };

    static ComponentValues calculate(double target_f0_hz, double base_c2_farads) {
        ComponentValues vals;
        vals.cutoff_freq_hz = target_f0_hz;
        vals.c2_farads = base_c2_farads;
        vals.c1_farads = 2.0 * base_c2_farads; // Для характеристики Баттерворта
        vals.r1_ohms = 1.0 / (2.0 * M_PI * target_f0_hz * base_c2_farads * std::sqrt(2.0));
        vals.r2_ohms = vals.r1_ohms;
        vals.quality_factor = 1.0 / std::sqrt(2.0);
        return vals;
    }
};
