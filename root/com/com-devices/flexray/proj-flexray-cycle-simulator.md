# ⚙️ Симуляція кадрування та тайм-слотів FlexRay циклу

Програмне моделювання комунікаційного циклу FlexRay є необхідним етапом при створенні засобів налагодження бортового програмного забезпечення (наприклад, емуляторів шини, програм обробки логів або симуляторів шинного трафіку в середовищі HIL-тестування — Hardware-in-the-Loop). Реалізація симулятора вимагає точного математичного відтворення двох контрольних сум (Header CRC та Frame CRC), а також моделювання логіки арбітражу у статичному (TDMA) та динамічному (FTDMA) сегментах комунікаційного циклу.

Нижче детально розібрано алгоритмічне підґрунтя кадування FlexRay та наведено повні робочі приклади симулятора на мовах C та C++.

---

## Математичні поліноми та алгоритми CRC FlexRay

Специфікація FlexRay (ISO 17458-2) визначає два незалежні алгоритми циклічного надлишкового коду (CRC), кожен з яких має власні поліноми, розрядність та початкові значення:

### 1. Header CRC (11 бітів)
Використовується для захисту критично важливих полів заголовка: Sync Indicator, Startup Indicator, Frame ID та Payload Length.
- **Поліном:** `G(x) = x¹¹ + x⁹ + x⁸ + x⁷ + x⁵ + x³ + 1` (у шістнадцятковій нотації: `0x385`).
- **Початкове значення (Initial Value):** `0x01A`.
- **Довжина вхідного вектора:** 20 бітів.
- **Порядок бітів:** Біти вводяться у регістр зсуву зліва направо, починаючи з найстаршого біта (MSB).

Вхідне 20-бітне слово для Header CRC конструюється за схемою:
```
[Sync (1b) | Startup (1b) | Frame ID (11b) | Payload Length (7b)]
```

Обчислення Header CRC виконується шляхом послідовного зсуву бітів вхідного слова крізь 11-бітний регістр зворотного зв'язку за методом ділення многочленів у полі Галуа $GF(2)$. Якщо найстарший біт поточного стану регістра дорівнює `1`, поточне значення регістра виконує побітову операцію XOR із кодовим поліномом `0x385`.

### 2. Frame CRC (24 біти)
Використовується для захисту всього кадру (всіх 5 байтів заголовка та всіх байтів корисного навантаження).
- **Поліном:** `G(x) = x²⁴ + x²² + x²⁰ + x¹⁹ + x¹⁸ + x¹⁶ + x¹⁴ + x¹³ + x¹¹ + x¹⁰ + x⁸ + x⁷ + x⁶ + x³ + x + 1` (`0x5B2EC7`).
- **Початкове значення (Initial Value):** `0xFEDCBA`.
- **Розрядність:** 24 біти (3 байти).
- **Здатність виявлення:** Гарантовано виявляє будь-які 5 послідовних або випадкових бітових помилок на довжині кадру до 254 байтів.

Обчислення Frame CRC охоплює повний бітовий потік кадру. Блок-схема упаковки байтів заголовка перед передачею в генератор CRC24 має вигляд:
- Байт 0: `[PayloadPreamble(1b) | NullFrame(1b) | Sync(1b) | Startup(1b) | FrameID[10:8](3b)]`
- Байт 1: `[FrameID[7:0](8b)]`
- Байт 2: `[PayloadLength[11:8](4b) | HeaderCRC[10:7](4b)]`
- Байт 3: `[HeaderCRC[6:0](7b) | 0(1b)]`
- Байт 4: `[CycleCount[5:0](6b) | 0(2b)]`

---

## Повний вихідний код симулятора FlexRay

Приклади нижче демонструють побудову кадрів, розрахунок обох контрольних сум та перевірку цілісності кадру при зчитуванні.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FLEXRAY_HEADER_SIZE       5
#define FLEXRAY_TRAILER_SIZE      3
#define FLEXRAY_MAX_PAYLOAD_WORDS  127
#define FLEXRAY_MAX_PAYLOAD_BYTES  (FLEXRAY_MAX_PAYLOAD_WORDS * 2)

