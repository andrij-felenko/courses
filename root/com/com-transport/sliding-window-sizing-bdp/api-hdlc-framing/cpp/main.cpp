#include <cstdint>

namespace hdlc {

enum class FrameCategory : uint8_t {
    Information = 0x00,
    Supervisory = 0x01,
    Unnumbered  = 0x03
};

enum class SupervisoryType : uint8_t {
    ReceiveReady        = 0x00, // RR  (00b << 2)
    ReceiveNotReady     = 0x04, // RNR (01b << 2)
    Reject              = 0x08, // REJ (10b << 2)
    SelectiveReject     = 0x0C  // SREJ(11b << 2)
};

struct ControlByteMod8 {
    uint8_t raw;

    [[nodiscard]] constexpr FrameCategory Category() const noexcept {
        if ((raw & 0x01) == 0x00) return FrameCategory::Information;
        return ((raw & 0x03) == 0x01) ? FrameCategory::Supervisory : FrameCategory::Unnumbered;
    }

    [[nodiscard]] constexpr uint8_t SeqSend() const noexcept {
        return (raw >> 1) & 0x07;
    }

    [[nodiscard]] constexpr uint8_t SeqRecv() const noexcept {
        return (raw >> 5) & 0x07;
    }

    [[nodiscard]] constexpr bool PollFinal() const noexcept {
        return ((raw >> 4) & 0x01) != 0;
    }

    [[nodiscard]] constexpr SupervisoryType SuperType() const noexcept {
        return static_cast<SupervisoryType>(raw & 0x0C);
    }
};

} // namespace hdlc
