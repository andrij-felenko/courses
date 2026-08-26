# ⚙️ Апаратні механізми пакета: скремблер LFSR, бітовий синхронізатор і CRC-16

Коли мікроконтролер надсилає сирий потік байтів у радіоефір, перша наївна спроба передати довгу послідовність нулів або одиниць закінчується аварією прийому: аналоговий частотний дискримінатор втрачає рівень постійної складової, фазове автопідстроювання частоти (AFC) з'їжджає, а бітовий тактовий генератор модему (Bit Slicer) втрачає прив'язку до фронтів і починає плодити бітові помилки.

Щоб радіотракт залишався працездатним незалежно від того, які саме дані передає застосунок, у радіотрансивер вбудовують **апаратний кадровий процесор (Packet Handler)**. Він бере на себе чотири критичні операції:
1. Формування та розпізнавання преамбули для тактової синхронізації;
2. Детекцію синхрослова для побайтового вирівнювання;
3. Псевдовипадкове відбілювання даних (Data Whitening) через регістр зсуву з лінійним зворотним зв'язком (LFSR);
4. Апаратне обчислення та перевірку контрольної суми CRC-16.

Розгляньмо фізичні та алгоритмічні механізми кожного вузла й реалізуймо повний програмний емулятор кадрового процесора мовами C та C++.

## Математика відбілювання даних (LFSR Data Whitening)

У частотній модуляції FSK логічний нуль передається однією частотою (`f_0 - Δf`), а логічна одиниця — іншою (`f_0 + Δf`). Якщо передавати підряд 50 нульових байтів, передавач безперервно випромінюватиме незмінну зміщену частоту. На боці приймача це сприймається як паразитна постійна напруга (DC offset) на виході частотного детектора. Блокувальні конденсатори тракту низької частоти зрізають цю постійну складову, через що корисний сигнал схлопується до нуля. Крім того, випромінювання фіксованої частоти концентрує всю енергію передавача в одній спектральній лінії, що порушує регуляторні норми ETSI та FCC щодо граничної спектральної густини потужності.

Апаратний скремблер усуває ці проблеми: він побітово додає за модулем 2 (XOR) вхідні дані з псевдовипадковою бітовою послідовністю (Pseudo-Random Binary Sequence, PRBS), що генерується регістром зсуву з лінійним зворотним зв'язком (LFSR).

У трансиверах класів CC1101, nRF24L01 та SX1262 використовується стандартний незвідний примітивний поліном 7-го порядку:

```
P(x) = x^7 + x^4 + 1
```

Початковий стан регістра (Seed) встановлюється в `0x7F` (усі одиниці: `1111111_2`).

Оскільки період максимальної послідовності для 7-бітного регістра становить `2^7 - 1 = 127` бітів, спектр випромінювання рівномірно розмазується по всій смузі каналу, а середня кількість нулів та одиниць у будь-якому блоці даних вирівнюється у пропорції 50:50. Це забезпечує ідеальний баланс постійної складової (DC balance) та гарантує наявність частих переходів `0 ↔ 1`, необхідних для утримання фази приймального бітового генератора.

Для кожного вхідного біта скремблер виконує таку послідовність кроків:
1. Біт зворотного зв'язку обчислюється як виключне «АБО» старшого та четвертого розрядів: `feedback = bit[6] ^ bit[3]`;
2. Вихідний біт маски знімається зі старшого розряду `bit[6]`;
3. Регістр зсувається вліво на 1 розряд, а в молодший біт записується обчислений `feedback`;
4. Вхідний інформаційний біт ксориться з вихідним бітом маски: `out_bit = in_bit ^ mask_bit`.

Оскільки операція додавання за модулем 2 є самозворотною (`A ⊕ B ⊕ B = A`), дескремблер у приймачі працює за абсолютно ідентичним алгоритмом і з тим самим початковим заповненням `0x7F`.

## Бітова та байтова синхронізація

Перед корисним пакетом передавач завжди відправляє службові синхронізувальні поля:

- **Преамбула (Preamble)**: регулярна послідовність чергування бітів `10101010` (`0xAA`) або `01010101` (`0x55`) тривалістю від 2 до 8 байтів. Вона надає аналоговому блоку AGC час на підлаштування підсилення, а цифровому блоку Clock Recovery — можливість зафіксувати фазу бітових імпульсів за допомогою цифрового контуру ФАПЧ (Digital PLL / Bit Slicer);
- **Синхрослово (Sync Word / Access Address)**: унікальна бітова послідовність довжиною 2, 3 або 4 байти (наприклад, `0xD391` у CC1101 або `0x2DD4` у nRF24). Коли апаратний корелятор знаходить точний збіг синхрослова в потоці розпізнаних бітів, він генерує внутрішній строб початку байтового вирівнювання: наступний біт вважається старшим бітом першого байта кадру, і потік перемикається у буфер FIFO.

