/* Шаблонний клас розрідженої таблиці мовою C++20 */
template <typename T, typename BinaryOp = std::ranges::min>
requires std::invocable<BinaryOp, T, T> && 
         std::copy_constructible<T>
class SparseTable {
public:
    using value_type = T;
    using size_type = std::size_t;
    using binary_op_type = BinaryOp;

private:
    BinaryOp op_;
    size_type n_{0};
    size_type levels_{0};
    std::vector<T> table_;
};
