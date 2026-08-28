template <typename T, typename Allocator = std::allocator<T>>
class DynamicArray {
public:
    DynamicArray();
    void push_back(const T& item);
    void push_back(T&& item);
    
    // Вкладений шаблон методу (Member Function Template)
    template <typename InputIterator>
    void assign(InputIterator first, InputIterator last);

private:
    T* buffer_{nullptr};
    std::size_t size_{0};
    std::size_t capacity_{0};
};

// Зовнішнє визначення звичайного конструктора:
template <typename T, typename Allocator>
DynamicArray<T, Allocator>::DynamicArray()
    : buffer_(nullptr), size_(0), capacity_(0) {}

// Зовнішнє визначення методу push_back:
template <typename T, typename Allocator>
void DynamicArray<T, Allocator>::push_back(const T& item) {
    // Тіло методу
}

// Зовнішнє визначення вкладеного методу-шаблону:
template <typename T, typename Allocator>
template <typename InputIterator>
void DynamicArray<T, Allocator>::assign(InputIterator first, InputIterator last) {
    // Вкладений метод має два рівні параметризації
}
