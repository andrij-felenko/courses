struct __attribute__((packed)) FrameHeader {
    uint8_t  version;
    uint32_t length;   // невирівняне поле (зсув 1)
    uint16_t crc;
};

void handle(const uint8_t *raw) {
    const struct FrameHeader *hdr = (const struct FrameHeader *)raw;

    uint32_t len = hdr->length;   // OK: компілятор читає побайтово, вирівняно
    if (len > MAX_FRAME) reject();
    // ...працюємо з len (це вже звичайне число в регістрі)
}
