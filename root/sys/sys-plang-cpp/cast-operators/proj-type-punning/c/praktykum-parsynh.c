#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#pragma pack(push, 1)
typedef struct {
    char     riff_id[4];     // "RIFF"
    uint32_t riff_size;
    char     wave_id[4];     // "WAVE"
    char     fmt_id[4];      // "fmt "
    uint32_t fmt_size;       // 16 для PCM
    uint16_t audio_format;   // 1 для PCM
    uint16_t num_channels;   // 1 (моно), 2 (стерео)
    uint32_t sample_rate;    // 44100, 48000 тощо
    uint32_t byte_rate;
    uint16_t block_align;
    uint16_t bits_per_sample;// 16, 24 тощо
    char     data_id[4];     // "data"
    uint32_t data_size;
} WavHeaderC;
#pragma pack(pop)

bool parse_wav_header_c(const uint8_t* buffer, size_t len, WavHeaderC* out) {
    if (len < sizeof(WavHeaderC) || !out) {
        return false;
    }
    memcpy(out, buffer, sizeof(WavHeaderC));
    return memcmp(out->riff_id, "RIFF", 4) == 0 && memcmp(out->wave_id, "WAVE", 4) == 0;
}
