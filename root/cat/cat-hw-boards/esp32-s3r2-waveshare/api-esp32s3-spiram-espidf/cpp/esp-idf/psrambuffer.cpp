#include <cstddef>
#include <cstdint>
#include <memory>
#include <stdexcept>
#include "esp_heap_caps.h"

template <typename T>
class PsramBuffer {
private:
    T* data_;
    size_t count_;

public:
    explicit PsramBuffer(size_t count) : count_(count), data_(nullptr) {
        size_t bytes = count * sizeof(T);
        data_ = static_cast<T*>(heap_caps_malloc(bytes, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
        
        if (!data_) {
            throw std::bad_alloc();
        }
    }

    ~PsramBuffer() {
        if (data_) {
            heap_caps_free(data_);
        }
    }

    T& operator[](size_t index) { return data_[index]; }
    const T& operator[](size_t index) const { return data_[index]; }
    T* data() { return data_; }
    size_t size() const { return count_; }
};
