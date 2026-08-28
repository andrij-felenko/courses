#include <cstdint>
#include <cstddef>

namespace embedded::config {

struct MinimalProfile {
    static constexpr bool kNoSys = true;
    static constexpr size_t kMemAlignment = 4;
    static constexpr size_t kMemSize = 8 * 1024;

    static constexpr size_t kNumPbuf = 8;
    static constexpr size_t kNumTcpPcb = 2;
    static constexpr size_t kNumTcpListen = 1;
    static constexpr size_t kNumTcpSeg = 12;

    static constexpr size_t kPbufPoolSize = 8;
    static constexpr size_t kPbufPoolBufSize = 512;

    static constexpr uint16_t kTcpMss = 536;
    static constexpr uint16_t kTcpWnd = 2 * kTcpMss;
    static constexpr uint16_t kTcpSndBuf = 2 * kTcpMss;
};

} // namespace embedded::config
