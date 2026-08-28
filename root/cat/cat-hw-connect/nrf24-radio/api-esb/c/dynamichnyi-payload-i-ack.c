#define FEATURE       0x1D
#define DYNPD         0x1C
#define EN_DPL        2         // біт «динамічний payload» у FEATURE
#define EN_ACK_PAY    1         // біт «ACK з вантажем» у FEATURE
#define W_ACK_PAYLOAD 0xA8      // SPI-команда: покласти вантаж у майбутній ACK

// увімкнути динамічний payload + ACK-payload для труби 1
void nrf_enable_dynamic_ack_payload(void) {
    // FEATURE: підняти EN_DPL і EN_ACK_PAY
    nrf_write_reg(FEATURE, (1 << EN_DPL) | (1 << EN_ACK_PAY));
    // DYNPD: дозволити динамічну довжину саме на трубі 1 (біт 1)
    nrf_write_reg(DYNPD, (1 << 1));
}

// приймач: заздалегідь покласти 3 байти вантажу в ACK для труби 1
void nrf_load_ack_payload(const uint8_t *data, uint8_t len) {
    csn_low();
    spi_xfer(W_ACK_PAYLOAD | 1);            // молодші 3 біти команди — номер труби
    for (uint8_t i = 0; i < len; i++) spi_xfer(data[i]);
    csn_high();
}
