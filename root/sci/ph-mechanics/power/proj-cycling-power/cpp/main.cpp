#include <cmath>
#include <cstdio>
#include <optional>
#include <stdexcept>

constexpr double G = 9.80665;      // м/с², стандартне прискорення вільного падіння

struct Bike {
    double mass;                   // кг — гонщик, велосипед, бідони, все, що їде
    double cda = 0.36;             // м² — C_d·A, уся аеродинаміка посадки одним числом
    double crr = 0.005;            // безрозмірний коефіцієнт кочення шини
    double rho = 1.225;            // кг/м³ — густина повітря
    double eta = 0.97;             // частка потужності, що доходить від педалей до колеса
};

struct Budget {
    double gravity, rolling, air, bearings, drivetrain;
    double total() const { return gravity + rolling + air + bearings + drivetrain; }
};

double air_density(double altitude_m, std::optional<double> temp_C = std::nullopt) {
    const double t = temp_C.value_or(15.0 - 0.0065 * altitude_m);   // стандартний градієнт
    const double p = 101325.0 * std::pow(1.0 - 2.25577e-5 * altitude_m, 5.25588);
    return p / (287.05 * (t + 273.15));                              // ρ = p / (R·T)
}

Budget power_budget(const Bike& b, double v, double grade = 0.0, double headwind = 0.0) {
    const double theta = std::atan(grade);   // ухил у відсотках — тангенс, не синус
    const double v_air = v + headwind;       // зустрічний вітер додатний, попутний від'ємний
    Budget w{};
    w.gravity  = b.mass * G * std::sin(theta) * v;
    w.rolling  = b.crr * b.mass * G * std::cos(theta) * v;
    w.air      = 0.5 * b.rho * b.cda * v_air * std::fabs(v_air) * v;  // ×v ШЛЯХОВОЮ!
    w.bearings = v * (91.0 + 8.7 * v) * 1e-3;                         // Martin та ін., 1998
    const double wheel = w.gravity + w.rolling + w.air + w.bearings;
    w.drivetrain = wheel * (1.0 / b.eta - 1.0);                       // ділення, не доданок
    return w;
}

double pedal_power(const Bike& b, double v, double grade = 0.0, double headwind = 0.0) {
    return power_budget(b, v, grade, headwind).total();
}

double speed_for_power(const Bike& b, double power, double grade = 0.0,
                       double headwind = 0.0, double tol = 1e-9) {
    const double v_calm = std::fmax(0.0, -headwind);   // де повітряна швидкість обнуляється
    double lo, hi;
    if (pedal_power(b, v_calm, grade, headwind) >= power) {
        lo = 0.0;  hi = v_calm;      // сильний попутний: розв'язок нижче швидкості вітру
    } else {
        lo = v_calm;  hi = v_calm + 1.0;
        while (pedal_power(b, hi, grade, headwind) < power) {
            hi = v_calm + 2.0 * (hi - v_calm);          // межа тікає вгору як v³ — швидко
            if (hi - v_calm > 1e3)
                throw std::runtime_error("розв'язку немає — перевір знаки ухилу й вітру");
        }
    }
    while (hi - lo > tol) {
        const double mid = 0.5 * (lo + hi);
        (pedal_power(b, mid, grade, headwind) < power ? lo : hi) = mid;
    }
    return 0.5 * (lo + hi);
}

int main() {
    const Bike climb{78.0, 0.36, 0.005, air_density(1200.0), 0.97};
    const Budget w = power_budget(climb, 4.2, 0.081);
    std::printf("тяжіння %.1f | кочення %.1f | повітря %.1f | підшипники %.1f | трансмісія %.1f\n",
                w.gravity, w.rolling, w.air, w.bearings, w.drivetrain);
    std::printf("РАЗОМ %.1f Вт\n", w.total());

    const Bike flat{78.0, 0.30, 0.005, 1.225, 0.97};      // рівнина, рівень моря
    std::printf("250 Вт -> %.2f км/год\n", 3.6 * speed_for_power(flat, 250.0));
}
