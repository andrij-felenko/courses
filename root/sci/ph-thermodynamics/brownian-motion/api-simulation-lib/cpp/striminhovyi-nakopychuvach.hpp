namespace brownian {

class StreamAccumulator {
public:
    explicit StreamAccumulator(std::size_t num_lags);
    ~StreamAccumulator() = default;

    void push_step(std::size_t lag, double dx, double dy, double dz = 0.0);
    [[nodiscard]] MsdAnalysis finalize() const;

private:
    std::vector<double> msd_sum_;
    std::vector<std::size_t> sample_count_;
};

} // namespace brownian
