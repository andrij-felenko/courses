#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

// Стан біжучого диспаритету
typedef enum {
    RD_MINUS = -1,
    RD_PLUS  = 1
} running_disparity_t;

// Тип символу: дані (D) або керуючий символ (K)
typedef enum {
    SYMBOL_DATA = 0,
    SYMBOL_K28_5 = 1, // 0xBC: COM (Comma / вирівнювання кадрів)
    SYMBOL_K28_1 = 2, // 0x3C: SKP (Skip / вирівнювання частот)
    SYMBOL_K28_7 = 3  // 0xF7: Спеціальний тренувальний патерн
} symbol_type_t;

// Структура стану кодера
typedef struct {
    running_disparity_t rd;
} enc8b10b_state_t;

// Таблиця 5b/6b для RD = -1 (значення: 6 біт коду)
static const uint8_t LUT_5B6B[32] = {
    0x27, 0x1E, 0x1D, 0x23, 0x1B, 0x25, 0x26, 0x07,
    0x17, 0x29, 0x2A, 0x0B, 0x2C, 0x0D, 0x0E, 0x38,
    0x19, 0x31, 0x32, 0x13, 0x34, 0x15, 0x16, 0x28,
    0x0C, 0x1A, 0x12, 0x39, 0x14, 0x35, 0x36, 0x2B
};

// Таблиця 3b/4b для RD = -1 (значення: 4 біти коду)
static const uint8_t LUT_3B4B[8] = {
    0x0B, 0x09, 0x0A, 0x03, 0x07, 0x05, 0x06, 0x04
};

// Ініціалізація стану кодера (стандарт вимагає починати з RD_MINUS)
void enc8b10b_init(enc8b10b_state_t *enc) {
    if (enc) {
        enc->rd = RD_MINUS;
    }
}

// Підрахунок кількості одиниць у двійковому числі
static inline int count_ones(uint32_t val, int bits) {
    int cnt = 0;
    for (int i = 0; i < bits; i++) {
        if ((val >> i) & 1) cnt++;
    }
    return cnt;
}

// Кодування одного байта або K-символу
uint16_t enc8b10b_encode(enc8b10b_state_t *enc, uint8_t byte, symbol_type_t type) {
    uint8_t code_6b = 0;
    uint8_t code_4b = 0;
    
    if (type == SYMBOL_DATA) {
        uint8_t in_5b = byte & 0x1F;
        uint8_t in_3b = (byte >> 5) & 0x07;
        
        code_6b = LUT_5B6B[in_5b];
        code_4b = LUT_3B4B[in_3b];
        
        // Спеціальні правила балансування за специфікацією IBM
        if (in_5b == 7 && enc->rd == RD_PLUS) code_6b = 0x38;
        if (in_3b == 3 && enc->rd == RD_PLUS) code_4b = 0x0C;
        if (in_3b == 7 && enc->rd == RD_PLUS) code_4b = 0x08;
    } else if (type == SYMBOL_K28_5) { // 0xBC (Кома)
        code_6b = (enc->rd == RD_MINUS) ? 0x2F : 0x10; // 111100 / 000011
        code_4b = (enc->rd == RD_MINUS) ? 0x05 : 0x0A; // 0101 / 1010
    } else if (type == SYMBOL_K28_1) { // 0x3C (SKP)
        code_6b = (enc->rd == RD_MINUS) ? 0x2F : 0x10;
        code_4b = (enc->rd == RD_MINUS) ? 0x09 : 0x06;
    } else if (type == SYMBOL_K28_7) { // 0xF7 (Training)
        code_6b = (enc->rd == RD_MINUS) ? 0x2F : 0x10;
        code_4b = (enc->rd == RD_MINUS) ? 0x07 : 0x08;
    }

    // Інверсія 6b при позитивному біжучому диспаритеті для незбалансованих слів
    int ones_6b = count_ones(code_6b, 6);
    if (enc->rd == RD_PLUS && (ones_6b != 3)) {
        code_6b = (~code_6b) & 0x3F;
    }
    
    // Оновлення RD після 6b підблоку
    int disp_6b = count_ones(code_6b, 6) - (6 - count_ones(code_6b, 6));
    if (disp_6b != 0) {
        enc->rd = (disp_6b > 0) ? RD_PLUS : RD_MINUS;
    }

    // Інверсія 4b при позитивному біжучому диспаритеті
    int ones_4b = count_ones(code_4b, 4);
    if (enc->rd == RD_PLUS && (ones_4b != 2)) {
        code_4b = (~code_4b) & 0x0F;
    }

    // Оновлення RD після 4b підблоку
    int disp_4b = count_ones(code_4b, 4) - (4 - count_ones(code_4b, 4));
    if (disp_4b != 0) {
        enc->rd = (disp_4b > 0) ? RD_PLUS : RD_MINUS;
    }

    // Складання 10-бітного канального символу (6b молодші, 4b старші)
    return ((uint16_t)code_4b << 6) | (code_6b & 0x3F);
}

int main(void) {
    enc8b10b_state_t encoder;
    enc8b10b_init(&encoder);

    printf("8b/10b Encoder Demonstration (SuperSpeed USB 3.0):\n");
    
    // Кодування службового символу K28.5 (COM)
    uint16_t com1 = enc8b10b_encode(&encoder, 0xBC, SYMBOL_K28_5);
    printf("K28.5 (RD-) -> 0x%03X (RD now: %s)\n", com1, encoder.rd > 0 ? "+1" : "-1");
    
    uint16_t com2 = enc8b10b_encode(&encoder, 0xBC, SYMBOL_K28_5);
    printf("K28.5 (RD+) -> 0x%03X (RD now: %s)\n", com2, encoder.rd > 0 ? "+1" : "-1");

    // Кодування потоку даних D0.0, D1.0, D2.0
    uint8_t data_bytes[4] = {0x00, 0x55, 0xAA, 0xFF};
    for (int i = 0; i < 4; i++) {
        uint16_t sym = enc8b10b_encode(&encoder, data_bytes[i], SYMBOL_DATA);
        printf("Data 0x%02X -> 0x%03X (RD: %s)\n", data_bytes[i], sym, encoder.rd > 0 ? "+1" : "-1");
    }

    return 0;
}
