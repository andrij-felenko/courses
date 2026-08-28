// C++ representation for Stream Parameters configuration
#include <cstdint>

struct alignas(4) StreamParamsConfig {
    IpcCmdHeader hdr;
    std::uint32_t compId{0};
    std::uint32_t bufferFmt{0};
    std::uint32_t frameFmt{0};
    std::uint32_t rate{48000};
    std::uint32_t channels{2};
    std::uint32_t bufferSize{16384};
    std::uint32_t periodSize{4096};
    std::uint32_t sampleContainerBytes{4};
    std::uint32_t hostPeriodBytes{4096};
    std::uint16_t reserved[4]{0};
};
