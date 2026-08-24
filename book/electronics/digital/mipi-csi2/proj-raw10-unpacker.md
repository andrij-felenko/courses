# ⚙️ Розпакування RAW10 та перевірка цілісності CSI-2

Розроблення низькорівневих драйверів камер для операційних систем реального часу, створення прошивок мікроконтролерів із вбудованими блоками захоплення відео та налагодження ПЛІС/FPGA-модулів приймання швидкісних потоків вимагають глибокого розуміння побайтового аналізу сирого кадру MIPI CSI-2. Хоча в серійних смартфонах та автомобільних процесорах десеріалізація фізичного рівня D-PHY та первинне розбирання пакетів виконуються спеціалізованими апаратними IP-блоками, під час роботи з налагоджувальними платами, програмованими логічними матрицями без вбудованого апаратного ISP або діагностичними аналізаторами логіки розбір структури пакетів лягає на процесор або тестове програмне забезпечення.

У цій практичній роботі розглянуто завершений модуль низькорівневого аналізу довгого пакета MIPI CSI-2: верифікація та апаратна корекція 24-бітного заголовка Packet Header за допомогою синдромного декодера Хеммінга, розрахунок контрольної суми CRC-16-CCITT над масивом байтів корисного навантаження (Payload) та попіксельне розгортання щільно упакованого масиву RAW10 у лінійний буфер 16-бітних цілих чисел.

---

### Архітектура та математика розбору пакета

Вхідний бінарний буфер містить суцільний зріз байтів, захоплених апаратним блоком прийому після виявлення маркера початку передавання SoT (Start of Transmission):

```
СТРУКТУРА ВХІДНОГО БУФЕРА ДОВГОГО ПАКЕТА CSI-2:
┌───────────────────┬───────────────────────────────────┬───────────────────┐
│ Заголовок (4 B)   │  Корисне навантаження (WC байтів) │ Кінцевик (2 B)    │
│ DI + WC_L + WC_H  │  Упаковані байти пікселів RAW10   │ Контрольна сума   │
│ + Байт ECC        │  (кожні 5 байтів = 4 пікселі)     │ CRC-16-CCITT      │
└───────────────────┴───────────────────────────────────┴───────────────────┘
```

#### 1. Декодування та корекція заголовка (Header ECC)
Перші 3 байти заголовка містять 24 біти інформації: ідентифікатор даних `DI` (віртуальний канал `VC` та тип даних `DT`) і 16-бітний лічильник байтів корисного навантаження `Word Count` (`WC`). Четвертий байт несе 6 бітів паритету `P[5:0]`, обчислених передавачем на основі перевірної матриці Хеммінга.

Приймач заново розраховує біти парності `P_calc[5:0]` від прийнятих 24 бітів і знаходить вектор синдрому:
```
Syndrome[5:0] = P_received[5:0] ⊕ P_calc[5:0]
```
Якщо синдром дорівнює нулю, заголовок цілісний. Якщо синдром ненульовий, він однозначно вказує на позицію ушкодженого біта (0..23) у полі даних. Інвертуючи відповідний біт за допомогою операції XOR, алгоритм миттєво відновлює істинні значення `DI` та `WC` без переривання оброблення кадру. Якщо ж синдром свідчить про подвійну помилку, пакет визнається фатально пошкодженим.

#### 2. Верифікація масиву пікселів за CRC-16
Корисне навантаження довжиною `WC` байтів захищене 16-бітною контрольною сумою `CRC-16-CCITT` з поліномом `0x1021` та початковим заповненням `0xFFFF`. Алгоритм послідовно пропускає всі байти рядка через бітовий зсувний регістр зі зворотним зв'язком і порівнює результат із двома контрольними байтами кінцевика `PF`.

