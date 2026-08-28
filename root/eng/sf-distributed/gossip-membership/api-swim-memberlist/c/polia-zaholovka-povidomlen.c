#pragma pack(push, 1)
struct swim_probe_header {
    uint16_t magic;          /* Магічне число протоколу: 0x5357 ("SW") */
    uint8_t  msg_type;       /* Тип повідомлення: PING (0x01), ACK (0x02), PING_REQ (0x03) */
    uint8_t  flags;          /* Бітові прапорці: [0-3] LHM рівень, [4] IPv6, [5-7] резерв */
    uint64_t seq_no;         /* Монотонний номер послідовності зонду для точного матчингу Ack */
    uint32_t target_ip;      /* IPv4-адреса цілі (використовується в PING_REQ, інакше 0) */
    uint16_t target_port;    /* Порт цілі (використовується в PING_REQ, інакше 0) */
};
#pragma pack(pop)
