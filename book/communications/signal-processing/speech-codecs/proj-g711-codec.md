# ⚙️ Реалізація кодека G.711 A-law та µ-law мовами C та C++

У цьому практичному проекті розроблено високопродуктивну реалізацію логарифмічного компандування та декомпандування мовного сигналу за стандартом ITU-T G.711. Розглянуто як обчислювальний підхід на основі побітових операцій та зсувів, так і підхід на основі заздалегідь згенерованих таблиць пошуку (Lookup Tables, LUT). Програма перетворює 16-бітний лінійний PCM-сигнал (8000 Гц) у 8-бітний стиснутий потік A-law або µ-law та відновлює його назад із мінімальною квадратичною помилкою.

## 1. Механізм стиснення та відрізково-лінійна апроксимація

Стандарт G.711 перетворює 16-бітні лінійні відліки PCM у 8-бітні закодовані байти за допомогою відрізково-лінійної апроксимації логарифмічної кривої стиснення.

Для A-law діапазон амплітуд розділено на 8 сегментів (інтервалів або хорд) для додатних значень та 8 сегментів для від'ємних значень. Кожен сегмент містить рівно 16 рівнів квантування:
- **Сегмент 0**: відліки від 0 до 31 (крок квантування = 1, максимальна роздільна здатність).
- **Сегмент 1**: відліки від 32 до 63 (крок квантування = 1).
- **Сегмент 2**: відліки від 64 до 127 (крок квантування = 2).
- **Сегмент 3**: відліки від 128 до 255 (крок квантування = 4).
- **Сегмент 4**: відліки від 256 до 511 (крок квантування = 8).
- **Сегмент 5**: відліки від 512 до 1023 (крок квантування = 16).
- **Сегмент 6**: відліки від 1024 до 2047 (крок квантування = 32).
- **Сегмент 7**: відліки від 2048 до 4095 (крок квантування = 64, найгрубше квантування).

Алгоритм обчислювального перетворення PCM у A-law складається з наступних кроків:
1. **Аналіз знака**: вилучається знаковий біт. Для додатних відліків знаковий біт MSB вихідного байта встановлюється у `1`, для від'ємних — у `0` (з інверсією амплітуди).
2. **Обмеження амплітуди (Clipping)**: вхідні значення затискаються у межах максимального динамічного діапазону від -32512 до +32512.
3. **Пошук сегмента**: за допомогою пошуку позиції старшої одиниці у побітовому представленні визначається номер сегмента `eee` (від 0 до 7).
4. **Формування мантиси**: з відповідного зсунутого значення вилучаються 4 біти квантованої мантиси `ssss`.
5. **Упаковка та інверсія біт**: сформований байт `[s | eee | ssss]` піддається побітовому XOR із маскою `0xD5` (інверсія парних біт). Це є вимовою стандарту ITU-T G.711 для A-law, яка гарантує появу частих переходів `0 ↔ 1` у фізичному мідному каналі зв'язку для стійкої синхронізації фазового автопідстроювання частоти (ФАПЧ/PLL) повторювачів TDM.

Для µ-law алгоритм додає зміщення `bias = 33` до вхідного сигналу перед вилученням експоненти, що зсуває межі сегментів і розширює роздільність для надтихих сигналів, а наприкінці виконує повну інверсію всіх бітів байта (XOR з `0xFF`).

## 2. Обчислювальний підхід проти Lookup Tables (LUT)

У виборі архітектури реалізації кодека на медіа-серверах постає вибір між двома підходами:
- **Обчислювальний підхід (Bit-shifting)**: виконує розбірку знака, зсуви бітів та вибір сегмента через умови `if/else` або інструкції пошуку старшої одиниці (наприклад, `__builtin_clz` або `_BitScanReverse`). Цей підхід не споживає оперативну пам'ять та ідеально підходить для мікроконтролерів із малим обсягом кЕшу L1.
- **Табличний підхід (LUT)**: використовує заздалегідь обчислені масиви в оперативній пам'яті:
  - `linear_to_alaw_table[65536]`: таблиця розміром 64 КБ, яка миттєво перетворює будь-яке 16-бітне значення PCM у 8-бітний байт A-law за один виклик `alaw = LUT[pcm + 32768]`.
  - `alaw_to_linear_table[256]`: таблиця розміром всього 512 байт, яка розкодовує 8-бітний байт назад у 16-бітне лінійне значення PCM.

У сучасних багатопотокових медіа-серверах (Asterisk, FreeSWITCH) табличний підхід LUT для декодування (масив на 256 елементів) є абсолютним стандартом, оскільки 512 байт повністю вміщуються у найшвидший кЕш L1 Data CPU, забезпечуючи швидкість обробки понад 100 мільйонів відліків на секунду на один потік процесора.

