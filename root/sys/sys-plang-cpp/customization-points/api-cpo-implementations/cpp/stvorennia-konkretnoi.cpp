namespace my_framework {
    // Структура тегу точки налаштування "connect"
    struct connect_t {
        template<typename Sender, typename Receiver>
            requires tag_invocable<connect_t, Sender, Receiver>
        constexpr decltype(auto) operator()(Sender&& s, Receiver&& r) const
            noexcept(noexcept(tag_invoke(connect_t{}, std::forward<Sender>(s), std::forward<Receiver>(r))))
        {
            return tag_invoke(connect_t{}, std::forward<Sender>(s), std::forward<Receiver>(r));
        }
    };

    // Глобальний об'єкт точки налаштування connect
    inline constexpr connect_t connect{};
}
