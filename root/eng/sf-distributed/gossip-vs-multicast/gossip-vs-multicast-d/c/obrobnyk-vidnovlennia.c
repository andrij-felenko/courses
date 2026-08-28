#include <stdint.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define BWP_MSG_REPAIR_REQ 0x03
#define BWP_MSG_REPAIR_RES 0x04

struct bwp_repair_header {
    uint8_t  type;
    uint8_t  flags;
    uint16_t reserved;
    uint64_t missing_seq;
    uint32_t sender_node_id;
} __attribute__((packed));

int send_gossip_repair_request(int unicast_fd, const struct sockaddr_in *peer_addr,
                               uint64_t seq, uint32_t my_id) {
    struct bwp_repair_header req;
    req.type = BWP_MSG_REPAIR_REQ;
    req.flags = 0;
    req.reserved = 0;
    req.missing_seq = htobe64(seq);
    req.sender_node_id = htonl(my_id);

    ssize_t sent = sendto(unicast_fd, &req, sizeof(req), 0,
                          (const struct sockaddr *)peer_addr, sizeof(*peer_addr));
    return (sent == sizeof(req)) ? 0 : -1;
}