/* Заголовок кадру FlexRay */
typedef struct {
    bool     payload_preamble;
    bool     null_frame;
    bool     sync_frame;
    bool     startup_frame;
    uint16_t frame_id;       /* 1 .. 2047 */
    uint16_t payload_length; /* Довжина у 16-біт словах (0 .. 127) */
    uint16_t header_crc;     /* 11-бітний CRC */
    uint8_t  cycle_count;    /* 0 .. 63 */
} flexray_header_t;

/* Повний кадр FlexRay */
typedef struct {
    flexray_header_t header;
    uint8_t          payload[FLEXRAY_MAX_PAYLOAD_BYTES];
    uint32_t         frame_crc; /* 24-бітний CRC */
} flexray_frame_t;

/* Обчислення 11-бітного Header CRC (Поліном 0x385, init 0x01A) */
uint16_t flexray_compute_header_crc(const flexray_header_t* hdr) {
    uint32_t crc = 0x01A;
    uint32_t poly = 0x385;
    
    /* Формування 20-бітного вектора: [Sync(1) | Startup(1) | FrameID(11) | Length(7)] */
    uint32_t data_word = 0;
    data_word |= ((uint32_t)hdr->sync_frame & 0x01) << 19;
    data_word |= ((uint32_t)hdr->startup_frame & 0x01) << 18;
    data_word |= ((uint32_t)hdr->frame_id & 0x7FF) << 7;
    data_word |= ((uint32_t)hdr->payload_length & 0x7F);

    for (int i = 19; i >= 0; i--) {
        uint32_t bit = (data_word >> i) & 0x01;
        uint32_t crc_msb = (crc >> 10) & 0x01;
        crc = (crc << 1) & 0x7FF;
        if (bit ^ crc_msb) {
            crc ^= poly;
        }
    }
    return (uint16_t)(crc & 0x7FF);
}

/* Обчислення 24-бітного Frame CRC (Поліном 0x5B2EC7, init 0xFEDCBA) */
uint32_t flexray_compute_frame_crc(const flexray_frame_t* frame) {
    uint32_t crc = 0xFEDCBA;
    uint32_t poly = 0x5B2EC7;
    uint32_t payload_bytes = (uint32_t)frame->header.payload_length * 2;

    /* Упаковка байтів заголовка у формат передачі */
    uint8_t header_bytes[FLEXRAY_HEADER_SIZE];
    header_bytes[0] = (frame->header.payload_preamble << 6) |
                      (frame->header.null_frame << 5) |
                      (frame->header.sync_frame << 4) |
                      (frame->header.startup_frame << 3) |
                      ((frame->header.frame_id >> 8) & 0x07);
    header_bytes[1] = frame->header.frame_id & 0xFF;
    header_bytes[2] = ((frame->header.payload_length >> 4) & 0x0F) |
                      ((frame->header.header_crc >> 7) & 0xF0);
    header_bytes[3] = (frame->header.header_crc << 1) & 0xFE;
    header_bytes[4] = frame->header.cycle_count & 0x3F;

    /* Обробка байтів заголовка */
    for (int b = 0; b < FLEXRAY_HEADER_SIZE; b++) {
        for (int i = 7; i >= 0; i--) {
            uint32_t bit = (header_bytes[b] >> i) & 0x01;
            uint32_t crc_msb = (crc >> 23) & 0x01;
            crc = (crc << 1) & 0xFFFFFF;
            if (bit ^ crc_msb) {
                crc ^= poly;
            }
        }
    }

    /* Обробка байтів даних */
    for (uint32_t b = 0; b < payload_bytes; b++) {
        for (int i = 7; i >= 0; i--) {
            uint32_t bit = (frame->payload[b] >> i) & 0x01;
            uint32_t crc_msb = (crc >> 23) & 0x01;
            crc = (crc << 1) & 0xFFFFFF;
            if (bit ^ crc_msb) {
                crc ^= poly;
            }
        }
    }
    return crc & 0xFFFFFF;
}

