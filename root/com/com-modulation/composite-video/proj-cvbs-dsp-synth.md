# ⚙️ Програмний синтезатор тестових таблиць CVBS

Створення цифрового синтезатора композитного відеосигналу CVBS без використання спеціалізованих мікросхем відеокодерів (таких як Analog Devices ADV7125 або Maxim Integrated MAX7456) є класичною задачею цифрової обробки сигналів (DSP) для вбудованих систем, мікроконтролерів із швидкісним ЦАП (ESP32, STM32H7) та програмованих логічних інтегральних схем (FPGA).

У цьому проекті реалізовано повнофункціональний програмний синтезатор стандартного телевізійного рядка PAL із випробувальною таблицею 75% кольорових смуг (EBU Color Bars), що працює на підвищеній частоті дискретизації `F[s] = 17.734475 МГц` (строго 4-кратна частота колірної піднесучої PAL).

### Архітектура дискретної генерації та вибір частоти квантування

Для точного формування фази квадратурної модуляції без нагромадження накопичувальної похибки частота дискретизації вихідного цифро-аналогового перетворювача (ЦАП) повинна бути жорстко синхронізована з колірною піднесучою:

```
F[s] = 4 · f[sc] = 4 · 4433618.75 Гц = 17734475 Гц (17.734475 МГц)
```

За такої тактової частоти на один період колірної піднесучої припадає рівно 4 дискретні відліки. Фазовий крок між сусідніми відліками становить:

```
Δφ = 2π / 4 = π / 2 = 90°
```

Це спрощує тригонометричні обчислення квадратурної модуляції. Значення функцій `sin(k·π/2)` та `cos(k·π/2)` набувають циклічних значень з масиву `[0, 1, 0, -1]`, що дозволяє виконувати синтез у реальному часі навіть на процесорних ядрах без апаратного блоку обчислення дійсних чисел із рухомою комою (FPU).

Тривалість одного рядка системи PAL становить строго `64.0 мкс`. Кількість дискретних відліків у буфері одного рядка дорівнює:

```
N[line] = 64.0 мкс · 17.734475 МГц = 1135 відліків
```

### Рівні квантування 8-бітного ЦАП у шкалі IRE

Повний розмах вихідної напруги ЦАП від `0.0 В` (дно синхроімпульсу `-40 IRE`) до `1.0 В` (пік білого `+100 IRE`) відображається на 8-бітний діапазон квантування від `0` до `255`:

```
DAC(IRE) = (IRE + 40) / 140 · 255
```

Розрахунок ключових опорних рівнів кодера:
- **Дно синхроімпульсу (`-40 IRE`, `0.000 В`):** `DAC = 0`
- **Рівень гасіння / Чорний PAL (`0 IRE`, `0.286 В`):** `DAC = (0 + 40) / 140 · 255 ≈ 73`
- **П'єдестал NTSC (`+7.5 IRE`, `0.340 В`):** `DAC = (7.5 + 40) / 140 · 255 ≈ 86`
- **Рівень 75% білого (`+75 IRE`, `0.821 В`):** `DAC = (75 + 40) / 140 · 255 ≈ 209`
- **Пік 100% білого (`+100 IRE`, `1.000 В`):** `DAC = (100 + 40) / 140 · 255 = 255`
- **Амплітуда колірного спалаху (`±20 IRE`):** `A[burst] = 20 / 140 · 255 ≈ 36` відліків ЦАП

Застосування 8-бітного перетворювача забезпечує теоретичне відношення сигнал/шум квантування близько `SNR ≈ 6.02 · 8 + 1.76 ≈ 49.9 дБ`, що ідеально узгоджується з граничними вимогами аналогового мовлення (не гірше `50 дБ`).

### Програмна реалізація генератора на C та C++

У наведених нижче модулях реалізовано формування повного телевізійного рядка: переднього майданчика гасіння, синхроімпульсу, проміжного майданчика, 10 періодів колірного спалаху з автоматичним перемиканням фази маятника Бруха (`±135°`), заднього майданчика та 8 активних колірних смуг EBU (White 75%, Yellow, Cyan, Green, Magenta, Red, Blue, Black).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define PAL_SAMPLE_RATE_HZ 17734475.0
#define PAL_LINE_SAMPLES    1135
#define PAL_F_SC_HZ        4433618.75
#define PI                 3.14159265358979323846

