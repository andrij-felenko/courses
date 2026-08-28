#include <cstdint>
#include <array>

struct nvme_tcp_icresp_pdu {
    nvme_tcp_hdr  hdr;          // Заголовок PDU (type = 0x01, hlen = 128)
    std::uint16_t pfv;          // Підтверджена версія протоколу (0x0000)
    std::uint8_t  cpda;         // Controller PDU Data Alignment
    std::uint8_t  digest_flags; // Підтверджені прапорці цілісності digests
    std::uint32_t maxh2cdata;   // Узгоджена межа розміру кадру H2CData
    std::array<std::uint8_t, 112> reserved;
};
