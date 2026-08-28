#include <cstdint>

class BufferHandle {
public:
    explicit BufferHandle(int32_t id) noexcept : id_(id) {}
    explicit operator bool() const noexcept { return id_ >= 0; }
    [[nodiscard]] int32_t get() const noexcept { return id_; }

private:
    int32_t id_;
};

void process() {
    int32_t raw_fd = 105;
    // Виклик explicit-конструктора
    BufferHandle handle = static_cast<BufferHandle>(raw_fd);

    // Виклик explicit-оператора operator bool()
    bool is_valid = static_cast<bool>(handle);
}
