#include <cstdint>
#include <vector>
#include <array>
#include <optional>
#include <span>
#include <memory>
#include <iostream>
#include <string_view>

constexpr size_t BufferCapacity = 1024;
constexpr size_t MaxPayloadSize = 512;
constexpr size_t MaskBits = 64;

/* Збережений пакет у буфері ретрансляції */
struct PacketSlot {
    uint64_t seq_num{0};
    std::vector<uint8_t> payload;
    bool valid{false};
};

/* Кільцевий буфер джерела */
class PbcastBuffer {
public:
    explicit PbcastBuffer(uint64_t sender_id, uint64_t initial_seq = 0)
        : sender_id_(sender_id), low_watermark_(initial_seq), received_mask_(0) {
        slots_.resize(BufferCapacity);
    }

    [[nodiscard]] uint64_t sender_id() const noexcept { return sender_id_; }
    [[nodiscard]] uint64_t low_watermark() const noexcept { return low_watermark_; }
    [[nodiscard]] uint64_t received_mask() const noexcept { return received_mask_; }

private:
    uint64_t sender_id_;
    uint64_t low_watermark_;
    uint64_t received_mask_;
    std::vector<PacketSlot> slots_;
};
