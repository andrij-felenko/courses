namespace user_space {
    class DataPacket {
    private:
        std::string header_;
        std::vector<uint8_t> payload_;

    public:
        DataPacket(std::string h, std::vector<uint8_t> p)
            : header_(std::move(h)), payload_(std::move(p)) {}

        // Дружня точка налаштування, що знаходиться виключно через ADL
        friend void serialize(std::ostream& os, const DataPacket& packet) {
            os << "Packet[" << packet.header_ << "]: " << packet.payload_.size() << " bytes";
        }
    };
}
