#include <array>
#include <cmath>
#include <optional>
#include <numbers>
#include <span>
#include <algorithm>

template <std::size_t N>
class ManipulatorKinematics {
public:
    static_assert(N > 0 && N <= 8, "Кількість ланок повинна бути від 1 до 8");

    struct Vec3 {
        float x{0.0f}, y{0.0f}, z{0.0f};

        [[nodiscard]] constexpr Vec3 operator+(const Vec3& o) const noexcept {
            return {x + o.x, y + o.y, z + o.z};
        }
        [[nodiscard]] constexpr Vec3 operator-(const Vec3& o) const noexcept {
            return {x - o.x, y - o.y, z - o.z};
        }
        [[nodiscard]] constexpr Vec3 cross(const Vec3& o) const noexcept {
            return {y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x};
        }
        [[nodiscard]] constexpr float dot(const Vec3& o) const noexcept {
            return x * o.x + y * o.y + z * o.z;
        }
        [[nodiscard]] float norm() const noexcept {
            return std::sqrt(dot(*this));
        }
    };

    struct Mat4 {
        std::array<std::array<float, 4>, 4> data{};

        static constexpr Mat4 identity() noexcept {
            Mat4 m{};
            for (std::size_t i = 0; i < 4; ++i) m.data[i][i] = 1.0f;
            return m;
        }

        [[nodiscard]] constexpr Mat4 operator*(const Mat4& o) const noexcept {
            Mat4 res{};
            for (std::size_t r = 0; r < 4; ++r) {
                for (std::size_t c = 0; c < 4; ++c) {
                    res.data[r][c] = data[r][0] * o.data[0][c] +
                                     data[r][1] * o.data[1][c] +
                                     data[r][2] * o.data[2][c] +
                                     data[r][3] * o.data[3][c];
                }
            }
            return res;
        }

        [[nodiscard]] constexpr Vec3 translation() const noexcept {
            return {data[0][3], data[1][3], data[2][3]};
        }

        [[nodiscard]] constexpr Vec3 z_axis() const noexcept {
            return {data[0][2], data[1][2], data[2][2]};
        }
    };

    struct DHJoint {
        float theta{0.0f};  // кут суглоба (рад)
        float d{0.0f};      // зміщення вздовж Z_(i-1) (м)
        float a{0.0f};      // довжина спільного перпендикуляра X_i (м)
        float alpha{0.0f};  // скручування ланки (рад)
        bool is_revolute{true};
        float q_min{-std::numbers::pi_v<float>};
        float q_max{std::numbers::pi_v<float>};
    };

    using JointArray = std::array<DHJoint, N>;
    using JointAngles = std::array<float, N>;
    using Jacobian = std::array<std::array<float, N>, 6>;

    explicit constexpr ManipulatorKinematics(JointArray joints) noexcept
        : joints_(joints) {}

    [[nodiscard]] static Mat4 compute_dh_transform(float theta, float d, float a, float alpha) noexcept {
        const float ct = std::cos(theta), st = std::sin(theta);
        const float ca = std::cos(alpha), sa = std::sin(alpha);

        Mat4 m{};
        m.data[0] = { ct,  -st * ca,   st * sa,  a * ct };
        m.data[1] = { st,   ct * ca,  -ct * sa,  a * st };
        m.data[2] = { 0.0f,      sa,        ca,       d };
        m.data[3] = { 0.0f,    0.0f,      0.0f,    1.0f };
        return m;
    }

    [[nodiscard]] Mat4 forward_kinematics(const JointAngles& q) const noexcept {
        Mat4 current = Mat4::identity();
        for (std::size_t i = 0; i < N; ++i) {
            const float theta = joints_[i].is_revolute ? joints_[i].theta + q[i] : joints_[i].theta;
            const float d = joints_[i].is_revolute ? joints_[i].d : joints_[i].d + q[i];
            current = current * compute_dh_transform(theta, d, joints_[i].a, joints_[i].alpha);
        }
        return current;
    }

