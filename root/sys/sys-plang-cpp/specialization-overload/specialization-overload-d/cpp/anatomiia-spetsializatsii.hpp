// 1. Первинний шаблон структури
template<typename T, typename Allocator = std::allocator<T>>
struct DataBuffer {
    void store(const T& item);
};

// 2. Часткова спеціалізація для будь-яких вказівників T*
template<typename T, typename Allocator>
struct DataBuffer<T*, Allocator> {
    void store(const T* item); // Специфічна логіка збереження вказівників
};

// 3. Повна спеціалізація для конкретного типу void
template<>
struct DataBuffer<void, std::allocator<void>> {
    void store_raw(const void* item, std::size_t bytes);
};
