template <class T, class D = std::default_delete<T>>
class unique_ptr {
    T* p_;                                  // єдине поле з даними
    [[no_unique_address]] D d_;             // видалювач; порожній — не займає місця

public:
    explicit unique_ptr(T* p = nullptr) noexcept : p_(p) {}
    ~unique_ptr() { if (p_) d_(p_); }

    unique_ptr(const unique_ptr&)            = delete;   // копії немає
    unique_ptr& operator=(const unique_ptr&) = delete;

    unique_ptr(unique_ptr&& o) noexcept : p_(std::exchange(o.p_, nullptr)) {}
    // ...
};
