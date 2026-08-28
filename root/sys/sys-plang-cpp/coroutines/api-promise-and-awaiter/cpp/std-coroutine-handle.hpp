template<class Promise> struct coroutine_handle {
    constexpr coroutine_handle() noexcept;
    constexpr coroutine_handle(nullptr_t) noexcept;
    coroutine_handle& operator=(nullptr_t) noexcept;

    static coroutine_handle from_promise(Promise&);
    constexpr void* address() const noexcept;
    static constexpr coroutine_handle from_address(void* addr);
    constexpr operator coroutine_handle<>() const noexcept;

    constexpr explicit operator bool() const noexcept;
    bool done() const;

    void resume() const;
    void operator()() const;                 // те саме, що resume()
    void destroy() const;

    Promise& promise() const;
};
