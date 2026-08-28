// 1. Первинний шаблон класу
template<typename T, typename Allocator = std::allocator<T>>
class Buffer {
public:
    void allocate(std::size_t n);
};

// 2. Часткова спеціалізація для вказівників (зберігає параметризацію T)
template<typename T, typename Allocator>
class Buffer<T*, Allocator> {
public:
    void allocate(std::size_t n);
};

// 3. Часткова спеціалізація для пар типів
template<typename T1, typename T2, typename Allocator>
class Buffer<std::pair<T1, T2>, Allocator> {
public:
    void allocate(std::size_t n);
};

// 4. Повна (явна) спеціалізація для конкретного типу void
template<>
class Buffer<void, std::allocator<void>> {
public:
    void allocate_raw(std::size_t bytes);
};
