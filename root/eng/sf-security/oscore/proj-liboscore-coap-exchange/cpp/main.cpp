#include "oscore_context.hpp"
#include "oscore_packet.hpp"
#include <iostream>
#include <array>

int main() {
    std::cout << "--- C++20 Obgortka nad OSCORE (RFC 8613) ---\n";

    std::array<std::uint8_t, 16> master_secret{0x01, 0x02, 0x03, 0x04};
    std::array<std::uint8_t, 8> master_salt{0x10, 0x20};

    {
        oscore::OscoreContext ctx(master_secret, master_salt);

        std::array<std::uint8_t, 4> coap_header{0x40, 0x01, 0x00, 0x01};
        auto aad = oscore::OscorePacket::build_aad(coap_header);
        std::cout << "[Main] AAD block built, size: " << aad.size() << " bytes.\n";

        std::array<std::uint8_t, 1> kid{0x01};
        auto option = oscore::OscorePacket::encode_option(ctx.next_sequence_number(), kid);
        std::cout << "[Main] OSCORE Option 9 built, size: " << option.size() << " bytes.\n";
    }

    return 0;
}
