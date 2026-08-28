#include <iostream>
#include <vector>
#include <cmath>
#include <complex>
#include <iomanip>
#include <string>

// Фізичні константи
constexpr double PI = 3.14159265358979323846;

// Структура для збереження входжувальних параметрів оптичної системи
struct OpticalSetup {
    double n1 = 1.52;             // Показник заломлення скляної призми (крон)
    double n2 = 1.00;             // Показник заломлення проміжного зазору (повітря)
    double n3 = 1.52;             // Показник заломлення вихідної призми
    double wavelength_nm = 632.8; // Довжина хвилі червоного гелій-неонового лазера (нм)
    double theta_deg = 45.0;      // Кут падіння світла у першому середовищі (град)
};

// Структура для результатів обчислення еванесцентного поля
struct FieldResults {
    double theta_c_deg;
    double kappa_z_nm;     // Коефіцієнт згасання (1/нм)
    double d_p_nm;         // Глибина проникнення амплітуди поля (нм)
    double d_I_nm;         // Глибина згасання інтенсивності поля (нм)
    double k_x_nm;         // Тангенціальне хвильове число (1/нм)
    bool is_total_reflection;
};

// Функція розрахунку параметрів еванесцентної хвилі
FieldResults analyze_evanescent_wave(const OpticalSetup& setup) {
    FieldResults res{};
    
    // Перевірка умови існування кута ПВВ
    if (setup.n1 <= setup.n2) {
        res.is_total_reflection = false;
        return res;
    }

    res.theta_c_deg = std::asin(setup.n2 / setup.n1) * (180.0 / PI);
    res.is_total_reflection = (setup.theta_deg > res.theta_c_deg);

    if (res.is_total_reflection) {
        double theta_rad = setup.theta_deg * (PI / 180.0);
        double k0 = 2.0 * PI / setup.wavelength_nm;
        double sin_theta = std::sin(theta_rad);

        // Обчислення тангенціального числа та коефіцієнта згасання
        res.k_x_nm = k0 * setup.n1 * sin_theta;
        double rad_val = setup.n1 * setup.n1 * sin_theta * sin_theta - setup.n2 * setup.n2;
        res.kappa_z_nm = k0 * std::sqrt(rad_val);
        
        res.d_p_nm = 1.0 / res.kappa_z_nm;
        res.d_I_nm = res.d_p_nm / 2.0;
    }

    return res;
}

// Розрахунок коефіцієнта тунелювання FTIR для s- та p-поляризацій
double calculate_ftir_transmission(const OpticalSetup& setup, double gap_d_nm, bool is_p_pol = false) {
    double theta_rad = setup.theta_deg * (PI / 180.0);
    double k0 = 2.0 * PI / setup.wavelength_nm;
    double sin_theta = std::sin(theta_rad);
    double cos_theta = std::cos(theta_rad);

    double kappa_z = k0 * std::sqrt(setup.n1 * setup.n1 * sin_theta * sin_theta - setup.n2 * setup.n2);

    double p1, p2;
    if (!is_p_pol) {
        // s-поляризація (TE)
        p1 = setup.n1 * cos_theta;
        p2 = kappa_z / k0; // Уявна адмітанс-складова
    } else {
        // p-поляризація (TM)
        p1 = cos_theta / setup.n1;
        p2 = (kappa_z / k0) / (setup.n2 * setup.n2);
    }

    double A = std::pow(p1 * p1 + p2 * p2, 2.0) / (4.0 * p1 * p1 * p2 * p2);
    
    // Запобігання переповненню sinh при великих d
    double arg = kappa_z * gap_d_nm;
    if (arg > 20.0) {
        // Асимптотичне наближення для великих зазорів
        return (4.0 / A) * std::exp(-2.0 * arg);
    }

    double sinh_val = std::sinh(arg);
    return 1.0 / (1.0 + A * sinh_val * sinh_val);
}

int main() {
    OpticalSetup setup;
    FieldResults res = analyze_evanescent_wave(setup);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "===================================================================\n";
    std::cout << "   ЧИСЕЛЬНЕ МОДЕЛЬУВАННЯ ЕВАНЕСЦЕНТНОЇ ХВИЛІ ТА ТУНЕЛЬУВАННЯ FTIR\n";
    std::cout << "===================================================================\n";
    std::cout << "Параметри системи:\n";
    std::cout << "  - Показник заломлення скляної призми n1: " << setup.n1 << "\n";
    std::cout << "  - Показник заломлення зазору (повітря) n2: " << setup.n2 << "\n";
    std::cout << "  - Довжина хвилі лазера lambda0:            " << setup.wavelength_nm << " нм\n";
    std::cout << "  - Заданий кут падіння theta1:              " << setup.theta_deg << " deg\n";
    std::cout << "  - Обчислений критичний кут theta_c:        " << res.theta_c_deg << " deg\n\n";

    if (!res.is_total_reflection) {
        std::cout << "ПОМИЛКА: Кут падіння менший за критичний! Повне відбиття відсутнє.\n";
        return 0;
    }

    std::cout << "РЕЖИМ ПОВНОГО ВНУТРІШНЬОГО ВІДБИТТЯ ПІДТВЕРДЖЕНО.\n";
    std::cout << "Глибина проникнення амплітуди полів d_p: " << res.d_p_nm << " нм\n";
    std::cout << "Глибина згасання інтенсивності поля d_I: " << res.d_I_nm << " нм\n\n";

    std::cout << "1. ПРОФІЛЬ ЗГАСАННЯ ЕЛЕКТРИЧНОГО ПОЛЯ ВГЛИБ ЗАЗОРУ:\n";
    std::cout << "   z (нм)  | z / d_p | Амплітуда E(z)/E0 | Інтенсивність I(z)/I0\n";
    std::cout << "-----------+---------+-------------------+----------------------\n";

    for (double z = 0.0; z <= 3.1 * res.d_p_nm; z += 0.5 * res.d_p_nm) {
        double E_norm = std::exp(-z / res.d_p_nm);
        double I_norm = E_norm * E_norm;
        std::cout << std::setw(9) << z << "  |  "
                  << std::setw(6) << z / res.d_p_nm << " |     "
                  << std::setw(9) << E_norm << "     |      "
                  << std::setw(9) << I_norm << "\n";
    }

    std::cout << "\n2. ТУНЕЛЬНЕ ПРОХОДЖЕННЯ FTIR (T-кофіцієнт vs Ширина зазору d):\n";
    std::cout << "   d (нм)  | d / lambda0 | s-поляризація Ts (%) | Втрати (dB)\n";
    std::cout << "-----------+-------------+----------------------+--------------\n";

    for (double d = 0.0; d <= 1001.0; d += 100.0) {
        double Ts = calculate_ftir_transmission(setup, d, false);
        double loss_db = (Ts > 1e-12) ? -10.0 * std::log10(Ts) : 120.0;
        std::cout << std::setw(9) << d << "  |   "
                  << std::setw(8) << d / setup.wavelength_nm << "  |       "
                  << std::setw(8) << Ts * 100.0 << " %    |  "
                  << std::setw(8) << loss_db << " dB\n";
    }

    return 0;
}