#### 3. Геометрія розпакування RAW10
Формат RAW10 упаковує 4 пікселі 10-бітної розрядності (значення від 0 до 1023) у 5 послідовних байтів:
- Байти `0..3` містять старші 8 бітів `[9:2]` для кожного з чотирьох пікселів `P0, P1, P2, P3`.
- Байт `4` ділиться на чотири 2-бітні поля, що несуть молодші біти `[1:0]` відповідних пікселів.

Програмний розпакувальник витягує старші байти, зсуває їх уліво на 2 розряди і накладає молодші біти за допомогою побітового «АБО» (`|`).

---

### Реалізація розпакувальника на C та C++

Нижче наведено повноцінний вихідний код модуля розбору пакета. Версія для C++ використовує сучасні ідіоми: безпечні перегляди пам'яті `std::span`, повернення помилок через `std::expected`, автоматичне керування ресурсами та `constexpr`-таблиці синдромів.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define CSI2_DT_RAW10 0x2B
#define CRC16_CCITT_POLY 0x1021

typedef enum {
    CSI2_OK = 0,
    CSI2_ERR_NULL_PTR = -1,
    CSI2_ERR_BUFFER_TOO_SMALL = -2,
    CSI2_ERR_INVALID_DATA_TYPE = -3,
    CSI2_ERR_ECC_UNCORRECTABLE = -4,
    CSI2_ERR_CRC_MISMATCH = -5
} csi2_status_t;

typedef struct {
    uint8_t virtual_channel;
    uint8_t data_type;
    uint16_t word_count;
    bool ecc_corrected;
} csi2_header_t;

// Розрахунок 6 бітів паритету Хеммінга для 24-бітного заголовка
static uint8_t csi2_calc_ecc(uint32_t data24) {
    uint8_t p0 = 0, p1 = 0, p2 = 0, p3 = 0, p4 = 0, p5 = 0;
    
    #define BIT(n) ((data24 >> (n)) & 1U)
    p0 = BIT(0)^BIT(1)^BIT(2)^BIT(4)^BIT(5)^BIT(7)^BIT(8)^BIT(10)^BIT(11)^BIT(13)^BIT(14)^BIT(16)^BIT(20)^BIT(21)^BIT(23);
    p1 = BIT(0)^BIT(1)^BIT(3)^BIT(4)^BIT(6)^BIT(7)^BIT(9)^BIT(10)^BIT(12)^BIT(13)^BIT(15)^BIT(17)^BIT(20)^BIT(22)^BIT(23);
    p2 = BIT(0)^BIT(2)^BIT(3)^BIT(5)^BIT(6)^BIT(7)^BIT(11)^BIT(12)^BIT(13)^BIT(18)^BIT(19)^BIT(20)^BIT(22)^BIT(23);
    p3 = BIT(1)^BIT(2)^BIT(3)^BIT(8)^BIT(9)^BIT(10)^BIT(11)^BIT(12)^BIT(13)^BIT(14)^BIT(15)^BIT(18)^BIT(19)^BIT(21)^BIT(22)^BIT(23);
    p4 = BIT(4)^BIT(5)^BIT(6)^BIT(7)^BIT(8)^BIT(9)^BIT(10)^BIT(11)^BIT(12)^BIT(13)^BIT(14)^BIT(15)^BIT(16)^BIT(17)^BIT(21)^BIT(22)^BIT(23);
    p5 = BIT(16)^BIT(17)^BIT(18)^BIT(19)^BIT(20)^BIT(21)^BIT(22)^BIT(23);
    #undef BIT

    return (uint8_t)(p0 | (p1 << 1) | (p2 << 2) | (p3 << 3) | (p4 << 4) | (p5 << 5));
}

