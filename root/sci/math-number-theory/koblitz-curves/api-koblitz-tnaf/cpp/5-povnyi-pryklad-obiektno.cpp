#include <cstdint>
#include <array>
#include <span>
#include <vector>
#include <expected>

namespace koblitz {

template <size_t M>
class Engine {
public:
    explicit Engine(const DomainParams<M>& params) : params_(params) {}

    [[nodiscard]] std::expected<Point<M>, Status> scalar_multiply(
        const Point<M>& base,
        std::span<const uint64_t, DomainParams<M>::Words> scalar,
        uint8_t window_size = 4
    ) const noexcept {
        return scalar_multiply_wtnaf(params_, base, scalar, window_size);
    }

private:
    DomainParams<M> params_;
};

} // namespace koblitz
