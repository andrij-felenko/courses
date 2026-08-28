/* cpp */
#include <expected>
#include <filesystem>
#include <span>
#include <string_view>

namespace navigation::wmm {

enum class WmmApiError {
    FileNotFound,
    CorruptedData,
    InvalidCoordinates,
    YearOutOfBands
};

class WorldMagneticModel {
public:
    [[nodiscard]] static std::expected<WorldMagneticModel, WmmApiError> load_from_file(
        const std::filesystem::path& model_path
    ) noexcept;

    [[nodiscard]] std::expected<WmmElements, WmmApiError> calculate(
        const WmmInput& input
    ) const noexcept;
};

} // namespace navigation::wmm
