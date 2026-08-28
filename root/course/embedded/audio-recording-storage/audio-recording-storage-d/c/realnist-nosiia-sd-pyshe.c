#include <stdint.h>
#include <string.h>

#define CHUNK 4096                 // пишемо на картку кратно сектору (512)
static uint8_t  acc[CHUNK];        // буфер-амортизатор між звуком і карткою
static uint32_t acc_len = 0;       // скільки байт уже накопичено
static uint32_t data_bytes = 0;    // усього звуку записано (для заголовка)

// f_write / f_sync — з файлової системи (напр. FatFs); file — відкритий файл.
// Приймає блок звуку; на картку зливає лише повними шматками CHUNK.
void sd_stream(FIL *file, const int16_t *blk, uint32_t n) {
    const uint8_t *src = (const uint8_t *)blk;
    uint32_t bytes = n * sizeof(int16_t);

    while (bytes) {
        uint32_t room = CHUNK - acc_len;
        uint32_t take = (bytes < room) ? bytes : room;
        memcpy(acc + acc_len, src, take);
        acc_len += take; src += take; bytes -= take;

        if (acc_len == CHUNK) {                  // буфер повний — злив на картку
            UINT wr;
            f_write(file, acc, CHUNK, &wr);      // один великий вирівняний запис
            data_bytes += wr;
            acc_len = 0;
        }
    }
}
