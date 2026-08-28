namespace my_lib {
    namespace __draw_detail {
        // Крок 1: Оголошення видаленої функції в отруєному контексті.
        // Це блокує нескінченну рекурсію, якщо ADL знову знайде назву draw
        void draw() = delete;

        // Крок 2: Опис концептів для послідовного вибору гілки диспетчеризації
        template<typename T>
        concept has_member_draw = requires(T&& t) {
            std::forward<T>(t).draw();
        };

        template<typename T>
        concept has_adl_draw = !has_member_draw<T> && requires(T&& t) {
            draw(std::forward<T>(t)); // ADL шукає у внутрішньому просторі __draw_detail
        };

        // Крок 3: Головний тип функтора
        struct __draw_fn {
            // Гілка 1: Виклик методу-члена класу t.draw()
            template<has_member_draw T>
            constexpr auto operator()(T&& t) const
                noexcept(noexcept(std::forward<T>(t).draw()))
            {
                return std::forward<T>(t).draw();
            }

            // Гілка 2: Виклик функції draw(t) через ADL у ізольованому контексті
            template<has_adl_draw T>
            constexpr auto operator()(T&& t) const
                noexcept(noexcept(draw(std::forward<T>(t))))
            {
                return draw(std::forward<T>(t));
            }

            // Заборона шкідливих операцій над CPO об'єктом
            __draw_fn() = default;
            __draw_fn(const __draw_fn&) = delete;
            __draw_fn(__draw_fn&&) = delete;
            __draw_fn& operator=(const __draw_fn&) = delete;
            __draw_fn& operator=(__draw_fn&&) = delete;
        };
    }

    // Крок 4: Глобальна inline constexpr константа CPO
    inline constexpr __draw_detail::__draw_fn draw{};
}
