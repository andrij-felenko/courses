/* Структура затримкової матриці мовою C++ з підтримкою RAII */
class DelayMatrixCpp {
public:
    DelayMatrixCpp(std::span<const double> signal, size_t m, size_t delay)
        : m_cols(m) {
        if (signal.size() <= (m - 1) * delay) {
            throw std::invalid_argument("Довжина сигналу менша за необхідний інтервал затримки");
        }
        m_rows = signal.size() - (m - 1) * delay;
        m_data.resize(m_rows * m_cols);

        for (size_t i = 0; i < m_rows; ++i) {
            for (size_t j = 0; j < m_cols; ++j) {
                m_data[i * m_cols + j] = signal[i + j * delay];
            }
        }
    }

    [[nodiscard]] size_t rows() const noexcept { return m_rows; }
    [[nodiscard]] size_t cols() const noexcept { return m_cols; }
    [[nodiscard]] double operator()(size_t r, size_t c) const { return m_data[r * m_cols + c]; }
    [[nodiscard]] const std::vector<double>& raw_data() const noexcept { return m_data; }

private:
    size_t m_rows{0};
    size_t m_cols{0};
    std::vector<double> m_data;
};
