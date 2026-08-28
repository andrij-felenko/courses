template <typename T>
class PropagateConst {
    T ptr_;
public:
    template <typename U>
    explicit PropagateConst(U&& u) : ptr_(std::forward<U>(u)) {}

    auto* get() noexcept { return ptr_.get(); }
    const auto* get() const noexcept { return ptr_.get(); }

    auto* operator->() noexcept { return get(); }
    const auto* operator->() const noexcept { return get(); }

    auto& operator*() noexcept { return *get(); }
    const auto& operator*() const noexcept { return *get(); }
};
