# 📋 API бібліотеки libopus: кодування та декодування у C та C++

Офіційна бібліотека `libopus` надає низькорівневий C API для реалізації аудіозв'язку високої чіткості у реальному часі. У цій довідковій вставці описано контракт публічного API, параметри конфігурації, правила керування пам'яттю, структуру заголовка Opus-пакета та механізми обробки помилок при розробці високонавантажених WebRTC-серверів, VoIP-клієнтів та систем конференц-зв'язку.

## 1. Архітектурний контракт та керування пам'яттю

Бібліотека `libopus` розроблена за принципом відсутності прихованого виділення динамічної пам'яті всередині обчислювальних функцій кодування та декодування. Це гарантує детермінований час виконання без ризику затримок на збирання сміття або блокування системних викликів `malloc`.

Розробник має два способи керування пам'яттю об'єктів кодера (`OpusEncoder`) та декодера (`OpusDecoder`):
1. **Виділення в купі (Heap Allocation)**: за допомогою функцій `opus_encoder_create()` та `opus_decoder_create()`. Бібліотека сама виділяє необхідну пам'ять та повертає вказівник на структуру. Звільнення виконується викликами `opus_encoder_destroy()` та `opus_decoder_destroy()`.
2. **Статичне виділення або виділення на стеку (Static/Stack Allocation)**: розробник дізнається точний розмір структури в байтах через виклики `opus_encoder_get_size(channels)` або `opus_decoder_get_size(channels)`, виділяє буфер необхідного розміру (наприклад, у плоских масивах або пам'яті shared memory), після чого ініціалізує об'єкт викликами `opus_encoder_init()` або `opus_decoder_init()`.

Правила багатопотоковості (Thread Safety): окремий екземпляр `OpusEncoder` або `OpusDecoder` не є потокобезпечним. Заборонено паралельно викликати `opus_encode()` або `opus_decode()` для одного і того ж об'єкта з різних потоків виконання без зовнішнього мутекса. Однак незалежні екземпляри кодерів у різних потоках обробки медиа-сервера працюють повністю паралельно без глобальних блокувань.

## 2. Анатомія заголовка Opus-пакета (TOC Byte)

Кожен вихідний пакет Opus починається з так званого байта змісту (Table of Contents, TOC Byte), який описує режим роботи кодека, частотну смугу, кількість каналів та структуру кадрів у пакеті.

Структура байта TOC:
- **Біти 7–3 (5 біт)**: номер конфігурації `config` (від 0 до 31). Цей номер визначає:
  - Рушій кодування: SILK-only (конфігурації 0–11), Hybrid (конфігурації 12–15), CELT-only (конфігурації 16–31).
  - Смугу аудіочастот: NB (4 кГц), MB (6 кГц), WB (8 кГц), SWB (12 кГц), FB (20 кГц).
  - Тривалість кадру: 2.5 мс, 5 мс, 10 мс, 20 мс, 40 мс, 60 мс.
- **Біт 2 (1 біт)**: прапорець каналів `s` (`0` — моно, `1` — стерео).
- **Біти 1–0 (2 біти)**: код кількості кадрів у пакеті `c`:
  - `00`: 1 кадр у пакеті.
  - `01`: 2 кадри у пакеті з однаковою тривалістю.
  - `10`: 2 кадри у пакеті з різною тривалістю.
  - `11`: довільна кількість кадрів (VBR/CBR пакетний режим).

Завдяки самоописовому байту TOC декодер миттєво визначає структуру пакета без додаткових метаданих у протоколах сигналізації.

## 3. Детальний довідник Control API (opus_encoder_ctl)

Конфігурація кодера здійснюється через варіативний макрос `opus_encoder_ctl(encoder, request, ...)`:

### Режими застосування та бітрейт
- `OPUS_SET_APPLICATION(int application)`: встановлює профіль застосування. Приймає `OPUS_APPLICATION_VOIP` (активує LPC/SILK для мови), `OPUS_APPLICATION_AUDIO` (активує MDCT/CELT для музики) або `OPUS_APPLICATION_RESTRICTED_LOWDELAY` (мінімальна затримка).
- `OPUS_SET_BITRATE(int bitrate)`: встановлює цільовий бітрейт у бітах за секунду (наприклад, `24000` для 24 кбіт/с). Значення `OPUS_AUTO` обирає бітрейт за замовчуванням, `OPUS_BITRATE_MAX` встановлює максимально можливий бітрейт.
- `OPUS_SET_VBR(int vbr)`: вмикає (`1`) або вимикає (`0`) змінний бітрейт (Variable Bitrate). VBR покращує якість на складних ділянках сигналу та заощаджує біти на простих.
- `OPUS_SET_VBR_CONSTRAINT(int constraint)`: вмикає (`1`) обмежений VBR (Constrained VBR), який гарантує, що усереднений бітрейт на короткому проміжку часу не перевищує заданий ліміт, що критично для потоків із фіксованим буфером каналу.

### Профіль складності та адаптація до мережі
- `OPUS_SET_COMPLEXITY(int complexity)`: налаштовує обчислювальну складність алгоритмів пошуку від 0 до 10. Значення `0` забезпечує найшвидше кодування з мінімальним навантаженням на процесор (корисно для слабких мікроконтролерів або сотень паралельних каналів), значення `10` забезпечує максимальну якість за рахунок глибокого алгоритмічного перебору.
- `OPUS_SET_INBAND_FEC(int fec)`: вмикає (`1`) вбудовану компенсацію втрат пакетів (In-band Forward Error Correction). При активованому FEC кодер додає дубльовану низькоякісну інформацію про попередній кадр у поточний пакет, якщо мережа демонструє високі втрати.
- `OPUS_SET_PACKET_LOSS_PERC(int percentage)`: інформує кодер про поточний відсоток втрат пакетів у мережі (від 0 до 100%). На основі цього показника кодер динамічно вирішує, яку частку бітрейту виділити на кодування дублюючих даних FEC.
- `OPUS_SET_DTX(int dtx)`: вмикає (`1`) переривчасте передавання (Discontinuous Transmission). Якщо вхідний сигнал є тишею, кодер випромінює спеціальні пакети комфортного шуму (CNG) розміром всього 2–3 байти раз на кілька сотень мілісекунд.

## 4. Коди помилок та обробка виняткових ситуацій

Усі функції бібліотеки `libopus` повертають від'ємні цілі числа у разі виникнення збою. Для перетворення коду помилки у зрозумілий текстовий рядок використовується функція `opus_strerror(error_code)`.

Класифікація кодів помилок:
- `OPUS_OK` (`0`): операція виконана успішно.
- `OPUS_BAD_ARG` (`-1`): передано невалідний аргумент (наприклад, непідтримувана частота дискретизації, нульовий вказівник або некоректна кількість каналів).
- `OPUS_BUFFER_TOO_SMALL` (`-2`): наданий вихідний буфер занадто малий для розміщення закодованого пакета або декодованого PCM-кадру.
- `OPUS_INTERNAL_ERROR` (`-3`): внутрішній збій алгоритму кодера або декодера.
- `OPUS_INVALID_PACKET` (`-4`): переданий пакет Opus пошкоджений, має неправильну структуру заголовка TOC або порушену довжину.
- `OPUS_UNIMPLEMENTED` (`-5`): запитаний режим або функція не реалізована у даній збірці бібліотеки.
- `OPUS_INVALID_STATE` (`-6`): об'єкт кодера або декодера перебуває у невалідному стані (наприклад, спроба викликати функції після руйнування об'єкта).
- `OPUS_ALLOC_FAIL` (`-7`): не вдалося виділити необхідну пам'ять при створенні об'єкта.

