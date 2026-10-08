#ifndef WAV_HEADER_HPP
#define WAV_HEADER_HPP

#include <cstdint>
#include <cstddef>
#include <cstring>

/**
 * @brief Упакована 44-байтна C++ POD-структура заголовка WAV-файлу (RIFF/WAVE PCM).
 * Призначена для збереження метаданих аудіозапису (частота дискретизації, розрядність,
 * кількість каналів та підсумковий розмір записаного PCM-потоку).
 */
#pragma pack(push, 1)
struct WavHeader {
    char riff_id[4]{'R', 'I', 'F', 'F'};     ///< Сигнатура контейнера "RIFF"
    uint32_t overall_size{36};                 ///< Загальний розмір файлу мінус 8 байтів (36 + data_bytes)
    char wave_id[4]{'W', 'A', 'V', 'E'};     ///< Формат заголовка "WAVE"

    char fmt_id[4]{'f', 'm', 't', ' '};      ///< Маркер підблоку формату "fmt "
    uint32_t fmt_chunk_size{16};             ///< Розмір розшифровки формату (16 байтів для неспрямованого PCM)
    uint16_t format_tag{1};                  ///< Код аудіоформату: 1 = Linear PCM без стиснення
    uint16_t num_channels{1};                ///< Кількість аудіоканалів (1 = моно, 2 = стерео)
    uint32_t sample_rate{16000};             ///< Частота дискретизації у Гц (наприклад, 16000 Гц)
    uint32_t byte_rate{32000};               ///< Пропускна здатність: sample_rate * num_channels * (bits / 8)
    uint16_t block_align{2};                 ///< Розмір одного кадру в байтах: num_channels * (bits / 8)
    uint16_t bits_per_sample{16};            ///< Глибина кодування семплу в бітах (16, 24 або 32)

    char data_id[4]{'d', 'a', 't', 'a'};     ///< Маркер початку аудіоданих "data"
    uint32_t data_bytes{0};                  ///< Підсумковий розмір аудіопотоку в байтах

    /**
     * @brief Автоматично оновлює поля розмірів заголовка на основі обсягу PCM-даних.
     * @param pcm_bytes Фактична кількість записаних байтів аудіо.
     */
    void updateSizes(uint32_t pcm_bytes) noexcept {
        data_bytes = pcm_bytes;
        overall_size = pcm_bytes + 36;
    }

    /**
     * @brief Перевіряє коректність структури WAV-заголовка за стандартними сигнатурами RIFF/WAVE.
     * @return true, якщо всі ідентифікатори та формат відповідають стандарту PCM WAV.
     */
    bool isValid() const noexcept {
        return (std::memcmp(riff_id, "RIFF", 4) == 0) &&
               (std::memcmp(wave_id, "WAVE", 4) == 0) &&
               (std::memcmp(fmt_id, "fmt ", 4) == 0) &&
               (std::memcmp(data_id, "data", 4) == 0) &&
               (format_tag == 1) &&
               (num_channels > 0) &&
               (sample_rate > 0) &&
               (bits_per_sample > 0);
    }

    /**
     * @brief Допоміжна фабрична функція для створення ініціалізованого заголовка WAV.
     * @param rate Частота дискретизації у Гц (за замовчуванням 16000 Гц).
     * @param bits Розрядність семплу в бітах (за замовчуванням 16 біт).
     * @param channels Кількість каналів (1 = моно, 2 = стерео).
     * @param initial_pcm_bytes Початковий обсяг записаних байтів.
     * @return Згенерована структура WavHeader.
     */
    static WavHeader createPcmHeader(uint32_t rate, uint16_t bits, uint16_t channels, uint32_t initial_pcm_bytes = 0) noexcept {
        WavHeader header;
        header.num_channels = channels;
        header.sample_rate = rate;
        header.bits_per_sample = bits;
        header.block_align = static_cast<uint16_t>(channels * (bits / 8));
        header.byte_rate = rate * header.block_align;
        header.updateSizes(initial_pcm_bytes);
        return header;
    }
};
#pragma pack(pop)

// Гарантуємо відсутність компіляторних падінгів у структурі WAV-заголовка
static_assert(sizeof(WavHeader) == 44, "Розмір структури WavHeader повинен становити точно 44 байти!");

#endif // WAV_HEADER_HPP
