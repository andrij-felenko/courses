# ⚙️ Реалізація конвертера RGB ↔ YCbCr на цілочисельній арифметиці

Конверсія колірних форматів між RGB24 та YCbCr у реальному часі зіштовхується з високим обчислювальним навантаженням математики з плаваючою комою, що робить критичною низькорівневу оптимізацію на цілочисельній арифметиці з фіксованою комою (*fixed-point arithmetic*). Для досягнення максимальної продуктивності на процесорах без FPU або у високочастотних обробниках відеокадрів застосовують цілочисельний формат Q16.16, масштабування бітовими зсувами, урахування кроку пам'яті (*stride/pitch*) та SIMD-векторизацію в реалізаціях мовами C та C++.

### 1. Архітектурні виклики обробки відео та вибір розрядності Q16.16

Обробка сучасних відеопотоків роздільної здатності 4K (3840×2160 пікселів) із частотою 60 кадрів на секунду вимагає обчислення та перезапису понад 497 мільйонів окремих колірних компонентів щосекунди. Застосування математичних операцій із плаваючою комою одиничної чи подвійної точності (`float` або `double`) створює критичні затримки в конвеєрі обробки зображень. По-перше, виконання дійсного множення й додавання у математичному співпроцесорі (FPU) вимагає більше тактів, ніж цілочисельні інструкції ALU. По-друге, неперервна конверсія цілочисельних відліків із сенсора камери у дійсний формат і зворотне перетворення у цілі числа `uint8_t` для фреймбуфера генерують значні накладні витрати на такти процесора.

Для усунення дійсної арифметики в обчисленнях застосовується метод масштабування коефіцієнтів матриці на цілочисельну константу ступеня двійки `2^N`. Формат **Q16.16** означає, що 32-бітне ціле число зі знаком (`int32_t`) розбивається на дві рівні частини: 16 старших бітів відводяться під цілу частину числа, а 16 молодших бітів — під дробову частину. 

Множником для переведення дійсного коефіцієнта у формат Q16.16 є значення `2^16 = 65536`:

```
K_fixed = round(K_float · 65536)
```

Приклад розрахунку коефіцієнтів прямими матричними рівняннями ITU-R BT.601 Full Range для компонента яркості `Y`:
- Дійсна формула: `Y = 0.299000·R + 0.587000·G + 0.114000·B`
- Коефіцієнт червоного: `round(0.299000 · 65536) = 19595`
- Коефіцієнт зеленого: `round(0.587000 · 65536) = 38470`
- Коефіцієнт синього: `round(0.114000 · 65536) = 7471`

Після виконання цілочисельного множення `19595·R + 38470·G + 7471·B` результат ділиться на 65536 за допомогою швидкого бітового зсуву вправо `>> 16`. Вибір саме 16-бітного зсуву є математично оптимальним компромісом: він гарантує похибку обчислення колірності менше 0.5 LSB (найменшого значущого біта), що є абсолютно невидимим для людського ока, і водночас захищає 32-бітний акумулятор від цілочисельного переповнення, оскільки максимальна сума `255·(19595 + 38470 + 7471) = 16711680` вільно вміщується у діапазон signed 32-bit integer (`2147483647`).

### 2. Урахування кроку рядка пам'яті (Stride/Pitch) та вирівнювання

У реальних графічних системах (V4L2, DirectShow, FFmpeg, VA-API) растрові кадри зображень рідко зберігаються у пам'яті як суцільний неперервний масив байтів. Через вимоги швидкого прямого доступу до пам'яті (DMA) та кеш-ліній процесора (64 байти), довжина кожного рядка кадру вирівнюється по межі 64, 128 або 256 байтів.

Фактична довжина рядка у пам'яті називається **кроком рядка (*stride* або *pitch*)**. Наприклад, для відеокадру роздільністю 1920×1080 пікселів ширина кадру становить 1920 байтів, але крок рядка в пам'яті може дорівнювати 2048 байтам. Останні 128 байтів кожного рядка є вирівнювальним заповненням (*padding*), яке не містить піксельних даних.

Ігнорування параметра `stride` при обробці буферів призводить до фатального зсуву зображення по діагоналі або виходу за межі виділеної пам'яті (*segmentation fault*). Тому професійний алгоритм конверсії завжди приймає окремі параметри `stride` для кожного колірного каналу.

### 3. Захист від переповнення та обрізання діапазонів (Clamping)

Через обрізання дробової частини при бітових зсувах та апроксимацію обернених матриць, під час зворотного перетворення `YCbCr → RGB` результат математичного розрахунку для деяких крайніх пікселів може вийти за межі допустимого 8-бітного діапазону `[0, 255]`. Наприклад, насичений синій або червоний колір може обчислитися як `-12` або `268`.

Запис таких значень у змінну типу `uint8_t` без перевірки викликає цілочисельне циклічне переповнення: значення `268` перетвориться на `12` (темний колір замість яскравого), викликаючи ефектні, але руйнівні колірні артефакти на екрані.

Для запобігання переповненню застосовується операція затискання (*saturating / clamping*):

```
val = min(max(val, 0), 255)
```

