#include "cc1101.h"
#include "spi_hal.h"
#include <string.h>

#define WRITE_BURST 0x40
#define READ_SINGLE 0x80
#define READ_BURST  0xC0

#define SRES  0x30
#define SRX   0x34
#define STX   0x35
#define SIDLE 0x36
#define SFRX  0x3A
#define SFTX  0x3B
#define RXBYTES 0x3B

static void write_reg(uint8_t addr, uint8_t value) {
    spi_hal_cs_low();
    spi_hal_transfer(addr);
    spi_hal_transfer(value);
    spi_hal_cs_high();
}

static uint8_t read_reg(uint8_t addr) {
    spi_hal_cs_low();
    spi_hal_transfer(addr | READ_SINGLE);
    uint8_t val = spi_hal_transfer(0x00);
    spi_hal_cs_high();
    return val;
}

static void strobe(uint8_t cmd) {
    spi_hal_cs_low();
    spi_hal_transfer(cmd);
    spi_hal_cs_high();
}

static void write_burst(uint8_t addr, const uint8_t* data, uint8_t len) {
    spi_hal_cs_low();
    spi_hal_transfer(addr | WRITE_BURST);
    for (uint8_t i = 0; i < len; ++i) {
        spi_hal_transfer(data[i]);
    }
    spi_hal_cs_high();
}

static void read_burst(uint8_t addr, uint8_t* data, uint8_t len) {
    spi_hal_cs_low();
    spi_hal_transfer(addr | READ_BURST);
    for (uint8_t i = 0; i < len; ++i) {
        data[i] = spi_hal_transfer(0x00);
    }
    spi_hal_cs_high();
}

static void reset(void) {
    spi_hal_cs_low();
    while (!spi_hal_is_miso_low());
    spi_hal_transfer(SRES);
    while (!spi_hal_is_miso_low());
    spi_hal_cs_high();
}

void cc1101_init(cc1101_t* ctx) {
    spi_hal_init();
    reset();
    
    // Базові налаштування на 433 МГц (спрощено)
    write_reg(0x0B, 0x06); // FSCTRL1
    write_reg(0x0C, 0x00); // FSCTRL0
    write_reg(0x0D, 0x10); // FREQ2
    write_reg(0x0E, 0xA7); // FREQ1
    write_reg(0x0F, 0x62); // FREQ0
    write_reg(0x10, 0xC8); // MDMCFG4
    write_reg(0x11, 0x93); // MDMCFG3
    write_reg(0x12, 0x03); // MDMCFG2
    write_reg(0x18, 0x18); // MCSM0
    
    strobe(SRX);
    
    ctx->state = CC1101_STATE_RX;
    ctx->rx_ready = false;
    ctx->tx_busy = false;
    ctx->rx_len = 0;
}

void cc1101_update(cc1101_t* ctx) {
    if (ctx->state == CC1101_STATE_TX) {
        if (!spi_hal_get_gdo0()) { // Передача завершена
            ctx->tx_busy = false;
            strobe(SRX);
            ctx->state = CC1101_STATE_RX;
        }
    } else if (ctx->state == CC1101_STATE_RX) {
        if (spi_hal_get_gdo0()) { // Прийнято дані
            uint8_t rx_bytes = read_reg(RXBYTES | READ_BURST) & 0x7F;
            if (rx_bytes > 0) {
                uint8_t len;
                read_burst(0x3F, &len, 1);
                if (len > 0 && len <= 64) {
                    read_burst(0x3F, ctx->rx_buffer, len);
                    ctx->rx_len = len;
                    ctx->rx_ready = true;
                }
                strobe(SFRX); // Очищення RX FIFO
                strobe(SRX);
            }
        }
    }
}

bool cc1101_send(cc1101_t* ctx, const uint8_t* data, uint8_t len) {
    if (ctx->state == CC1101_STATE_TX || len == 0 || len > 60) return false;
    
    strobe(SIDLE);
    strobe(SFTX);
    
    write_reg(0x3F, len);
    write_burst(0x3F, data, len);
    
    strobe(STX);
    ctx->state = CC1101_STATE_TX;
    ctx->tx_busy = true;
    return true;
}

bool cc1101_receive(cc1101_t* ctx, uint8_t* data, uint8_t* len) {
    if (ctx->rx_ready) {
        memcpy(data, ctx->rx_buffer, ctx->rx_len);
        *len = ctx->rx_len;
        ctx->rx_ready = false;
        return true;
    }
    return false;
}

cc1101_state_t cc1101_get_state(const cc1101_t* ctx) {
    return ctx->state;
}
