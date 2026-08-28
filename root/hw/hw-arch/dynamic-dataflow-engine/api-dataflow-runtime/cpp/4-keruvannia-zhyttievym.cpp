#include <memory>
#include <expected>

namespace dataflow {

struct EngineConfig {
    uint32_t worker_threads{0};
    size_t   token_queue_capacity{4096};
    uint32_t max_frames{256};
    uint32_t slots_per_frame{16};
};

enum class Status : int32_t {
    Ok                 = 0,
    InvalidArg         = -1,
    QueueFull          = -2,
    FrameExhausted     = -3,
    IStructDuplicate   = -4,
    NodeOutOfBounds    = -5,
    NoMemory           = -6
};

class Engine {
public:
    static std::expected<std::unique_ptr<Engine>, Status> create(const EngineConfig& cfg);
    virtual ~Engine() = default;

    virtual Status shutdown() noexcept = 0;
};

} // namespace dataflow
