namespace interpol {

template <std::floating_point T = double>
class BarycentricInterpolator {
public:
    explicit BarycentricInterpolator(size_t initial_capacity = 8, T eps = static_cast<T>(1e-12));
    
    // Переміщення дозволено, копіювання дозволено
    BarycentricInterpolator(const BarycentricInterpolator&) = default;
    BarycentricInterpolator(BarycentricInterpolator&&) noexcept = default;
    BarycentricInterpolator& operator=(const BarycentricInterpolator&) = default;
    BarycentricInterpolator& operator=(BarycentricInterpolator&&) noexcept = default;
    ~BarycentricInterpolator() = default;

    // Додавання вузлів та оцінка
    bool add_point(T x, T y);
    [[nodiscard]] std::optional<T> evaluate(T target_x) const noexcept;
    [[nodiscard]] T operator()(T target_x) const; // Викидає std::out_of_range при n==0

    // Стан та очищення
    void clear() noexcept;
    [[nodiscard]] size_t size() const noexcept;
    [[nodiscard]] bool empty() const noexcept;
    [[nodiscard]] std::span<const T> x_nodes() const noexcept;
    [[nodiscard]] std::span<const T> y_nodes() const noexcept;
    [[nodiscard]] std::span<const T> weights() const noexcept;

private:
    std::vector<T> x_;
    std::vector<T> y_;
    std::vector<T> weights_;
    T eps_;
};

} // namespace interpol
