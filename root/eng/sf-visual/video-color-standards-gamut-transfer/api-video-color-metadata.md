# 📋 Структура метаданих колірних просторів у відеопотоках

Довідкова вставка описує синтаксис, структуру та формати метаданих колірних просторів (Video Usability Information, VUI), що впроваджуються у заголовки елементарних бітових потоків та контейнери відеокодеків H.264, H.265 (HEVC), AV1 та VP9. Вводу цих даних присвячено окремий розбір, оскільки неправильно зчитаний прапор у заголовку потоку призводить до спотворення кольорів на екрані пристрою (неконтрольоване перенасичення червоного Red Crush, блідий контраст, зсув типом гамми) навіть при ідеально декодованій матриці пікселів.

Вставка описує числові константи стандартів ISO/IEC 23001-8 / ITU-T H.273, додаткові метадані розширеного динамічного діапазону HDR10 (SMPTE ST 2086 / CTA-861.3), поля медіабібліотеки FFmpeg (libavutil / libavcodec), API фреймворку GStreamer, веб-інтерфейси W3C Media Capabilities та параметри CLI-команд для перекодування медіафайлів.

## 1. Специфікація параметрів колірності ITU-T H.273 / VUI

У бітових потоках сучасних відеокодеків H.264 та H.265 структура VUI упаковується всередину заголовка SPS (Sequence Parameter Set). Послідовне зчитування синтаксичних елементів починається після активації прапорців `vui_parameters_present_flag`, `video_signal_type_present_flag` та `colour_description_present_flag`. Якщо дані прапорці відсутні у бітовому потоці, декодер не має права вгадувати параметри випадковим чином, а зобов'язаний застосовувати стандартизовані правила за замовчуванням: для відео високої чіткості HD приймаються параметри BT.709 з обмеженим діапазоном, а для відео стандартної чіткості SD — параметри BT.601.

Власне опис колірності (Color Description Triple) складається з трьох числових байтів та одного прапора амплітудного розмаху.

### 1.1. Color Primaries (`color_primaries`)

Визначає хроматичні координати `(x, y)` червоного, зеленого, синього первинних випромінювачів та реперної точки білого світла (D65 або C) на колірній діаграмі CIE 1931. Цей параметр задає кути трикутника колірного охоплення, у межах якого дисплей малює усі можливі колірні відтінки. Вибір стандарту `color_primaries` прямо впливає на точність рендерингу людського тону шкіри, природних пейзажів та насичених світлових спецефектів.

| Значення (Enum) | Назва стандарту | Базове застосування | Координати R (x, y) | Координати G (x, y) | Координати B (x, y) | Точка білого |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **BT.709** | HDTV, sRGB, Веб | (0.640, 0.330) | (0.300, 0.600) | (0.150, 0.060) | D65 (0.3127, 0.3290) |
| **2** | **Unspecified** | Невизначено | — | — | — | — |
| **4** | **BT.470M** | NTSC (1953) | (0.670, 0.330) | (0.210, 0.710) | (0.140, 0.080) | C (0.3101, 0.3162) |
| **5** | **BT.601 PAL** | PAL / SECAM SD | (0.640, 0.330) | (0.290, 0.600) | (0.150, 0.060) | D65 (0.3127, 0.3290) |
| **6** | **BT.601 NTSC** | NTSC SD (SMPTE 170M) | (0.630, 0.340) | (0.310, 0.595) | (0.155, 0.070) | D65 (0.3127, 0.3290) |
| **9** | **BT.2020** | UHDTV, 4K/8K HDR | (0.708, 0.292) | (0.170, 0.797) | (0.131, 0.046) | D65 (0.3127, 0.3290) |
| **10** | **SMPTE 431** | DCI-P3 (Кіно) | (0.680, 0.320) | (0.265, 0.690) | (0.150, 0.060) | Театральний білий |
| **11** | **SMPTE 432** | Display P3 (Apple) | (0.680, 0.320) | (0.265, 0.690) | (0.150, 0.060) | D65 (0.3127, 0.3290) |

Координати первинних випромінювачів задають колориметричний багет. Якщо відтворити кадр із кодом `color_primaries=9` (BT.2020) на звичайному sRGB-моніторі без попереднього матричного перерахунку первинних координат (Gamut Mapping), кольори будуть виглядати катастрофічно тьмяними та блідими, оскільки монітор физично не зможе випромінювати лазерні довжини хвиль стандарту BT.2020. Для коректного відображення на SDR-екрані декодер виконує 3D LUT стиснення колірного об'єму.

