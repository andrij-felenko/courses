#include <cstdint>
#include <array>

struct nvme_tcp_icreq_pdu {
    nvme_tcp_hdr  hdr;          // Заголовок PDU (type = 0x00, hlen = 128)
    std::uint16_t pfv;          // Protocol Format Version (0x0000)
    std::uint8_t  hpda;         // Host PDU Data Alignment (0 = без вирівнювання)
    std::uint8_t  digest_flags; // Біт 0: Header Digest Enable, Біт 1: Data Digest Enable
    std::uint32_t maxh2cdata;   // Максимальний розмір H2CData PDU від хоста (байтів)
    std::array<std::uint8_t, 112> reserved;
};
