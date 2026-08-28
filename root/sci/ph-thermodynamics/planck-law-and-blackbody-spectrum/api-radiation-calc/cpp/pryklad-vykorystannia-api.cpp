#include <iostream>
#include <iomanip>
#include "blackbody.hpp"

int main() {
    constexpr double temp_sun = 5778.0;

    // Обчислення яскравості C++20
    auto rad_res = blackbody::spectral_radiance(500.0e-9, temp_sun);
    if (!rad_res) {
        std::cerr << "Помилка обчислення: " << static_cast<int>(rad_res.error()) << '\n';
        return 1;
    }

    auto peak_res = blackbody::wien_peak(temp_sun);
    std::cout << std::scientific << std::setprecision(3);
    std::cout << "Спектральна яскравість на 500 нм: " << *rad_res << " Вт/(м²·ст·м)\n";
    if (peak_res) {
        std::cout << "Пік випромінювання Віна:          " << (*peak_res * 1.0e9) << " нм\n";
    }

    // Інтегрування у видимому діапазоні
    blackbody::IntegrationConfig cfg{.max_subintervals = 2000, .use_gauss_legendre = true};
    auto band_res = blackbody::integrate_band(temp_sun, 380.0e-9, 780.0e-9, cfg);
    if (band_res) {
        std::cout << "Потужність у видимому спектрі:   " << band_res->integrated_emittance << " Вт/м²\n";
    }

    return 0;
}
