template <typename... Filters>
class MoveAwarePipeline {
    std::tuple<Filters...> filters_;

public:
    template <typename Event>
    constexpr bool process(Event&& event) const {
        return std::apply([&](const auto&... f) {
            // Передача універсального посилання гарантує відсутність небажаних копіювань
            return (f(std::forward<Event>(event)) && ...);
        }, filters_);
    }
};
