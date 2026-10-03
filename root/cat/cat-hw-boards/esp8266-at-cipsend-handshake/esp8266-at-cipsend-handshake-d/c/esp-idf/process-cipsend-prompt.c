#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

typedef enum {
    CIPSEND_STATE_IDLE,
    CIPSEND_STATE_WAIT_PROMPT,
    CIPSEND_STATE_SENDING_DATA,
    CIPSEND_STATE_WAIT_RESULT
} CipsendState;

bool process_cipsend_prompt(uint8_t rx_byte, CipsendState* state) {
    static uint8_t prev_byte = 0;
    
    if (*state == CIPSEND_STATE_WAIT_PROMPT) {
        // Пошук послідовності '> ' (0x3E 0x20)
        if (prev_byte == '>' && rx_byte == ' ') {
            *state = CIPSEND_STATE_SENDING_DATA;
            prev_byte = 0;
            return true; // Символ-запрошення успішно розпізнано!
        }
        prev_byte = rx_byte;
    }
    return false;
}
