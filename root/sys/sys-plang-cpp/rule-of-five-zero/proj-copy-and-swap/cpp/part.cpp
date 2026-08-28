Buffer& operator=(const Buffer& other) {
    char* fresh = new char[other.size];        // ← «як добути блок» — уже було в конструкторі
    std::memcpy(fresh, other.data, other.size); // ← «як копіювати блок» — теж
    delete[] data;                              // ← «як віддати блок» — уже було в деструкторі
    data = fresh;
    size = other.size;
    return *this;
}

Buffer& operator=(Buffer&& other) noexcept {
    if (this != &other) {                       // ← сторожа, яку легко забути
        delete[] data;                          // ← «як віддати блок» — утретє
        data = std::exchange(other.data, nullptr);
        size = std::exchange(other.size, 0);
    }
    return *this;
}
