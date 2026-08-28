// Widget.cpp
#include "Widget.h"
#include <mutex>
#include <string>

struct Widget::Impl {
    mutable std::mutex mtx_;
    std::string protected_data_;

    void set_data(std::string data) {
        std::lock_guard<std::mutex> lock(mtx_);
        protected_data_ = std::move(data);
    }

    std::string get_data() const {
        std::lock_guard<std::mutex> lock(mtx_);
        return protected_data_;
    }
};
