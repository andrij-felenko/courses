#include <cstdint>
#include <array>
#include <concepts>
#include <optional>

/* Клас двоточкового лінійного калібратора */
template <typename RawType = int32_t, typename PhysType = int32_t>
class TwoPointCalibrator {
public:
    constexpr TwoPointCalibrator(RawType raw1, RawType raw2, PhysType phys1, PhysType phys2)
        : raw_p1_(raw1), raw_p2_(raw2), phys_p1_(phys1), phys_p2_(phys2) {}

    [[nodiscard]] constexpr PhysType to_physical(RawType raw_adc) const noexcept {
        const RawType raw_delta = raw_p2_ - raw_p1_;
        if (raw_delta == 0) {
            return phys_p1_;
        }
        const auto scaled = static_cast<int64_t>(raw_adc - raw_p1_) * (phys_p2_ - phys_p1_);
        return phys_p1_ + static_cast<PhysType>(scaled / raw_delta);
    }

private:
    RawType raw_p1_{0};
    RawType raw_p2_{1};
    PhysType phys_p1_{0};
    PhysType phys_p2_{1};
};

/* Шаблонний експоненційний IIR-фільтр на фіксованій комі */
template <uint8_t ShiftK, typename SampleType = int32_t>
class FastEmaFilter {
public:
    constexpr FastEmaFilter() = default;

    SampleType update(SampleType input) noexcept {
        if (!initialized_) {
            accumulator_ = static_cast<int64_t>(input) << ShiftK;
            initialized_ = true;
        }
        accumulator_ += input - (accumulator_ >> ShiftK);
        return static_cast<SampleType>(accumulator_ >> ShiftK);
    }

    void reset() noexcept {
        initialized_ = false;
        accumulator_ = 0;
    }

private:
    int64_t accumulator_{0};
    bool initialized_{false};
};

/* Шаблонний фільтр рухомого середнього з вікном фіксованого розміру */
template <std::size_t WindowSize = 20, typename SampleType = int32_t>
class WindowedMovingAverage {
public:
    constexpr WindowedMovingAverage() {
        buffer_.fill(0);
    }

    SampleType update(SampleType input) noexcept {
        sum_ -= buffer_[index_];
        buffer_[index_] = input;
        sum_ += input;
        index_ = (index_ + 1) % WindowSize;
        if (count_ < WindowSize) {
            ++count_;
        }
        return static_cast<SampleType>(sum_ / count_);
    }

    void reset() noexcept {
        buffer_.fill(0);
        sum_ = 0;
        index_ = 0;
        count_ = 0;
    }

private:
    std::array<SampleType, WindowSize> buffer_{};
    int64_t sum_{0};
    std::size_t index_{0};
    std::size_t count_{0};
};
