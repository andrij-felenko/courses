// Показовий прогін модуля просторових перетворень.
// Збірка: c++ -std=c++23 -O2 cpp/*.cpp -o axes-demo
#include "attitude.hpp"
#include "mounting.hpp"
#include "tumbling_fit.hpp"

#include <array>
#include <format>
#include <iostream>
#include <numbers>
#include <random>
#include <vector>

namespace {

using nav::Matrix3;
using nav::Vector3;

constexpr float kPi = std::numbers::pi_v<float>;
constexpr float kRad2Deg = 180.0F / kPi;
constexpr float kDeg2Rad = kPi / 180.0F;

void print_vec(std::string_view tag, const Vector3& v) {
    std::cout << std::format("  {:<26} [{: .5f} {: .5f} {: .5f}]\n", tag, v.x, v.y, v.z);
}

void print_mat(std::string_view tag, const Matrix3& m) {
    std::cout << std::format("  {}\n", tag);
    for (const auto& row : m.r) {
        std::cout << std::format("      [{: .4f} {: .4f} {: .4f}]\n", row[0], row[1], row[2]);
    }
}

void demo_frames() {
    std::cout << "== 1. Світові базиси: NED <-> ENU ==\n";
    const Vector3 v_ned{12.0F, -3.0F, -50.0F};   // північ, схід, вниз: висота 50 м
    const Vector3 v_enu = nav::swap_ned_enu(v_ned);
    print_vec("v_ned (N, E, D)", v_ned);
    print_vec("v_enu (E, N, U)", v_enu);
    print_vec("назад у NED", nav::swap_ned_enu(v_enu));

    constexpr Matrix3 p_ned{{{{0.25F, 0.02F, 0.00F},
                              {0.02F, 0.30F, 0.00F},
                              {0.00F, 0.00F, 1.20F}}}};
    constexpr Matrix3 p_enu = nav::swap_ned_enu(p_ned);   // квадратична форма рахується ще на компіляції
    print_mat("P_enu = T·P_ned·Tᵀ", p_enu);
    std::cout << std::format("  слід коваріації зберігся: {:.4f} -> {:.4f}\n",
                             p_ned.r[0][0] + p_ned.r[1][1] + p_ned.r[2][2],
                             p_enu.r[0][0] + p_enu.r[1][1] + p_enu.r[2][2]);
}

void demo_mounting() {
    std::cout << "\n== 2. Плата, перекіс і конвеєр вирівнювання ==\n";
    std::cout << std::format("  унікальних дискретних орієнтацій плати: {}\n",
                             nav::enumerate_board_rotations().size());

    nav::SensorCalibration cal;
    // Плата стоїть носом праворуч: у тіло вектор переходить поворотом на −90° за курсом.
    cal.set_board(nav::BoardRotation{0, 0, 3});
    print_mat("R_board (YAW_90)", cal.board());

    cal.set_scale(Matrix3{{{{1.0120F, 0.0040F, -0.0020F},
                            {0.0040F, 0.9910F, 0.0030F},
                            {-0.0020F, 0.0030F, 1.0070F}}}});

    if (const auto ok = cal.set_misalignment({0.4F * kDeg2Rad, 2.0F * kDeg2Rad, -0.7F * kDeg2Rad});
        !ok) {
        std::cout << "  перекіс поза межами малокутової моделі — калібрування відхилено\n";
        return;
    }

    const std::array<Vector3, 4> poly{Vector3{0.0500F, -0.0300F, 0.1100F},    // b0, м/с²
                                      Vector3{0.0008F, -0.0005F, 0.0012F},    // b1, м/с²/°C
                                      Vector3{}, Vector3{}};
    cal.set_bias_polynomial(std::span<const Vector3, 4>{poly}, 25.0F);

    if (!cal.sane()) {
        std::cout << std::format("  калібрування зіпсоване, похибка ортогональності {:.2e}\n",
                                 cal.orthogonality_error());
        return;
    }
    std::cout << std::format("  похибка ортогональності поворотів: {:.2e}\n",
                             cal.orthogonality_error());

    print_vec("b_bias(+25 °C)", cal.bias_at(25.0F));
    print_vec("b_bias(+60 °C)", cal.bias_at(60.0F));

    // Числа з розділу про такт польотного контролера, переведені в м/с².
    const Vector3 a_raw = Vector3{0.02F, -0.05F, 1.01F} * nav::kGravity;
    print_vec("a_raw (сенсор)", a_raw);
    print_vec("a_body (FRD, +60 °C)", cal.apply(a_raw, 60.0F));

    std::cout << std::format("  перекіс 2.0° при розгоні 10 м/с² дає хибні {:.3f} м/с² на осі Y\n",
                             10.0F * std::sin(2.0F * kDeg2Rad));
}

// Розв'язок M·x = t для нижньої трикутної M — щоб зліпити синтетичні виміри.
Vector3 lower_solve(const Matrix3& m, const Vector3& t) {
    const float x0 = t.x / m.r[0][0];
    const float x1 = (t.y - m.r[1][0] * x0) / m.r[1][1];
    const float x2 = (t.z - m.r[2][0] * x0 - m.r[2][1] * x1) / m.r[2][2];
    return {x0, x1, x2};
}

void report(std::string_view tag, const std::expected<nav::TumbleFit, nav::FitError>& fit) {
    if (!fit) {
        std::cout << std::format("  {}: {}\n", tag, nav::describe(fit.error()));
        return;
    }
    std::cout << std::format("  {}: ітерацій {}, RMS {:.4f}% g\n", tag, fit->iterations,
                             fit->rms_rel * 100.0F);
    print_mat("M знайдена", fit->m);
    print_vec("bias знайдений", fit->bias);
}

void demo_calibration() {
    std::cout << "\n== 3. Статичне калібрування акселерометра ==\n";

    // Правда, якої алгоритм не знає.
    const Matrix3 m_true{{{{1.0200F, 0.0F, 0.0F},
                           {0.0100F, 0.9800F, 0.0F},
                           {-0.0080F, 0.0120F, 1.0100F}}}};
    const Vector3 b_true{0.1500F, -0.2200F, 0.3100F};

    constexpr float k = 0.57735027F;   // 1/sqrt(3): кутові положення куба
    const std::array<Vector3, 14> dir{
        Vector3{1, 0, 0}, Vector3{-1, 0, 0}, Vector3{0, 1, 0},
        Vector3{0, -1, 0}, Vector3{0, 0, 1}, Vector3{0, 0, -1},
        Vector3{k, k, k}, Vector3{k, k, -k}, Vector3{k, -k, k}, Vector3{k, -k, -k},
        Vector3{-k, k, k}, Vector3{-k, k, -k}, Vector3{-k, -k, k}, Vector3{-k, -k, -k}};

    std::mt19937 rng{20260829U};                        // фіксоване зерно: прогін повторюваний
    std::normal_distribution<float> noise{0.0F, 0.01F};

    std::vector<Vector3> averages;
    averages.reserve(dir.size());
    for (const auto& d : dir) {
        // Ідеальний вимір: M·(a − b) = g·d, тобто a = M⁻¹·(g·d) + b.
        const Vector3 ideal = lower_solve(m_true, d * nav::kGravity) + b_true;
        std::vector<Vector3> burst;
        burst.reserve(64);
        for (int s = 0; s < 64; ++s) {
            burst.push_back(ideal + Vector3{noise(rng), noise(rng), noise(rng)});
        }
        const auto mean = nav::still_average(burst, 0.30F);
        if (!mean) {
            std::cout << "  апарат не стояв у позиції — набір відкинуто\n";
            return;
        }
        averages.push_back(*mean);
    }

    const std::span<const Vector3> faces{averages.data(), 6};
    report("6 граней, діагональна модель",
           nav::fit_static_positions(faces, nav::kGravity, nav::SensorModel::Diagonal));
    // Шість граней дають шість рівнянь — на дев'ять невідомих їх бракує.
    report("6 граней, тривісна модель",
           nav::fit_static_positions(faces, nav::kGravity, nav::SensorModel::Triaxial));
    report("14 положень, тривісна модель",
           nav::fit_static_positions(averages, nav::kGravity, nav::SensorModel::Triaxial));
    print_mat("M справжня", m_true);
    print_vec("bias справжній", b_true);
}

void demo_coning() {
    std::cout << "\n== 4. Конічний рух: що губить просте підсумовування приростів ==\n";
    constexpr float amp = 0.02F;              // кутова амплітуда коливання, рад
    constexpr float freq = 100.0F;            // частота вібрації, Гц
    const float w = 2.0F * kPi * freq;
    constexpr float dt_fast = 0.0005F;        // швидкий контур 2 кГц
    constexpr int slow_div = 8;               // повільний контур 250 Гц
    constexpr int steps = 4000;               // 2 секунди

    nav::AttitudeEstimator with_coning{{.kp = 0.0F, .ki = 0.0F}, true};
    nav::AttitudeEstimator without_coning{{.kp = 0.0F, .ki = 0.0F}, false};

    for (int k = 0; k < steps; ++k) {
        const float t = static_cast<float>(k) * dt_fast;
        // p і q зсунуті по фазі на 90°: амплітуда швидкості A·ω.
        const Vector3 omega{amp * w * std::sin(w * t), amp * w * std::cos(w * t), 0.0F};
        with_coning.push_gyro(omega, dt_fast);
        without_coning.push_gyro(omega, dt_fast);
        if ((k + 1) % slow_div == 0) {
            with_coning.update(std::nullopt, dt_fast * slow_div);
            without_coning.update(std::nullopt, dt_fast * slow_div);
        }
    }

    constexpr float seconds = steps * dt_fast;
    const float yaw_with = with_coning.euler().yaw * kRad2Deg;
    const float yaw_without = without_coning.euler().yaw * kRad2Deg;
    std::cout << std::format("  теоретичний дрейф 0.5·A²·ω = {:.3f} °/с\n",
                             0.5F * amp * amp * w * kRad2Deg);
    std::cout << std::format("  з конічною поправкою: курс {:+8.3f}°  ({:.3f} °/с)\n",
                             yaw_with, yaw_with / seconds);
    std::cout << std::format("  без поправки:         курс {:+8.3f}°  ({:.3f} °/с)\n",
                             yaw_without, yaw_without / seconds);
    std::cout << std::format("  розбіжність за 2 с:   {:+8.3f}°\n", yaw_with - yaw_without);
}

void demo_complementary() {
    std::cout << "\n== 5. Корекція за вертикаллю і вивчення зсуву гіроскопа ==\n";
    nav::AttitudeEstimator filter{{.kp = 1.2F, .ki = 0.10F}, true};

    constexpr float true_roll = 20.0F * kDeg2Rad;
    const Vector3 accel{0.0F, std::sin(true_roll) * nav::kGravity,
                        std::cos(true_roll) * nav::kGravity};
    const Vector3 gyro_reading{0.02F, -0.01F, 0.0F};   // самий лише зсув нуля, рад/с
    constexpr float dt_fast = 0.001F;

    for (int step = 0; step < 5000; ++step) {          // 5 секунд
        filter.push_gyro(gyro_reading, dt_fast);
        if ((step + 1) % 4 == 0) filter.update(accel, 4.0F * dt_fast);
        if ((step + 1) % 1000 == 0) {
            const auto e = filter.euler();
            std::cout << std::format(
                "  t={:.0f} c  крен {:6.2f}°  тангаж {:6.2f}°  зсув гіро [{: .4f} {: .4f}] рад/с\n",
                static_cast<float>(step + 1) * dt_fast, e.roll * kRad2Deg, e.pitch * kRad2Deg,
                filter.gyro_bias().x, filter.gyro_bias().y);
        }
    }
    std::cout << std::format("  істина: крен {:.2f}°, зсув [{: .4f} {: .4f}]; акселерометр "
                             "відхилено {} разів\n",
                             true_roll * kRad2Deg, gyro_reading.x, gyro_reading.y,
                             filter.rejected_accel());
}

void demo_gimbal_lock() {
    std::cout << "\n== 6. Шарнірний замок у кінематиці Ейлера ==\n";
    const Vector3 omega{0.0F, 0.0F, 0.01F};   // шум гіроскопа 0.01 рад/с
    for (const float pitch_deg : {0.0F, 89.9F, 89.99999F}) {
        const nav::EulerAngles angles{0.0F, pitch_deg * kDeg2Rad, 0.0F};
        if (const auto rates = nav::euler_rates(angles, omega)) {
            std::cout << std::format("  тангаж {:9.5f}°: dψ/dt = {:10.3f} °/с\n", pitch_deg,
                                     rates->yaw * kRad2Deg);
        } else {
            std::cout << std::format("  тангаж {:9.5f}°: сингулярність, кути Ейлера тут "
                                     "не визначені\n", pitch_deg);
        }
    }
    // Кватерніон тієї самої орієнтації жодної особливої точки не має.
    const auto q = nav::Quaternion::from_euler({0.0F, 90.0F * kDeg2Rad, 0.0F});
    print_vec("ніс у світі при θ=90°", q.rotate({1.0F, 0.0F, 0.0F}));
    std::cout << std::format("  норма кватерніона: {:.7f}\n", q.norm());
}

void demo_interpolation() {
    std::cout << "\n== 7. Інтегрування великого кроку та інтерполяція ==\n";
    const Vector3 omega{0.0F, 0.0F, 400.0F * kDeg2Rad};   // швидке рискання
    constexpr float dt = 0.001F;
    const auto linear = nav::Quaternion{}.integrate_gyro(omega, dt);
    const auto exact = nav::Quaternion{} * nav::Quaternion::from_rotation_vector(omega * dt);
    std::cout << std::format("  за 1 мс при 400 °/с: Ейлер 1-го порядку {:.6f}°, "
                             "експонента {:.6f}°\n",
                             linear.to_euler().yaw * kRad2Deg, exact.to_euler().yaw * kRad2Deg);

    const auto q1 = nav::Quaternion{};
    const auto q2 = nav::Quaternion::from_euler({0.0F, 0.0F, 90.0F * kDeg2Rad});
    const auto q3 = nav::Quaternion::from_euler({0.0F, 0.0F, 5.0F * kDeg2Rad});
    std::cout << std::format("  дуга 90°, t=0.5:  slerp {:.4f}°  nlerp {:.4f}°\n",
                             nav::slerp(q1, q2, 0.5F).to_euler().yaw * kRad2Deg,
                             nav::nlerp(q1, q2, 0.5F).to_euler().yaw * kRad2Deg);
    std::cout << std::format("  дуга 5°,  t=0.5:  slerp {:.6f}°  nlerp {:.6f}°\n",
                             nav::slerp(q1, q3, 0.5F).to_euler().yaw * kRad2Deg,
                             nav::nlerp(q1, q3, 0.5F).to_euler().yaw * kRad2Deg);
}

}  // namespace

int main() {
    demo_frames();
    demo_mounting();
    demo_calibration();
    demo_coning();
    demo_complementary();
    demo_gimbal_lock();
    demo_interpolation();
    return 0;
}
