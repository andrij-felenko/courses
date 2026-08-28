#include <cstdint>
#include <iostream>
#include <optional>

class EventGapTracker {
public:
    static constexpr uint8_t  MaxRetries = 3;
    static constexpr uint32_t TimeoutMs  = 800;

    void onSequenceReceived(uint16_t receivedSeq,
                            uint32_t currentTimeMs,
                            uint8_t sysId,
                            uint8_t compId) {
        if (!m_initialized) {
            m_expectedSequence = static_cast<uint16_t>((receivedSeq + 1) & 0xFFFF);
            m_initialized = true;
            return;
        }

        if (receivedSeq == m_expectedSequence) {
            m_expectedSequence = static_cast<uint16_t>((m_expectedSequence + 1) & 0xFFFF);
            if (m_gapActive && m_expectedSequence > m_gapLastSeq) {
                m_gapActive = false;
                m_retryCount = 0;
            }
        } else {
            const uint16_t diff = static_cast<uint16_t>(receivedSeq - m_expectedSequence);
            if (diff < 32768) {
                m_gapActive = true;
                m_gapFirstSeq = m_expectedSequence;
                m_gapLastSeq = static_cast<uint16_t>((receivedSeq - 1) & 0xFFFF);
                m_lastRequestTimeMs = currentTimeMs;
                m_retryCount = 1;

                sendRequestEvent(sysId, compId, m_gapFirstSeq, m_gapLastSeq);
            }
        }
    }

    void poll(uint32_t currentTimeMs, uint8_t sysId, uint8_t compId) {
        if (!m_gapActive) {
            return;
        }

        if (currentTimeMs - m_lastRequestTimeMs >= TimeoutMs) {
            if (m_retryCount < MaxRetries) {
                ++m_retryCount;
                m_lastRequestTimeMs = currentTimeMs;
                sendRequestEvent(sysId, compId, m_gapFirstSeq, m_gapLastSeq);
            } else {
                std::cerr << "[ARQ] Gap " << m_gapFirstSeq << ".." << m_gapLastSeq
                          << " dropped after max retries!\n";
                m_expectedSequence = static_cast<uint16_t>((m_gapLastSeq + 1) & 0xFFFF);
                m_gapActive = false;
                m_retryCount = 0;
            }
        }
    }

private:
    void sendRequestEvent(uint8_t sys, uint8_t comp, uint16_t firstSeq, uint16_t lastSeq) {
        std::cout << "[ARQ] Requesting events " << firstSeq << ".." << lastSeq
                  << " from sys=" << static_cast<int>(sys)
                  << " comp=" << static_cast<int>(comp) << "\n";
    }

    uint16_t m_expectedSequence{0};
    uint16_t m_gapFirstSeq{0};
    uint16_t m_gapLastSeq{0};
    uint32_t m_lastRequestTimeMs{0};
    uint8_t  m_retryCount{0};
    bool     m_initialized{false};
    bool     m_gapActive{false};
};
