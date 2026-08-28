#include <cstdint>

namespace jinv {
enum class SecurityFlags : uint32_t {
    Ok = 0,
    Anomalous = 1 << 0,
    LowEmbedding = 1 << 1,
    Singular = 1 << 2,
    CmWeak = 1 << 3
};

[[nodiscard]] SecurityFlags audit_security(
    const ShortWeierstrassCurve& crv,
    int64_t p,
    int64_t order
);
}
