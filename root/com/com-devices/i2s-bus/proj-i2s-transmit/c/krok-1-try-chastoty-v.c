#include <stdint.h>

// Опис бажаного потоку — усе, що треба, щоб апаратура вивела три частоти.
typedef struct {
    uint32_t sample_rate;   // fs, Гц (напр. 48000)
    uint8_t  bits;          // біт на канал (16, 24, 32)
    uint8_t  channels;      // 2 для стерео
    uint8_t  need_mclk;     // 1, якщо ЦАП вимагає окремий MCLK
} i2s_format_t;

void i2s_tx_set_clocks(const i2s_format_t *f) {
    // 1) MCLK. Багато чіпів беруть MCLK = 256·fs; периферія дає його на пін.
    //    SCK потім породжується як частка від MCLK.
    uint32_t mclk_hz = f->sample_rate * 256;

    // 2) Дільник MCLK → SCK. Скільки тактів SCK у одному MCLK-циклі кадру:
    //    SCK = fs · bits · channels, тож дільник = MCLK / SCK.
    uint32_t sck_hz  = f->sample_rate * f->bits * f->channels;
    uint32_t bck_div = mclk_hz / sck_hz;         // = 256 / (bits·channels)

    I2S_CLKM_CONF   = clkm_from_hz(mclk_hz);      // тактовий блок → MCLK
    I2S_TX_BCK_DIV  = bck_div;                     // MCLK / bck_div = SCK
    // WS виводиться апаратно як SCK / (bits·channels) — його не задають окремо.
}
