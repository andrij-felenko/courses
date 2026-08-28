// Нешаблонний базовий клас (реалізація у .cpp файлі)
class RawVectorBase {
protected:
    void* data_;
    std::size_t capacity_;
    std::size_t size_;

    RawVectorBase();
    ~RawVectorBase();

    void raw_grow(std::size_t element_size);
    void raw_throw_out_of_range() const;
};

// Шаблонна обгортка (тільки тонкі inline-методи контролю типів)
template <typename T>
class Vector : private RawVectorBase {
public:
    void push_back(const T& val) {
        if (size_ >= capacity_) {
            raw_grow(sizeof(T));
        }
        new (static_cast<T*>(data_) + size_) T(val);
        ++size_;
    }

    T& at(std::size_t index) {
        if (index >= size_) raw_throw_out_of_range();
        return static_cast<T*>(data_)[index];
    }
};
