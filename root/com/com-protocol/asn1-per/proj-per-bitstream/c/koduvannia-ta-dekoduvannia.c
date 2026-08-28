/* Структура повідомлення */
typedef struct {
    uint8_t mmec;             /* 0..255 */
    uint32_t m_tmsi;          /* 32 біти */
    uint8_t establishment_cause; /* 0..7 */
    bool spare_bit;
} RRCConnectionRequest_r8;

/* Кодування повідомлення у буфер */
bool encode_rrc_connection_request(const RRCConnectionRequest_r8 *msg, uint8_t *out_buf, size_t cap, size_t *out_len) {
    BitWriter bw;
    bit_writer_init(&bw, out_buf, cap);

    /* 1. criticalExtensions: CHOICE index 0 (rrcConnectionRequest-r8 з 2 варіантів) -> 1 біт */
    if (!bit_writer_put_bits(&bw, 0, 1)) return false;

    /* 2. ue-Identity: CHOICE index 0 (s-TMSI з 2 варіантів: s-TMSI=0, randomValue=1) -> 1 біт */
    if (!bit_writer_put_bits(&bw, 0, 1)) return false;

    /* 3. s-TMSI.mmec: INTEGER (0..255) -> 8 бітів */
    if (!bit_writer_put_constrained_int(&bw, msg->mmec, 0, 255)) return false;

    /* 4. s-TMSI.m-TMSI: INTEGER (0..4294967295) -> 32 біти */
    if (!bit_writer_put_constrained_int(&bw, msg->m_tmsi, 0, 4294967295LL)) return false;

    /* 5. establishmentCause: ENUMERATED (8 значень -> 0..7) -> 3 біти */
    if (!bit_writer_put_constrained_int(&bw, msg->establishment_cause, 0, 7)) return false;

    /* 6. spare: BIT STRING SIZE(1) -> 1 біт */
    if (!bit_writer_put_bit(&bw, msg->spare_bit)) return false;

    /* Разом записано: 1 + 1 + 8 + 32 + 3 + 1 = 46 бітів */
    *out_len = bit_writer_get_length_bytes(&bw);
    return true;
}

/* Декодування повідомлення з буфера */
bool decode_rrc_connection_request(const uint8_t *in_buf, size_t len, RRCConnectionRequest_r8 *out_msg) {
    BitReader br;
    bit_reader_init(&br, in_buf, len);

    uint32_t crit_choice = 0;
    if (!bit_reader_get_bits(&br, 1, &crit_choice)) return false;
    if (crit_choice != 0) return false; /* Підтримуємо тільки r8 */

    uint32_t ue_id_choice = 0;
    if (!bit_reader_get_bits(&br, 1, &ue_id_choice)) return false;
    if (ue_id_choice != 0) return false; /* s-TMSI */

    int64_t mmec_val = 0;
    if (!bit_reader_get_constrained_int(&br, 0, 255, &mmec_val)) return false;
    out_msg->mmec = (uint8_t)mmec_val;

    int64_t m_tmsi_val = 0;
    if (!bit_reader_get_constrained_int(&br, 0, 4294967295LL, &m_tmsi_val)) return false;
    out_msg->m_tmsi = (uint32_t)m_tmsi_val;

    int64_t cause_val = 0;
    if (!bit_reader_get_constrained_int(&br, 0, 7, &cause_val)) return false;
    out_msg->establishment_cause = (uint8_t)cause_val;

    if (!bit_reader_get_bit(&br, &out_msg->spare_bit)) return false;

    return true;
}

int main(void) {
    uint8_t packet[16];
    size_t packet_len = 0;

    RRCConnectionRequest_r8 tx_msg = {
        .mmec = 0xE8,               /* Код MME = 232 */
        .m_tmsi = 0x3C4D5E6F,        /* M-TMSI абонента */
        .establishment_cause = 4,    /* mo-Data */
        .spare_bit = false
    };

    if (encode_rrc_connection_request(&tx_msg, packet, sizeof(packet), &packet_len)) {
        printf("Закодовано успішно! Довжина: %zu байтів (46 корисних бітів)\nHex дамп: ", packet_len);
        for (size_t i = 0; i < packet_len; i++) {
            printf("%02X ", packet[i]);
        }
        printf("\n");
    }

    RRCConnectionRequest_r8 rx_msg;
    if (decode_rrc_connection_request(packet, packet_len, &rx_msg)) {
        printf("Декодовано: MMEC=0x%02X, M-TMSI=0x%08X, Cause=%u, Spare=%d\n",
               rx_msg.mmec, rx_msg.m_tmsi, rx_msg.establishment_cause, rx_msg.spare_bit);
    }
    return 0;
}
