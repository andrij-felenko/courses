namespace CM {
using VectorFunc = std::function<void(std::span<const double>, std::span<const double>, std::span<double>)>;

class System {
public:
    System(std::size_t dim_center, std::size_t dim_stable);
    
    void set_matrix_A(std::span<const double> A);
    void set_matrix_B(std::span<const double> B);
    void set_nonlinearity_f(VectorFunc f);
    void set_nonlinearity_g(VectorFunc g);

    [[nodiscard]] std::size_t dim_center() const noexcept;
    [[nodiscard]] std::size_t dim_stable() const noexcept;
};
} // namespace CM
