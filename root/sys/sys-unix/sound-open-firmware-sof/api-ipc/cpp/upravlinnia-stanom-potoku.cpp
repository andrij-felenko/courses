// C++ representation for Stream Trigger control
#include <cstdint>

enum class StreamTriggerOp : std::uint32_t {
    Start   = 0,
    Stop    = 1,
    Pause   = 2,
    Release = 3
};

struct alignas(4) StreamTriggerCmd {
    IpcCmdHeader hdr;
    std::uint32_t compId{0};
    StreamTriggerOp trigger{StreamTriggerOp::Start};
};
