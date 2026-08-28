#define RX_MAX_SENDERS 16

typedef struct {
    uint8_t sysid;
    uint8_t compid;
    uint8_t last_seq;
} sender_t;

typedef struct {
    uint8_t  chan;
    uint32_t verdict[4];        /* індекс = значення mavlink_framing_t */
    uint64_t whole;             /* цілих кадрів                        */
    uint64_t lost;              /* дірок у нумерації                   */
    uint32_t alien;             /* «погана сума», що насправді чужий msgid */
    sender_t sender[RX_MAX_SENDERS];
    unsigned senders;
} rx_t;