### 1.2. Transfer Characteristics (`transfer_characteristics`)

Визначає неколінійну електрооптичну функцію передачі (EOTF) чи оптоелектронну функцію (OETF), яка вирівнює рівні цифрового сигналу з інтенсивністю випромінювання екрана. Ця функція компенсує неколінійну чутливість людського ока. Застосування правильної кривої гамми є ключовим для запобігання втрати розрізнення у глибоких тінях та відсутності сходинок квантування на яскравих обличчях.

| Значення (Enum) | Назва функції | Опис та застосування |
| :--- | :--- | :--- |
| **1** | **BT.709** | Стандартна крива SDR (степенева функція `γ ≈ 1.96` з лінійною ділянкою біля нуля) |
| **2** | **Unspecified** | Невизначено (за замовчуванням приймається BT.709 для HD або BT.601 для SD) |
| **4** | **Gamma 2.2** | Степенева крива `γ = 2.2` (старі монітори NTSC / PC) |
| **5** | **Gamma 2.8** | Степенева крива `γ = 2.8` (старі ТБ PAL / SECAM) |
| **6** | **BT.601** | Еквівалентно BT.709 для відео стандартної чіткості |
| **13** | **sRGB** | Крива sRGB (веб-графіка, близька до Gamma 2.2 з коротким лінійним хвостом) |
| **16** | **SMPTE ST 2084** | **PQ (Perceptual Quantizer)** — HDR10 / Dolby Vision (абсолютна шкала до 10 000 ніт) |
| **18** | **ARIB STD-B67** | **HLG (Hybrid Log-Gamma)** — відносна шкала HDR для ефірного ТБ |

Функція передачі є ключовим роздільником між SDR та HDR відеоконтентом. Для стандартного SDR значення `1` або `6` задає відносну шкалу яскравості від 0 до 100%, тоді як значення `16` (PQ) визначає абсолютні ніти (калібровану яскравість від 0.0001 до 10 000 ніт). Помилка в описі перехідної характеристики призводить до суттєвих темних або пересвічених спотворень гами (Gamma Shift).

### 1.3. Matrix Coefficients (`matrix_coefficients`)

Визначає конкретну лінійну матрицю, використану для перетворення R'G'B' у Luma/Chroma (Y'CbCr). Цей параметр інформує декодер про те, які саме вагові коефіцієнти яркості `W_R, W_G, W_B` використовувалися під час підготовки відеопотоку.

| Значення (Enum) | Назва матриці | Опис вагових коефіцієнтів Y' |
| :--- | :--- | :--- |
| **0** | **RGB / GBR** | Прямий простір RGB (без матрицювання, `Y=G, Cb=B, Cr=R`) |
| **1** | **BT.709** | `Y' = 0.2126·R' + 0.7152·G' + 0.0722·B'` (HDTV) |
| **5 / 6** | **BT.601** | `Y' = 0.2990·R' + 0.5870·G' + 0.1140·B'` (SDTV PAL/NTSC) |
| **9** | **BT.2020 NCL** | `Y' = 0.2627·R' + 0.6780·G' + 0.0593·B'` (UHDTV нелінійне матрицювання) |
| **10** | **BT.2020 CL** | Лінійне матрицювання BT.2020 (у лінійному світловому просторі RGB) |

Застосування невідповідної матриці викликає хроматичні зміщення. Якщо кадр, задований коефіцієнтами BT.709 (`matrix_coefficients=1`), проігнорувати і декодувати за коефіцієнтами BT.601, на екрані з'явиться шкідливе перенасичення червоних тонів (Red Crush) та розмиття зеленого тла.

### 1.4. Full Range Flag (`full_range_flag` / `color_range`)

Визначає квантувальний амплітудний розмах цифрових відліків у піксельному буфері.

* **`0` (Limited / Studio Range):** Y' в межах `16..235`, Cb/Cr в межах `16..240` (для 8 біт). Збережено інженерний Footroom (0..15) та Headroom (236..255) для відсікання аналогових шумів та перерегулювання ФНЧ.
* **`1` (Full Range):** Y', Cb, Cr в межах `0..255` (для 8 біт). Призначено для комп'ютерної графіки, фотографій та комп'ютерних моніторів.