/* Рівні напруги у квантах 8-бітного ЦАП */
#define DAC_SYNC_TIP       0
#define DAC_BLANKING       73
#define DAC_WHITE_100      255
#define DAC_BURST_AMP      36

/* Структура параметрів однієї кольорової смуги (75% EBU) */
typedef struct {
    float y_norm;      /* Нормована яскравість 0.0 .. 1.0 */
    float u_norm;      /* Компонент U */
    float v_norm;      /* Компонент V */
} ColorBarEBU;

static const ColorBarEBU EBU_BARS[8] = {
    { 0.75f,  0.000f,  0.000f }, /* Білий 75% */
    { 0.64f, -0.327f,  0.075f }, /* Жовтий */
    { 0.53f,  0.110f, -0.461f }, /* Ціан */
    { 0.41f, -0.217f, -0.386f }, /* Зелений */
    { 0.34f,  0.217f,  0.386f }, /* Пурпур */
    { 0.23f, -0.110f,  0.461f }, /* Червоний */
    { 0.11f,  0.327f, -0.075f }, /* Синій */
    { 0.00f,  0.000f,  0.000f }  /* Чорний */
};

/* Генерація одного телевізійного рядка PAL CVBS у буфер ЦАП */
void generate_pal_cvbs_line(uint8_t *buffer, uint32_t line_number) {
    bool is_v_inverted = (line_number % 2 != 0);
    double omega_sc = 2.0 * PI * PAL_F_SC_HZ / PAL_SAMPLE_RATE_HZ;
    double burst_phase_offset = is_v_inverted ? (3.0 * PI / 4.0) : (-3.0 * PI / 4.0);

    /* Часові межі у відліках (за Fs = 17.734475 МГц):
       Front Porch: 0..27 (1.5 мкс)
       Sync Tip:    27..110 (4.7 мкс)
       Breezeway:   110..126 (0.9 мкс)
       Color Burst: 126..170 (2.5 мкс, 10 періодів)
       Back Porch:  170..213 (2.4 мкс)
       Active Area: 213..1135 (52.0 мкс) */
    const uint32_t idx_sync_start  = 27;
    const uint32_t idx_sync_end    = 110;
    const uint32_t idx_burst_start = 126;
    const uint32_t idx_burst_end   = 170;
    const uint32_t idx_active_start = 213;

    for (uint32_t i = 0; i < PAL_LINE_SAMPLES; ++i) {
        if (i < idx_sync_start) {
            buffer[i] = DAC_BLANKING; /* Передній майданчик гасіння */
        } else if (i < idx_sync_end) {
            buffer[i] = DAC_SYNC_TIP; /* Рядковий синхроімпульс */
        } else if (i < idx_burst_start) {
            buffer[i] = DAC_BLANKING; /* Проміжний майданчик Breezeway */
        } else if (i < idx_burst_end) {
            /* Колірний спалах (Colorburst) на рівні гасіння */
            double burst_val = DAC_BURST_AMP * sin(omega_sc * (double)i + burst_phase_offset);
            int32_t sample = (int32_t)(DAC_BLANKING + burst_val + 0.5);
            buffer[i] = (uint8_t)(sample < 0 ? 0 : (sample > 255 ? 255 : sample));
        } else if (i < idx_active_start) {
            buffer[i] = DAC_BLANKING; /* Залишок заднього майданчика */
        } else {
            /* Активне відео: 8 смуг */
            uint32_t active_idx = i - idx_active_start;
            uint32_t bar_width = (PAL_LINE_SAMPLES - idx_active_start) / 8;
            uint32_t bar_idx = active_idx / bar_width;
            if (bar_idx > 7) bar_idx = 7;

            const ColorBarEBU *bar = &EBU_BARS[bar_idx];
            double y_dac = DAC_BLANKING + bar->y_norm * (DAC_WHITE_100 - DAC_BLANKING);

            /* Модуляція піднесучої: C(t) = U·sin(ωt) ± V·cos(ωt) */
            double v_sign = is_v_inverted ? -1.0 : 1.0;
            double u_mod = bar->u_norm * sin(omega_sc * (double)i);
            double v_mod = v_sign * bar->v_norm * cos(omega_sc * (double)i);
            double chroma_dac = (u_mod + v_mod) * (DAC_WHITE_100 - DAC_BLANKING);

            int32_t total_val = (int32_t)(y_dac + chroma_dac + 0.5);
            buffer[i] = (uint8_t)(total_val < 0 ? 0 : (total_val > 255 ? 255 : total_val));
        }
    }
}
```
```cpp
#include <cstdint>
#include <vector>
#include <array>
#include <cmath>
#include <numbers>
#include <span>
#include <algorithm>

