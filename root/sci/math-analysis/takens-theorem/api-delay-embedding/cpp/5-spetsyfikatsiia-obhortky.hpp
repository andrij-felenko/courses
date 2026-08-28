namespace takens {

class DelayMatrix {
public:
    DelayMatrix() noexcept = default;
    DelayMatrix(size_t rows, size_t cols, size_t delay, std::vector<double> data);

    [[nodiscard]] size_t rows() const noexcept { return m_rows; }
    [[nodiscard]] size_t cols() const noexcept { return m_cols; }
    [[nodiscard]] size_t delay() const noexcept { return m_delay; }

    [[nodiscard]] double operator()(size_t r, size_t c) const {
        return m_data[r * m_cols + c];
    }

    [[nodiscard]] std::span<const double> row(size_t r) const {
        return std::span<const double>(&m_data[r * m_cols], m_cols);
    }

    [[nodiscard]] const std::vector<double>& data() const noexcept { return m_data; }

private:
    size_t m_rows{0};
    size_t m_cols{0};
    size_t m_delay{0};
    std::vector<double> m_data;
};

struct MutualInfoResult {
    std::vector<double> mi_values;
    size_t optimal_delay;
};

struct FNNResult {
    std::vector<double> fnn_ratios;
    size_t optimal_dim;
};

class Embedder {
public:
    explicit Embedder(std::span<const double> signal, Config config = Config{});

    [[nodiscard]] std::expected<MutualInfoResult, Status> compute_mutual_information() const;
    [[nodiscard]] std::expected<FNNResult, Status> compute_fnn(size_t delay) const;

    [[nodiscard]] std::expected<DelayMatrix, Status> embed(size_t delay, size_t dim) const;
    [[nodiscard]] std::expected<DelayMatrix, Status> auto_embed() const;

    [[nodiscard]] std::expected<double, Status> estimate_lyapunov(const DelayMatrix& matrix) const;

private:
    std::span<const double> m_signal;
    Config m_config;
};

} // namespace takens
