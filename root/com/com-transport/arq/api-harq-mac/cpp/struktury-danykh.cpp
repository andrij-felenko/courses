#include <cstdint>
#include <vector>
#include <span>
#include <memory>

enum class HarqRedundancyVersion : uint8_t {
    Rv0 = 0,  // Систематичні біти + базовий паритет
    Rv2 = 2,  // Перша порція додаткового паритету
    Rv3 = 3,  // Друга порція додаткового паритету
    Rv1 = 1   // Залишкова порція паритету
};

enum class HarqProcessState : uint8_t {
    Idle = 0,
    ActiveTx,
    WaitingFeedback,
    MaxRetriesExceeded
};

enum class HarqFeedback : uint8_t {
    Nack = 0,
    Ack = 1,
    Dtx = 2  // Discontinuous Transmission
};

struct HarqTxProcessDescriptor {
    uint8_t process_id = 0;
    HarqProcessState state = HarqProcessState::Idle;
    bool ndi = false;
    HarqRedundancyVersion rv = HarqRedundancyVersion::Rv0;
    uint8_t transmission_count = 0;
    uint8_t mcs_index = 0;
    uint32_t transport_block_size = 0;
    uint32_t code_bits_len = 0;
    std::span<const uint8_t> payload;
};

struct HarqRxBufferDescriptor {
    uint8_t process_id = 0;
    bool last_ndi = false;
    uint8_t combined_transmissions = 0;
    std::vector<int8_t> llr_buffer;  // Квантовані значення LLR (від -127 до +127)
    bool crc_pass = false;
};
