/* g711_codec.c - Високопродуктивна реалізація G.711 мовою C */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define G711_MAX_PCM 32512
#define G711_BIAS 33

/* Таблиця швидкого мапування сегментів для A-law */
static const uint8_t g711_seg_end[8] = {
    0x1F, 0x3F, 0x7F, 0xFF, 0x1FF, 0x3FF, 0x7FF, 0xFFF
};

static inline int search_segment(int val, const uint8_t *table, int size) {
    for (int i = 0; i < size; i++) {
        if (val <= table[i]) {
            return i;
        }
    }
    return size;
}

uint8_t g711_linear_to_alaw(int16_t pcm_val) {
    int mask;
    int seg;
    uint8_t aval;

    if (pcm_val >= 0) {
        mask = 0xD5; /* Додатний знак: MSB = 1 */
    } else {
        mask = 0x55; /* Від'ємний знак: MSB = 0 */
        pcm_val = -pcm_val - 1;
        if (pcm_val < 0) pcm_val = 32767;
    }

    if (pcm_val > G711_MAX_PCM) {
        pcm_val = G711_MAX_PCM;
    }

    seg = search_segment(pcm_val >> 3, g711_seg_end, 8);

    if (seg >= 8) {
        return (uint8_t)(0x7F ^ mask);
    } else {
        aval = (uint8_t)(seg << 4);
        if (seg < 2) {
            aval |= (pcm_val >> 1) & 0x0F;
        } else {
            aval |= (pcm_val >> (seg + 2)) & 0x0F;
        }
        return (aval ^ mask);
    }
}

int16_t g711_alaw_to_linear(uint8_t a_val) {
    int t;
    int seg;

    a_val ^= 0xD5;
    t = (a_val & 0x0F) << 4;
    seg = ((unsigned int)a_val & 0x70) >> 4;

    switch (seg) {
        case 0:
            t += 8;
            break;
        case 1:
            t += 0x108;
            break;
        default:
            t += 0x108;
            t <<= (seg - 1);
            break;
    }
    return (a_val & 0x80) ? (int16_t)t : (int16_t)(-t);
}

uint8_t g711_linear_to_ulaw(int16_t pcm_val) {
    int mask;
    int seg;
    uint8_t uval;

    if (pcm_val < 0) {
        pcm_val = G711_BIAS - pcm_val;
        mask = 0x7F;
    } else {
        pcm_val += G711_BIAS;
        mask = 0xFF;
    }

    if (pcm_val > 0x7FFF) pcm_val = 0x7FFF;

    seg = search_segment(pcm_val, (const uint8_t[]){0x3F,0x7F,0xFF,0x1FF,0x3FF,0x7FF,0xFFF,0x1FFF}, 8);

    if (seg >= 8) {
        return (uint8_t)(0x7F ^ mask);
    } else {
        uval = (uint8_t)((seg << 4) | ((pcm_val >> (seg + 3)) & 0x0F));
        return (uval ^ mask);
    }
}

int16_t g711_ulaw_to_linear(uint8_t u_val) {
    int t;

    u_val = ~u_val;
    t = (((u_val & 0x0F) << 3) + G711_BIAS) << ((unsigned int)(u_val & 0x70) >> 4);
    return (u_val & 0x80) ? (int16_t)(G711_BIAS - t) : (int16_t)(t - G711_BIAS);
}

int main(void) {
    int16_t original_pcm = 12345;
    uint8_t alaw_encoded = g711_linear_to_alaw(original_pcm);
    int16_t decoded_pcm = g711_alaw_to_linear(alaw_encoded);

    printf("G.711 A-law test:\n");
    printf("Original PCM: %d\n", original_pcm);
    printf("Encoded A-law byte: 0x%02X\n", alaw_encoded);
    printf("Decoded PCM:  %d (Error: %d)\n", decoded_pcm, abs(original_pcm - decoded_pcm));

    return 0;
}
