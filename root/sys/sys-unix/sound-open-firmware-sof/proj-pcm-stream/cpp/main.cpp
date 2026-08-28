// C++ implementation of SOF IPC stream emulator using RAII and std::span
#include <iostream>
#include <vector>
#include <memory>
#include <span>
#include <array>
#include <system_error>
#include <algorithm>
#include <cstring>

namespace sof {

enum class IpcCmd : uint32_t {
    StreamParams = 0x0001,
    StreamTriggerStart = 0x0002,
    StreamTriggerStop = 0x0003
};

struct alignas(4) IpcHeader {
    uint32_t size;
    uint32_t cmd;
};

struct alignas(4) StreamParamsMsg {
    IpcHeader hdr;
    uint32_t comp_id;
    uint32_t rate;
    uint32_t channels;
    uint32_t buffer_size;
    uint32_t period_size;
};

class DspMailbox {
public:
    static constexpr size_t SRAM_SIZE = 1024;

    bool sendMessage(std::span<const uint8_t> msg) {
        if (msg.size() > SRAM_SIZE) {
            return false;
        }
        std::copy(msg.begin(), msg.end(), m_sram.begin());
        m_doorbellHostToDsp = true;
        // Mock DSP acknowledgement
        m_doorbellHostToDsp = false;
        m_doorbellDspToHost = true;
        return true;
    }

private:
    std::array<uint8_t, SRAM_SIZE> m_sram{};
    bool m_doorbellHostToDsp{false};
    bool m_doorbellDspToHost{false};
};

class PcmStream {
public:
    PcmStream(std::shared_ptr<DspMailbox> mailbox, uint32_t rate, uint32_t channels)
        : m_mailbox(std::move(mailbox)), m_periodBytes(4096), m_dmaBuffer(m_periodBytes * 4, 0)
    {
        StreamParamsMsg msg{};
        msg.hdr.size = sizeof(StreamParamsMsg);
        msg.hdr.cmd = static_cast<uint32_t>(IpcCmd::StreamParams);
        msg.comp_id = 1;
        msg.rate = rate;
        msg.channels = channels;
        msg.buffer_size = static_cast<uint32_t>(m_dmaBuffer.size());
        msg.period_size = static_cast<uint32_t>(m_periodBytes);

        auto bytesSpan = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&msg), sizeof(msg));

        if (!m_mailbox->sendMessage(bytesSpan)) {
            throw std::runtime_error("Failed to send IPC StreamParams to DSP Mailbox");
        }

        std::cout << "[SOF C++] Stream configured: " << rate << " Hz, "
                  << channels << " ch, buffer " << m_dmaBuffer.size() << " B\n";
    }

    ~PcmStream() {
        std::cout << "[SOF C++] Stream destroyed, resources freed via RAII.\n";
    }

    void writePcmData(std::span<const uint8_t> samples) {
        size_t available = m_dmaBuffer.size() - m_hostPtr;
        size_t toWrite = std::min(samples.size(), available);
        
        std::copy_n(samples.begin(), toWrite, m_dmaBuffer.begin() + m_hostPtr);
        m_hostPtr = (m_hostPtr + toWrite) % m_dmaBuffer.size();

        if (samples.size() > toWrite) {
            size_t remainder = samples.size() - toWrite;
            std::copy_n(samples.begin() + toWrite, remainder, m_dmaBuffer.begin());
            m_hostPtr = remainder;
        }
    }

    [[nodiscard]] size_t getHostPointer() const noexcept {
        return m_hostPtr;
    }

private:
    std::shared_ptr<DspMailbox> m_mailbox;
    size_t m_periodBytes;
    std::vector<uint8_t> m_dmaBuffer;
    size_t m_hostPtr{0};
};

} // namespace sof
