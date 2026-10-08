#ifndef OSCORE_PACKET_HPP
#define OSCORE_PACKET_HPP

#include <vector>
#include <cstdint>
#include <span>
#include <iostream>

namespace oscore {

class OscorePacket {
public:
    static std::vector<std::uint8_t> build_aad(std::span<const std::uint8_t> header) {
        std::vector<std::uint8_t> aad;
        aad.reserve(2 + header.size());
        aad.push_back(0x84); /* CBOR array header */
        aad.push_back(0x01); /* OSCORE version 1 */
        aad.insert(aad.end(), header.begin(), header.end());
        return aad;
    }

    static std::vector<std::uint8_t> encode_option(std::uint64_t seq, std::span<const std::uint8_t> kid) {
        std::vector<std::uint8_t> option;
        option.push_back(0x09); /* Flag byte: PIV and KID present */
        option.push_back(static_cast<std::uint8_t>((seq >> 8) & 0xFF));
        option.push_back(static_cast<std::uint8_t>(seq & 0xFF));
        option.insert(option.end(), kid.begin(), kid.end());
        return option;
    }
};

} // namespace oscore

#endif // OSCORE_PACKET_HPP
