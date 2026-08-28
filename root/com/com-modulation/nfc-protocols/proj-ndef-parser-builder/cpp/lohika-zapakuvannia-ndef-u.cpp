namespace ndef {

class TlvWrapper {
public:
    static std::vector<uint8_t> wrap_ndef(std::span<const uint8_t> ndef_msg) {
        std::vector<uint8_t> result;
        size_t ndef_len = ndef_msg.size();
        size_t tlv_header_len = (ndef_len < 255) ? 2 : 4;
        result.reserve(tlv_header_len + ndef_len + 1);

        result.push_back(0x03); // NDEF TLV Tag

        if (ndef_len < 255) {
            result.push_back(static_cast<uint8_t>(ndef_len));
        } else {
            result.push_back(0xFF);
            result.push_back(static_cast<uint8_t>(ndef_len >> 8));
            result.push_back(static_cast<uint8_t>(ndef_len & 0xFF));
        }

        result.insert(result.end(), ndef_msg.begin(), ndef_msg.end());
        result.push_back(0xFE); // Terminator TLV

        return result;
    }
};

} // namespace ndef
