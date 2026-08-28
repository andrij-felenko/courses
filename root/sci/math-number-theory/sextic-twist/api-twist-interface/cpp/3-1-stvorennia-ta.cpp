#include <memory>
#include <expected>

class TwistContext {
public:
    enum class CurveId : std::uint32_t { kBn254 = 1, kBls12_381 = 2 };
    enum class TwistType : std::uint32_t { kDType = 0, kMType = 1 };

    static std::expected<std::unique_ptr<TwistContext>, TwistStatus> create(
        CurveId curve_id,
        TwistType twist_type
    ) noexcept;

    ~TwistContext() noexcept;
};
