namespace mavftp {

enum class UploadState {
    Idle,
    Creating,
    Writing,
    Closing,
    Success,
    Failed
};

class FileUploadClient {
public:
    [[nodiscard]] Packet startUpload(std::string_view remotePath, std::span<const uint8_t> data) {
        state_ = UploadState::Creating;
        data_ = data;
        bytesWritten_ = 0;
        return PacketBuilder::makeCreateFile(++nextSeq_, remotePath);
    }

    [[nodiscard]] UploadState state() const noexcept { return state_; }
    [[nodiscard]] size_t bytesWritten() const noexcept { return bytesWritten_; }

    std::expected<std::optional<Packet>, ErrorCode> handlePacket(const Packet& pkt) {
        if (pkt.opcode == Opcode::Nak) {
            state_ = UploadState::Failed;
            return std::unexpected(static_cast<ErrorCode>(pkt.data[0]));
        }

        if (pkt.opcode != Opcode::Ack) return std::nullopt;

        switch (state_) {
        case UploadState::Creating:
            if (pkt.reqOpcode == Opcode::CreateFile) {
                session_ = pkt.session;
                state_ = UploadState::Writing;
                bytesWritten_ = 0;

                const size_t chunkSize = std::min(data_.size(), MaxDataLen);
                return PacketBuilder::makeWriteFile(++nextSeq_, session_, 0, data_.subspan(0, chunkSize));
            }
            break;

        case UploadState::Writing:
            if (pkt.reqOpcode == Opcode::WriteFile) {
                const size_t lastChunk = std::min(data_.size() - bytesWritten_, MaxDataLen);
                bytesWritten_ += lastChunk;

                if (bytesWritten_ < data_.size()) {
                    const size_t nextChunk = std::min(data_.size() - bytesWritten_, MaxDataLen);
                    return PacketBuilder::makeWriteFile(++nextSeq_, session_, static_cast<uint32_t>(bytesWritten_),
                                                        data_.subspan(bytesWritten_, nextChunk));
                } else {
                    state_ = UploadState::Closing;
                    return PacketBuilder::makeTerminate(++nextSeq_, session_);
                }
            }
            break;

        case UploadState::Closing:
            if (pkt.reqOpcode == Opcode::TerminateSession) {
                state_ = UploadState::Success;
                return std::nullopt;
            }
            break;

        default:
            break;
        }

        return std::nullopt;
    }

private:
    UploadState state_{UploadState::Idle};
    uint8_t session_{0};
    uint16_t nextSeq_{0};
    std::span<const uint8_t> data_;
    size_t bytesWritten_{0};
};

} // namespace mavftp
