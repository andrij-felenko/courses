template <typename T>
class OptionalStorage {
    alignas(T) std::byte buffer_[sizeof(T)];
    bool engaged_ = false;

public:
    template <typename... Args>
    void emplace(Args&&... args) {
        if (engaged_) {
            get_ptr()->~T();
        }
        ::new (static_cast<void*>(buffer_)) T(std::forward<Args>(args)...);
        engaged_ = true;
    }

    T* get_ptr() noexcept {
        return reinterpret_cast<T*>(buffer_); // ← ПОМИЛКА: ланцюжок походження розірвано
    }
};