При плутанині даного прапора виникають наймасовіші скарги користувачів на якість відтворення: зображення стає або вицвілим сірим (Limited відтворено як Full), або втрачає деталі у тінях та світлих ділянках через жорсткий кліпінг (Full відтворено як Limited).

## 2. Положення колірних відліків (Chroma Sample Location)

При кодуванні у форматі субдискретизації 4:2:0 відліки колірності `Cb` та `Cr` піддаються просторовому проріджуванню в 2 рази по горизонталі та вертикалі. Синтаксичний елемент `chroma_sample_loc_type` описує фазовий зсув сітки колірності відносно пікселів яркості `Y`:

1. **`0` (Left / MPEG-2):** Відліки колірності вирівняні по вертикалі з лівим стовпчиком пікселів яркості у блоці 2×2. Стандарт для цифрового ТБ та кодеків H.264 / H.265.
2. **`1` (Center / JPEG):** Відліки колірності розташовані строго в геометричному центрі блоку 2×2 пікселів яркості. Стандарт для фотографій JPEG та відеокодека WebP.
3. **`2` (Top-Left):** Відліки колірності суміщені з верхнім лівим пікселем яркості.
4. **`3` (Top-Center):** Вирівнювання по верхній межі та центру.

Нехтування цим параметром під час інтерполяції (упсамплінгу) колірних площин викликає мікроскопічний просторовий зсув колірних меж на половину пікселя, що створює ефект колірного розмиття (chroma bleeding) на текст та контрастні контури.

## 3. Статичні метадані HDR (SMPTE ST 2086 та CTA-861.3)

Для відеопотоків розширеного динамічного діапазону (HDR10) метадані передаються через SEI-повідомлення (Supplemental Enhancement Information) контейнера або потоку.

### 3.1. Mastering Display Color Volume (SMPTE ST 2086)

Описує колірні можливості еталонного студійного монітора, на якому виконувався фінальний колірокорекційний монтаж (grading) фільму:

* `display_primaries`: Хроматичні координати `(x, y)` R, G, B каліброваного дисплея (з точністю 0.00002).
* `white_point`: Хроматичні координати точки білого еталонного дисплея.
* `max_display_mastering_luminance`: Максимальна яскравість монітора в нітах (cd/m²), наприклад 1000 ніт або 4000 ніт.
* `min_display_mastering_luminance`: Мінімальна яскравість монітора в нітах, наприклад 0.005 ніт.

### 3.2. Content Light Level Information (CTA-861.3)

Описує статистики яркості безпосередньо самого контенту для налаштування тономапінгу (Tone Mapping) на споживчому телевізорі:

* `MaxCLL` (Maximum Content Light Level): Яскравість найяскравішого поодинокого пікселя в усьому відеофільмі (у нітах).
* `MaxFALL` (Maximum Frame-Average Light Level): Максимальна середня яскравість серед усіх кадрів відеофільму (у нітах).

Ці параметри дозволяють дисплею з обмеженою піковою яскравістю (наприклад, OLED-телевізору на 700 ніт) інтелектуально стискати динамічний діапазон кадру 1000 чи 4000 ніт без зрізання деталей у світлих зонах.

## 4. Бітова упаковка VUI у заголовку SPS кодека H.264

Структура VUI упаковується в елементарний бітовий потік H.264 за допомогою безнаправленого кодування експоненційним кодом Голомба (ue(v)) та побітових прапорців u(1). Нижче наведено структуру зчитування NAL-юніта SPS:

