namespace std::execution {
    struct set_value_t   { template <typename... Ts> void operator()(auto&& rcvr, Ts&&... args) const; };
    struct set_error_t   { template <typename E>     void operator()(auto&& rcvr, E&& err) const; };
    struct set_stopped_t { void operator()(auto&& rcvr) const; };

    inline constexpr set_value_t set_value{};
    inline constexpr set_error_t set_error{};
    inline constexpr set_stopped_t set_stopped{};

    template <typename S>
    concept sender = requires {
        typename completion_signatures_of_t<S>;
    };

    template <typename Sch>
    concept scheduler = requires(Sch sch) {
        { schedule(sch) } -> sender;
    };

    template <typename Op>
    concept operation_state = requires(Op& op) {
        { start(op) } noexcept;
    };
}
