#ifndef NAIVE_BUFFER_HPP
#define NAIVE_BUFFER_HPP

#include <iostream>
#include <vector>
#include <algorithm>
#include <stdexcept>
#include <string>

template <typename T>
class NaiveBuffer {
private:
    T* data_;
    std::size_t capacity_;
    std::size_t size_;

    void reallocate(std::size_t new_cap) {
        T* new_data = new T[new_cap];
        for (std::size_t i = 0; i < size_; ++i) {
            new_data[i] = std::move(data_[i]);
        }
        delete[] data_;
        data_ = new_data;
        capacity_ = new_cap;
    }

public:
    NaiveBuffer() : data_(nullptr), capacity_(0), size_(0) {}

    ~NaiveBuffer() {
        delete[] data_;
    }

    void push(const T& item) {
        if (size_ >= capacity_) {
            std::size_t next_cap = capacity_ == 0 ? 8 : capacity_ * 2;
            reallocate(next_cap);
        }
        data_[size_++] = item;
    }

    void sort_elements() {
        if (size_ <= 1) return;
        std::sort(data_, data_ + size_);
    }

    void print_diagnostics(const std::string& prefix) const {
        std::cout << "[" << prefix << "] Buffer at " << static_cast<const void*>(data_)
                  << ", Size: " << size_ << ", Capacity: " << capacity_ << "\n";
    }

    std::size_t size() const { return size_; }
    std::size_t capacity() const { return capacity_; }
};

#endif // NAIVE_BUFFER_HPP
