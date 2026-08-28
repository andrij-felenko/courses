/* Інтерфейс Disjoint Sparse Table мовою C++ */
template <typename T, typename BinaryOp = std::plus<T>>
requires std::invocable<BinaryOp, T, T> && std::copy_constructible<T>
class DisjointSparseTable {
public:
    using value_type = T;
    using size_type = std::size_t;

    explicit DisjointSparseTable(std::span<const T> values, BinaryOp op = BinaryOp{});
    [[nodiscard]] std::optional<T> query(size_type l, size_type r) const noexcept;
    [[nodiscard]] size_type size() const noexcept;
    [[nodiscard]] bool empty() const noexcept;

private:
    BinaryOp op_;
    size_type n_{0};
    size_type padded_n_{0};
    size_type levels_{0};
    std::vector<T> table_;
};