:::tabs
```c
/* c */
void parse_vui_parameters(BitReader *br, VUIParameters *vui) {
    vui->aspect_ratio_info_present_flag = read_bits(br, 1);
    if (vui->aspect_ratio_info_present_flag) {
        vui->aspect_ratio_idc = read_bits(br, 8);
        if (vui->aspect_ratio_idc == Extended_SAR) {
            vui->sar_width  = read_bits(br, 16);
            vui->sar_height = read_bits(br, 16);
        }
    }
    vui->overscan_info_present_flag = read_bits(br, 1);
    
    vui->video_signal_type_present_flag = read_bits(br, 1);
    if (vui->video_signal_type_present_flag) {
        vui->video_format = read_bits(br, 3);
        vui->video_full_range_flag = read_bits(br, 1);
        vui->colour_description_present_flag = read_bits(br, 1);
        
        if (vui->colour_description_present_flag) {
            vui->colour_primaries         = read_bits(br, 8);
            vui->transfer_characteristics = read_bits(br, 8);
            vui->matrix_coefficients      = read_bits(br, 8);
        }
    }
}
```
```cpp
// cpp
#include <cstdint>

namespace h264 {

struct VUIParameters {
    bool aspect_ratio_info_present{false};
    uint8_t aspect_ratio_idc{0};
    uint16_t sar_width{0};
    uint16_t sar_height{0};
    bool overscan_info_present{false};
    bool video_signal_type_present{false};
    uint8_t video_format{0};
    bool video_full_range{false};
    bool colour_description_present{false};
    uint8_t colour_primaries{2};
    uint8_t transfer_characteristics{2};
    uint8_t matrix_coefficients{2};
};

class BitStreamReader;

VUIParameters parse_vui_parameters_cpp(BitStreamReader& reader) {
    VUIParameters vui;
    vui.aspect_ratio_info_present = (reader.read_bits(1) != 0);
    if (vui.aspect_ratio_info_present) {
        vui.aspect_ratio_idc = static_cast<uint8_t>(reader.read_bits(8));
        if (vui.aspect_ratio_idc == 255 /* Extended_SAR */) {
            vui.sar_width  = static_cast<uint16_t>(reader.read_bits(16));
            vui.sar_height = static_cast<uint16_t>(reader.read_bits(16));
        }
    }
    vui.overscan_info_present = (reader.read_bits(1) != 0);
    vui.video_signal_type_present = (reader.read_bits(1) != 0);
    if (vui.video_signal_type_present) {
        vui.video_format = static_cast<uint8_t>(reader.read_bits(3));
        vui.video_full_range = (reader.read_bits(1) != 0);
        vui.colour_description_present = (reader.read_bits(1) != 0);
        if (vui.colour_description_present) {
            vui.colour_primaries         = static_cast<uint8_t>(reader.read_bits(8));
            vui.transfer_characteristics = static_cast<uint8_t>(reader.read_bits(8));
            vui.matrix_coefficients      = static_cast<uint8_t>(reader.read_bits(8));
        }
    }
    return vui;
}

} // namespace h264
```
:::

Неправильний парсинг безнаправленого поля Голомба зміщує вказівник зчитування бітів, через що усі наступні прапорці розбору кадру стають фальшивими.

## 5. Структури C API у бібліотеці FFmpeg (libavutil)

У медіабібліотеці FFmpeg опис колірного простору декодованого кадру зберігається у структурі `AVFrame` (файл заголовка `<libavutil/pixdesc.h>` та `<libavutil/frame.h>`):

:::tabs
```c
#include <libavutil/frame.h>
#include <libavutil/pixfmt.h>

/* Структура кадру у C API FFmpeg */
typedef struct AVFrame {
    uint8_t *data[AV_NUM_DATA_POINTERS];
    int linesize[AV_NUM_DATA_POINTERS];
    
    int width, height;
    enum AVPixelFormat format; /* наприклад, AV_PIX_FMT_YUV420P */

    /* Метадані колірного простору кадру */
    enum AVColorRange color_range;            /* AVCOL_RANGE_MPEG (Limited) чи AVCOL_RANGE_JPEG (Full) */
    enum AVColorPrimaries color_primaries;    /* AVCOL_PRI_BT709, AVCOL_PRI_BT2020 тощо */
    enum AVColorTransferCharacteristic color_trc; /* AVCOL_TRC_BT709, AVCOL_TRC_SMPTE2084 тощо */
    enum AVColorSpace colorspace;             /* AVCOL_SPC_BT709, AVCOL_SPC_BT2020_NCL тощо */
    
    enum AVChromaLocation chroma_location;   /* AVCHROMA_LOC_LEFT, AVCHROMA_LOC_CENTER */
} AVFrame;
```
```cpp
// cpp
extern "C" {
#include <libavutil/frame.h>
#include <libavutil/pixfmt.h>
}

// У C++20 метадані колірності AVFrame доступні через прямий доступ до полів структури
struct FrameColorMetadata {
    AVColorRange range{AVCOL_RANGE_MPEG};
    AVColorPrimaries primaries{AVCOL_PRI_BT709};
    AVColorTransferCharacteristic trc{AVCOL_TRC_BT709};
    AVColorSpace space{AVCOL_SPC_BT709};

    static FrameColorMetadata extract(const AVFrame& frame) noexcept {
        return FrameColorMetadata{
            .range = frame.color_range,
            .primaries = frame.color_primaries,
            .trc = frame.color_trc,
            .space = frame.colorspace
        };
    }
};
```
:::

