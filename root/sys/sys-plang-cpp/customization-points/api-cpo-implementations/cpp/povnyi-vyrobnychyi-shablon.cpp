namespace my_framework {
    namespace __tag_invoke_detail {
        // Оголошення незавершеної функції в отруєному контексті
        void tag_invoke();

        // Концепт перевірки спроможності виклику tag_invoke для даного тегу та аргументів
        template<typename Tag, typename... Args>
        concept tag_invocable = requires(Tag&& tag, Args&&... args) {
            tag_invoke(std::forward<Tag>(tag), std::forward<Args>(args)...);
        };

        // Функтор диспетчеризації
        struct __tag_invoke_fn {
            template<typename Tag, typename... Args>
                requires tag_invocable<Tag, Args...>
            constexpr decltype(auto) operator()(Tag&& tag, Args&&... args) const
                noexcept(noexcept(tag_invoke(std::forward<Tag>(tag), std::forward<Args>(args)...)))
            {
                return tag_invoke(std::forward<Tag>(tag), std::forward<Args>(args)...);
            }
        };
    }

    // Єдиний глобальний об'єкт диспетчеризації
    inline constexpr __tag_invoke_detail::__tag_invoke_fn tag_invoke{};

    // Допоміжний концепт для публічного користування
    template<typename Tag, typename... Args>
    concept tag_invocable = __tag_invoke_detail::tag_invocable<Tag, Args...>;
}