## 3. Крайові випадки та обробка переповнень

Під час роботи з 16-бітними цілими числами зі знаком (`int16_t`) виникає декілька критичних крайових випадків:
- **Переповнення при інверсії знака (`-32768`)**: виклик `-pcm_val` для мінімального 16-бітного числа `-32768` у мовах C та C++ викликає знакове переповнення (Undefined Behavior у C). Кодек повинен явно перевіряти та перехоплювати це значення, насичуючи його до `-32767` або відсікаючи за порогом `G711_MAX_PCM`.
- **Насичення амплітуди (Clipping Saturation)**: амплітуди, що перевищують `+32512` або нижчі за `-32512`, повинні строго обрізатися до цих меж, щоб уникнути циклічного зсуву та викривлення знакового біта.
- **Точність відновлення сигналу**: декодування G.711 є втратним. При зворотному перетворенні 8-бітного байта у 16-бітний PCM відновлене значення встановлюється посередині відповідного інтервалу квантування (додається половина кроку квантування), що мінімізує середньоквадратичну помилку відновлення (MSE).

## 4. Високопродуктивна реалізація мовами C та C++

Наведений нижче код демонструє дві реалізації: низькорівневу реалізацію мовою C із побітовими операціями та обробкою масивів через вказівники, а також ідіоматичну реалізацію мовою C++20 з використанням `std::span`, безпечних константних виразів `constexpr` та векторної обробки потоків.

