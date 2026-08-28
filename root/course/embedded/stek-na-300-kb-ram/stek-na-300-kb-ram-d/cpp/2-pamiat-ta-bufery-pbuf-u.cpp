#include <span>
#include <cstdint>

namespace embedded::net {

struct PbufView {
    struct pbuf* raw{nullptr};

    [[nodiscard]] std::span<const uint8_t> payload() const noexcept {
        if (raw == nullptr || raw->payload == nullptr) {
            return {};
        }
        return {static_cast<const uint8_t*>(raw->payload), raw->len};
    }

    [[nodiscard]] uint16_t totalLength() const noexcept {
        return raw != nullptr ? raw->tot_len : 0;
    }

    [[nodiscard]] bool isChained() const noexcept {
        return raw != nullptr && raw->next != nullptr;
    }
};

} // namespace embedded::net
