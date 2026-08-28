namespace sgh {
class OrdinalNode {
public:
    virtual ~OrdinalNode() = default;
    [[nodiscard]] virtual uint64_t evaluate(uint64_t n) const = 0;
    [[nodiscard]] virtual std::string to_string() const = 0;
    [[nodiscard]] virtual std::unique_ptr<OrdinalNode> clone() const = 0;
    [[nodiscard]] virtual std::unique_ptr<OrdinalNode> fundamental_step(uint64_t n) const = 0;
    [[nodiscard]] virtual bool is_zero() const noexcept { return false; }
    [[nodiscard]] virtual bool is_successor() const noexcept { return false; }
    [[nodiscard]] virtual bool is_limit() const noexcept { return false; }
};
using OrdinalPtr = std::unique_ptr<OrdinalNode>;
}