## Обчислення та виявлення помилок за допомогою CRC-16

Для захисту від спотворень пакет завершується 16-бітною контрольною сумою. Стандартний поліном CCITT:

```
P_CRC(x) = x^16 + x^12 + x^5 + 1  (шістнадцятковий коефіцієнт 0x1021)
Початкове значення (Init): 0xFFFF
```

Математично цей поліном гарантує:
- 100% виявлення всіх поодиноких бітових помилок;
- 100% виявлення всіх подвійних бітових помилок для пакетів довжиною до 2048 байтів;
- 100% виявлення будь-якої непарної кількості помилок;
- 100% виявлення пачкових помилок (Burst Errors) довжиною до 16 бітів підряд.

Якщо апаратний блок перевірки CRC приймача виявляє невідповідність суми в кінці пакета, він автоматично скидає покажчик FIFO і відкидає пошкоджений кадр без генерації переривання успішного прийому (`RX_DONE`).

## Програмна реалізація Packet Engine

Наведений нижче модуль кадрової обробки реалізує повний цикл формування, скремблювання, розпакування та верифікації радіопакетів.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define PREAMBLE_BYTE     0xAA
#define PREAMBLE_LEN      4
#define SYNC_WORD         0xD391
#define CRC16_POLY        0x1021
#define CRC16_INIT        0xFFFF
#define LFSR_SEED         0x7F
#define MAX_PAYLOAD_LEN   64
#define MAX_FRAME_LEN     (PREAMBLE_LEN + 2 + 1 + MAX_PAYLOAD_LEN + 2)

typedef struct {
    uint8_t payload[MAX_PAYLOAD_LEN];
    uint8_t length;
    bool    crc_ok;
} RxPacketResult;

// Ініціалізація та обчислення CRC-16 CCITT
uint16_t crc16_update(uint16_t crc, uint8_t data) {
    crc ^= ((uint16_t)data << 8);
    for (uint8_t i = 0; i < 8; i++) {
        if (crc & 0x8000) {
            crc = (crc << 1) ^ CRC16_POLY;
        } else {
            crc = (crc << 1);
        }
    }
    return crc;
}

// 7-бітний LFSR скремблер (x^7 + x^4 + 1)
void lfsr_whiten(uint8_t *data, size_t len) {
    uint8_t lfsr = LFSR_SEED;
    for (size_t i = 0; i < len; i++) {
        uint8_t out_byte = 0;
        for (int bit = 7; bit >= 0; bit--) {
            uint8_t lfsr_out = (lfsr >> 6) & 0x01;
            uint8_t feedback = ((lfsr >> 6) ^ (lfsr >> 3)) & 0x01;
            lfsr = ((lfsr << 1) | feedback) & 0x7F;

            uint8_t in_bit = (data[i] >> bit) & 0x01;
            out_byte |= ((in_bit ^ lfsr_out) << bit);
        }
        data[i] = out_byte;
    }
}

// Формування кадру для відправки в ефір
size_t packet_encode(const uint8_t *payload, uint8_t payload_len, uint8_t *frame_out) {
    if (payload_len > MAX_PAYLOAD_LEN) return 0;

    size_t idx = 0;

    // 1. Преамбула (4 байти 0xAA)
    for (size_t i = 0; i < PREAMBLE_LEN; i++) {
        frame_out[idx++] = PREAMBLE_BYTE;
    }

    // 2. Синхрослово (0xD391, MSB first)
    frame_out[idx++] = (uint8_t)(SYNC_WORD >> 8);
    frame_out[idx++] = (uint8_t)(SYNC_WORD & 0xFF);

    // 3. Байт довжини корисного навантаження
    uint8_t len_byte = payload_len;
    frame_out[idx++] = len_byte;

    // 4. Тимчасовий буфер для скремблювання корисного навантаження
    uint8_t whitened_payload[MAX_PAYLOAD_LEN];
    memcpy(whitened_payload, payload, payload_len);
    lfsr_whiten(whitened_payload, payload_len);

    memcpy(&frame_out[idx], whitened_payload, payload_len);
    idx += payload_len;

    // 5. Розрахунок CRC-16 (по довжині та скрембльованому payload)
    uint16_t crc = CRC16_INIT;
    crc = crc16_update(crc, len_byte);
    for (size_t i = 0; i < payload_len; i++) {
        crc = crc16_update(crc, whitened_payload[i]);
    }

    frame_out[idx++] = (uint8_t)(crc >> 8);
    frame_out[idx++] = (uint8_t)(crc & 0xFF);

    return idx;
}

