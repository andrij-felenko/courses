class CustomNode {
public:
    // Одиночні форми виділення
    static void* operator new(std::size_t size);
    static void* operator new(std::size_t size, const std::nothrow_t&) noexcept;
    static void* operator new(std::size_t size, std::align_val_t align);

    // Масивні форми виділення
    static void* operator new[](std::size_t size);
    static void* operator new[](std::size_t size, std::align_val_t align);

    // Одиночні форми звільнення
    static void operator delete(void* ptr) noexcept;
    static void operator delete(void* ptr, std::size_t size) noexcept;
    static void operator delete(void* ptr, std::align_val_t align) noexcept;
    static void operator delete(void* ptr, std::size_t size, std::align_val_t align) noexcept;

    // Масивні форми звільнення
    static void operator delete[](void* ptr) noexcept;
    static void operator delete[](void* ptr, std::size_t size) noexcept;
};
