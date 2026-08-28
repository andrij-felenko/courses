namespace user_space {
    struct MyOperationState {
        void start() noexcept {}
    };

    struct MySender {
        // Реалізація точки налаштування connect для MySender
        template<typename Receiver>
        friend auto tag_invoke(my_framework::connect_t, MySender&& self, Receiver&& r) noexcept {
            return MyOperationState{};
        }
    };
}
