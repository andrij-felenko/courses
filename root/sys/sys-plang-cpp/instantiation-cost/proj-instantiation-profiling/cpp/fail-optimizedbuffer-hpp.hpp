#ifndef OPTIMIZED_BUFFER_HPP
#define OPTIMIZED_BUFFER_HPP

#include <cstddef>
#include <utility>
#include <algorithm>

// 1. Нешаблонний базовий клас (винесений у .cpp)
class BufferBase {
protected:
    void* data_;
    std::size_t capacity_;
    std::size_t size_;

    BufferBase();
    ~BufferBase();

    void raw_reallocate(std::size_t new_cap, std::size_t element_size);
    void raw_push(const void* item_ptr, std::size_t element_size);
    void raw_print_diagnostics(const char* prefix) const;

public:
    std::size_t size() const { return size_; }
    std::size_t capacity() const { return capacity_; }
};

// 2. Шаблонний клас для типів значень (Value Types)
template <typename T>
class OptimizedBuffer : public BufferBase {
public:
    OptimizedBuffer() = default;

    ~OptimizedBuffer() {
        T* items = static_cast<T*>(data_);
        for (std::size_t i = 0; i < size_; ++i) {
            items[i].~T();
        }
    }

    void push(const T& item) {
        if (size_ >= capacity_) {
            std::size_t next_cap = capacity_ == 0 ? 8 : capacity_ * 2;
            raw_reallocate(next_cap, sizeof(T));
        }
        new (static_cast<T*>(data_) + size_) T(item);
        ++size_;
    }

    void sort_elements() {
        if (size_ <= 1) return;
        T* items = static_cast<T*>(data_);
        std::sort(items, items + size_);
    }

    void print_diagnostics(const char* prefix) const {
        raw_print_diagnostics(prefix);
    }
};

// 3. Часткова спеціалізація для згортання всіх типів вказівників (Pointer Folding)
template <typename T>
class OptimizedBuffer<T*> : private BufferBase {
public:
    OptimizedBuffer() = default;

    void push(T* item) {
        raw_push(&item, sizeof(void*));
    }

    void sort_elements() {
        if (size_ <= 1) return;
        void** items = static_cast<void**>(data_);
        std::sort(items, items + size_, [](const void* a, const void* b) {
            return static_cast<const T*>(a) < static_cast<const T*>(b);
        });
    }

    void print_diagnostics(const char* prefix) const {
        raw_print_diagnostics(prefix);
    }

    using BufferBase::size;
    using BufferBase::capacity;
};

// 4. Заборона неявної інстанціації у файлах споживачів (extern template)
extern template class OptimizedBuffer<int>;
extern template class OptimizedBuffer<double>;

#endif // OPTIMIZED_BUFFER_HPP
