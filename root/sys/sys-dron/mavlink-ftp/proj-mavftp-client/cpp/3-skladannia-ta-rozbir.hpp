namespace mavftp {

class PacketBuilder {
public:
    static Packet makeOpenRO(uint16_t seq, std::string_view path) noexcept {
        Packet pkt{};
        pkt.seqNumber = seq;
        pkt.opcode = Opcode::OpenFileRO;
        const size_t copyLen = std::min(path.size(), MaxDataLen - 1);
        std::memcpy(pkt.data, path.data(), copyLen);
        pkt.data[copyLen] = '\0';
        pkt.size = static_cast<uint8_t>(copyLen + 1);
        return pkt;
    }

    static Packet makeCreateFile(uint16_t seq, std::string_view path) noexcept {
        Packet pkt{};
        pkt.seqNumber = seq;
        pkt.opcode = Opcode::CreateFile;
        const size_t copyLen = std::min(path.size(), MaxDataLen - 1);
        std::memcpy(pkt.data, path.data(), copyLen);
        pkt.data[copyLen] = '\0';
        pkt.size = static_cast<uint8_t>(copyLen + 1);
        return pkt;
    }

    static Packet makeWriteFile(uint16_t seq, uint8_t session, uint32_t offset, std::span<const uint8_t> chunk) noexcept {
        Packet pkt{};
        pkt.seqNumber = seq;
        pkt.session = session;
        pkt.opcode = Opcode::WriteFile;
        pkt.offset = offset;
        const size_t writeLen = std::min(chunk.size(), MaxDataLen);
        std::memcpy(pkt.data, chunk.data(), writeLen);
        pkt.size = static_cast<uint8_t>(writeLen);
        return pkt;
    }

    static Packet makeBurstRead(uint16_t seq, uint8_t session, uint32_t offset) noexcept {
        Packet pkt{};
        pkt.seqNumber = seq;
        pkt.session = session;
        pkt.opcode = Opcode::BurstReadFile;
        pkt.offset = offset;
        pkt.size = 0;
        return pkt;
    }

    static Packet makeCalcCRC32(uint16_t seq, std::string_view path) noexcept {
        Packet pkt{};
        pkt.seqNumber = seq;
        pkt.opcode = Opcode::CalcFileCRC32;
        const size_t copyLen = std::min(path.size(), MaxDataLen - 1);
        std::memcpy(pkt.data, path.data(), copyLen);
        pkt.data[copyLen] = '\0';
        pkt.size = static_cast<uint8_t>(copyLen + 1);
        return pkt;
    }

    static Packet makeTerminate(uint16_t seq, uint8_t session) noexcept {
        Packet pkt{};
        pkt.seqNumber = seq;
        pkt.session = session;
        pkt.opcode = Opcode::TerminateSession;
        return pkt;
    }

    static Packet makeResetSessions(uint16_t seq) noexcept {
        Packet pkt{};
        pkt.seqNumber = seq;
        pkt.opcode = Opcode::ResetSessions;
        return pkt;
    }
};

} // namespace mavftp
