#include <cstdint>
#include <cstddef>

namespace embedded::config {

struct ZeroCopyHighSpeedProfile {
    static constexpr bool kNoSys = false;
    static constexpr size_t kMemAlignment = 32; /* D-Cache Line Size */
    static constexpr size_t kMemSize = 32 * 1024;

    static constexpr size_t kNumPbuf = 32;
    static constexpr size_t kNumTcpPcb = 16;
    static constexpr size_t kNumTcpListen = 4;
    static constexpr size_t kNumTcpSeg = 64;

    static constexpr size_t kPbufPoolSize = 24;
    static constexpr size_t kPbufPoolBufSize = 1536; /* Single full Ethernet frame */

    static constexpr uint16_t kTcpMss = 1460;
    static constexpr uint16_t kTcpWnd = 6 * kTcpMss;
    static constexpr uint16_t kTcpSndBuf = 6 * kTcpMss;
    static constexpr bool kHardwareChecksumOffload = true;
};

} // namespace embedded::config
