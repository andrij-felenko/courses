#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <stdexcept>

// Фізичні константи в системі СІ
constexpr double HBAR = 1.054571817e-34; // Зведена стала Планка [Дж·с]
constexpr double KB   = 1.380649e-23;    // Стала Больцмана [Дж/К]
constexpr double QE   = 1.602176634e-19; // Елементарний заряд [Кл]
constexpr double PI   = 3.14159265358979323846;

class QuantumNoiseCalculator {
public:
    // Обчислення спектральної густини шуму напруги S_V(nu) за Калленом — Велтоном
    static double callenWeltonNoise(double rOhm, double tempK, double freqHz) {
        if (rOhm < 0 || tempK < 0 || freqHz < 0) {
            throw std::invalid_argument("Фізичні параметри повинні бути невід'ємними.");
        }
        
        double hNu = 2.0 * PI * HBAR * freqHz;
        if (tempK <= 1e-9) {
            return 2.0 * rOhm * hNu; // Межа T -> 0 K
        }
        
        double x = hNu / (2.0 * KB * tempK);
        double cothVal = 0.0;
        if (x < 1e-4) {
            cothVal = 1.0 / x + x / 3.0;
        } else if (x > 50.0) {
            cothVal = 1.0;
        } else {
            cothVal = (std::exp(x) + std::exp(-x)) / (std::exp(x) - std::exp(-x));
        }
        
        return 2.0 * rOhm * hNu * cothVal;
    }

    // Обчислення спектральної густини струмового шуму S_I(V) Шотткі
    static double shotNoiseTunnelJunction(double voltageV, double tempK, double rJunction, double fanoFactor = 1.0) {
        if (rJunction <= 0) {
            throw std::invalid_argument("Опір контакту має бути додатним.");
        }
        
        double currentI = voltageV / rJunction;
        double eV = QE * std::abs(voltageV);
        
        if (tempK <= 1e-9) {
            return 2.0 * fanoFactor * QE * std::abs(currentI);
        }
        
        double x = eV / (2.0 * KB * tempK);
        double cothVal = 0.0;
        if (x < 1e-4) {
            cothVal = 1.0 / x + x / 3.0;
        } else if (x > 50.0) {
            cothVal = 1.0;
        } else {
            cothVal = (std::exp(x) + std::exp(-x)) / (std::exp(x) - std::exp(-x));
        }
        
        return fanoFactor * QE * std::abs(currentI) * cothVal;
    }
};

int main() {
    std::cout << std::scientific << std::setprecision(3);
    
    double rResistor = 50.0;
    double tCryo = 0.020; // 20 мК
    
    std::cout << "=== 1. Квантовий шум Джонсона — Найквіста S_V(nu) ===\n";
    std::vector<double> freqs = {1e6, 1e9, 5e9, 20e9, 100e9};
    for (double f : freqs) {
        try {
            double sv = QuantumNoiseCalculator::callenWeltonNoise(rResistor, tCryo, f);
            double svClass = 4.0 * rResistor * KB * tCryo;
            std::cout << "f = " << std::setw(6) << f / 1e9 << " ГГц | S_V = " << sv 
                      << " В²/Гц | Перевищення: " << std::fixed << std::setprecision(2) << sv / svClass << "x\n"
                      << std::scientific << std::setprecision(3);
        } catch (const std::exception& e) {
            std::cerr << "Помилка обчислення: " << e.what() << '\n';
        }
    }

    std::cout << "\n=== 2. Дробовий шум Шотткі S_I(V) у тунельному контакті ===\n";
    std::vector<double> voltages = {0.001, 0.010, 0.100};
    for (double v : voltages) {
        try {
            double si1 = QuantumNoiseCalculator::shotNoiseTunnelJunction(v, tCryo, 1000.0, 1.0);
            double si05 = QuantumNoiseCalculator::shotNoiseTunnelJunction(v, tCryo, 1000.0, 0.5);
            std::cout << "V = " << std::setw(5) << v * 1e3 << " мВ | S_I(F=1.0) = " << si1 
                      << " А²/Гц | S_I(F=0.5) = " << si05 << " А²/Гц\n";
        } catch (const std::exception& e) {
            std::cerr << "Помилка обчислення: " << e.what() << '\n';
        }
    }

    return 0;
}