## 5. Робочі приклади реалізації мовами C та C++

:::tabs
```c
/* opus_demo.c - Використання libopus API мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <opus/opus.h>

#define SAMPLE_RATE 48000
#define CHANNELS 1
#define FRAME_SIZE 960 /* 20 мс при 48 кГц */
#define MAX_PACKET_SIZE 1500

int main(void) {
    int error = OPUS_OK;

    /* 1. Створення та ініціалізація кодера */
    OpusEncoder *encoder = opus_encoder_create(SAMPLE_RATE, CHANNELS, OPUS_APPLICATION_VOIP, &error);
    if (error != OPUS_OK) {
        fprintf(stderr, "Помилка створення кодера: %s\n", opus_strerror(error));
        return EXIT_FAILURE;
    }

    /* 2. Налаштування параметрів кодера через control-виклики */
    opus_encoder_ctl(encoder, OPUS_SET_BITRATE(24000));          /* 24 кбіт/с */
    opus_encoder_ctl(encoder, OPUS_SET_VBR(1));                  /* Змінний бітрейт VBR */
    opus_encoder_ctl(encoder, OPUS_SET_COMPLEXITY(8));           /* Обчислювальна складність 0-10 */
    opus_encoder_ctl(encoder, OPUS_SET_INBAND_FEC(1));           /* Ввімкнути In-Band FEC */
    opus_encoder_ctl(encoder, OPUS_SET_PACKET_LOSS_PERC(10));    /* Очікувані втрати 10% */

    /* 3. Створення декодера */
    OpusDecoder *decoder = opus_decoder_create(SAMPLE_RATE, CHANNELS, &error);
    if (error != OPUS_OK) {
        fprintf(stderr, "Помилка створення декодера: %s\n", opus_strerror(error));
        opus_encoder_destroy(encoder);
        return EXIT_FAILURE;
    }

    /* Буфери для PCM та стиснутих даних */
    int16_t pcm_in[FRAME_SIZE] = {0};
    uint8_t opus_packet[MAX_PACKET_SIZE];
    int16_t pcm_out[FRAME_SIZE];

    /* 4. Кодування кадру PCM -> Opus */
    opus_int32 bytes_encoded = opus_encode(encoder, pcm_in, FRAME_SIZE, opus_packet, MAX_PACKET_SIZE);
    if (bytes_encoded < 0) {
        fprintf(stderr, "Помилка кодування: %s\n", opus_strerror(bytes_encoded));
    } else {
        printf("Успішно закодовано %d відліків у пакет розміром %d байт\n", FRAME_SIZE, bytes_encoded);
    }

    /* 5. Декодування кадру Opus -> PCM */
    int samples_decoded = opus_decode(decoder, opus_packet, bytes_encoded, pcm_out, FRAME_SIZE, 0);
    if (samples_decoded < 0) {
        fprintf(stderr, "Помилка декодування: %s\n", opus_strerror(samples_decoded));
    } else {
        printf("Успішно декодовано %d відліків PCM\n", samples_decoded);
    }

    /* 6. Звільнення ресурсів */
    opus_encoder_destroy(encoder);
    opus_decoder_destroy(decoder);

    return EXIT_SUCCESS;
}
```
```cpp
// opus_demo.cpp - RAII обгортка та безпечний C++20 інтерфейс для libopus
#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <stdexcept>
#include <string_view>
#include <opus/opus.h>

namespace opus {

class OpusException : public std::runtime_error {
public:
    explicit OpusException(int error_code)
        : std::runtime_error(opus_strerror(error_code)), code_(error_code) {}

    [[nodiscard]] int code() const noexcept { return code_; }
private:
    int code_;
};

struct EncoderDeleter {
    void operator()(OpusEncoder* enc) const noexcept {
        if (enc) opus_encoder_destroy(enc);
    }
};

struct DecoderDeleter {
    void operator()(OpusDecoder* dec) const noexcept {
        if (dec) opus_decoder_destroy(dec);
    }
};

class Encoder {
public:
    Encoder(int sample_rate, int channels, int application) {
        int err = OPUS_OK;
        encoder_.reset(opus_encoder_create(sample_rate, channels, application, &err));
        if (err != OPUS_OK) {
            throw OpusException(err);
        }
    }

    void set_bitrate(int bitrate_bps) {
        int err = opus_encoder_ctl(encoder_.get(), OPUS_SET_BITRATE(bitrate_bps));
        if (err != OPUS_OK) throw OpusException(err);
    }

    void set_inband_fec(bool enable) {
        int err = opus_encoder_ctl(encoder_.get(), OPUS_SET_INBAND_FEC(enable ? 1 : 0));
        if (err != OPUS_OK) throw OpusException(err);
    }

    [[nodiscard]] size_t encode(std::span<const int16_t> pcm_input, std::span<uint8_t> packet_output) {
        opus_int32 res = opus_encode(
            encoder_.get(),
            pcm_input.data(),
            static_cast<int>(pcm_input.size()),
            packet_output.data(),
            static_cast<opus_int32>(packet_output.size())
        );
        if (res < 0) {
            throw OpusException(res);
        }
        return static_cast<size_t>(res);
    }

private:
    std::unique_ptr<OpusEncoder, EncoderDeleter> encoder_;
};

class Decoder {
public:
    Decoder(int sample_rate, int channels) {
        int err = OPUS_OK;
        decoder_.reset(opus_decoder_create(sample_rate, channels, &err));
        if (err != OPUS_OK) {
            throw OpusException(err);
        }
    }

    [[nodiscard]] size_t decode(std::span<const uint8_t> packet_input, std::span<int16_t> pcm_output, bool decode_fec = false) {
        int res = opus_decode(
            decoder_.get(),
            packet_input.data(),
            static_cast<opus_int32>(packet_input.size()),
            pcm_output.data(),
            static_cast<int>(pcm_output.size()),
            decode_fec ? 1 : 0
        );
        if (res < 0) {
            throw OpusException(res);
        }
        return static_cast<size_t>(res);
    }

private:
    std::unique_ptr<OpusDecoder, DecoderDeleter> decoder_;
};

} // namespace opus

int main() {
    try {
        constexpr int sample_rate = 48000;
        constexpr int channels = 1;
        constexpr size_t frame_size = 960; // 20 ms

        opus::Encoder encoder(sample_rate, channels, OPUS_APPLICATION_VOIP);
        encoder.set_bitrate(32000);
        encoder.set_inband_fec(true);

        opus::Decoder decoder(sample_rate, channels);

        std::vector<int16_t> pcm_in(frame_size, 1000);
        std::vector<uint8_t> opus_packet(1500);
        std::vector<int16_t> pcm_out(frame_size);

        size_t bytes = encoder.encode(pcm_in, opus_packet);
        std::cout << "C++ Opus Wrapper: Encoded " << bytes << " bytes.\n";

        size_t samples = decoder.decode(std::span(opus_packet.data(), bytes), pcm_out);
        std::cout << "C++ Opus Wrapper: Decoded " << samples << " samples.\n";

    } catch (const opus::OpusException& e) {
        std::cerr << "Opus Error: " << e.what() << " (code " << e.code() << ")\n";
        return 1;
    }

    return 0;
}
```
:::
