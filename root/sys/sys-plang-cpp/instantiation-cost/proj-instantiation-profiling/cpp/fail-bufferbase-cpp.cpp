#include "OptimizedBuffer.hpp"
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <stdexcept>

BufferBase::BufferBase() : data_(nullptr), capacity_(0), size_(0) {}

BufferBase::~BufferBase() {
    std::free(data_);
}

void BufferBase::raw_reallocate(std::size_t new_cap, std::size_t element_size) {
    void* new_data = std::realloc(data_, new_cap * element_size);
    if (!new_data && new_cap > 0) {
        throw std::bad_alloc();
    }
    data_ = new_data;
    capacity_ = new_cap;
}

void BufferBase::raw_push(const void* item_ptr, std::size_t element_size) {
    if (size_ >= capacity_) {
        std::size_t next_cap = capacity_ == 0 ? 8 : capacity_ * 2;
        raw_reallocate(next_cap, element_size);
    }
    char* target = static_cast<char*>(data_) + (size_ * element_size);
    std::memcpy(target, item_ptr, element_size);
    ++size_;
}

void BufferBase::raw_print_diagnostics(const char* prefix) const {
    std::cout << "[" << prefix << "] Base Buffer at " << data_
              << ", Size: " << size_ << ", Capacity: " << capacity_ << "\n";
}

// Повна явна інстанціація найпопулярніших типів (генерація символів у цьому .o)
template class OptimizedBuffer<int>;
template class OptimizedBuffer<double>;
