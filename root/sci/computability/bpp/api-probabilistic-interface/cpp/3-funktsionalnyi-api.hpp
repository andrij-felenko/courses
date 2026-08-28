// cpp
#include <span>
#include <expected>

namespace bpp {

class BppEngine {
public:
    explicit BppEngine(BppConfig config);
    ~BppEngine();

    [[nodiscard]] std::expected<Status, Status> execute(
        std::span<const std::uint8_t> data, 
        ExecutionStats& stats) const noexcept;

    [[nodiscard]] static std::uint32_t calculate_required_rounds(
        double max_eps, 
        double delta_gap) noexcept;

private:
    BppConfig config_;
};

} // namespace bpp
