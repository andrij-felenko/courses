template <typename... Filters>
class EventPipeline {
    std::tuple<Filters...> filters_;

public:
    constexpr explicit EventPipeline(Filters... filters)
        : filters_(std::move(filters)...) {}

    template <typename Event>
    [[nodiscard]] constexpr bool process(const Event& event) const noexcept {
        return std::apply([&](const auto&... filter_instances) noexcept {
            // Унарна права згортка логічного І: (filter_instances(event) && ...)
            // Гарантує виконання за правилом короткого замикання (short-circuit)
            return (filter_instances(event) && ...);
        }, filters_);
    }
};
