namespace stats {

template <typename FloatType>
[[nodiscard]] FloatType StreamingAccumulator<FloatType>::sample_variance() const noexcept;

template <typename FloatType>
[[nodiscard]] FloatType StreamingAccumulator<FloatType>::population_variance() const noexcept;

template <typename FloatType>
[[nodiscard]] FloatType StreamingAccumulator<FloatType>::stddev() const noexcept;

template <typename FloatType>
[[nodiscard]] FloatType StreamingAccumulator<FloatType>::skewness() const noexcept;

template <typename FloatType>
[[nodiscard]] FloatType StreamingAccumulator<FloatType>::kurtosis() const noexcept;

} // namespace stats
