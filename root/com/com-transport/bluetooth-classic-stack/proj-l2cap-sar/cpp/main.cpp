#include <cstdint>
#include <vector>
#include <span>
#include <unordered_map>
#include <optional>
#include <functional>

class L2capSarEngine {
public:
    static constexpr uint16_t kMaxMtu = 1024;
    static constexpr uint16_t kCidSdp = 0x0001;
    static constexpr uint16_t kCidSignaling = 0x0002;
    static constexpr uint16_t kCidDynamicStart = 0x0040;

    enum class SarState {
        Idle,
        Accumulating,
        Complete,
        ErrorOverflow,
        ErrorCorrupt
    };

    enum class PacketBoundary : uint8_t {
        StartNonFlushable = 0x00,
        Continuation      = 0x01,
        StartAutoFlushable= 0x02
    };

    struct ChannelContext {
        uint16_t handle{0};
        SarState state{SarState::Idle};
        uint16_t expected_len{0};
        uint16_t cid{0};
        std::vector<uint8_t> buffer{};

        void reset() {
            state = SarState::Idle;
            expected_len = 0;
            cid = 0;
            buffer.clear();
        }
    };

    using PacketHandler = std::function<void(uint16_t handle, uint16_t cid, std::span<const uint8_t> payload)>;

    explicit L2capSarEngine(PacketHandler handler = nullptr)
        : packet_handler_(std::move(handler)) {}

    void set_packet_handler(PacketHandler handler) {
        packet_handler_ = std::move(handler);
    }

    bool process_acl_fragment(uint16_t handle, PacketBoundary pb, std::span<const uint8_t> data) {
        if (data.empty()) {
            return false;
        }

        auto& ctx = channels_[handle];
        ctx.handle = handle;

        if (pb == PacketBoundary::StartAutoFlushable || pb == PacketBoundary::StartNonFlushable) {
            if (data.size() < sizeof(uint16_t) * 2) {
                ctx.state = SarState::ErrorCorrupt;
                return false;
            }

            uint16_t length = static_cast<uint16_t>(data[0]) | (static_cast<uint16_t>(data[1]) << 8);
            uint16_t cid = static_cast<uint16_t>(data[2]) | (static_cast<uint16_t>(data[3]) << 8);

            if (length > kMaxMtu) {
                ctx.state = SarState::ErrorOverflow;
                return false;
            }

            ctx.expected_len = length;
            ctx.cid = cid;
            ctx.buffer.clear();
            ctx.buffer.reserve(length);

            auto payload = data.subspan(4);
            if (payload.size() > ctx.expected_len) {
                ctx.state = SarState::ErrorCorrupt;
                return false;
            }

            ctx.buffer.insert(ctx.buffer.end(), payload.begin(), payload.end());

            if (ctx.buffer.size() == ctx.expected_len) {
                ctx.state = SarState::Complete;
                dispatch(ctx);
                ctx.reset();
                return true;
            }

            ctx.state = SarState::Accumulating;
            return true;

        } else if (pb == PacketBoundary::Continuation) {
            if (ctx.state != SarState::Accumulating) {
                ctx.state = SarState::ErrorCorrupt;
                return false;
            }

            if (ctx.buffer.size() + data.size() > ctx.expected_len) {
                ctx.state = SarState::ErrorOverflow;
                return false;
            }

            ctx.buffer.insert(ctx.buffer.end(), data.begin(), data.end());

            if (ctx.buffer.size() == ctx.expected_len) {
                ctx.state = SarState::Complete;
                dispatch(ctx);
                ctx.reset();
                return true;
            }

            return true;
        }

        return false;
    }

private:
    void dispatch(const ChannelContext& ctx) {
        if (packet_handler_) {
            packet_handler_(ctx.handle, ctx.cid, std::span<const uint8_t>(ctx.buffer));
        }
    }

    std::unordered_map<uint16_t, ChannelContext> channels_{};
    PacketHandler packet_handler_{};
};
