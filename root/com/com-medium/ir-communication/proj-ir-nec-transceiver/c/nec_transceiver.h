/* nec_transceiver.h - Драйвер протоколу NEC на мові C */
#ifndef NEC_TRANSCEIVER_H
#define NEC_TRANSCEIVER_H

#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t address;
    uint8_t address_inv;
    uint8_t command;
    uint8_t command_inv;
    bool is_repeat;
} nec_packet_t;

typedef enum {
    NEC_RX_STATE_IDLE,
    NEC_RX_STATE_LEADER_BURST,
    NEC_RX_STATE_LEADER_SPACE,
    NEC_RX_STATE_BIT_PULSE,
    NEC_RX_STATE_BIT_SPACE
} nec_rx_state_t;

typedef struct {
    nec_rx_state_t state;
    uint32_t last_capture_us;
    uint32_t raw_data;
    uint8_t bit_index;
    nec_packet_t packet;
    bool packet_ready;
} nec_receiver_t;

void nec_receiver_init(nec_receiver_t *rx);
void nec_receiver_on_edge(nec_receiver_t *rx, uint32_t timestamp_us, bool pin_state);
bool nec_receiver_get_packet(nec_receiver_t *rx, nec_packet_t *out_packet);

#endif /* NEC_TRANSCEIVER_H */
