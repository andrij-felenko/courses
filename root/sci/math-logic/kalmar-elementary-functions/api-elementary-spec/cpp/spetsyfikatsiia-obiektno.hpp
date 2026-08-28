namespace kalmar {

class Expression {
public:
    Expression(Expression&& other) noexcept;
    Expression& operator=(Expression&& other) noexcept;
    ~Expression() = default;

    Expression(const Expression&) = delete;
    Expression& operator=(const Expression&) = delete;

    [[nodiscard]] Expression clone() const;

    [[nodiscard]] size_t tower_height() const noexcept;
    [[nodiscard]] size_t node_count() const noexcept;

    [[nodiscard]] std::expected<uint64_t, StatusCode> 
    evaluate(std::span<uint64_t> env) const noexcept;

    [[nodiscard]] std::expected<bool, StatusCode> 
    evaluate_as_predicate(std::span<uint64_t> env) const noexcept;

    static Expression make_constant(uint64_t val);
    static Expression make_variable(size_t var_idx);
    static Expression make_add(Expression lhs, Expression rhs);
    static Expression make_sub(Expression lhs, Expression rhs);
    static Expression make_mul(Expression lhs, Expression rhs);
    static Expression make_div(Expression lhs, Expression rhs);
    static Expression make_pow(Expression base, Expression exponent);
    static Expression make_sum(size_t var_idx, Expression bound, Expression body);
    static Expression make_prod(size_t var_idx, Expression bound, Expression body);
    static Expression make_search(size_t var_idx, Expression bound, Expression predicate);

private:
    std::unique_ptr<AstNode> root_;
    explicit Expression(std::unique_ptr<AstNode> root) noexcept;
};

} // namespace kalmar