/* Перевірка цілісності кадру */
bool flexray_verify_frame(const flexray_frame_t* frame) {
    uint16_t expected_header_crc = flexray_compute_header_crc(&frame->header);
    if (expected_header_crc != frame->header.header_crc) {
        printf("[ERROR] Header CRC Mismatch! Calc: 0x%03X, Recv: 0x%03X\n",
               expected_header_crc, frame->header.header_crc);
        return false;
    }

    uint32_t expected_frame_crc = flexray_compute_frame_crc(frame);
    if (expected_frame_crc != frame->frame_crc) {
        printf("[ERROR] Frame CRC Mismatch! Calc: 0x%06X, Recv: 0x%06X\n",
               expected_frame_crc, frame->frame_crc);
        return false;
    }

    return true;
}

int main(void) {
    flexray_frame_t frame;
    memset(&frame, 0, sizeof(frame));

    frame.header.payload_preamble = false;
    frame.header.null_frame = true;
    frame.header.sync_frame = true;
    frame.header.startup_frame = false;
    frame.header.frame_id = 12;      /* Статичний слот №12 */
    frame.header.payload_length = 4; /* 4 слова = 8 байтів */
    frame.header.cycle_count = 1;

    frame.header.header_crc = flexray_compute_header_crc(&frame.header);

    /* Копіювання сигнальних даних у байтовий масив */
    uint16_t test_data[4] = { 0x1234, 0x5678, 0x9ABC, 0xDEF0 };
    memcpy(frame.payload, test_data, sizeof(test_data));

    frame.frame_crc = flexray_compute_frame_crc(&frame);

    printf("FlexRay Frame Simulator (C99 Execution):\n");
    printf("----------------------------------------\n");
    printf("Frame ID:       %u (Static Slot)\n", frame.header.frame_id);
    printf("Payload Length: %u words (%u bytes)\n", frame.header.payload_length, frame.header.payload_length * 2);
    printf("Header CRC:     0x%03X\n", frame.header.header_crc);
    printf("Frame CRC:      0x%06X\n", frame.frame_crc);

    bool is_valid = flexray_verify_frame(&frame);
    printf("Verification:   %s\n", is_valid ? "PASSED (OK)" : "FAILED");

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <cstdint>
#include <span>
#include <expected>
#include <iomanip>

class FlexRayFrame {
public:
    static constexpr uint16_t HEADER_CRC_POLY = 0x385;
    static constexpr uint32_t FRAME_CRC_POLY  = 0x5B2EC7;

    struct Header {
        bool     payload_preamble{false};
        bool     null_frame{true};
        bool     sync_frame{false};
        bool     startup_frame{false};
        uint16_t frame_id{1};       // 1 .. 2047
        uint16_t payload_length{0}; // в 16-бітних словах (0 .. 127)
        uint16_t header_crc{0};     // 11-бітний CRC
        uint8_t  cycle_count{0};    // 0 .. 63
    };

    enum class FrameError {
        InvalidPayloadSize,
        InvalidHeaderCRC,
        InvalidFrameCRC
    };

    explicit FlexRayFrame(Header header, std::span<const uint16_t> data_words)
        : header_(header) {
        payload_.resize(data_words.size() * 2);
        for (size_t i = 0; i < data_words.size(); ++i) {
            payload_[i * 2]     = static_cast<uint8_t>(data_words[i] >> 8);
            payload_[i * 2 + 1] = static_cast<uint8_t>(data_words[i] & 0xFF);
        }
        header_.payload_length = static_cast<uint16_t>(data_words.size());
        header_.header_crc = compute_header_crc();
        frame_crc_ = compute_frame_crc();
    }

    [[nodiscard]] uint16_t compute_header_crc() const noexcept {
        uint32_t crc = 0x01A;
        uint32_t data_word = 0;
        data_word |= (static_cast<uint32_t>(header_.sync_frame) & 0x01) << 19;
        data_word |= (static_cast<uint32_t>(header_.startup_frame) & 0x01) << 18;
        data_word |= (static_cast<uint32_t>(header_.frame_id) & 0x7FF) << 7;
        data_word |= (static_cast<uint32_t>(header_.payload_length) & 0x7F);

        for (int i = 19; i >= 0; --i) {
            uint32_t bit = (data_word >> i) & 0x01;
            uint32_t crc_msb = (crc >> 10) & 0x01;
            crc = (crc << 1) & 0x7FF;
            if (bit ^ crc_msb) {
                crc ^= HEADER_CRC_POLY;
            }
        }
        return static_cast<uint16_t>(crc & 0x7FF);
    }

    [[nodiscard]] uint32_t compute_frame_crc() const noexcept {
        uint32_t crc = 0xFEDCBA;

        std::array<uint8_t, 5> header_bytes{};
        header_bytes[0] = (header_.payload_preamble << 6) |
                          (header_.null_frame << 5) |
                          (header_.sync_frame << 4) |
                          (header_.startup_frame << 3) |
                          ((header_.frame_id >> 8) & 0x07);
        header_bytes[1] = header_.frame_id & 0xFF;
        header_bytes[2] = ((header_.payload_length >> 4) & 0x0F) |
                          ((header_.header_crc >> 7) & 0xF0);
        header_bytes[3] = (header_.header_crc << 1) & 0xFE;
        header_bytes[4] = header_.cycle_count & 0x3F;

        auto process_byte = [&crc](uint8_t byte) {
            for (int i = 7; i >= 0; --i) {
                uint32_t bit = (byte >> i) & 0x01;
                uint32_t crc_msb = (crc >> 23) & 0x01;
                crc = (crc << 1) & 0xFFFFFF;
                if (bit ^ crc_msb) {
                    crc ^= FRAME_CRC_POLY;
                }
            }
        };

        for (uint8_t b : header_bytes) {
            process_byte(b);
        }
        for (uint8_t b : payload_) {
            process_byte(b);
        }
        return crc & 0xFFFFFF;
    }

    [[nodiscard]] std::expected<void, FrameError> verify() const noexcept {
        if (compute_header_crc() != header_.header_crc) {
            return std::unexpected(FrameError::InvalidHeaderCRC);
        }
        if (compute_frame_crc() != frame_crc_) {
            return std::unexpected(FrameError::InvalidFrameCRC);
        }
        return {};
    }

    [[nodiscard]] Header header() const noexcept { return header_; }
    [[nodiscard]] uint32_t frame_crc() const noexcept { return frame_crc_; }
    [[nodiscard]] std::span<const uint8_t> payload() const noexcept { return payload_; }

private:
    Header header_;
    std::vector<uint8_t> payload_;
    uint32_t frame_crc_{0};
};

int main() {
    FlexRayFrame::Header hdr{
        .payload_preamble = false,
        .null_frame       = true,
        .sync_frame       = true,
        .startup_frame    = false,
        .frame_id         = 12,
        .cycle_count      = 1
    };

    const std::array<uint16_t, 4> data{ 0x1234, 0x5678, 0x9ABC, 0xDEF0 };
    FlexRayFrame frame(hdr, data);

    std::cout << "FlexRay Frame Simulator (C++20 Modern Execution):\n";
    std::cout << "-------------------------------------------------\n";
    std::cout << "Frame ID:       " << frame.header().frame_id << " (Static Slot)\n";
    std::cout << "Payload Length: " << static_cast<int>(frame.header().payload_length) << " words\n";
    std::cout << "Header CRC:     0x" << std::hex << std::uppercase << frame.header().header_crc << "\n";
    std::cout << "Frame CRC:      0x" << frame.frame_crc() << std::dec << "\n";

    auto result = frame.verify();
    if (result.has_value()) {
        std::cout << "Verification:   PASSED (OK)\n";
    } else {
        std::cout << "Verification:   FAILED\n";
    }

    return 0;
}
```
:::

---

## Покроковий розбір алгоритмів симулятора

### 1. Упаковка бітових полів (Bit Packing)
Перед обчисленням 24-бітного Frame CRC заголовок кадру перетворюється на 5-байтовий масив `header_bytes`. Оскільки поля FlexRay не вирівняні за межами байтів (наприклад, `Frame ID` займає 11 бітів, а `Header CRC` — 11 бітів), пакування виконується за допомогою бітових зсувів:
- Старші 3 біти `Frame ID` поміщаються в молодші 3 біти `header_bytes[0]`.
- Молодші 8 бітів `Frame ID` записуються в `header_bytes[1]`.
- `Payload Length` (12 бітів) та старші біти `Header CRC` розбиваються між `header_bytes[2]` та `header_bytes[3]`.

Помилка у зсуві бодай на 1 біт призводить до катастрофічного відхилення підсумкового CRC24.

### 2. Ділення многочленів у полі GF(2)
Обчислення обох контрольних сум виконується шляхом побітового ділення вхідного вектора на кодовий поліном за модулем 2 (операція XOR). У програмі це реалізовано у циклі по кожному біту зсуву:
- Змінна `crc` зсувається вліво на 1 біт (`crc << 1`).
- Перевіряється старший біт `crc_msb` до зсуву.
- Якщо `crc_msb ^ bit` дорівнює `1`, виконується `crc ^= poly`.

У реальних мікроконтролерах обчислення CRC виконується апаратним регістром зсуву з лінійним зворотним зв'язком (LFSR, Linear Feedback Shift Register) без участі процесорного ядра. Программная реалізація в симуляторі моделює цей процес біт-за-бітом.

### 3. Перевірка цілісності та емуляція збоїв каналу
Функція `verify()` (у C++20 версії на базі `std::expected`) дозволяє перевірити кадр після проходження крізь симульований канал зв'язку. Якщо під час передачі виникає завада (наприклад, інверсія біта в масиві `payload_`), розрахований контрольний код `compute_frame_crc()` не збігається з збереженим `frame_crc_`. Приймач виявляє цю помилку та повертає статус `FrameError::InvalidFrameCRC`, запобігаючи попаданню некоректних даних у контролер керування двигуном або гальмами.

### 4. Конфігурація пам'яті Message RAM та прив'язка до слотів
У реальному мікроконтролері буфери повідомлень зберігаються в пам'яті Message RAM. Симулятор імплементує спрощене структурування: кожен кадр має унікальний `frame_id`, за яким контролер визначає, в якому саме сегменті циклу передавати дані:
- Якщо `frame_id <= gNumberOfStaticSlots`, кадр призначено для статичного сегмента (TDMA). Усі такі кадри мають суворо однакову довжину `payload_length`.
- Якщо `frame_id > gNumberOfStaticSlots`, кадр передається у динамічному сегменті (FTDMA) з використанням мініслотів.
- Якщо буфер не оновлюється процесором до початку статичного слота, контролер автоматично формує порожній кадр (Null Frame), виставляючи `null_frame = 0` у заголовку.

### 5. Порівняльний аналіз обчислювальної складності CRC
Обчислення CRC біт-за-бітом є наочним, але вимагає 8 ітерацій циклу на кожен байт. У серійних прошивках застосовують таблично-прискорений метод (Table-driven CRC) з 256 елементами в Flash-пам'яті, що дозволяє обробляти по 1 байту за ітерацію. Апаратний модуль FlexRay у контролерах Aurix або SPC5 обробляє бітовий потік паралельно на апаратному зсувному регістрі LFSR прямо під час передачі сигнальних фронтів на шину.

### 6. Інструкція з компіляції та запуску
Програма не має зовнішніх залежностей і збирається будь-яким сучасним компілятором:

```bash
# Компіляція C-версії (C99)
gcc -std=c99 -Wall -Wextra main.c -o flexray_sim_c
./flexray_sim_c

# Компіляція C++ версії (C++20)
g++ -std=c++20 -Wall -Wextra main.cpp -o flexray_sim_cpp
./flexray_sim_cpp
```