Для створення автоматичного обробника колірного перетворення FFmpeg надає API `SwsContext` (бібліотека `libswscale`):

:::tabs
```c
/* c */
#include <libswscale/swscale.h>
#include <libavutil/frame.h>

/**
 * Налаштування конвертера swscale з урахуванням колірних метаданих кадру
 */
struct SwsContext* create_color_converter(const AVFrame *src_frame,
                                           int dst_w, int dst_h,
                                           enum AVPixelFormat dst_fmt)
{
    struct SwsContext *sws_ctx = sws_getContext(
        src_frame->width, src_frame->height, src_frame->format,
        dst_w, dst_h, dst_fmt,
        SWS_BILINEAR, NULL, NULL, NULL
    );

    if (!sws_ctx) return NULL;

    /* Встановлення коефіцієнтів джерела та призначення */
    int src_colorspace = (src_frame->colorspace == AVCOL_SPC_BT2020_NCL) ? SWS_CS_BT2020 : SWS_CS_ITU709;
    int dst_colorspace = SWS_CS_DEFAULT; /* sRGB / BT.709 */

    int src_range = (src_frame->color_range == AVCOL_RANGE_JPEG) ? 1 : 0;
    int dst_range = 1; /* Full range RGB для відображення на моніторі */

    const int *inv_table, *table;
    int src_full, dst_full;
    int brightness, contrast, saturation;

    /* Зчитати поточні коефіцієнти */
    sws_getColorspaceDetails(sws_ctx, (int**)&inv_table, &src_full,
                             (int**)&table, &dst_full,
                             &brightness, &contrast, &saturation);

    inv_table = sws_getCoefficients(src_colorspace);
    table = sws_getCoefficients(dst_colorspace);

    /* Перевизначити матриці та рівні квантування */
    sws_setColorspaceDetails(sws_ctx, inv_table, src_range,
                             table, dst_range,
                             brightness, contrast, saturation);

    return sws_ctx;
}
```
```cpp
// cpp
#include <memory>
#include <stdexcept>
extern "C" {
#include <libswscale/swscale.h>
#include <libavutil/frame.h>
}

namespace media {

struct SwsDeleter {
    void operator()(SwsContext* ptr) const noexcept {
        if (ptr) sws_freeContext(ptr);
    }
};

using UniqueSwsContext = std::unique_ptr<SwsContext, SwsDeleter>;

/**
 * Ідіоматична C++ обгортка над SwsContext з автоматичним керуванням ресурсами (RAII)
 */
class ColorScalePipeline {
public:
    ColorScalePipeline(const AVFrame& src_frame, int dst_width, int dst_height, AVPixelFormat dst_format) {
        SwsContext* ctx = sws_getContext(
            src_frame.width, src_frame.height, src_frame.format,
            dst_width, dst_height, dst_format,
            SWS_BILINEAR, nullptr, nullptr, nullptr
        );

        if (!ctx) {
            throw std::runtime_error("Не вдалося створити SwsContext для колірного перетворення");
        }

        ctx_.reset(ctx);
        configure_color_spaces(src_frame);
    }

    SwsContext* get() const noexcept { return ctx_.get(); }

private:
    void configure_color_spaces(const AVFrame& src_frame) {
        int src_cs = (src_frame.colorspace == AVCOL_SPC_BT2020_NCL) ? SWS_CS_BT2020 : SWS_CS_ITU709;
        int dst_cs = SWS_CS_DEFAULT;

        int src_range = (src_frame.color_range == AVCOL_RANGE_JPEG) ? 1 : 0;
        int dst_range = 1;

        const int *inv_table = sws_getCoefficients(src_cs);
        const int *table = sws_getCoefficients(dst_cs);

        int dummy_src_full, dummy_dst_full;
        int brightness, contrast, saturation;

        sws_getColorspaceDetails(ctx_.get(), const_cast<int**>(&inv_table), &dummy_src_full,
                                 const_cast<int**>(&table), &dummy_dst_full,
                                 &brightness, &contrast, &saturation);

        sws_setColorspaceDetails(ctx_.get(), inv_table, src_range,
                                 table, dst_range,
                                 brightness, contrast, saturation);
    }

    UniqueSwsContext ctx_;
};

} // namespace media
```
:::

