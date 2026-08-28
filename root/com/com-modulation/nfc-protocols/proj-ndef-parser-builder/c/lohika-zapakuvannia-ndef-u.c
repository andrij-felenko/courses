size_t ndef_wrap_in_tlv(const uint8_t *ndef_msg, size_t ndef_len, uint8_t *tag_mem, size_t max_tag_mem) {
    size_t tlv_header_len = (ndef_len < 255) ? 2 : 4;
    size_t total_len = tlv_header_len + ndef_len + 1; // +1 для Terminator TLV (0xFE)

    if (total_len > max_tag_mem) return 0;

    size_t offset = 0;
    tag_mem[offset++] = 0x03; // NDEF Message TLV Tag

    if (ndef_len < 255) {
        tag_mem[offset++] = (uint8_t)ndef_len;
    } else {
        tag_mem[offset++] = 0xFF; // Індикатор трибайтового поля довжини
        tag_mem[offset++] = (uint8_t)(ndef_len >> 8);
        tag_mem[offset++] = (uint8_t)(ndef_len & 0xFF);
    }

    memcpy(&tag_mem[offset], ndef_msg, ndef_len);
    offset += ndef_len;

    tag_mem[offset++] = 0xFE; // Terminator TLV Tag

    return offset;
}
