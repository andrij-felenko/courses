struct Ipv4Header {
    uint8_t version : 4;
    uint8_t ihl     : 4;
    uint8_t dscp    : 6;
    uint8_t ecn     : 2;
};

consteval auto verify_bitfield_layout(std::meta::info header_type) -> bool {
    size_t total_bits = 0;
    for (auto member : std::meta::nonstatic_data_members_of(header_type)) {
        if (std::meta::is_bit_field(member)) {
            total_bits += std::meta::bit_size_of(member);
        }
    }
    return total_bits == 16;
}

static_assert(verify_bitfield_layout(^^Ipv4Header));
