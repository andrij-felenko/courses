#define RX_ADDR_P0    0x0A
#define RX_ADDR_P1    0x0B
#define RX_ADDR_P2    0x0C      // далі P3=0x0D, P4=0x0E, P5=0x0F

// записати БАГАТОБАЙТОВУ адресу (для P0/P1): 5 байтів у регістр
void nrf_write_addr(uint8_t reg, const uint8_t *addr, uint8_t len) {
    csn_low();
    spi_xfer(W_REGISTER | reg);
    for (uint8_t i = 0; i < len; i++) spi_xfer(addr[i]);
    csn_high();
}

void nrf_setup_pipes(void) {
    uint8_t base[5]   = {0xC2, 0xC2, 0xC2, 0xC2, 0xC2};  // адреса P1 (спільний префікс)
    nrf_write_addr(RX_ADDR_P1, base, 5);                  // повна адреса P1

    // P2 і P3 — лише молодший байт; старші 4 позичать у P1
    nrf_write_reg(RX_ADDR_P2, 0xC3);                      // адреса = C2 C2 C2 C2 C3
    nrf_write_reg(RX_ADDR_P3, 0xC4);                      // адреса = C2 C2 C2 C2 C4

    // увімкнути труби P1,P2,P3 (біти 1,2,3) у EN_RXADDR
    nrf_write_reg(EN_RXADDR, (1 << 1) | (1 << 2) | (1 << 3));
}
