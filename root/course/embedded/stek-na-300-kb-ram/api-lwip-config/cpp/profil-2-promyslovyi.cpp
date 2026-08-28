#include <cstdint>
#include <cstddef>

namespace embedded::config {

struct IndustrialRtosProfile {
    static constexpr bool kNoSys = false;
    static constexpr size_t kMemAlignment = 4;
    static constexpr size_t kMemSize = 20 * 1024;

    static constexpr size_t kNumPbuf = 16;
    static constexpr size_t kNumTcpPcb = 8;
    static constexpr size_t kNumTcpListen = 4;
    static constexpr size_t kNumTcpSeg = 32;

    static constexpr size_t kPbufPoolSize = 16;
    static constexpr size_t kPbufPoolBufSize = 512;

    static constexpr uint16_t kTcpMss = 1460;
    static constexpr uint16_t kTcpWnd = 3 * kTcpMss;
    static constexpr uint16_t kTcpSndBuf = 3 * kTcpMss;
    static constexpr bool kEnableSockets = true;
};

} // namespace embedded::config
