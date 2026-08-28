#include <cstddef>
#include <cstring>
#include <utility>

class Buffer {
    char*       data = nullptr;
    std::size_t size = 0;
public:
    Buffer() = default;
    explicit Buffer(std::size_t n) : data(new char[n]), size(n) {}

    // єдине місце, де написано «як добути й скопіювати блок»
    Buffer(const Buffer& other)
        : data(other.size ? new char[other.size] : nullptr), size(other.size) {
        if (size) std::memcpy(data, other.data, size);
    }

    // ОБОВ'ЯЗКОВИЙ — і не заради швидкості, див. пастку нижче
    Buffer(Buffer&& other) noexcept
        : data(std::exchange(other.data, nullptr)),
          size(std::exchange(other.size, 0)) {}

    // єдине місце, де написано «як віддати блок»
    ~Buffer() { delete[] data; }

    // прихований друг: невидимий звичайному пошуку, знаходиться через ADL
    friend void swap(Buffer& a, Buffer& b) noexcept {
        using std::swap;
        swap(a.data, b.data);
        swap(a.size, b.size);
    }

    // один оператор на копіювальне й переміщувальне присвоєння
    Buffer& operator=(Buffer rhs) noexcept {
        swap(*this, rhs);
        return *this;
    }
};