:::tabs
```c
/* g711_codec.c - Високопродуктивна реалізація G.711 мовою C */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define G711_MAX_PCM 32512
#define G711_BIAS 33

/* Таблиця швидкого мапування сегментів для A-law */
static const uint8_t g711_seg_end[8] = {
    0x1F, 0x3F, 0x7F, 0xFF, 0x1FF, 0x3FF, 0x7FF, 0xFFF
};

static inline int search_segment(int val, const uint8_t *table, int size) {
    for (int i = 0; i < size; i++) {
        if (val <= table[i]) {
            return i;
        }
    }
    return size;
}

uint8_t g711_linear_to_alaw(int16_t pcm_val) {
    int mask;
    int seg;
    uint8_t aval;

    if (pcm_val >= 0) {
        mask = 0xD5; /* Додатний знак: MSB = 1 */
    } else {
        mask = 0x55; /* Від'ємний знак: MSB = 0 */
        pcm_val = -pcm_val - 1;
        if (pcm_val < 0) pcm_val = 32767;
    }

    if (pcm_val > G711_MAX_PCM) {
        pcm_val = G711_MAX_PCM;
    }

    seg = search_segment(pcm_val >> 3, g711_seg_end, 8);

    if (seg >= 8) {
        return (uint8_t)(0x7F ^ mask);
    } else {
        aval = (uint8_t)(seg << 4);
        if (seg < 2) {
            aval |= (pcm_val >> 1) & 0x0F;
        } else {
            aval |= (pcm_val >> (seg + 2)) & 0x0F;
        }
        return (aval ^ mask);
    }
}

int16_t g711_alaw_to_linear(uint8_t a_val) {
    int t;
    int seg;

    a_val ^= 0xD5;
    t = (a_val & 0x0F) << 4;
    seg = ((unsigned int)a_val & 0x70) >> 4;

    switch (seg) {
        case 0:
            t += 8;
            break;
        case 1:
            t += 0x108;
            break;
        default:
            t += 0x108;
            t <<= (seg - 1);
            break;
    }
    return (a_val & 0x80) ? (int16_t)t : (int16_t)(-t);
}

uint8_t g711_linear_to_ulaw(int16_t pcm_val) {
    int mask;
    int seg;
    uint8_t uval;

    if (pcm_val < 0) {
        pcm_val = G711_BIAS - pcm_val;
        mask = 0x7F;
    } else {
        pcm_val += G711_BIAS;
        mask = 0xFF;
    }

    if (pcm_val > 0x7FFF) pcm_val = 0x7FFF;

    seg = search_segment(pcm_val, (const uint8_t[]){0x3F,0x7F,0xFF,0x1FF,0x3FF,0x7FF,0xFFF,0x1FFF}, 8);

    if (seg >= 8) {
        return (uint8_t)(0x7F ^ mask);
    } else {
        uval = (uint8_t)((seg << 4) | ((pcm_val >> (seg + 3)) & 0x0F));
        return (uval ^ mask);
    }
}

int16_t g711_ulaw_to_linear(uint8_t u_val) {
    int t;

    u_val = ~u_val;
    t = (((u_val & 0x0F) << 3) + G711_BIAS) << ((unsigned int)(u_val & 0x70) >> 4);
    return (u_val & 0x80) ? (int16_t)(G711_BIAS - t) : (int16_t)(t - G711_BIAS);
}

int main(void) {
    int16_t original_pcm = 12345;
    uint8_t alaw_encoded = g711_linear_to_alaw(original_pcm);
    int16_t decoded_pcm = g711_alaw_to_linear(alaw_encoded);

    printf("G.711 A-law test:\n");
    printf("Original PCM: %d\n", original_pcm);
    printf("Encoded A-law byte: 0x%02X\n", alaw_encoded);
    printf("Decoded PCM:  %d (Error: %d)\n", decoded_pcm, abs(original_pcm - decoded_pcm));

    return 0;
}
```
```cpp
// g711_codec.cpp - Ідіоматична реалізація G.711 мовою C++20
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <cmath>
#include <cstdint>
#include <algorithm>

namespace g711 {

constexpr int16_t MAX_PCM = 32512;
constexpr int16_t BIAS = 33;

constexpr std::array<uint16_t, 8> SEG_END_ALAW = {
    0x1F, 0x3F, 0x7F, 0xFF, 0x1FF, 0x3FF, 0x7FF, 0xFFF
};

class Codec {
public:
    [[nodiscard]] static constexpr uint8_t encode_alaw(int16_t pcm_val) noexcept {
        int mask = (pcm_val >= 0) ? 0xD5 : 0x55;
        if (pcm_val < 0) {
            pcm_val = -pcm_val - 1;
            if (pcm_val < 0) pcm_val = 32767;
        }

        pcm_val = std::min(pcm_val, MAX_PCM);

        int pcm_shifted = pcm_val >> 3;
        int seg = 0;
        while (seg < 8 && pcm_shifted > SEG_END_ALAW[seg]) {
            ++seg;
        }

        if (seg >= 8) {
            return static_cast<uint8_t>(0x7F ^ mask);
        }

        uint8_t aval = static_cast<uint8_t>(seg << 4);
        if (seg < 2) {
            aval |= (pcm_val >> 1) & 0x0F;
        } else {
            aval |= (pcm_val >> (seg + 2)) & 0x0F;
        }
        return static_cast<uint8_t>(aval ^ mask);
    }

    [[nodiscard]] static constexpr int16_t decode_alaw(uint8_t a_val) noexcept {
        a_val ^= 0xD5;
        int t = (a_val & 0x0F) << 4;
        int seg = (a_val & 0x70) >> 4;

        switch (seg) {
            case 0:  t += 8; break;
            case 1:  t += 0x108; break;
            default: t = (t + 0x108) << (seg - 1); break;
        }
        return (a_val & 0x80) ? static_cast<int16_t>(t) : static_cast<int16_t>(-t);
    }

    static void encode_stream_alaw(std::span<const int16_t> pcm_in, std::span<uint8_t> alaw_out) {
        const size_t count = std::min(pcm_in.size(), alaw_out.size());
        for (size_t i = 0; i < count; ++i) {
            alaw_out[i] = encode_alaw(pcm_in[i]);
        }
    }

    static void decode_stream_alaw(std::span<const uint8_t> alaw_in, std::span<int16_t> pcm_out) {
        const size_t count = std::min(alaw_in.size(), pcm_out.size());
        for (size_t i = 0; i < count; ++i) {
            pcm_out[i] = decode_alaw(alaw_in[i]);
        }
    }
};

} // namespace g711

int main() {
    const std::vector<int16_t> pcm_buffer = { 0, 100, 500, 2000, 10000, -5000, 32000 };
    std::vector<uint8_t> alaw_buffer(pcm_buffer.size());
    std::vector<int16_t> restored_pcm(pcm_buffer.size());

    g711::Codec::encode_stream_alaw(pcm_buffer, alaw_buffer);
    g711::Codec::decode_stream_alaw(alaw_buffer, restored_pcm);

    std::cout << "G.711 C++20 Stream Processing Results:\n";
    for (size_t i = 0; i < pcm_buffer.size(); ++i) {
        std::cout << "PCM In: " << pcm_buffer[i]
                  << " -> A-law: 0x" << std::hex << (int)alaw_buffer[i] << std::dec
                  << " -> PCM Out: " << restored_pcm[i]
                  << " (Diff: " << std::abs(pcm_buffer[i] - restored_pcm[i]) << ")\n";
    }

    return 0;
}
```
:::
