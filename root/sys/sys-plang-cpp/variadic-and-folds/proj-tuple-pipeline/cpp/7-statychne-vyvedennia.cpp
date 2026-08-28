template <typename... Filters>
class SafePipeline {
    std::tuple<Filters...> filters_;

public:
    template <typename Event>
    constexpr bool process(const Event& event) const
        noexcept((noexcept(std::declval<Filters>()(event)) && ...))
    {
        return std::apply([&](const auto&... f) noexcept((noexcept(f(event)) && ...)) {
            return (f(event) && ...);
        }, filters_);
    }
};
