namespace std {

template <class... Signatures>
class move_only_function;

template <class R, class... Args>
class move_only_function<R(Args...)> {
public:
    using result_type = R;

    constexpr move_only_function() noexcept;
    constexpr move_only_function(nullptr_t) noexcept;
    move_only_function(move_only_function&&) noexcept;
    template <class F>
    move_only_function(F&& f);

    move_only_function(const move_only_function&) = delete;
    move_only_function& operator=(const move_only_function&) = delete;
    move_only_function& operator=(move_only_function&&) noexcept;

    explicit operator bool() const noexcept;
    R operator()(Args... args) const;
};

} // namespace std
