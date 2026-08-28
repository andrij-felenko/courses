#include "darcy_api.h"
#include <iostream>
#include <iomanip>

int main() {
    // Створення пористого середовища (пісковик 250 mD, пористість 22%)
    auto rock = darcy::PorousMedium::from_millidarcy(250.0, 0.22);

    fluid_properties_t water{WATER_VISCOSITY_20C, WATER_DENSITY_20C};
    fluid_properties_t heavy_oil{0.050, 920.0}; // Нафта з в'язкістю 50 сП

    const double area = 0.01;       // 100 см² (0.01 м²)
    const double length = 0.20;     // 20 см (0.20 м)
    const double delta_p = 200000.0; // 200 кПа перепад тиску

    double q_water = darcy_compute_flow_rate(area, rock.permeability_m2(), length, delta_p, &water);
    double q_oil   = darcy_compute_flow_rate(area, rock.permeability_m2(), length, delta_p, &heavy_oil);

    double v_d_water = q_water / area;
    double v_p_water = rock.pore_velocity(v_d_water);

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Проникаюча здатність керна: " << rock.permeability_darcy() << " D (" 
              << rock.permeability_m2() << " м²)\n";
    std::cout << "Витрата води Q: " << q_water * 1.0e6 << " мл/с\n";
    std::cout << "Витрата важкої нафти Q: " << q_oil * 1.0e6 << " мл/с\n";
    std::cout << "Швидкість Дарсі води v_d: " << v_d_water * 1000.0 << " мм/с\n";
    std::cout << "Дійсна порова швидкість води v_p: " << v_p_water * 1000.0 << " мм/с\n";

    return 0;
}
