// Конфігурація TPACKET_V3 на мові C++ з використанням типів C++20
#include <linux/if_packet.h>
#include <sys/socket.h>
#include <system_error>
#include <cstdint>

void setup_tpacket_v3_ring(int socket_fd) {
    tpacket_req3 req{};
    req.tp_block_size = 1024 * 1024; // 1 MB
    req.tp_block_nr = 64;            // 64 MB
    req.tp_frame_size = 2048;
    req.tp_frame_nr = (req.tp_block_size * req.tp_block_nr) / req.tp_frame_size;
    req.tp_retire_blk_tov = 10;      // 10 ms timeout
    req.tp_feature_req_word = TP_FT_REQ_FILL_RXHASH;

    if (::setsockopt(socket_fd, SOL_PACKET, PACKET_RX_RING, &req, sizeof(req)) < 0) {
        throw std::system_error(errno, std::generic_category(), "Не вдалося налаштувати PACKET_RX_RING");
    }
}
