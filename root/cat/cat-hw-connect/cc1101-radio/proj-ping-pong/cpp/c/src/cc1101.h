#ifndef CC1101_H
#define CC1101_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    CC1101_STATE_IDLE,
    CC1101_STATE_RX,
    CC1101_STATE_TX
} cc1101_state_t;

typedef struct {
    cc1101_state_t state;
    uint8_t rx_buffer[64];
    uint8_t rx_len;
    bool rx_ready;
    bool tx_busy;
} cc1101_t;

void cc1101_init(cc1101_t* ctx);
void cc1101_update(cc1101_t* ctx);
bool cc1101_send(cc1101_t* ctx, const uint8_t* data, uint8_t len);
bool cc1101_receive(cc1101_t* ctx, uint8_t* data, uint8_t* len);
cc1101_state_t cc1101_get_state(const cc1101_t* ctx);

#endif
