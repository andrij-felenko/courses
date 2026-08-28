// MCP23017, банк A: P0..P3 — виходи (світлодіоди), P4 — вхід із підтяжкою.
#define MCP_ADDR  0x20
#define IODIRA    0x00      // 1 = вхід, 0 = вихід
#define GPPUA     0x0C      // 1 = увімкнути внутрішню підтяжку ~100 кОм
#define GPIOA     0x12      // читання/запис ніжок банку A

static void mcp_reg(uint8_t reg, uint8_t value) {
    Wire.beginTransmission(MCP_ADDR);
    Wire.write(reg);                    // спершу адреса регістра…
    Wire.write(value);                  // …потім дані в нього
    Wire.endTransmission();
}

void mcp_setup() {
    Wire.begin();
    mcp_reg(IODIRA, 0b00010000);        // P4 — вхід, P0..P3 — виходи
    mcp_reg(GPPUA,  0b00010000);        // підтяжка на P4: кнопка на землю
    mcp_reg(GPIOA,  0b00000000);        // push-pull: 0 і 1 однаково сильні
}
