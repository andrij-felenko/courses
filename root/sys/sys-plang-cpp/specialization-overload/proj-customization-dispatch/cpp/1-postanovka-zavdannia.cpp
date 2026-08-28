#include <vector>
#include <cstdint>
#include <cstring>
#include <string>
#include <iostream>
#include <type_traits>
#include <concepts>
#include <span>
#include <bit>

class BinaryBuffer {
public:
    void write_raw(const void* data, std::size_t size) {
        const auto* bytes = static_cast<const uint8_t*>(data);
        storage_.insert(storage_.end(), bytes, bytes + size);
    }

    [[nodiscard]] const std::vector<uint8_t>& data() const noexcept {
        return storage_;
    }

    [[nodiscard]] std::size_t size() const noexcept {
        return storage_.size();
    }

    void clear() noexcept {
        storage_.clear();
    }

private:
    std::vector<uint8_t> storage_;
};
