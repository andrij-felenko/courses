#include <iostream>
#include <memory>
#include <stdexcept>
#include <utility>
#include <new>
#include <cstddef>

template <typename T, std::size_t Alignment = 64>
class DynamicArray {
private:
    T* data_{nullptr};
    std::size_t size_{0};
    std::size_t capacity_{0};

    // Оптимізоване виділення вирівняного блоку пам'яті без виклику конструкторів
    static T* allocate_aligned(std::size_t capacity) {
        if (capacity == 0) return nullptr;
        std::size_t bytes = capacity * sizeof(T);
        std::size_t aligned_bytes = (bytes + Alignment - 1) & ~(Alignment - 1);
        
        void* ptr = ::operator new[](aligned_bytes, std::align_val_t{Alignment});
        return static_cast<T*>(ptr);
    }

    static void deallocate_aligned(T* ptr) noexcept {
        if (ptr) {
            ::operator delete[](ptr, std::align_val_t{Alignment});
        }
    }

    void reallocate(std::size_t new_capacity) {
        T* new_data = allocate_aligned(new_capacity);
        std::size_t i = 0;
        try {
            // Переміщення або копіювання елементів у новий буфер
            for (; i < size_; ++i) {
                new (new_data + i) T(std::move_if_noexcept(data_[i]));
            }
        } catch (...) {
            // Знищення вже створених об'єктів у разі винятку
            for (std::size_t j = 0; j < i; ++j) {
                new_data[j].~T();
            }
            deallocate_aligned(new_data);
            throw;
        }

        // Знищення старих елементів і звільнення буфера
        for (std::size_t j = 0; j < size_; ++j) {
            data_[j].~T();
        }
        deallocate_aligned(data_);

        data_ = new_data;
        capacity_ = new_capacity;
    }

public:
    DynamicArray() = default;

    explicit DynamicArray(std::size_t initial_capacity) {
        reserve(initial_capacity);
    }

    ~DynamicArray() noexcept {
        clear();
        deallocate_aligned(data_);
    }

    // Заборона копіювання для простоти (можна реалізувати глибоке копіювання)
    DynamicArray(const DynamicArray&) = delete;
    DynamicArray& operator=(const DynamicArray&) = delete;

    // Підтримка Move-семантики (RAII)
    DynamicArray(DynamicArray&& other) noexcept
        : data_(other.data_), size_(other.size_), capacity_(other.capacity_) {
        other.data_ = nullptr;
        other.size_ = 0;
        other.capacity_ = 0;
    }

    DynamicArray& operator=(DynamicArray&& other) noexcept {
        if (this != &other) {
            clear();
            deallocate_aligned(data_);

            data_ = other.data_;
            size_ = other.size_;
            capacity_ = other.capacity_;

            other.data_ = nullptr;
            other.size_ = 0;
            other.capacity_ = 0;
        }
        return *this;
    }

    void reserve(std::size_t new_capacity) {
        if (new_capacity > capacity_) {
            reallocate(new_capacity);
        }
    }

    template <typename... Args>
    T& emplace_back(Args&&... args) {
        if (size_ >= capacity_) {
            std::size_t next_cap = (capacity_ == 0) ? 4 : capacity_ * 2;
            reserve(next_cap);
        }
        T* slot = data_ + size_;
        new (slot) T(std::forward<Args>(args)...);
        ++size_;
        return *slot;
    }

    void push_back(const T& value) {
        emplace_back(value);
    }

    void push_back(T&& value) {
        emplace_back(std::move(value));
    }

    void clear() noexcept {
        for (std::size_t i = 0; i < size_; ++i) {
            data_[i].~T();
        }
        size_ = 0;
    }

    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] std::size_t capacity() const noexcept { return capacity_; }
    [[nodiscard]] bool empty() const noexcept { return size_ == 0; }

    T& operator[](std::size_t index) noexcept { return data_[index]; }
    const T& operator[](std::size_t index) const noexcept { return data_[index]; }

    T& at(std::size_t index) {
        if (index >= size_) {
            throw std::out_of_range("Індекс вийшов за межі DynamicArray");
        }
        return data_[index];
    }

    // Підтримка ітераторів для range-based for
    T* begin() noexcept { return data_; }
    T* end() noexcept { return data_ + size_; }
    const T* begin() const noexcept { return data_; }
    const T* end() const noexcept { return data_ + size_; }
};

int main() {
    try {
        DynamicArray<int> arr;
        for (int i = 1; i <= 8; ++i) {
            arr.push_back(i * 100);
        }

        std::cout << "C++ DynamicArray (Розмір: " << arr.size() 
                  << ", Місткість: " << arr.capacity() << "):\n";

        for (int val : arr) {
            std::cout << val << " ";
        }
        std::cout << "\nДоступ через at(3): " << arr.at(3) << "\n";

    } catch (const std::exception& ex) {
        std::cerr << "Виняток: " << ex.what() << "\n";
    }
    return 0;
}
