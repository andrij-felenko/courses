#include <algorithm>
#include <cstring>
#include <utility>

class Buffer {
    char*  data = nullptr;
    size_t size = 0;
public:
    explicit Buffer(size_t n) : data(new char[n]), size(n) {}

    // 1. деструктор: delete[] на nullptr — законна дія без наслідків
    ~Buffer() { delete[] data; }

    // 2. копіювальний конструктор: власний блок для нового об'єкта
    Buffer(const Buffer& other)
        : data(new char[other.size]), size(other.size) {
        std::memcpy(data, other.data, size);
    }

    // 3. копіювальне присвоєння: спершу здобути, потім віддати старе
    Buffer& operator=(const Buffer& other) {
        char* fresh = new char[other.size];      // якщо кине — стан незмінний
        std::memcpy(fresh, other.data, other.size);
        delete[] data;
        data = fresh;
        size = other.size;
        return *this;
    }

    // 4. переміщувальний конструктор: забрати й знеструмити джерело
    Buffer(Buffer&& other) noexcept
        : data(std::exchange(other.data, nullptr)),
          size(std::exchange(other.size, 0)) {}

    // 5. переміщувальне присвоєння
    Buffer& operator=(Buffer&& other) noexcept {
        if (this != &other) {
            delete[] data;
            data = std::exchange(other.data, nullptr);
            size = std::exchange(other.size, 0);
        }
        return *this;
    }
};