// Декодування та верифікація прийнятого кадру
bool packet_decode(const uint8_t *frame, size_t frame_len, RxPacketResult *result) {
    if (frame_len < (PREAMBLE_LEN + 2 + 1 + 2)) return false;

    // 1. Пошук синхрослова
    size_t sync_pos = 0;
    bool sync_found = false;
    for (size_t i = 0; i <= frame_len - 2; i++) {
        uint16_t sw = ((uint16_t)frame[i] << 8) | frame[i + 1];
        if (sw == SYNC_WORD) {
            sync_pos = i + 2;
            sync_found = true;
            break;
        }
    }
    if (!sync_found) return false;

    // 2. Читання довжини
    if (sync_pos >= frame_len) return false;
    uint8_t payload_len = frame[sync_pos++];
    if (payload_len > MAX_PAYLOAD_LEN) return false;
    if (sync_pos + payload_len + 2 > frame_len) return false;

    // 3. Перевірка CRC
    uint16_t calc_crc = CRC16_INIT;
    calc_crc = crc16_update(calc_crc, payload_len);
    for (size_t i = 0; i < payload_len; i++) {
        calc_crc = crc16_update(calc_crc, frame[sync_pos + i]);
    }

    uint16_t rx_crc = ((uint16_t)frame[sync_pos + payload_len] << 8) | 
                      frame[sync_pos + payload_len + 1];

    result->length = payload_len;
    result->crc_ok = (calc_crc == rx_crc);

    if (!result->crc_ok) {
        return false;
    }

    // 4. Дескремблювання даних
    memcpy(result->payload, &frame[sync_pos], payload_len);
    lfsr_whiten(result->payload, payload_len);

    return true;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <algorithm>

namespace RadioHardware {

class PacketEngine {
public:
    static constexpr uint8_t  PreambleByte   = 0xAA;
    static constexpr size_t   PreambleLength = 4;
    static constexpr uint16_t SyncWord       = 0xD391;
    static constexpr uint16_t Crc16Poly      = 0x1021;
    static constexpr uint16_t Crc16Init      = 0xFFFF;
    static constexpr uint8_t  LfsrSeed       = 0x7F;
    static constexpr size_t   MaxPayloadSize = 64;
    static constexpr size_t   MaxFrameSize   = PreambleLength + 2 + 1 + MaxPayloadSize + 2;

    struct DecodedPacket {
        std::array<uint8_t, MaxPayloadSize> payload{};
        size_t                              length{0};
    };

    // Статичний розрахунок CRC-16 CCITT
    static constexpr uint16_t updateCrc(uint16_t crc, uint8_t byte) noexcept {
        crc ^= static_cast<uint16_t>(byte) << 8;
        for (size_t i = 0; i < 8; ++i) {
            if ((crc & 0x8000U) != 0U) {
                crc = static_cast<uint16_t>((crc << 1) ^ Crc16Poly);
            } else {
                crc = static_cast<uint16_t>(crc << 1);
            }
        }
        return crc;
    }

    // Побітове скремблювання/дескремблювання LFSR (x^7 + x^4 + 1)
    static void applyWhitening(std::span<uint8_t> buffer) noexcept {
        uint8_t lfsr = LfsrSeed;
        for (auto& byte : buffer) {
            uint8_t whitened = 0;
            for (int bit = 7; bit >= 0; --bit) {
                const uint8_t lfsrOut  = (lfsr >> 6) & 0x01U;
                const uint8_t feedback = ((lfsr >> 6) ^ (lfsr >> 3)) & 0x01U;
                lfsr = static_cast<uint8_t>(((lfsr << 1) | feedback) & 0x7FU);

                const uint8_t inBit = (byte >> bit) & 0x01U;
                whitened |= static_cast<uint8_t>((inBit ^ lfsrOut) << bit);
            }
            byte = whitened;
        }
    }

    // Пакування кадру для передавача
    static std::optional<size_t> encode(
        std::span<const uint8_t> payload,
        std::span<uint8_t>       frameOut) noexcept 
    {
        if (payload.size() > MaxPayloadSize) return std::nullopt;
        const size_t totalNeeded = PreambleLength + 2 + 1 + payload.size() + 2;
        if (frameOut.size() < totalNeeded) return std::nullopt;

        size_t idx = 0;

        // 1. Преамбула
        for (size_t i = 0; i < PreambleLength; ++i) {
            frameOut[idx++] = PreambleByte;
        }

        // 2. Синхрослово
        frameOut[idx++] = static_cast<uint8_t>(SyncWord >> 8);
        frameOut[idx++] = static_cast<uint8_t>(SyncWord & 0xFFU);

        // 3. Довжина
        const auto lenByte = static_cast<uint8_t>(payload.size());
        frameOut[idx++] = lenByte;

        // 4. Копіювання та скремблювання корисних даних
        const size_t payloadStart = idx;
        std::copy(payload.begin(), payload.end(), frameOut.begin() + payloadStart);
        applyWhitening(frameOut.subspan(payloadStart, payload.size()));
        idx += payload.size();

        // 5. CRC-16
        uint16_t crc = Crc16Init;
        crc = updateCrc(crc, lenByte);
        for (size_t i = payloadStart; i < idx; ++i) {
            crc = updateCrc(crc, frameOut[i]);
        }

        frameOut[idx++] = static_cast<uint8_t>(crc >> 8);
        frameOut[idx++] = static_cast<uint8_t>(crc & 0xFFU);

        return idx;
    }

    // Розпакування та перевірка кадру
    static std::optional<DecodedPacket> decode(std::span<const uint8_t> frame) noexcept {
        constexpr size_t minFrameSize = PreambleLength + 2 + 1 + 2;
        if (frame.size() < minFrameSize) return std::nullopt;

        // 1. Пошук синхрослова
        size_t syncPos = 0;
        bool found = false;
        for (size_t i = 0; i + 1 < frame.size(); ++i) {
            const uint16_t sw = (static_cast<uint16_t>(frame[i]) << 8) | frame[i + 1];
            if (sw == SyncWord) {
                syncPos = i + 2;
                found = true;
                break;
            }
        }
        if (!found || syncPos >= frame.size()) return std::nullopt;

        // 2. Довжина payload
        const uint8_t payloadLen = frame[syncPos++];
        if (payloadLen > MaxPayloadSize || (syncPos + payloadLen + 2 > frame.size())) {
            return std::nullopt;
        }

        // 3. Перевірка CRC
        uint16_t calculatedCrc = Crc16Init;
        calculatedCrc = updateCrc(calculatedCrc, payloadLen);
        for (size_t i = 0; i < payloadLen; ++i) {
            calculatedCrc = updateCrc(calculatedCrc, frame[syncPos + i]);
        }

        const uint16_t receivedCrc = (static_cast<uint16_t>(frame[syncPos + payloadLen]) << 8) |
                                     frame[syncPos + payloadLen + 1];

        if (calculatedCrc != receivedCrc) {
            return std::nullopt;
        }

        // 4. Дескремблювання у вихідний результат
        DecodedPacket packet{};
        packet.length = payloadLen;
        std::copy_n(frame.data() + syncPos, payloadLen, packet.payload.begin());
        applyWhitening(std::span<uint8_t>(packet.payload.data(), packet.length));

        return packet;
    }
};

} // namespace RadioHardware
```
:::

## Крайові випадки та пастки обробки кадрів

1. **Втрата бітової синхронізації в преамбулі**: якщо приймач увімкнувся в режимі RX пізно (під час звучання середини преамбули), схема Clock Recovery може не встигнути зафіксувати фазу до початку синхрослова. Як наслідок, корелятор синхрослова пропустить кадр. У надійних мережах довжину преамбули збільшують до 6–8 байтів;
2. **Фантомне виявлення синхрослова в шумі (False Sync Trigger)**: якщо в ефірі немає сигналу, але приймач слухає ефір з максимальним підсиленням AGC, тепловий шум генерує випадкову послідовність бітів. Імовірність випадкового збігу 16-бітного синхрослова становить 1 / 2^16 ≈ 1.5 · 10^(-5). На бітовій швидкості 250 кбіт/с це означає хибне спрацьовування кожні 2–4 секунди. Щоб уникнути зайвого завантаження мікроконтролера, використовують 32-бітні синхрослова або вмикають попередню фільтрацію за рівнем сигналу (Carrier Sense / Preamble Detect);
3. **Захист від переповнення буфера (FIFO Overrun)**: якщо мікроконтролер не встигає вичитати прийнятий пакет по SPI до приходу наступного, FIFO переповнюється і трансивер блокує прийом нових кадрів. У таких випадках драйвер зобов'язаний виконати строб-команду скидання `CMD_FLUSHRX`;
4. **Порядок передачі бітів (Bit Endianness)**: у радіопротоколах стандартним є передача MSB First (старший біт першим) для радіочастотних полів кадру та LSB First для деяких стандартів (наприклад, Bluetooth Low Energy). Невідповідність налаштування бітового порядку в трансивері та програмному скремблері призводить до повної втрати зв'язку.
