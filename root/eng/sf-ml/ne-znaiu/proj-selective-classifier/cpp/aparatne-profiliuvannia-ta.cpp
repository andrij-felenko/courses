// RAII обгортка для профілювання тактів DWT на C++20
class DwtCycleProfiler {
public:
    DwtCycleProfiler() noexcept : start_(DWT->CYCCNT) {}
    [[nodiscard]] uint32_t elapsed() const noexcept {
        return DWT->CYCCNT - start_;
    }
private:
    uint32_t start_{0};
};

template <std::size_t N>
uint32_t profile_selective_filter_cpp(
    std::span<const float> logits,
    const SelectiveClassifierEngine<N>& engine
) {
    DwtCycleProfiler profiler;
    auto res = engine.evaluate(logits);
    return profiler.elapsed();
}