У C-версії застосовується швидка інлайн-функція або LUT-таблиця, а в сучасній C++20 використовується стандартний алгоритм `std::clamp`.

### 4. Вихідний код реалізації конвертера

Нижче наведено робочі реалізації прямого та зворотного перетворень для стандарту BT.601 Full Range із підтримкою кроку рядка пам'яті.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stddef.h>

/* Коефіцієнти BT.601 Full Range у форматі Q16.16 (масштаб 65536) */
#define FIX_Y_R  19595  /*  0.299000 * 65536 */
#define FIX_Y_G  38470  /*  0.587000 * 65536 */
#define FIX_Y_B   7471  /*  0.114000 * 65536 */

#define FIX_CB_R -11058 /* -0.168736 * 65536 */
#define FIX_CB_G -21710 /* -0.331264 * 65536 */
#define FIX_CB_B  32768 /*  0.500000 * 65536 */

#define FIX_CR_R  32768 /*  0.500000 * 65536 */
#define FIX_CR_G -27439 /* -0.418688 * 65536 */
#define FIX_CR_B  -5329 /* -0.081312 * 65536 */

/* Коефіцієнти зворотного перетворення BT.601 Full Range Q16.16 */
#define FIX_INV_CR_R  91881  /*  1.402000 * 65536 */
#define FIX_INV_CB_G -22554  /* -0.344136 * 65536 */
#define FIX_INV_CR_G -46802  /* -0.714136 * 65536 */
#define FIX_INV_CB_B 116130  /*  1.772000 * 65536 */

static inline uint8_t clamp_u8(int32_t val) {
    if (val < 0) return 0;
    if (val > 255) return 255;
    return (uint8_t)val;
}

/* Конверсія упакованого буфера RGB24 -> YCbCr444 з урахуванням кроку stride */
void rgb24_to_ycbcr444_c(const uint8_t* rgb, size_t rgb_stride,
                         uint8_t* y_plane, size_t y_stride,
                         uint8_t* cb_plane, size_t cb_stride,
                         uint8_t* cr_plane, size_t cr_stride,
                         size_t width, size_t height)
{
    for (size_t y = 0; y < height; ++y) {
        const uint8_t* rgb_row = rgb + y * rgb_stride;
        uint8_t* y_row  = y_plane + y * y_stride;
        uint8_t* cb_row = cb_plane + y * cb_stride;
        uint8_t* cr_row = cr_plane + y * cr_stride;

        for (size_t x = 0; x < width; ++x) {
            int32_t r = rgb_row[x * 3 + 0];
            int32_t g = rgb_row[x * 3 + 1];
            int32_t b = rgb_row[x * 3 + 2];

            int32_t luma = (FIX_Y_R * r + FIX_Y_G * g + FIX_Y_B * b) >> 16;
            int32_t cb   = ((FIX_CB_R * r + FIX_CB_G * g + FIX_CB_B * b) >> 16) + 128;
            int32_t cr   = ((FIX_CR_R * r + FIX_CR_G * g + FIX_CR_B * b) >> 16) + 128;

            y_row[x]  = clamp_u8(luma);
            cb_row[x] = clamp_u8(cb);
            cr_row[x] = clamp_u8(cr);
        }
    }
}