    [[nodiscard]] Jacobian compute_jacobian(const JointAngles& q) const noexcept {
        Jacobian jac{};
        std::array<Mat4, N + 1> frames{};
        frames[0] = Mat4::identity();

        Mat4 current = Mat4::identity();
        for (std::size_t i = 0; i < N; ++i) {
            const float theta = joints_[i].is_revolute ? joints_[i].theta + q[i] : joints_[i].theta;
            const float d = joints_[i].is_revolute ? joints_[i].d : joints_[i].d + q[i];
            current = current * compute_dh_transform(theta, d, joints_[i].a, joints_[i].alpha);
            frames[i + 1] = current;
        }

        const Vec3 p_ee = frames[N].translation();

        for (std::size_t i = 0; i < N; ++i) {
            const Vec3 z_i = frames[i].z_axis();
            const Vec3 p_i = frames[i].translation();

            if (joints_[i].is_revolute) {
                const Vec3 j_v = z_i.cross(p_ee - p_i);
                jac[0][i] = j_v.x;
                jac[1][i] = j_v.y;
                jac[2][i] = j_v.z;
                jac[3][i] = z_i.x;
                jac[4][i] = z_i.y;
                jac[5][i] = z_i.z;
            } else {
                jac[0][i] = z_i.x;
                jac[1][i] = z_i.y;
                jac[2][i] = z_i.z;
                jac[3][i] = 0.0f;
                jac[4][i] = 0.0f;
                jac[5][i] = 0.0f;
            }
        }
        return jac;
    }

    [[nodiscard]] std::optional<JointAngles> inverse_kinematics_dls(
        const Vec3& target_pos,
        const JointAngles& q_init,
        int max_iters = 50,
        float tolerance = 1e-4f,
        float lambda = 0.1f) const noexcept {

        JointAngles q = q_init;
        const float lambda_sq = lambda * lambda;

        for (int iter = 0; iter < max_iters; ++iter) {
            const Mat4 t_ee = forward_kinematics(q);
            const Vec3 err = target_pos - t_ee.translation();

            if (err.norm() < tolerance) {
                return q; // Збіжність досягнута
            }

            const Jacobian jac = compute_jacobian(q);

            // A = J_pos * J_pos^T + lambda^2 * I (розмірність 3x3)
            std::array<std::array<float, 3>, 3> a_mat{};
            for (std::size_t r = 0; r < 3; ++r) {
                for (std::size_t c = 0; c < 3; ++c) {
                    float sum = 0.0f;
                    for (std::size_t k = 0; k < N; ++k) {
                        sum += jac[r][k] * jac[c][k];
                    }
                    a_mat[r][c] = sum + (r == c ? lambda_sq : 0.0f);
                }
            }

            const float det = a_mat[0][0] * (a_mat[1][1] * a_mat[2][2] - a_mat[1][2] * a_mat[2][1]) -
                              a_mat[0][1] * (a_mat[1][0] * a_mat[2][2] - a_mat[1][2] * a_mat[2][0]) +
                              a_mat[0][2] * (a_mat[1][0] * a_mat[2][1] - a_mat[1][1] * a_mat[2][0]);

            if (std::abs(det) < 1e-7f) return std::nullopt;
            const float inv_det = 1.0f / det;

            std::array<std::array<float, 3>, 3> a_inv{};
            a_inv[0][0] = (a_mat[1][1] * a_mat[2][2] - a_mat[1][2] * a_mat[2][1]) * inv_det;
            a_inv[0][1] = (a_mat[0][2] * a_mat[2][1] - a_mat[0][1] * a_mat[2][2]) * inv_det;
            a_inv[0][2] = (a_mat[0][1] * a_mat[1][2] - a_mat[0][2] * a_mat[1][1]) * inv_det;

            a_inv[1][0] = (a_mat[1][2] * a_mat[2][0] - a_mat[1][0] * a_mat[2][2]) * inv_det;
            a_inv[1][1] = (a_mat[0][0] * a_mat[2][2] - a_mat[0][2] * a_mat[2][0]) * inv_det;
            a_inv[1][2] = (a_mat[0][2] * a_mat[1][0] - a_mat[0][0] * a_mat[1][2]) * inv_det;

            a_inv[2][0] = (a_mat[1][0] * a_mat[2][1] - a_mat[1][1] * a_mat[2][0]) * inv_det;
            a_inv[2][1] = (a_mat[0][1] * a_mat[2][0] - a_mat[0][0] * a_mat[2][1]) * inv_det;
            a_inv[2][2] = (a_mat[0][0] * a_mat[1][1] - a_mat[0][1] * a_mat[1][0]) * inv_det;

            const std::array<float, 3> err_arr{err.x, err.y, err.z};
            std::array<float, 3> v_temp{};
            for (std::size_t r = 0; r < 3; ++r) {
                v_temp[r] = a_inv[r][0] * err_arr[0] +
                            a_inv[r][1] * err_arr[1] +
                            a_inv[r][2] * err_arr[2];
            }

            for (std::size_t i = 0; i < N; ++i) {
                const float dq = jac[0][i] * v_temp[0] +
                                 jac[1][i] * v_temp[1] +
                                 jac[2][i] * v_temp[2];

                q[i] = std::clamp(q[i] + dq, joints_[i].q_min, joints_[i].q_max);
            }
        }
        return std::nullopt; // Не вдалося зійтися за задану кількість ітерацій
    }

private:
    JointArray joints_;
};
