struct RRCConnectionRequest_r8 {
    uint8_t mmec;
    uint32_t m_tmsi;
    uint8_t establishment_cause;
    bool spare_bit;
};

[[nodiscard]] std::expected<size_t, BitError> encode_rrc(const RRCConnectionRequest_r8& msg, std::span<uint8_t> out_buf) {
    BitWriter bw(out_buf);

    if (auto r = bw.put_bits(0, 1); !r) return std::unexpected(r.error());
    if (auto r = bw.put_bits(0, 1); !r) return std::unexpected(r.error());
    if (auto r = bw.put_constrained_int(msg.mmec, 0, 255); !r) return std::unexpected(r.error());
    if (auto r = bw.put_constrained_int(msg.m_tmsi, 0, 4294967295LL); !r) return std::unexpected(r.error());
    if (auto r = bw.put_constrained_int(msg.establishment_cause, 0, 7); !r) return std::unexpected(r.error());
    if (auto r = bw.put_bit(msg.spare_bit); !r) return std::unexpected(r.error());

    return bw.byte_length();
}

[[nodiscard]] std::expected<RRCConnectionRequest_r8, BitError> decode_rrc(std::span<const uint8_t> in_buf) {
    BitReader br(in_buf);
    RRCConnectionRequest_r8 msg{};

    auto crit_choice = br.get_bits(1);
    if (!crit_choice || *crit_choice != 0) return std::unexpected(BitError::InvalidRange);

    auto ue_id_choice = br.get_bits(1);
    if (!ue_id_choice || *ue_id_choice != 0) return std::unexpected(BitError::InvalidRange);

    auto mmec = br.get_constrained_int(0, 255);
    if (!mmec) return std::unexpected(mmec.error());
    msg.mmec = static_cast<uint8_t>(*mmec);

    auto m_tmsi = br.get_constrained_int(0, 4294967295LL);
    if (!m_tmsi) return std::unexpected(m_tmsi.error());
    msg.m_tmsi = static_cast<uint32_t>(*m_tmsi);

    auto cause = br.get_constrained_int(0, 7);
    if (!cause) return std::unexpected(cause.error());
    msg.establishment_cause = static_cast<uint8_t>(*cause);

    auto spare = br.get_bit();
    if (!spare) return std::unexpected(spare.error());
    msg.spare_bit = *spare;

    return msg;
}

int main() {
    std::vector<uint8_t> buffer(16, 0);
    RRCConnectionRequest_r8 tx_msg{
        .mmec = 0xE8,
        .m_tmsi = 0x3C4D5E6F,
        .establishment_cause = 4,
        .spare_bit = false
    };

    auto enc_res = encode_rrc(tx_msg, buffer);
    if (enc_res) {
        size_t len = *enc_res;
        std::cout << std::format("Закодовано успішно! Довжина: {} байтів\nHex дамп: ", len);
        for (size_t i = 0; i < len; ++i) {
            std::cout << std::format("{:02X} ", buffer[i]);
        }
        std::cout << "\n";

        auto dec_res = decode_rrc(std::span(buffer.data(), len));
        if (dec_res) {
            const auto& rx = *dec_res;
            std::cout << std::format("Декодовано: MMEC=0x{:02X}, M-TMSI=0x{:08X}, Cause={}, Spare={}\n",
                                     rx.mmec, rx.m_tmsi, rx.establishment_cause, rx.spare_bit);
        }
    }
    return 0;
}
