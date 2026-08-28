#include <iostream>
#include <memory>
#include <span>
#include <vector>
#include <string>

namespace mavftp {

enum class ClientState {
    Idle,
    Opening,
    BurstStreaming,
    GapRecovery,
    Closing,
    VerifyCRC,
    Success,
    Failed
};

class BurstDownloadClient {
public:
    explicit BurstDownloadClient(size_t maxCapacity)
        : bufferCapacity_(maxCapacity) {
        buffer_.reserve(maxCapacity);
    }

    [[nodiscard]] ClientState state() const noexcept { return state_; }
    [[nodiscard]] uint32_t bytesReceived() const noexcept { return bytesReceived_; }
    [[nodiscard]] uint32_t fileSize() const noexcept { return fileSize_; }
    [[nodiscard]] std::span<const uint8_t> data() const noexcept { return buffer_; }

    [[nodiscard]] Packet startDownload(std::string_view remotePath) {
        state_ = ClientState::Opening;
        remotePath_ = remotePath;
        bytesReceived_ = 0;
        fileSize_ = 0;
        retryCount_ = 0;
        buffer_.clear();
        return PacketBuilder::makeOpenRO(++nextSeq_, remotePath);
    }

    std::expected<std::optional<Packet>, ErrorCode> handlePacket(const Packet& pkt) {
        if (pkt.opcode == Opcode::Nak) {
            const auto err = static_cast<ErrorCode>(pkt.data[0]);
            if (err == ErrorCode::EOF_Reached && state_ == ClientState::BurstStreaming) {
                state_ = ClientState::Closing;
                return PacketBuilder::makeTerminate(++nextSeq_, session_);
            }
            state_ = ClientState::Failed;
            return std::unexpected(err);
        }

        if (pkt.opcode != Opcode::Ack) {
            return std::nullopt;
        }

        switch (state_) {
        case ClientState::Opening:
            if (pkt.reqOpcode == Opcode::OpenFileRO) {
                session_ = pkt.session;
                if (pkt.size >= 4) {
                    std::memcpy(&fileSize_, pkt.data, 4);
                }
                state_ = ClientState::BurstStreaming;
                expectedBurstSeq_ = pkt.seqNumber + 1;
                retryCount_ = 0;
                return PacketBuilder::makeBurstRead(++nextSeq_, session_, 0);
            }
            break;

        case ClientState::BurstStreaming:
        case ClientState::GapRecovery:
            if (pkt.reqOpcode == Opcode::BurstReadFile || pkt.reqOpcode == Opcode::ReadFile) {
                // Виявлення пропуску пакетів
                if (state_ == ClientState::BurstStreaming && pkt.seqNumber != expectedBurstSeq_) {
                    state_ = ClientState::GapRecovery;
                    if (++retryCount_ > maxRetries_) {
                        state_ = ClientState::Failed;
                        return std::unexpected(ErrorCode::Fail);
                    }
                    return PacketBuilder::makeBurstRead(++nextSeq_, session_, bytesReceived_);
                }

                // Збереження отриманого блоку
                if (pkt.offset == bytesReceived_ && (bytesReceived_ + pkt.size) <= bufferCapacity_) {
                    buffer_.insert(buffer_.end(), pkt.data, pkt.data + pkt.size);
                    bytesReceived_ += pkt.size;
                    expectedBurstSeq_ = pkt.seqNumber + 1;
                    state_ = ClientState::BurstStreaming;
                    retryCount_ = 0;
                }

                // Перевірка завершення вичитування
                if (pkt.burstComplete == 1 || (fileSize_ > 0 && bytesReceived_ >= fileSize_)) {
                    state_ = ClientState::Closing;
                    return PacketBuilder::makeTerminate(++nextSeq_, session_);
                }
            }
            break;

        case ClientState::Closing:
            if (pkt.reqOpcode == Opcode::TerminateSession) {
                state_ = ClientState::VerifyCRC;
                return PacketBuilder::makeCalcCRC32(++nextSeq_, remotePath_);
            }
            break;

        case ClientState::VerifyCRC:
            if (pkt.reqOpcode == Opcode::CalcFileCRC32 && pkt.size == 4) {
                uint32_t remoteCRC = 0;
                std::memcpy(&remoteCRC, pkt.data, 4);
                const uint32_t localCRC = crc32(buffer_);
                if (localCRC == remoteCRC) {
                    state_ = ClientState::Success;
                    return std::nullopt;
                } else {
                    state_ = ClientState::Failed;
                    return std::unexpected(ErrorCode::Fail);
                }
            }
            break;

        default:
            break;
        }

        return std::nullopt;
    }

private:
    ClientState state_{ClientState::Idle};
    std::string remotePath_;
    uint8_t session_{0};
    uint16_t nextSeq_{0};
    uint16_t expectedBurstSeq_{0};
    uint32_t fileSize_{0};
    uint32_t bytesReceived_{0};
    size_t bufferCapacity_{0};
    std::vector<uint8_t> buffer_;
    uint32_t retryCount_{0};
    uint32_t maxRetries_{5};
};

} // namespace mavftp
