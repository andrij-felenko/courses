#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// Спрощені таблиці переходу станів CABAC H.264 (64 стани)
static const uint8_t rangeTabLPS[64][4] = {
    { 128, 176, 208, 240 }, { 128, 167, 197, 227 }, { 128, 158, 187, 216 }, { 123, 150, 178, 205 },
    { 116, 142, 169, 195 }, { 111, 135, 160, 185 }, { 105, 128, 152, 175 }, { 100, 122, 144, 166 },
    {  95, 116, 137, 158 }, {  90, 110, 130, 150 }, {  85, 104, 123, 142 }, {  81,  99, 117, 135 }
    // Повна таблиця H.264 містить 64 рядки
};

static const uint8_t transIdxMPS[64] = {
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
    17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
    33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
    49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 62, 63
};

static const uint8_t transIdxLPS[64] = {
    0, 0, 1, 2, 2, 4, 4, 5, 6, 7, 8, 9, 9, 11, 11, 12,
    13, 13, 15, 15, 16, 16, 18, 18, 19, 19, 21, 21, 22, 22, 24, 24,
    25, 25, 27, 27, 28, 28, 30, 30, 31, 31, 33, 33, 34, 34, 36, 36,
    37, 37, 39, 39, 40, 40, 42, 42, 43, 43, 45, 45, 46, 46, 48, 48
};

// Контекстне середовище кодера
typedef struct {
    uint8_t pStateIdx; // Індекс стану ймовірності (0..63)
    uint8_t valMPS;    // Найімовірніший символ (0 або 1)
} CabacContext;

typedef struct {
    uint32_t low;       // Регістр нижньої межі (10+ бітів)
    uint32_t range;     // Регістр діапазону (9 бітів, 256..510)
    uint32_t bitsOutstanding; // Кількість підвішених бітів переносу
    uint8_t* buffer;    // Вихідний буфер бітстріму
    size_t   bytePos;   // Поточна позиція в байтовому буфері
    uint8_t  bitBuf;    // Поточний накопичувач бітів (8 біт)
    int      bitLeft;   // Кількість вільних біт у накопичувачі
} CabacEncoder;

void cabac_init(CabacEncoder* enc, uint8_t* out_buf) {
    enc->low = 0;
    enc->range = 510; // Початковий діапазон H.264
    enc->bitsOutstanding = 0;
    enc->buffer = out_buf;
    enc->bytePos = 0;
    enc->bitBuf = 0;
    enc->bitLeft = 8;
}

// Запис одного біта у вихідний байтовий потік
static void put_bit(CabacEncoder* enc, int bit) {
    enc->bitBuf = (enc->bitBuf << 1) | (bit & 1);
    enc->bitLeft--;
    if (enc->bitLeft == 0) {
        enc->buffer[enc->bytePos++] = enc->bitBuf;
        enc->bitBuf = 0;
        enc->bitLeft = 8;
    }
}

// Вивід біта з урахуванням переносу (Carry bit propagation)
static void put_bit_with_outstanding(CabacEncoder* enc, int bit) {
    put_bit(enc, bit);
    while (enc->bitsOutstanding > 0) {
        put_bit(enc, !bit);
        enc->bitsOutstanding--;
    }
}

// Кодування одного двійкового символу (binVal) з оновленням контексту
void cabac_encode_bin(CabacEncoder* enc, CabacContext* ctx, int binVal) {
    // 1. Обчислення діапазону для LPS
    uint32_t rLPS = rangeTabLPS[ctx->pStateIdx][(enc->range >> 6) & 3];
    enc->range -= rLPS;

    if (binVal == ctx->valMPS) {
        // Кодування MPS (найімовірніший символ)
        ctx->pStateIdx = transIdxMPS[ctx->pStateIdx];
    } else {
        // Кодування LPS (малоймовірний символ)
        enc->low += enc->range;
        enc->range = rLPS;
        if (ctx->pStateIdx == 0) {
            ctx->valMPS = 1 - ctx->valMPS; // Інверсія MPS
        }
        ctx->pStateIdx = transIdxLPS[ctx->pStateIdx];
    }

    // 2. Ренормалізація та вивід бітів
    while (enc->range < 256) {
        if (enc->low < 256) {
            put_bit_with_outstanding(enc, 0);
        } else if (enc->low >= 512) {
            put_bit_with_outstanding(enc, 1);
            enc->low -= 512;
        } else {
            enc->bitsOutstanding++;
            enc->low -= 256;
        }
        enc->range <<= 1;
        enc->low <<= 1;
    }
}

int main(void) {
    uint8_t stream[64] = {0};
    CabacEncoder enc;
    CabacContext ctx = { .pStateIdx = 10, .valMPS = 0 }; // Початковий контекст

    cabac_init(&enc, stream);

    // Кодуємо тестову послідовність бінів: 0, 0, 1, 0, 1
    int test_bins[5] = {0, 0, 1, 0, 1};
    for (int i = 0; i < 5; i++) {
        cabac_encode_bin(&enc, &ctx, test_bins[i]);
    }

    printf("Сформовано байтів CABAC: %zu\n", enc.bytePos);
    return 0;
}
