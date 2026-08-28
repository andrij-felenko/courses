# MCP23017, банк A: P0..P3 — виходи (світлодіоди), P4 — вхід із підтяжкою.
from machine import I2C

MCP_ADDR = 0x20
IODIRA   = 0x00     # 1 = вхід, 0 = вихід
GPPUA    = 0x0C     # 1 = увімкнути внутрішню підтяжку ~100 кОм
GPIOA    = 0x12     # читання/запис ніжок банку A

def mcp_reg(reg, value):
    # адреса регістра + дані в нього однією транзакцією
    i2c.writeto_mem(MCP_ADDR, reg, bytes([value]))

def mcp_setup():
    mcp_reg(IODIRA, 0b00010000)         # P4 — вхід, P0..P3 — виходи
    mcp_reg(GPPUA,  0b00010000)         # підтяжка на P4: кнопка на землю
    mcp_reg(GPIOA,  0b00000000)         # push-pull: 0 і 1 однаково сильні