/* Конверсія YCbCr444 -> упакований буфер RGB24 */
void ycbcr444_to_rgb24_c(const uint8_t* y_plane, size_t y_stride,
                         const uint8_t* cb_plane, size_t cb_stride,
                         const uint8_t* cr_plane, size_t cr_stride,
                         uint8_t* rgb, size_t rgb_stride,
                         size_t width, size_t height)
{
    for (size_t y = 0; y < height; ++y) {
        const uint8_t* y_row  = y_plane + y * y_stride;
        const uint8_t* cb_row = cb_plane + y * cb_stride;
        const uint8_t* cr_row = cr_plane + y * cr_stride;
        uint8_t* rgb_row = rgb + y * rgb_stride;

        for (size_t x = 0; x < width; ++x) {
            int32_t luma = y_row[x];
            int32_t cb   = (int32_t)cb_row[x] - 128;
            int32_t cr   = (int32_t)cr_row[x] - 128;

            int32_t r = luma + ((FIX_INV_CR_R * cr) >> 16);
            int32_t g = luma + ((FIX_INV_CB_G * cb + FIX_INV_CR_G * cr) >> 16);
            int32_t b = luma + ((FIX_INV_CB_B * cb) >> 16);

            rgb_row[x * 3 + 0] = clamp_u8(r);
            rgb_row[x * 3 + 1] = clamp_u8(g);
            rgb_row[x * 3 + 2] = clamp_u8(b);
        }
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <algorithm>
#include <stdexcept>

namespace color_space {

constexpr int32_t kFixY_R  = 19595;
constexpr int32_t kFixY_G  = 38470;
constexpr int32_t kFixY_B  = 7471;

constexpr int32_t kFixCb_R = -11058;
constexpr int32_t kFixCb_G = -21710;
constexpr int32_t kFixCb_B = 32768;

constexpr int32_t kFixCr_R = 32768;
constexpr int32_t kFixCr_G = -27439;
constexpr int32_t kFixCr_B = -5329;

constexpr int32_t kFixInvCr_R = 91881;
constexpr int32_t kFixInvCb_G = -22554;
constexpr int32_t kFixInvCr_G = -46802;
constexpr int32_t kFixInvCb_B = 116130;

struct YCbCrBufferView {
    std::span<const uint8_t> y_plane;
    std::span<const uint8_t> cb_plane;
    std::span<const uint8_t> cr_plane;
    size_t y_stride{0};
    size_t cb_stride{0};
    size_t cr_stride{0};
    size_t width{0};
    size_t height{0};
};

class ColorConverter {
public:
    static void convert_rgb_to_ycbcr(std::span<const uint8_t> rgb_data, size_t rgb_stride,
                                     std::span<uint8_t> y_plane, size_t y_stride,
                                     std::span<uint8_t> cb_plane, size_t cb_stride,
                                     std::span<uint8_t> cr_plane, size_t cr_stride,
                                     size_t width, size_t height)
    {
        if (width == 0 || height == 0) {
            throw std::invalid_argument("Розміри кадру мають бути більшими за нуль");
        }

        for (size_t y = 0; y < height; ++y) {
            auto rgb_row = rgb_data.subspan(y * rgb_stride, width * 3);
            auto y_row   = y_plane.subspan(y * y_stride, width);
            auto cb_row  = cb_plane.subspan(y * cb_stride, width);
            auto cr_row  = cr_plane.subspan(y * cr_stride, width);

            for (size_t x = 0; x < width; ++x) {
                int32_t r = rgb_row[x * 3 + 0];
                int32_t g = rgb_row[x * 3 + 1];
                int32_t b = rgb_row[x * 3 + 2];

                int32_t luma = (kFixY_R * r + kFixY_G * g + kFixY_B * b) >> 16;
                int32_t cb   = ((kFixCb_R * r + kFixCb_G * g + kFixCb_B * b) >> 16) + 128;
                int32_t cr   = ((kFixCr_R * r + kFixCr_G * g + kFixCr_B * b) >> 16) + 128;

                y_row[x]  = static_cast<uint8_t>(std::clamp(luma, 0, 255));
                cb_row[x] = static_cast<uint8_t>(std::clamp(cb, 0, 255));
                cr_row[x] = static_cast<uint8_t>(std::clamp(cr, 0, 255));
            }
        }
    }

    static void convert_ycbcr_to_rgb(const YCbCrBufferView& view,
                                     std::span<uint8_t> rgb_out, size_t rgb_stride)
    {
        for (size_t y = 0; y < view.height; ++y) {
            auto y_row   = view.y_plane.subspan(y * view.y_stride, view.width);
            auto cb_row  = view.cb_plane.subspan(y * view.cb_stride, view.width);
            auto cr_row  = view.cr_plane.subspan(y * view.cr_stride, view.width);
            auto rgb_row = rgb_out.subspan(y * rgb_stride, view.width * 3);

            for (size_t x = 0; x < view.width; ++x) {
                int32_t luma = y_row[x];
                int32_t cb   = static_cast<int32_t>(cb_row[x]) - 128;
                int32_t cr   = static_cast<int32_t>(cr_row[x]) - 128;

                int32_t r = luma + ((kFixInvCr_R * cr) >> 16);
                int32_t g = luma + ((kFixInvCB_G * cb + kFixInvCr_G * cr) >> 16);
                int32_t b = luma + ((kFixInvCb_B * cb) >> 16);

                rgb_row[x * 3 + 0] = static_cast<uint8_t>(std::clamp(r, 0, 255));
                rgb_row[x * 3 + 1] = static_cast<uint8_t>(std::clamp(g, 0, 255));
                rgb_row[x * 3 + 2] = static_cast<uint8_t>(std::clamp(b, 0, 255));
            }
        }
    }
};

} // namespace color_space
```
:::

### 5. Апаратна векторизація SIMD (AVX2 та ARM NEON)

Попоіксельна обробка у звичайному скалярному циклі CPU, навіть із використанням фіксованої коми, обробляє лише один піксель за такт. Сучасні центральні процесори містять розширення SIMD (*Single Instruction, Multiple Data*), які дозволяють виконувати паралельну конверсію 8 або 16 пікселів за одну векторну інструкцію:

1. **x86_64 AVX2 / SSSE3:** Інструкція `_mm_maddubs_epi16` за один такт обчислює суму добутків знакових та беззнакових 8-бітних чисел, виконуючи матричне множення `RGB` на вагові коефіцієнти. Інструкція `_mm_packus_epi16` здійснює апаратне затискання з насиченням (*saturate*) 16-бітних результатів у 8-бітні значення без використання умовних розгалужень `if`.
2. **ARM NEON:** На процесорах смартфонів та комп'ютерів Apple Silicon застосовується інструкція `vmlal.u8` (векторне множення з накопиченням розширеної точності) та `vqrshrun.s16` (арифетичний зсув зі зведенням та насиченням). Це забезпечує обробку відеопотоків 4K 60fps на мобільних пристроях із мінімальним енергоспоживанням.
