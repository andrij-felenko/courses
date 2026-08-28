#include <string_view>
#include <span>

namespace physics::nonlinear::api {

class Hdf5Exporter {
public:
    [[nodiscard]] static std::expected<void, ApiErrorCode> save(
        std::string_view filepath,
        std::span<const double> w_matrix,
        std::size_t res_omega,
        std::size_t res_k) noexcept;
};

} // namespace physics::nonlinear::api
