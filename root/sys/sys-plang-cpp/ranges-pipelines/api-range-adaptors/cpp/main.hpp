// Концептуальна реалізація базового класу C++23 range_adaptor_closure:
namespace std::ranges {

template <typename D>
struct range_adaptor_closure {
    // Оператор pipe для зв'язування: range | closure
    template <range R>
    requires can_apply<D, R>
    [[nodiscard]] constexpr auto operator|(R&& r, const D& self) const {
        return self(std::forward<R>(r));
    }

    // Оператор pipe для композиції двох замикань: closure1 | closure2
    template <typename C2>
    [[nodiscard]] constexpr auto operator|(const D& self, const C2& c2) const {
        return views::pipeline(self, c2);
    }
};

} // namespace std::ranges
