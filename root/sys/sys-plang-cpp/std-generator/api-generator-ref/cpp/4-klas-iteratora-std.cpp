class generator::iterator {
public:
    using value_type = generator::value_type;
    using difference_type = generator::difference_type;
    using iterator_concept = std::input_iterator_tag;

    iterator() noexcept : coroutine_(nullptr) {}

    // Операція розіменовування повертає посилання на згенероване значення
    yielded operator*() const noexcept(std::is_nothrow_copy_constructible_v<yielded>) {
        return coroutine_.promise().value();
    }

    // Операція інкремента відновлює виконання корутини
    iterator& operator++() {
        coroutine_.promise().resume_next();
        return *this;
    }

    void operator++(int) {
        (void)operator++();
    }

    // Порівняння з сентинелом перевіряє завершення корутини
    friend bool operator==(const iterator& it, std::default_sentinel_t) noexcept {
        return it.coroutine_.done();
    }
private:
    std::coroutine_handle<promise_type> coroutine_{nullptr};
};
