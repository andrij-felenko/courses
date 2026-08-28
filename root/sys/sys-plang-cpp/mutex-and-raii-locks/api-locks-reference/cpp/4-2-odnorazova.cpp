namespace std {
    struct once_flag {
        constexpr once_flag() noexcept;
        once_flag(const once_flag&) = delete;
        once_flag& operator=(const once_flag&) = delete;
    };

    template <class Callable, class... Args>
    void call_once(once_flag& flag, Callable&& f, Args&&... args);
}
