#include <cstddef>
#include <expected>
#include <system_error>
#include <span>

namespace virasoro {

struct Config {
    double central_charge{0.0};
    int max_level{20};
    bool use_ghost_sector{false};
};

struct KacResult {
    double central_charge{0.0};
    double conformal_weight{0.0};
    int level{0};
    std::size_t dimension{0};
    double determinant{0.0};
    bool is_unitary{true};
};

struct CommutatorResult {
    int target_mode{0};
    double linear_coefficient{0.0};
    double central_term{0.0};
};

enum class ErrorCode {
    Success = 0,
    InvalidMode = -1,
    LevelExceeded = -2,
    NonUnitary = -3,
    NullPointer = -4,
    OutOfMemory = -5
};

class Evaluator {
private:
    Config config_;

public:
    explicit Evaluator(Config cfg) noexcept : config_(cfg) {}

    [[nodiscard]] std::expected<CommutatorResult, ErrorCode>
    compute_commutator(int n, int m) const noexcept;

    [[nodiscard]] std::expected<KacResult, ErrorCode>
    evaluate_kac_determinant(double conformal_weight_h, int level) const noexcept;

    [[nodiscard]] static double
    total_central_charge(int num_bosons, int num_fermions, bool include_brst_ghosts) noexcept;
};

} // namespace virasoro
