template <typename T>
class SimpleStack {
public:
    void push(const T& item);
    void push(T&& item);
    T pop();
    [[nodiscard]] bool empty() const noexcept;

private:
    T* data_{nullptr};
    std::size_t size_{0};
    std::size_t capacity_{0};
};
