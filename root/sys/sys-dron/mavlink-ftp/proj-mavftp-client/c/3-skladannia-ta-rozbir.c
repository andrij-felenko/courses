/* Допоміжні функції конвертації little-endian */
static inline uint16_t le16(uint16_t v) {
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    return (uint16_t)((v << 8) | (v >> 8));
#else
    return v;
#endif
}

static inline uint32_t le32(uint32_t v) {
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    return ((v >> 24) & 0xff) | ((v << 8) & 0xff0000) |
           ((v >> 8) & 0xff00) | ((v << 24) & 0xff000000);
#else
    return v;
#endif
}

/* Формування запиту OpenFileRO */
void mavftp_build_open_ro(mavftp_pkt_t *pkt, uint16_t seq, const char *path) {
    memset(pkt, 0, sizeof(*pkt));
    pkt->seq_number = le16(seq);
    pkt->opcode = MAVFTP_OP_OPEN_FILE_RO;
    size_t len = strlen(path) + 1;
    if (len > MAVFTP_MAX_DATA_LEN) len = MAVFTP_MAX_DATA_LEN;
    pkt->size = (uint8_t)len;
    memcpy(pkt->data, path, len);
    pkt->data[MAVFTP_MAX_DATA_LEN - 1] = '\0';
}

/* Формування запиту CreateFile */
void mavftp_build_create_file(mavftp_pkt_t *pkt, uint16_t seq, const char *path) {
    memset(pkt, 0, sizeof(*pkt));
    pkt->seq_number = le16(seq);
    pkt->opcode = MAVFTP_OP_CREATE_FILE;
    size_t len = strlen(path) + 1;
    if (len > MAVFTP_MAX_DATA_LEN) len = MAVFTP_MAX_DATA_LEN;
    pkt->size = (uint8_t)len;
    memcpy(pkt->data, path, len);
    pkt->data[MAVFTP_MAX_DATA_LEN - 1] = '\0';
}

/* Формування запиту WriteFile */
void mavftp_build_write_file(mavftp_pkt_t *pkt, uint16_t seq, uint8_t session, uint32_t offset, const uint8_t *src, uint8_t len) {
    memset(pkt, 0, sizeof(*pkt));
    pkt->seq_number = le16(seq);
    pkt->session = session;
    pkt->opcode = MAVFTP_OP_WRITE_FILE;
    pkt->offset = le32(offset);
    if (len > MAVFTP_MAX_DATA_LEN) len = MAVFTP_MAX_DATA_LEN;
    pkt->size = len;
    memcpy(pkt->data, src, len);
}

/* Формування запиту BurstReadFile */
void mavftp_build_burst_read(mavftp_pkt_t *pkt, uint16_t seq, uint8_t session, uint32_t offset) {
    memset(pkt, 0, sizeof(*pkt));
    pkt->seq_number = le16(seq);
    pkt->session = session;
    pkt->opcode = MAVFTP_OP_BURST_READ_FILE;
    pkt->offset = le32(offset);
    pkt->size = 0;
}

/* Формування запиту CalcFileCRC32 */
void mavftp_build_calc_crc32(mavftp_pkt_t *pkt, uint16_t seq, const char *path) {
    memset(pkt, 0, sizeof(*pkt));
    pkt->seq_number = le16(seq);
    pkt->opcode = MAVFTP_OP_CALC_FILE_CRC32;
    size_t len = strlen(path) + 1;
    if (len > MAVFTP_MAX_DATA_LEN) len = MAVFTP_MAX_DATA_LEN;
    pkt->size = (uint8_t)len;
    memcpy(pkt->data, path, len);
    pkt->data[MAVFTP_MAX_DATA_LEN - 1] = '\0';
}

/* Формування запиту TerminateSession */
void mavftp_build_terminate(mavftp_pkt_t *pkt, uint16_t seq, uint8_t session) {
    memset(pkt, 0, sizeof(*pkt));
    pkt->seq_number = le16(seq);
    pkt->session = session;
    pkt->opcode = MAVFTP_OP_TERMINATE_SESSION;
}
