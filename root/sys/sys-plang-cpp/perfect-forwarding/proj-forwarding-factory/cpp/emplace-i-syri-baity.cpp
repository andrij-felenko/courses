template <class T>
class Bin {
public:
    explicit Bin(std::size_t capacity)
        : raw_(static_cast<std::byte*>(
              ::operator new(capacity * sizeof(T), std::align_val_t{alignof(T)}))),
          cap_(capacity) {}

    ~Bin() {
        while (size_ > 0) { --size_; (*this)[size_].~T(); }
        ::operator delete(raw_, std::align_val_t{alignof(T)});
    }

    Bin(const Bin&) = delete;
    Bin& operator=(const Bin&) = delete;

    template <class... Args>
    T& emplace(Args&&... args) {
        if (size_ == cap_) throw std::length_error("Bin: місця немає");
        void* slot = raw_ + size_ * sizeof(T);
        T* made = ::new (slot) T(std::forward<Args>(args)...);
        ++size_;
        return *made;
    }

    T& operator[](std::size_t i) {
        return *std::launder(reinterpret_cast<T*>(raw_ + i * sizeof(T)));
    }

    std::size_t size() const { return size_; }

private:
    std::byte* raw_;
    std::size_t cap_;
    std::size_t size_ = 0;
};
