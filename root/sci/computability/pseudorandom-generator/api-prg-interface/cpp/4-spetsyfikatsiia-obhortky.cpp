#include <span>
#include <vector>
#include <memory>
#include <expected>

class NisanWigdersonEngine {
public:
    explicit NisanWigdersonEngine(
        const DesignConfig& config,
        std::span<const uint8_t> truth_table
    );
    
    ~NisanWigdersonEngine() = default;
    NisanWigdersonEngine(const NisanWigdersonEngine&) = delete;
    NisanWigdersonEngine& operator=(const NisanWigdersonEngine&) = delete;
    NisanWigdersonEngine(NisanWigdersonEngine&&) noexcept = default;
    NisanWigdersonEngine& operator=(NisanWigdersonEngine&&) noexcept = default;

    [[nodiscard]] std::expected<std::vector<uint8_t>, nw_status_t> 
    generateStream(std::span<const uint8_t> seed) const noexcept;
};
