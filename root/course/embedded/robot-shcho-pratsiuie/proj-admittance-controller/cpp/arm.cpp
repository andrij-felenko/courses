#include "arm.hpp"

#include <algorithm>
#include <cmath>
#include <optional>

namespace robot::arm {
namespace {

constexpr std::size_t kCart = compliance::kDof;
using Mat4 = std::array<float, 16>;
using Mat6 = std::array<std::array<float, kCart>, kCart>;

[[nodiscard]] constexpr Mat4 identity4() noexcept
{
    return Mat4{1.0f, 0.0f, 0.0f, 0.0f,
                0.0f, 1.0f, 0.0f, 0.0f,
                0.0f, 0.0f, 1.0f, 0.0f,
                0.0f, 0.0f, 0.0f, 1.0f};
}

[[nodiscard]] Mat4 operator*(const Mat4& a, const Mat4& b) noexcept
{
    Mat4 out{};
    for (std::size_t r = 0; r < 4; ++r) {
        for (std::size_t c = 0; c < 4; ++c) {
            float s = 0.0f;
            for (std::size_t k = 0; k < 4; ++k) {
                s += a[r * 4 + k] * b[k * 4 + c];
            }
            out[r * 4 + c] = s;
        }
    }
    return out;
}

[[nodiscard]] Mat4 link_transform(const Link& link, float theta) noexcept
{
    const float ct = std::cos(theta);
    const float st = std::sin(theta);
    const float ca = std::cos(link.alpha);
    const float sa = std::sin(link.alpha);
    return Mat4{ct, -st * ca, st * sa, link.a * ct,
                st, ct * ca, -ct * sa, link.a * st,
                0.0f, sa, ca, link.d,
                0.0f, 0.0f, 0.0f, 1.0f};
}

[[nodiscard]] Vec3 cross(const Vec3& a, const Vec3& b) noexcept
{
    return Vec3{a[1] * b[2] - a[2] * b[1],
                a[2] * b[0] - a[0] * b[2],
                a[0] * b[1] - a[1] * b[0]};
}

// A = J·Jᵀ — симетрична 6×6, ядро і маніпульованості, і DLS.
[[nodiscard]] Mat6 gram(const std::array<JointVector, kCart>& jac) noexcept
{
    Mat6 a{};
    for (std::size_t r = 0; r < kCart; ++r) {
        for (std::size_t c = 0; c < kCart; ++c) {
            float s = 0.0f;
            for (std::size_t k = 0; k < kJoints; ++k) {
                s += jac[r][k] * jac[c][k];
            }
            a[r][c] = s;
        }
    }
    return a;
}

// Розклад A = L·Lᵀ. Порожньо — матриця не додатно визначена, тобто
// рука фактично сидить у сингулярності.
[[nodiscard]] std::optional<Mat6> cholesky(const Mat6& a) noexcept
{
    Mat6 l{};
    for (std::size_t j = 0; j < kCart; ++j) {
        float diag = a[j][j];
        for (std::size_t k = 0; k < j; ++k) {
            diag -= l[j][k] * l[j][k];
        }
        if (diag <= 1.0e-12f) {
            return std::nullopt;
        }
        l[j][j] = std::sqrt(diag);
        for (std::size_t i = j + 1; i < kCart; ++i) {
            float s = a[i][j];
            for (std::size_t k = 0; k < j; ++k) {
                s -= l[i][k] * l[j][k];
            }
            l[i][j] = s / l[j][j];
        }
    }
    return l;
}

[[nodiscard]] Vector6 cholesky_solve(const Mat6& l, const Vector6& b) noexcept
{
    Vector6 y{};
    for (std::size_t i = 0; i < kCart; ++i) { // прямий хід: L·y = b
        float s = b[i];
        for (std::size_t k = 0; k < i; ++k) {
            s -= l[i][k] * y[k];
        }
        y[i] = s / l[i][i];
    }
    Vector6 x{};
    for (std::size_t i = kCart; i-- > 0;) { // зворотний хід: Lᵀ·x = y
        float s = y[i];
        for (std::size_t k = i + 1; k < kCart; ++k) {
            s -= l[k][i] * x[k];
        }
        x[i] = s / l[i][i];
    }
    return x;
}

} // namespace

Vec3 rotate(const Mat3& r, const Vec3& v) noexcept
{
    Vec3 out{};
    for (std::size_t i = 0; i < 3; ++i) {
        out[i] = r[3 * i] * v[0] + r[3 * i + 1] * v[1] + r[3 * i + 2] * v[2];
    }
    return out;
}

Vec3 rotate_inverse(const Mat3& r, const Vec3& v) noexcept
{
    Vec3 out{};
    for (std::size_t i = 0; i < 3; ++i) {
        out[i] = r[i] * v[0] + r[3 + i] * v[1] + r[6 + i] * v[2];
    }
    return out;
}

Vector6 rotate_to_base(const Mat3& r, const Vector6& body) noexcept
{
    const Vec3 linear = rotate(r, Vec3{body[0], body[1], body[2]});
    const Vec3 angular = rotate(r, Vec3{body[3], body[4], body[5]});
    return Vector6{linear[0], linear[1], linear[2], angular[0], angular[1], angular[2]};
}

Vector6 tool_gravity_wrench(const ToolInertia& tool, const Mat3& r_sensor) noexcept
{
    // Вага в базовій (горизонтованій) системі; поворот у систему давача
    // і робить її «блукаючою» по осях, щойно кисть змінює орієнтацію.
    const Vec3 g_base{0.0f, 0.0f, -tool.mass * tool.g};
    const Vec3 force = rotate_inverse(r_sensor, g_base);
    const Vec3 moment = cross(tool.com, force); // плече центра мас
    return Vector6{force[0], force[1], force[2], moment[0], moment[1], moment[2]};
}

Vector6 compensate_tool_gravity(const ToolInertia& tool, const Mat3& r_sensor,
                                const Vector6& raw) noexcept
{
    const Vector6 gravity = tool_gravity_wrench(tool, r_sensor);
    Vector6 out{};
    for (std::size_t i = 0; i < compliance::kDof; ++i) {
        out[i] = raw[i] - gravity[i];
    }
    return out;
}

Model::Model(std::span<const Link, kJoints> links) noexcept
{
    std::ranges::copy(links, links_.begin());
}

void Model::update(std::span<const float, kJoints> q) noexcept
{
    Mat4 t = identity4();
    std::array<Vec3, kJoints> axis{};
    std::array<Vec3, kJoints> origin{};

    for (std::size_t i = 0; i < kJoints; ++i) {
        // Вісь суглоба i — це z системи i−1, тобто третій стовпець T.
        axis[i] = Vec3{t[2], t[6], t[10]};
        origin[i] = Vec3{t[3], t[7], t[11]};
        t = t * link_transform(links_[i], q[i] + links_[i].theta_offset);
    }

    p_flange_ = Vec3{t[3], t[7], t[11]};
    r_flange_ = Mat3{t[0], t[1], t[2], t[4], t[5], t[6], t[8], t[9], t[10]};

    // Стовпець обертального суглоба: лінійна частина z × (p_e − p_i),
    // кутова — сама вісь z.
    for (std::size_t i = 0; i < kJoints; ++i) {
        const Vec3 lever{p_flange_[0] - origin[i][0],
                         p_flange_[1] - origin[i][1],
                         p_flange_[2] - origin[i][2]};
        const Vec3 linear = cross(axis[i], lever);
        for (std::size_t r = 0; r < 3; ++r) {
            jacobian_[r][i] = linear[r];
            jacobian_[3 + r][i] = axis[i][r];
        }
    }

    // w = sqrt(det(J·Jᵀ)) = добуток діагоналі L. Не розклалося — нуль,
    // тобто рука вже втратила напрямок руху.
    manipulability_ = 0.0f;
    if (const auto l = cholesky(gram(jacobian_)); l) {
        float w = 1.0f;
        for (std::size_t i = 0; i < kCart; ++i) {
            w *= (*l)[i][i];
        }
        manipulability_ = w;
    }
}

Vec3 Model::tool_point(const Vec3& offset_in_flange) const noexcept
{
    const Vec3 offset = rotate(r_flange_, offset_in_flange);
    return Vec3{p_flange_[0] + offset[0], p_flange_[1] + offset[1], p_flange_[2] + offset[2]};
}

std::expected<Model::JointMotion, KinematicFault> Model::joint_velocity(
    const Vector6& twist_base, float lambda_max, float w_threshold) const noexcept
{
    // У зручній робочій зоні демпфування нульове — псевдоінверсія точна.
    // Ближче до сингулярності lambda росте квадратично, м'яко жертвуючи
    // точністю швидкості заради скінченних обертів моторів.
    float lambda = 0.0f;
    if (manipulability_ < w_threshold && w_threshold > 0.0f) {
        const float k = 1.0f - manipulability_ / w_threshold;
        lambda = lambda_max * k * k;
    }

    std::optional<Mat6> l;
    for (int attempt = 0; attempt < 5 && !l; ++attempt) {
        Mat6 a = gram(jacobian_);
        for (std::size_t i = 0; i < kCart; ++i) {
            a[i][i] += lambda * lambda;
        }
        l = cholesky(a);
        if (!l) {
            // Числова обробка вже після регуляризації: краще неточна
            // швидкість, ніж NaN у команді на шину приводів.
            lambda = (lambda > 0.0f) ? lambda * 2.0f : lambda_max;
        }
    }
    if (!l) {
        return std::unexpected(KinematicFault::Singular);
    }

    const Vector6 y = cholesky_solve(*l, twist_base);
    JointMotion motion{.lambda = lambda};
    for (std::size_t j = 0; j < kJoints; ++j) {
        float s = 0.0f;
        for (std::size_t i = 0; i < kCart; ++i) {
            s += jacobian_[i][j] * y[i];
        }
        motion.q_dot[j] = s;
    }

    // Рівномірне масштабування зберігає НАПРЯМОК руху: різати кожну вісь
    // окремо означало б поїхати не туди, куди наказано.
    const auto peak = std::ranges::max(motion.q_dot, {}, [](float v) { return std::abs(v); });
    if (const float m = std::abs(peak); m > kMaxJointRate) {
        const float scale = kMaxJointRate / m;
        for (float& v : motion.q_dot) {
            v *= scale;
        }
    }
    return motion;
}

} // namespace robot::arm