## 6. Опис колірності у фреймворку GStreamer (`GstVideoColorimetry`)

У мультимедійному фреймворку GStreamer параметри колірного простору передаються у структурі `caps` каналу зв'язку елементів (пайплайну). Для роботи з ними використовується тип `GstVideoColorimetry`:

:::tabs
```c
/* c */
#include <gst/video/video-color.h>

void parse_colorimetry_c(void) {
    GstVideoColorimetry colorimetry;
    gst_video_colorimetry_from_string(&colorimetry, "2:4:5:1");
}
```
```cpp
// cpp
#include <gst/video/video-color.h>
#include <string_view>
#include <optional>

namespace gst {

std::optional<GstVideoColorimetry> parse_colorimetry(std::string_view colorimetry_str) {
    GstVideoColorimetry colorimetry{};
    if (gst_video_colorimetry_from_string(&colorimetry, colorimetry_str.data())) {
        return colorimetry;
    }
    return std::nullopt;
}

} // namespace gst
```
:::

Фреймворк GStreamer автоматично вставляє плагін `videoconvert` або GPU-елемент `glcolorconvert` при виявленні невідповідності атрибутів `colorimetry` між виходом декодера та входом дисплейного рендерера (наприклад, `xvimagesink` чи `glimagesink`).

## 7. Веб-стандарти W3C та WebRTC

У сучасних веб-браузерах конфігурація колірного простору передається через W3C API `MediaCapabilities` та параметри SDP для сесій WebRTC. Веб-застосунки використовують ці інтерфейси для перевірки апаратної підтримки розширеного динамічного діапазону HDR10 перед запуском відеопотоків надвисокої роздільної здатності.

```javascript
// Перевірка підтримки колірного простору та передавальної функції через W3C Media Capabilities API
navigator.mediaCapabilities.decodingInfo({
    type: 'file',
    videoConfiguration: {
        contentType: 'video/mp4; codecs="av01.0.08M.10"',
        width: 3840,
        height: 2160,
        bitrate: 15000000,
        framerate: 60,
        colorGamut: 'rec2020',
        transferFunction: 'pq',
        hdrMetadataType: 'smpteSt2086'
    }
}).then(result => {
    console.log("HDR BT.2020 підтримка:", result.supported, result.smooth);
});
```

У WebRTC параметри `colorSpace` передаються всередині заголовків RTP за допомогою розширення `urn:ietf:params:rtp-hdrext:video-color-space`. Це дозволяє приймачу WebRTC динамічно налаштовувати апаратні шейдери перетворення `YUV -> RGB` без розриву з'єднання при зміні джерела відеокамери.

## 8. Прапори CLI-інструментів FFmpeg для керування колірністю

При транскодуванні медіафайлів інструментом `ffmpeg` метадані колірності можна примусово зафіксувати або виправити за допомогою відповідних ключів CLI. Це дозволяє усунути помилки невірного декодування у старіших відеоколах та телевізійних консолях.

```bash
# Приклади команд транскодування з явним вказуванням метаданих BT.709 та BT.2020 HDR
ffmpeg -i input_sd.mp4 \
  -color_primaries bt709 \
  -color_trc bt709 \
  -colorspace bt709 \
  -color_range tv \
  -c:v libx264 -crf 18 output_hd.mp4

# Перекодування HDR10 у SDR із тономапінгом та правильними прапорами
ffmpeg -i input_hdr.mkv \
  -vf "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709:t=bt709:m=bt709,format=yuv420p" \
  -color_primaries bt709 \
  -color_trc bt709 \
  -colorspace bt709 \
  -color_range tv \
  -c:v libx264 -crf 20 output_sdr.mp4
```

Ключ `-color_range tv` відповідає розмаху Limited Range (16–235), а `-color_range pc` — розмаху Full Range (0–255). Явне записування цих прапорів у контейнер запобігає «блідому» відображенню чорного кольору під час програвання на ТБ та веб-плеєрах.
