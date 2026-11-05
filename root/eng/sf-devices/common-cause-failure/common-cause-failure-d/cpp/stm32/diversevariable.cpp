#include <cstdint>
#include <cstddef>

namespace Safety {

template <typename T>
class DiverseVariable {
private:
    T value_;
    T inverted_value_;
    static constexpr T Mask = static_cast<T>(~0ULL);

public:
    constexpr DiverseVariable() : value_(0), inverted_value_(Mask) {}
    
    explicit DiverseVariable(T val) 
        : value_(val), inverted_value_(val ^ Mask) {}

    [[nodiscard]] bool isValid() const noexcept {
        return (value_ ^ inverted_value_) == Mask;
    }

    [[nodiscard]] T getValue() const noexcept {
        return value_;
    }

    void update(T val) noexcept {
        value_ = val;
        inverted_value_ = val ^ Mask;
    }
};

enum class SecurityStatus : uint8_t {
    Valid = 0,
    MemoryCorrupted,
    CrossChannelDivergence
};

class CommonCauseGuardian {
private:
    static constexpr uint32_t MaxAllowedDelta = 15U;
    DiverseVariable<uint32_t> channel_b_store_{0};

    [[nodiscard]] static uint32_t computePrimaryAlgorithm(uint32_t raw) noexcept {
        return (raw * 1250U + 50U) / 100U;
    }

    [[nodiscard]] static uint32_t computeDiverseAlgorithm(uint32_t raw) noexcept {
        const uint32_t scaled = (raw * 10U);
        return (scaled * 125U / 10U);
    }

public:
    CommonCauseGuardian() = default;

    SecurityStatus evaluateDualChannel(uint32_t sampleA, uint32_t sampleB, uint32_t& safeResult) noexcept {
        // Крок 1: Обчислення первинного каналу у фазі T1
        const uint32_t outA = computePrimaryAlgorithm(sampleA);

        // Крок 2: Збереження комплементарного значення для захисту від SEU
        channel_b_store_.update(sampleB);

        // Перевірка цілісності оперативної пам'яті
        if (!channel_b_store_.isValid()) {
            safeResult = 0U;
            return SecurityStatus::MemoryCorrupted;
        }

        // Крок 3: Обчислення різнорідного каналу у фазі T2 (Часова різноманітність)
        const uint32_t outB = computeDiverseAlgorithm(channel_b_store_.getValue());

        // Крок 4: Перевірка розходження між різнорідними математичними моделями
        const int32_t divergence = static_cast<int32_t>(outA) - static_cast<int32_t>(outB);
        const uint32_t absDivergence = (divergence < 0) ? -divergence : divergence;

        if (absDivergence > MaxAllowedDelta) {
            safeResult = 0U;
            return SecurityStatus::CrossChannelDivergence;
        }

        safeResult = (outA + outB) / 2U;
        return SecurityStatus::Valid;
    }
};

} // namespace Safety