class PalCvbsSynthesizer {
public:
    static constexpr double SampleRateHz = 17734475.0;
    static constexpr std::size_t LineSamples = 1135;
    static constexpr double SubcarrierFreqHz = 4433618.75;

    static constexpr uint8_t DacSyncTip   = 0;
    static constexpr uint8_t DacBlanking  = 73;
    static constexpr uint8_t DacWhite100  = 255;
    static constexpr double  DacBurstAmp  = 36.0;

    struct ColorBar {
        float yNorm;
        float uNorm;
        float vNorm;
    };

    static constexpr std::array<ColorBar, 8> EbuBars {{
        { 0.75f,  0.000f,  0.000f }, // Білий 75%
        { 0.64f, -0.327f,  0.075f }, // Жовтий
        { 0.53f,  0.110f, -0.461f }, // Ціан
        { 0.41f, -0.217f, -0.386f }, // Зелений
        { 0.34f,  0.217f,  0.386f }, // Пурпур
        { 0.23f, -0.110f,  0.461f }, // Червоний
        { 0.11f,  0.327f, -0.075f }, // Синій
        { 0.00f,  0.000f,  0.000f }  // Чорний
    }};

    void generateLine(std::span<uint8_t, LineSamples> buffer, std::uint32_t lineNumber) const {
        const bool isVInverted = (lineNumber % 2 != 0);
        const double omegaSc = 2.0 * std::numbers::pi * SubcarrierFreqHz / SampleRateHz;
        const double burstPhaseOffset = isVInverted ? (3.0 * std::numbers::pi / 4.0) : (-3.0 * std::numbers::pi / 4.0);

        constexpr std::size_t SyncStart   = 27;
        constexpr std::size_t SyncEnd     = 110;
        constexpr std::size_t BurstStart  = 126;
        constexpr std::size_t BurstEnd    = 170;
        constexpr std::size_t ActiveStart = 213;

        for (std::size_t i = 0; i < LineSamples; ++i) {
            if (i < SyncStart) {
                buffer[i] = DacBlanking;
            } else if (i < SyncEnd) {
                buffer[i] = DacSyncTip;
            } else if (i < BurstStart) {
                buffer[i] = DacBlanking;
            } else if (i < BurstEnd) {
                const double burstVal = DacBurstAmp * std::sin(omegaSc * static_cast<double>(i) + burstPhaseOffset);
                buffer[i] = clampDac(static_cast<int32_t>(DacBlanking + burstVal + 0.5));
            } else if (i < ActiveStart) {
                buffer[i] = DacBlanking;
            } else {
                const std::size_t activeIdx = i - ActiveStart;
                const std::size_t barWidth = (LineSamples - ActiveStart) / 8;
                const std::size_t barIdx = std::min(activeIdx / barWidth, std::size_t{7});

                const auto& bar = EbuBars[barIdx];
                const double yDac = DacBlanking + bar.yNorm * (DacWhite100 - DacBlanking);

                const double vSign = isVInverted ? -1.0 : 1.0;
                const double uMod = bar.uNorm * std::sin(omegaSc * static_cast<double>(i));
                const double vMod = vSign * bar.vNorm * std::cos(omegaSc * static_cast<double>(i));
                const double chromaDac = (uMod + vMod) * (DacWhite100 - DacBlanking);

                buffer[i] = clampDac(static_cast<int32_t>(yDac + chromaDac + 0.5));
            }
        }
    }

private:
    static constexpr uint8_t clampDac(int32_t value) noexcept {
        return static_cast<uint8_t>(std::clamp(value, int32_t{0}, int32_t{255}));
    }
};
```
:::

### Організація потокового виведення через DMA

Для безперервної передачі відеопотоку без затримок процесора застосовується механізм прямого доступу до пам'яті (DMA) у режимі кільцевого подвійного буфера (*ping-pong double buffering*):
1. **Буфер А та Буфер Б.** Виділяються два масиви в оперативній пам'яті завширшки `1135 байтів` кожен.
2. **Переривання DMA Half-Transfer та Transfer-Complete.** Поки контролер DMA передає відліки з Буфера А до регістра ЦАП, процесорне ядро обчислює та заповнює Буфер Б даними наступного телевізійного рядка.
3. **Автоматичне перемикання дескрипторів.** Після завершення рядка контролер DMA безшовно перемикається на Буфер Б, генеруючи переривання, за яким процесор переходить до формування наступного рядка в Буфері А.

Така організація гарантує абсолютну відсутність джитера (тремтіння тактової частоти) у вихідному аналоговому сигналі, оскільки кожен такт видачі відліку тактується апаратним таймером ЦАП.

### Апаратна обв'язка та аналогове узгодження

Для перетворення розрахованих цифрових відліків на якісний аналоговий сигнал необхідне коректне апаратне узгодження вихідного каскаду.

#### 1. Аналоговий фільтр відновлення (Reconstruction LPF)
На виході ЦАП східчаста форма напруги створює дзеркальні гармоніки навколо тактової частоти `F[s] ± f`. Для їх придушення встановлюється активний аналоговий фільтр низьких частот (наприклад, 5-го порядку Чебишова або Баттерворта на базі швидкісного операційного підсилювача з частотою одиничного підсилення `f[T] > 100 МГц`) із частотою зрізу `6.0 МГц`. Нерівномірність групового часу запізнення в смузі `0 – 5.0 МГц` не повинна перевищувати `±30 нс`.

Крім того, процес вибірки-зберігання (ZOH, *Zero-Order Hold*) вносить природний спад амплітудно-частотної характеристики за законом `sinc(π·f / F[s])`. На частоті піднесучої `4.43 МГц` затухання становить близько `-0.9 дБ`. Для компенсації цього спаду в аналоговий фільтр вбудовують коригувальну диференціюючу RC-ланку (*sinc peaking equalizer*), яка піднімає АЧХ на високих частотах.

#### 2. Схема узгодження 75-омної лінії (Back-termination)
Вихід підсилювача з'єднується з коаксіальним роз'ємом через послідовний резистор номіналом ровно `75.0 Ом` (`1%`). 

При підключенні приймача з вхідним опором `75 Ом` утворюється дільник напруги `1:2`:

```
V[load] = V[source] · (75 Ом / (75 Ом + 75 Ом)) = 0.5 · V[source]
```

Тому вихідний підсилювач повинен генерувати подвоєний розмах напруги `2.0 В Vpp` (від `0.0 В` до `2.0 В`), щоб на навантаженні отримати стандартні `1.0 В Vpp`. Послідовний резистор `75 Ом` поглинає будь-які хвильові відбиття від кінця кабелю, повністю усуваючи повторні контури (гостинг / двоїння зображення) на екрані монітора.

### Контроль якості та налагодження

Налагодження синтезатора виконується у два етапи:
1. **Контроль форми сигналу осцилографом.** Перевіряється розмах напруги: дно синхроімпульсу повинно знаходитися строго на рівні `0.00 В`, рівень гасіння — `0.286 В`, розмах колірного спалаху — від `0.143 В` до `0.429 В`, а пік білого — `1.00 В`. Тривалість імпульсу синхронізації має становити `4.7 ± 0.2 мкс`.
2. **Контроль векторскопом.** Під час відображення колірних смуг вектори всіх 6 кольорів (жовтий, ціан, зелений, маджента, червоний, синій) повинні розташовуватися строго у відповідних секторах векторскопа, а фаза спалаху повинна чітко коливатися між кутами `+135°` та `-135°` без тремтіння та дрейфу амплітуди.
