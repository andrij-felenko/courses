namespace stats {

template <typename FloatType = double>
class StreamingAccumulator {
public:
    constexpr StreamingAccumulator() noexcept = default;
    void reset() noexcept;
};

} // namespace stats
