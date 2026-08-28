// Розпаковані канали й статистика — назовні, для логіки керування/OSD.
static uint16_t g_channels[16];
static struct {
    uint8_t up_rssi1, up_rssi2, up_lq;
    int8_t  up_snr;
    uint8_t ant, rf_mode, up_power;
    uint8_t dn_rssi, dn_lq;
    int8_t  dn_snr;
} g_link;

static void crsf_unpack_channels(const uint8_t *payload); // нижче
static void crsf_parse_link(const uint8_t *payload);      // нижче

// frame = { тип, дані..., CRC }; len = поле довжини (тип+дані+CRC).
static void crsf_dispatch(const uint8_t *frame, uint8_t len) {
    uint8_t type = frame[0];
    const uint8_t *payload = &frame[1];        // одразу після типу
    uint8_t payload_len = (uint8_t)(len - 2);  // мінус тип, мінус CRC

    switch (type) {
    case CRSF_TYPE_RC_CHANNELS_PACKED:
        // Рівно 16×11 біт = 22 байти. Інша довжина — не наш кадр, ігноруємо.
        if (payload_len == 22)
            crsf_unpack_channels(payload);
        break;

    case CRSF_TYPE_LINK_STATISTICS:
        if (payload_len == 10)
            crsf_parse_link(payload);
        break;

    default:
        // GPS (0x02), батарея (0x08), режим польоту… — тут не розбираємо.
        break;
    }
}