// Перевірка та відновлення заголовка пакета
static csi2_status_t csi2_parse_header(const uint8_t *raw_header, csi2_header_t *out_hdr) {
    uint32_t data24 = (uint32_t)raw_header[0] |
                      ((uint32_t)raw_header[1] << 8) |
                      ((uint32_t)raw_header[2] << 16);
    uint8_t rx_ecc = raw_header[3] & 0x3F;
    uint8_t calc_ecc = csi2_calc_ecc(data24);
    uint8_t syndrome = rx_ecc ^ calc_ecc;

    out_hdr->ecc_corrected = false;

    if (syndrome != 0) {
        // Таблиця відповідності синдрому до номеру пошкодженого біта (0..23)
        static const uint8_t syndrome_table[64] = {
            [0x07] = 0,  [0x0B] = 1,  [0x0D] = 2,  [0x0E] = 3,
            [0x13] = 4,  [0x15] = 5,  [0x16] = 6,  [0x19] = 7,
            [0x1A] = 8,  [0x1C] = 9,  [0x23] = 10, [0x25] = 11,
            [0x26] = 12, [0x29] = 13, [0x2A] = 14, [0x2C] = 15,
            [0x31] = 16, [0x32] = 17, [0x34] = 18, [0x38] = 19,
            [0x1F] = 20, [0x2F] = 21, [0x37] = 22, [0x3B] = 23
        };

        if (syndrome <= 0x3F && (syndrome == 0x01 || syndrome == 0x02 || syndrome == 0x04 ||
                                 syndrome == 0x08 || syndrome == 0x10 || syndrome == 0x20)) {
            // Помилка в самому біті ECC — дані заголовка не ушкоджені
            out_hdr->ecc_corrected = true;
        } else if (syndrome <= 0x3F && syndrome_table[syndrome] != 0) {
            uint8_t bit_idx = syndrome_table[syndrome];
            data24 ^= (1U << bit_idx); // Інверсія пошкодженого біта
            out_hdr->ecc_corrected = true;
        } else {
            return CSI2_ERR_ECC_UNCORRECTABLE;
        }
    }

    out_hdr->data_type = (uint8_t)(data24 & 0x3F);
    out_hdr->virtual_channel = (uint8_t)((data24 >> 6) & 0x03);
    out_hdr->word_count = (uint16_t)((data24 >> 8) & 0xFFFF);
    return CSI2_OK;
}

// Розрахунок контрольної суми CRC-16-CCITT над байтами Payload
static uint16_t csi2_calc_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (int b = 0; b < 8; b++) {
            if (crc & 0x8000) {
                crc = (uint16_t)((crc << 1) ^ CRC16_CCITT_POLY);
            } else {
                crc = (uint16_t)(crc << 1);
            }
        }
    }
    return crc;
}

