/* Шаблонний клас із підтримкою поліморфного алокатора std::pmr */
template <typename T, typename BinaryOp = std::ranges::min>
class PmrSparseTable {
public:
    using allocator_type = std::pmr::polymorphic_allocator<T>;

    explicit PmrSparseTable(std::span<const T> values, 
                            BinaryOp op = BinaryOp{}, 
                            allocator_type alloc = {});

    [[nodiscard]] std::optional<T> query(std::size_t l, std::size_t r) const noexcept;
    [[nodiscard]] allocator_type get_allocator() const noexcept;

private:
    BinaryOp op_;
    std::size_t n_{0};
    std::size_t levels_{0};
    std::pmr::vector<T> table_;
};
