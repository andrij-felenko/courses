#include <gsl/gsl>

// Декларуємо власника ресурсу
template <typename T>
class [[gsl::Owner(T)]] CustomBuffer {
    T* data_;
    size_t size_;
public:
    CustomBuffer(size_t n) : data_(new T[n]), size_(n) {}
    ~CustomBuffer() { delete[] data_; }
};

// Декларуємо невласницький в'ювер
template <typename T>
class [[gsl::Pointer(T)]] CustomBufferView {
    const T* ptr_;
    size_t size_;
public:
    CustomBufferView(const CustomBuffer<T>& buf) 
        : ptr_(buf.data()), size_(buf.size()) {}
};
