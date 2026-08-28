template<class Callback>
class stop_callback {
public:
    using callback_type = Callback;

    // Конструктори з реєстрацією
    template<class C>
    explicit stop_callback(const stop_token& st, C&& cb)
        noexcept(std::is_nothrow_constructible_v<Callback, C>);

    template<class C>
    explicit stop_callback(stop_token&& st, C&& cb)
        noexcept(std::is_nothrow_constructible_v<Callback, C>);

    // Деструктор зі зняттям підписки та блокуванням
    ~stop_callback();

    // Заборона копіювання та переміщення
    stop_callback(const stop_callback&) = delete;
    stop_callback(stop_callback&&) = delete;
    stop_callback& operator=(const stop_callback&) = delete;
    stop_callback& operator=(stop_callback&&) = delete;
};

// Настанова виведення типів аргументів шаблону (CTAD)
template<class Callback>
stop_callback(stop_token, Callback) -> stop_callback<Callback>;
