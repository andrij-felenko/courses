#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <iomanip>
#include <string>
#include <array>

// Структура для зберігання спектральних кольорових координат
struct ColorRGB {
    uint8_t r;
    uint8_t g;
    uint8_t b;

    std::string to_hex() const {
        char buf[8];
        std::snprintf(buf, sizeof(buf), "#%02X%02X%02X", r, g, b);
        return std::string(buf);
    }
};

// Аналітична апроксимація кривих чутливості ока CIE 1931 (Гаусові апроксимації)
struct CIE1931 {
    static double x_bar(double lambda_nm) {
        double t1 = (lambda_nm - 442.0) / ((lambda_nm < 442.0) ? 16.0 : 22.0);
        double t2 = (lambda_nm - 599.0) / ((lambda_nm < 599.0) ? 38.0 : 32.0);
        double t3 = (lambda_nm - 501.0) / ((lambda_nm < 501.0) ? 24.0 : 22.0);
        return 0.362 * std::exp(-0.5 * t1 * t1) + 1.056 * std::exp(-0.5 * t2 * t2) - 0.065 * std::exp(-0.5 * t3 * t3);
    }

    static double y_bar(double lambda_nm) {
        double t1 = (lambda_nm - 568.8) / ((lambda_nm < 568.8) ? 46.9 : 44.5);
        double t2 = (lambda_nm - 530.9) / ((lambda_nm < 530.9) ? 16.3 : 37.1);
        return 0.821 * std::exp(-0.5 * t1 * t1) + 0.286 * std::exp(-0.5 * t2 * t2);
    }

    static double z_bar(double lambda_nm) {
        double t1 = (lambda_nm - 437.0) / ((lambda_nm < 437.0) ? 11.8 : 19.8);
        double t2 = (lambda_nm - 459.0) / ((lambda_nm < 459.0) ? 26.0 : 26.0);
        return 1.217 * std::exp(-0.5 * t1 * t1) + 0.681 * std::exp(-0.5 * t2 * t2);
    }
};

class ThinFilmSimulator {
private:
    double n1; // середовище над плівкою (наприклад, повітря 1.00)
    double n2; // плівка (наприклад, мильний розчин 1.33)
    double n3; // середовище під плівкою (наприклад, скло 1.52 або повітря 1.00)

public:
    ThinFilmSimulator(double n1_val, double n2_val, double n3_val)
        : n1(n1_val), n2(n2_val), n3(n3_val) {}

    // Обчислення коефіцієнта відбиття R(lambda) за формулою Ері
    double calculate_reflectance(double lambda_nm, double d_nm, double theta1_rad = 0.0) const {
        double sin_theta2 = (n1 / n2) * std::sin(theta1_rad);
        if (std::abs(sin_theta2) > 1.0) return 1.0; // Повне внутрішнє відбиття
        double theta2_rad = std::asin(sin_theta2);

        double sin_theta3 = (n2 / n3) * std::sin(theta2_rad);
        double theta3_rad = (std::abs(sin_theta3) <= 1.0) ? std::asin(sin_theta3) : 0.0;

        // Амплітудні коефіцієнти відбиття Френеля для s-поляризації
        double r12 = (n1 * std::cos(theta1_rad) - n2 * std::cos(theta2_rad)) /
                     (n1 * std::cos(theta1_rad) + n2 * std::cos(theta2_rad));
        double r23 = (n2 * std::cos(theta2_rad) - n3 * std::cos(theta3_rad)) /
                     (n2 * std::cos(theta2_rad) + n3 * std::cos(theta3_rad));

        // Набіг фази за один подвійний прохід плівки
        constexpr double PI = 3.14159265358979323846;
        double beta = (4.0 * PI * n2 * d_nm * std::cos(theta2_rad)) / lambda_nm;

        // Формула Ері для коефіцієнта відбиття R
        double num = r12 * r12 + r23 * r23 + 2.0 * r12 * r23 * std::cos(beta);
        double den = 1.0 + r12 * r12 * r23 * r23 + 2.0 * r12 * r23 * std::cos(beta);

        return std::clamp(num / den, 0.0, 1.0);
    }

    // Симуляція інтерференційного кольору плівки товщиною d_nm у sRGB
    ColorRGB simulate_color(double d_nm, double theta1_rad = 0.0) const {
        double X = 0.0, Y = 0.0, Z = 0.0;
        double norm_y = 0.0;

        constexpr double LAMBDA_START = 380.0;
        constexpr double LAMBDA_END = 780.0;
        constexpr double STEP = 5.0;

        for (double lambda = LAMBDA_START; lambda <= LAMBDA_END; lambda += STEP) {
            double R_val = calculate_reflectance(lambda, d_nm, theta1_rad);
            double x_b = CIE1931::x_bar(lambda);
            double y_b = CIE1931::y_bar(lambda);
            double z_b = CIE1931::z_bar(lambda);

            X += R_val * x_b * STEP;
            Y += R_val * y_b * STEP;
            Z += R_val * z_b * STEP;
            norm_y += y_b * STEP;
        }

        // Нормалізація
        if (norm_y > 0.0) {
            X /= norm_y;
            Y /= norm_y;
            Z /= norm_y;
        }

        // Конверсія CIE XYZ у лінійне RGB (матриця D65 / sRGB)
        double r_lin =  3.2406 * X - 1.5372 * Y - 0.4986 * Z;
        double g_lin = -0.9689 * X + 1.8758 * Y + 0.0415 * Z;
        double b_lin =  0.0557 * X - 0.2040 * Y + 1.0570 * Z;

        // Гамма-корекція sRGB (γ = 2.2)
        auto gamma_correct = [](double val) -> uint8_t {
            val = std::clamp(val, 0.0, 1.0);
            double corrected = (val <= 0.0031308) ? (12.92 * val) : (1.055 * std::pow(val, 1.0 / 2.4) - 0.055);
            return static_cast<uint8_t>(std::round(corrected * 255.0));
        };

        return ColorRGB{gamma_correct(r_lin), gamma_correct(g_lin), gamma_correct(b_lin)};
    }
};

int main() {
    // Симуляція мильної бульбашки у повітрі (n1=1.0, n2=1.33, n3=1.0)
    ThinFilmSimulator soap_bubble(1.00, 1.33, 1.00);

    std::cout << "--- Симуляція кольору мильної плівки у повітрі ---\n";
    std::cout << std::left << std::setw(15) << "Товщина d (нм)" << std::setw(15) << "HEX Колір" << "Коментар\n";
    std::cout << "---------------------------------------------------------\n";

    std::vector<double> thicknesses = {10.0, 100.0, 250.0, 380.0, 500.0, 650.0, 1000.0};
    for (double d : thicknesses) {
        ColorRGB col = soap_bubble.simulate_color(d);
        std::string desc = (d < 30.0) ? "Надватонка плівка (чорна)" :
                           (d < 150.0) ? "Світло-жовта / білувата" :
                           (d < 300.0) ? "Яскраво-пурпурова / фіолетова" : "Зелена / переливчаста";
        std::cout << std::left << std::setw(15) << d << std::setw(15) << col.to_hex() << desc << "\n";
    }

    return 0;
}
