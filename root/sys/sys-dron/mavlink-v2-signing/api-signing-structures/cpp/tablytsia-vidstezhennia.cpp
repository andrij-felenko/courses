struct MavlinkSigningStream {
    uint8_t  link_id{0};    // Ідентифікатор лінку відправника (0..255)
    uint8_t  sysid{0};      // Системний ID апарата відправника (1..255)
    uint8_t  compid{0};     // ID компонента відправника (1..255)
    uint64_t timestamp{0};  // Останній прийнятий валідний таймстемп (48 біт)
};

struct MavlinkSigningStreams {
    static constexpr size_t kMaxStreams = 16;
    uint16_t num_signing_streams{0};
    std::array<MavlinkSigningStream, kMaxStreams> stream{};
};
