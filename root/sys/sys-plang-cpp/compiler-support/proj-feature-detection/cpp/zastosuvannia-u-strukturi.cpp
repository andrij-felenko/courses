// Приклад використання портативного атрибута
struct EmptyStatelessAllocator {};

template <typename T, typename Allocator = EmptyStatelessAllocator>
class CustomBuffer {
public:
    COMPAT_NODISCARD_MSG("Ignoring empty check result is likely a bug")
    bool empty() const noexcept {
        return size_ == 0;
    }

private:
    T* data_{nullptr};
    size_t size_{0};

    // Завдяки макросу розмір об'єкта не збільшується на 8 байтів вирівнювання у GCC, Clang та MSVC
    COMPAT_NO_UNIQUE_ADDRESS Allocator alloc_;
};
