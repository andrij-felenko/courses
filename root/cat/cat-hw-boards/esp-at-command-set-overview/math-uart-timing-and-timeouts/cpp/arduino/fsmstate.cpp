#include <Arduino.h>

constexpr size_t RX_BUF_SIZE = 512;
constexpr uint32_t T_CHAR_TIMEOUT_MS = 10;
constexpr uint32_t T_COMMAND_TIMEOUT_MS = 1000;

enum class FsmState {
    Idle,
    ReceiveStream,
    ParseFrame,
    Ready,
    TimeoutError
};

class AtParser {
private:
    uint8_t m_buffer[RX_BUF_SIZE];
    size_t m_head{0};
    size_t m_tail{0};
    uint32_t m_lastByteTimeMs{0};
    uint32_t m_cmdStartTimeMs{0};
    FsmState m_state{FsmState::Idle};

public:
    void onByteReceived(uint8_t byte, uint32_t currentTimeMs) {
        size_t nextHead = (m_head + 1) % RX_BUF_SIZE;
        if (nextHead != m_tail) {
            m_buffer[m_head] = byte;
            m_head = nextHead;
            m_lastByteTimeMs = currentTimeMs;
            if (m_state == FsmState::Idle) {
                m_state = FsmState::ReceiveStream;
            }
        }
    }

    void updateFsm(uint32_t currentTimeMs) {
        if (m_state == FsmState::ReceiveStream) {
            if ((currentTimeMs - m_lastByteTimeMs) >= T_CHAR_TIMEOUT_MS) {
                m_state = FsmState::ParseFrame;
            } else if ((currentTimeMs - m_cmdStartTimeMs) >= T_COMMAND_TIMEOUT_MS) {
                m_state = FsmState::TimeoutError;
            }
        }
    }
};
