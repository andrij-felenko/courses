template <class Callback>
class stop_callback {
public:
    using callback_type = Callback;

    // Реєстрація зворотного виклику
    template <class C>
    explicit stop_callback(const std::stop_token& st, C&& cb)
        noexcept(std::is_nothrow_constructible_v<Callback, C>);

    template <class C>
    explicit stop_callback(std::stop_token&& st, C&& cb)
        noexcept(std::is_nothrow_constructible_v<Callback, C>);

    // Деструктор (скасовує реєстрацію callback)
    ~stop_callback();

    stop_callback(const stop_callback&) = delete;
    stop_callback& operator=(const stop_callback&) = delete;
};
