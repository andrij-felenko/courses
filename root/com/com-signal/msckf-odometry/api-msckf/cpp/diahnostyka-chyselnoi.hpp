#include <memory>
#include <expected>

namespace msckf {

enum class Status {
    Success = 0,
    InvalidArgument,
    NotInitialized,
    TimeRegression,
    NumericalDivergence
};

class MsckfEngine {
public:
    explicit MsckfEngine(const MsckfConfig& config);
    ~MsckfEngine();

    MsckfEngine(const MsckfEngine&) = delete;
    MsckfEngine& operator=(const MsckfEngine&) = delete;
    MsckfEngine(MsckfEngine&&) noexcept;
    MsckfEngine& operator=(MsckfEngine&&) noexcept;

    // Скидання стану фільтра
    void reset();

    // Передача первинних даних
    std::expected<void, Status> feedImu(const ImuMeasurement& imu);
    std::expected<void, Status> feedFrame(const FeatureFrame& frame);

    // Отримання оцінки навігації
    [[nodiscard]] std::expected<EstimatorOutput, Status> getEstimate() const noexcept;
    [[nodiscard]] Diagnostics getDiagnostics() const noexcept;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace msckf