// Розпакування 5-байтних блоків RAW10 у 4 пікселі uint16_t
csi2_status_t csi2_unpack_raw10_packet(
    const uint8_t *packet_buf,
    size_t packet_size,
    uint16_t *out_pixels,
    size_t max_pixels,
    size_t *actual_pixels
) {
    if (!packet_buf || !out_pixels || !actual_pixels) return CSI2_ERR_NULL_PTR;
    if (packet_size < 6) return CSI2_ERR_BUFFER_TOO_SMALL;

    csi2_header_t hdr;
    csi2_status_t status = csi2_parse_header(packet_buf, &hdr);
    if (status != CSI2_OK) return status;

    if (hdr.data_type != CSI2_DT_RAW10) return CSI2_ERR_INVALID_DATA_TYPE;

    size_t expected_total_size = 4 + (size_t)hdr.word_count + 2;
    if (packet_size < expected_total_size) return CSI2_ERR_BUFFER_TOO_SMALL;

    const uint8_t *payload = packet_buf + 4;
    uint16_t rx_crc = (uint16_t)payload[hdr.word_count] |
                      ((uint16_t)payload[hdr.word_count + 1] << 8);
    uint16_t calc_crc = csi2_calc_crc16(payload, hdr.word_count);

    if (rx_crc != calc_crc) return CSI2_ERR_CRC_MISMATCH;

    size_t num_blocks = hdr.word_count / 5;
    size_t total_pixels = num_blocks * 4;
    if (total_pixels > max_pixels) total_pixels = max_pixels;

    size_t px_idx = 0;
    for (size_t i = 0; i < num_blocks && (px_idx + 3) < max_pixels; i++) {
        const uint8_t *b = payload + (i * 5);
        uint8_t lsb_byte = b[4];

        out_pixels[px_idx + 0] = (uint16_t)(((uint16_t)b[0] << 2) | ((lsb_byte >> 0) & 0x03));
        out_pixels[px_idx + 1] = (uint16_t)(((uint16_t)b[1] << 2) | ((lsb_byte >> 2) & 0x03));
        out_pixels[px_idx + 2] = (uint16_t)(((uint16_t)b[2] << 2) | ((lsb_byte >> 4) & 0x03));
        out_pixels[px_idx + 3] = (uint16_t)(((uint16_t)b[3] << 2) | ((lsb_byte >> 6) & 0x03));
        px_idx += 4;
    }

    *actual_pixels = px_idx;
    return CSI2_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <expected>
#include <array>

namespace mipi::csi2 {

constexpr uint8_t DT_RAW10 = 0x2B;
constexpr uint16_t CRC16_CCITT_POLY = 0x1021;

enum class ParseError {
    BufferTooSmall,
    InvalidDataType,
    EccUncorrectable,
    CrcMismatch
};

struct PacketHeader {
    uint8_t virtual_channel;
    uint8_t data_type;
    uint16_t word_count;
    bool ecc_corrected;
};

// Обчислення бітів паритету Хеммінга для 24-бітного заголовка
constexpr uint8_t calculate_ecc(uint32_t data24) noexcept {
    auto bit = [data24](int n) -> uint32_t { return (data24 >> n) & 1U; };
    uint8_t p0 = bit(0)^bit(1)^bit(2)^bit(4)^bit(5)^bit(7)^bit(8)^bit(10)^bit(11)^bit(13)^bit(14)^bit(16)^bit(20)^bit(21)^bit(23);
    uint8_t p1 = bit(0)^bit(1)^bit(3)^bit(4)^bit(6)^bit(7)^bit(9)^bit(10)^bit(12)^bit(13)^bit(15)^bit(17)^bit(20)^bit(22)^bit(23);
    uint8_t p2 = bit(0)^bit(2)^bit(3)^bit(5)^bit(6)^bit(7)^bit(11)^bit(12)^bit(13)^bit(18)^bit(19)^bit(20)^bit(22)^bit(23);
    uint8_t p3 = bit(1)^bit(2)^bit(3)^bit(8)^bit(9)^bit(10)^bit(11)^bit(12)^bit(13)^bit(14)^bit(15)^bit(18)^bit(19)^bit(21)^bit(22)^bit(23);
    uint8_t p4 = bit(4)^bit(5)^bit(6)^bit(7)^bit(8)^bit(9)^bit(10)^bit(11)^bit(12)^bit(13)^bit(14)^bit(15)^bit(16)^bit(17)^bit(21)^bit(22)^bit(23);
    uint8_t p5 = bit(16)^bit(17)^bit(18)^bit(19)^bit(20)^bit(21)^bit(22)^bit(23);

    return static_cast<uint8_t>(p0 | (p1 << 1) | (p2 << 2) | (p3 << 3) | (p4 << 4) | (p5 << 5));
}

// Парсер та коректор заголовка
std::expected<PacketHeader, ParseError> parse_header(std::span<const uint8_t, 4> raw) noexcept {
    uint32_t data24 = static_cast<uint32_t>(raw[0]) |
                      (static_cast<uint32_t>(raw[1]) << 8) |
                      (static_cast<uint32_t>(raw[2]) << 16);
    uint8_t rx_ecc = raw[3] & 0x3F;
    uint8_t calc_ecc = calculate_ecc(data24);
    uint8_t syndrome = rx_ecc ^ calc_ecc;

    bool corrected = false;
    if (syndrome != 0) {
        constexpr std::array<uint8_t, 64> syndrome_lut = [] {
            std::array<uint8_t, 64> lut{};
            lut[0x07] = 0;  lut[0x0B] = 1;  lut[0x0D] = 2;  lut[0x0E] = 3;
            lut[0x13] = 4;  lut[0x15] = 5;  lut[0x16] = 6;  lut[0x19] = 7;
            lut[0x1A] = 8;  lut[0x1C] = 9;  lut[0x23] = 10; lut[0x25] = 11;
            lut[0x26] = 12; lut[0x29] = 13; lut[0x2A] = 14; lut[0x2C] = 15;
            lut[0x31] = 16; lut[0x32] = 17; lut[0x34] = 18; lut[0x38] = 19;
            lut[0x1F] = 20; lut[0x2F] = 21; lut[0x37] = 22; lut[0x3B] = 23;
            return lut;
        }();

        if (syndrome <= 0x3F && (syndrome == 0x01 || syndrome == 0x02 || syndrome == 0x04 ||
                                 syndrome == 0x08 || syndrome == 0x10 || syndrome == 0x20)) {
            corrected = true;
        } else if (syndrome <= 0x3F && syndrome_lut[syndrome] != 0) {
            uint8_t bit_idx = syndrome_lut[syndrome];
            data24 ^= (1U << bit_idx);
            corrected = true;
        } else {
            return std::unexpected(ParseError::EccUncorrectable);
        }
    }

    return PacketHeader{
        .virtual_channel = static_cast<uint8_t>((data24 >> 6) & 0x03),
        .data_type = static_cast<uint8_t>(data24 & 0x3F),
        .word_count = static_cast<uint16_t>((data24 >> 8) & 0xFFFF),
        .ecc_corrected = corrected
    };
}

// Розрахунок CRC-16-CCITT
uint16_t calculate_crc16(std::span<const uint8_t> payload) noexcept {
    uint16_t crc = 0xFFFF;
    for (uint8_t byte : payload) {
        crc ^= static_cast<uint16_t>(static_cast<uint16_t>(byte) << 8);
        for (int b = 0; b < 8; ++b) {
            if (crc & 0x8000) {
                crc = static_cast<uint16_t>((crc << 1) ^ CRC16_CCITT_POLY);
            } else {
                crc = static_cast<uint16_t>(crc << 1);
            }
        }
    }
    return crc;
}

// Розпакування RAW10 пакета в контейнер std::vector<uint16_t>
std::expected<std::vector<uint16_t>, ParseError> unpack_raw10_packet(std::span<const uint8_t> packet) {
    if (packet.size() < 6) {
        return std::unexpected(ParseError::BufferTooSmall);
    }

    std::span<const uint8_t, 4> raw_hdr(packet.data(), 4);
    auto header_res = parse_header(raw_hdr);
    if (!header_res) {
        return std::unexpected(header_res.error());
    }

    const auto& hdr = *header_res;
    if (hdr.data_type != DT_RAW10) {
        return std::unexpected(ParseError::InvalidDataType);
    }

    if (packet.size() < 4 + static_cast<size_t>(hdr.word_count) + 2) {
        return std::unexpected(ParseError::BufferTooSmall);
    }

    auto payload = packet.subspan(4, hdr.word_count);
    uint16_t rx_crc = static_cast<uint16_t>(packet[4 + hdr.word_count]) |
                      (static_cast<uint16_t>(packet[4 + hdr.word_count + 1]) << 8);

    if (rx_crc != calculate_crc16(payload)) {
        return std::unexpected(ParseError::CrcMismatch);
    }

    size_t num_blocks = hdr.word_count / 5;
    std::vector<uint16_t> pixels;
    pixels.reserve(num_blocks * 4);

    for (size_t i = 0; i < num_blocks; ++i) {
        const uint8_t* b = &payload[i * 5];
        uint8_t lsb = b[4];

        pixels.push_back(static_cast<uint16_t>((static_cast<uint16_t>(b[0]) << 2) | ((lsb >> 0) & 0x03)));
        pixels.push_back(static_cast<uint16_t>((static_cast<uint16_t>(b[1]) << 2) | ((lsb >> 2) & 0x03)));
        pixels.push_back(static_cast<uint16_t>((static_cast<uint16_t>(b[2]) << 2) | ((lsb >> 4) & 0x03)));
        pixels.push_back(static_cast<uint16_t>((static_cast<uint16_t>(b[3]) << 2) | ((lsb >> 6) & 0x03)));
    }

    return pixels;
}

} // namespace mipi::csi2
```
:::

---

### Аналіз продуктивності та апаратні пастки

Під час розпакування сирих відеопотоків у реальному часі на центральному процесорі виникає суттєве навантаження на підсистему пам'яті. Для кадру з роздільною здатністю 4K (3840 × 2160 пікселів) за частоти 60 к/с процесор мусить щосекунди обробляти близько 500 мільйонів пікселів (понад 620 мегабайтів вхідного упакованого бінарного потоку, що перетворюється на 1 гігабайт 16-бітних слів).

Розглянемо ключові інженерні прийоми оптимізації цього конвеєра:

#### 1. Векторизація SIMD (ARM NEON / x86 AVX2)
Базовий скалярний цикл C/C++ виконує по 4 операції побітового зсуву, 4 операції логічного виділення маски та 4 операції «АБО» на кожні 5 вхідних байтів. Це створює вузьке місце за кількістю інструкцій цілочисельного конвеєра CPU.

За допомогою векторних розширень (наприклад, інструкцій ARM NEON у мобільних чипах Cortex-A або ядрах Apple Silicon) алгоритм розпакування прискорюється в 6–8 разів:
1. За допомогою векторної інструкції `vld1q_u8` у 128-бітний регістр NEON завантажуються одразу 16 байтів вхідного потоку.
2. Векторна таблична перестановка `vtbl2_u8` розділяє масив на старші байти пікселів і байти молодших бітів.
3. Векторні зсуви `vshlq_n_u16` та порозрядні маски накладаються паралельно над вісьмома 16-бітними регістрами за один машинний такт.

#### 2. Організація буферів DMA та крок рядка (Line Stride)
Контролери прямого доступу до пам'яті (DMA) у підсистемах захоплення відео (наприклад, у драйверах V4L2 під Linux) вимагають обов'язкового вирівнювання початкової адреси кожного рядка на границю кеш-лінії процесора (зазвичай 64 або 128 байтів).

Якщо ширина корисного навантаження рядка `Word Count` не є кратною 64 байтам, контролер доповнює кінець рядка фіктивними нулями в оперативній пам'яті (утворюється крок рядка, або англ. *line stride*). Програмний парсер повинен розраховувати адресу початку наступного пакета рядка не додаванням `WC + 6`, а з урахуванням апаратного зміщення:
```
const uint8_t *next_row_ptr = current_row_ptr + dma_stride_bytes;
```
Ігнорування параметра `stride` призводить до прогресуючого діагонального зсуву зображення (англ. *image tearing / skewing*) після кожного зчитаного рядка.

#### 3. Нульове копіювання (Zero-Copy) та прямий апаратний ISP
У промислових вбудованих пристроях центральний процесор майже ніколи не займається програмним розпакуванням пікселів під час звичайного запису відео. Потік MIPI CSI-2 через спеціалізований блок апаратного мосту (Hardware Bridge) спрямовується безпосередньо у вхідний конвеєр апаратного процесора обробки сигналів зображення (ISP).

ISP зчитує сирі 5-байтові блоки прямо з шини DMA за допомогою спеціалізованих апаратних зсувних регістрів, здійснює калібрування темнового струму матриці, просторове виправлення дефектних пікселів, баланс білого та [демозаїку Баєра](topic:algorithms/bayer-demosaic) «на льоту» на тактовій частоті системної шини без залучення ресурсів CPU. Програмний розбір застосовується під час калібрування сенсорів, діагностики каналу зв'язку та збереження сирих знімків без втрат у формат DNG/RAW.
