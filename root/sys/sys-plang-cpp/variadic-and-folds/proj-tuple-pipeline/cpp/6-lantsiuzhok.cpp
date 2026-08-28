template <typename... Actions>
class ActionPipeline {
    std::tuple<Actions...> actions_;

public:
    constexpr explicit ActionPipeline(Actions... actions)
        : actions_(std::move(actions)...) {}

    template <typename Event>
    void execute(const Event& event) const {
        std::apply([&](const auto&... action_instances) {
            // Згортка за оператором коми послідовно викликає кожну дію
            (action_instances(event), ...);
        }, actions_);
    }
};
