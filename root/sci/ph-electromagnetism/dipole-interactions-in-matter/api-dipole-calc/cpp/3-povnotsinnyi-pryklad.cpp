#include <iostream>
#include <array>
#include <cmath>
#include <expected>
#include <system_error>
#include <span>

namespace dipole::api {

enum class ErrorCode {
    Success = 0,
    NullPointer,
    Singularity,
    InvalidParameter
};

struct Vector3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr double dot(const Vector3& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }

    [[nodiscard]] constexpr Vector3 cross(const Vector3& o) const noexcept {
        return {
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        };
    }
};

struct DipoleState {
    Vector3 position{};
    Vector3 moment{};
    double cutoff{1e-9};
};

class DipoleCalculator {
private:
    static constexpr double k_e = 8.9875517923e9; // 1 / (4*pi*eps0)

public:
    [[nodiscard]] static std::expected<double, ErrorCode> calculate_potential(
        const DipoleState& state,
        Vector3 point) noexcept {
        
        if (state.cutoff < 0.0) {
            return std::unexpected(ErrorCode::InvalidParameter);
        }

        Vector3 R = {
            point.x - state.position.x,
            point.y - state.position.y,
            point.z - state.position.z
        };

        double r_sq = R.dot(R) + state.cutoff * state.cutoff;
        double r_len = std::sqrt(r_sq);
        double r_pow3 = r_len * r_sq;

        double dot_pR = state.moment.dot(R);
        return k_e * dot_pR / r_pow3;
    }

    [[nodiscard]] static std::expected<Vector3, ErrorCode> calculate_torque(
        const DipoleState& state,
        Vector3 ext_field) noexcept {
        
        return state.moment.cross(ext_field);
    }

    [[nodiscard]] static double calculate_potential_energy(
        const DipoleState& state,
        Vector3 ext_field) noexcept {
        
        return -state.moment.dot(ext_field);
    }
};

} // namespace dipole::api

int main() {
    using namespace dipole::api;

    DipoleState state{
        .position = {0.0, 0.0, 0.0},
        .moment = {0.0, 0.0, 3.33564e-30}, // 1 Debye
        .cutoff = 1e-9
    };

    Vector3 pt{1e-9, 0.0, 0.0};
    auto result = DipoleCalculator::calculate_potential(state, pt);

    if (result.has_value()) {
        std::cout << "Потенціал (1 Debye, 1 nm) = " << result.value() << " V\n";
    } else {
        std::cerr << "Помилка обчислення потенціалу!\n";
    }

    return 0;
}
