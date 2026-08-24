# 📋 Контракт мапування кадру: GStreamer ↔ cv::Mat

Аркуш для того, хто своїми руками перетворює буфер конвеєра на `cv::Mat`: сигнатури обох боків, поля структур, правило типових кроків із числами й таблиця «формат GStreamer → скільки заголовків і який код перетворення». Усе звірено з чинним кодом — гілка `main` GStreamer 1.x і гілка `4.x` OpenCV; де функція чи поле з'явилися пізніше за 1.0, версія стоїть поруч.

## Заголовки й збірка

```c
#include <gst/gst.h>
#include <gst/video/video.h>      /* GstVideoInfo, GstVideoFrame, GstVideoMeta */
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>    /* cvtColor, cvtColorTwoPlane, merge */
```

```
pkg-config --cflags --libs gstreamer-1.0 gstreamer-video-1.0
pkg-config --cflags --libs opencv4
```

Уся відеочастина живе в окремій бібліотеці `gstreamer-video-1.0`, не в ядрі: `gst/gst.h` про площини й кроки не знає нічого.

## Caps → GstVideoInfo

`GstVideoInfo` — це розібраний рядок caps: із тексту `video/x-raw, format=NV12, width=1366, height=768` вона робить формат, розміри й **типові** кроки та зсуви площин.

```c
void           gst_video_info_init          (GstVideoInfo *info);
gboolean       gst_video_info_from_caps     (GstVideoInfo *info, const GstCaps *caps);
GstCaps       *gst_video_info_to_caps       (const GstVideoInfo *info);
gboolean       gst_video_info_set_format    (GstVideoInfo *info, GstVideoFormat format,
                                             guint width, guint height);
GstVideoInfo  *gst_video_info_new           (void);                        /* 1.6  */
GstVideoInfo  *gst_video_info_new_from_caps (const GstCaps *caps);         /* 1.20 */
void           gst_video_info_free          (GstVideoInfo *info);          /* 1.6  */
gboolean       gst_video_info_align         (GstVideoInfo *info, GstVideoAlignment *align);
gboolean       gst_video_info_align_full    (GstVideoInfo *info, GstVideoAlignment *align,
                                             gsize plane_size[GST_VIDEO_MAX_PLANES]); /* 1.18 */
```

`gst_video_info_from_caps` повертає `FALSE`, коли caps не фіксовані або це взагалі не `video/x-raw`; нефіксовані caps ще й лишають у журналі GLib запис про невдалу перевірку аргументу. Повернене значення перевіряти обов'язково: доки [узгодження caps](topic:media-vision/caps-negotiation) не пройшло, структура не заповнена і читати з неї нічого.

Поля, які справді читають:

| Поле | Тип | Що в ньому |
| --- | --- | --- |
| `finfo` | `const GstVideoFormatInfo *` | опис формату: скільки площин, скільки компонент, як вони розкладені |
| `width`, `height` | `gint` | розміри кадру в пікселях |
| `size` | `gsize` | скільки байтів займає кадр за типовою розкладкою |
| `stride[4]` | `gint` | байтів від початку рядка до початку наступного, на кожну площину |
| `offset[4]` | `gsize` | де починається кожна площина, від початку буфера |
| `interlace_mode` | `GstVideoInterlaceMode` | черезрядковість; впливає на висоту поля |
| `colorimetry` | `GstVideoColorimetry` | матриця, діапазон, передавальна функція |
| `chroma_site` | `GstVideoChromaSite` | де саме сидить кольорова вибірка щодо яскравісних |
| `fps_n`, `fps_d`, `par_n`, `par_d` | `gint` | частота кадрів і співвідношення сторін пікселя |

Стеля `GST_VIDEO_MAX_PLANES` дорівнює 4 — усі масиви кроків і зсувів мають саме таку довжину.

Макроси-доступ (усі беруть `GstVideoInfo *`):

| Макрос | Дає |
| --- | --- |
| `GST_VIDEO_INFO_FORMAT(i)` | значення `GstVideoFormat` |
| `GST_VIDEO_INFO_WIDTH(i)`, `GST_VIDEO_INFO_HEIGHT(i)` | розміри кадру |
| `GST_VIDEO_INFO_SIZE(i)` | `info->size` |
| `GST_VIDEO_INFO_N_PLANES(i)` | скільки площин у форматі |
| `GST_VIDEO_INFO_N_COMPONENTS(i)` | скільки компонент — **це інше число** |
| `GST_VIDEO_INFO_PLANE_STRIDE(i,p)` | `info->stride[p]` |
| `GST_VIDEO_INFO_PLANE_OFFSET(i,p)` | `info->offset[p]` |
| `GST_VIDEO_INFO_COMP_WIDTH(i,c)`, `..._COMP_HEIGHT(i,c)` | розмір компоненти з урахуванням субдискретизації |
| `GST_VIDEO_INFO_COMP_PSTRIDE(i,c)` | байтів від однієї вибірки компоненти до наступної в рядку |
| `GST_VIDEO_INFO_FIELD_HEIGHT(i)` | висота одного поля; для звичайного відео дорівнює `height` |

## Правило типових кроків

Типовий крок GStreamer рахує однією формулою: округлити довжину рядка вгору до чотирьох байтів. Округлення — два бітові дії, тому воно й дешеве, і всюдисуще.

```
GST_ROUND_UP_2(n) = (n + 1) & ~1
GST_ROUND_UP_4(n) = (n + 3) & ~3
GST_ROUND_UP_8(n) = (n + 7) & ~7
```

| Формат | Площин | `stride[0]` | `stride[1]` | `stride[2]` | `size` |
| --- | --- | --- | --- | --- | --- |
| `BGR`, `RGB` | 1 | `RU4(w·3)` | — | — | `stride[0]·h` |
| `BGRx`, `BGRA`, `RGBx`, `RGBA` | 1 | `w·4` | — | — | `stride[0]·h` |
| `GRAY8` | 1 | `RU4(w)` | — | — | `stride[0]·h` |
| `GRAY16_LE`, `GRAY16_BE` | 1 | `RU4(w·2)` | — | — | `stride[0]·h` |
| `YUY2`, `UYVY`, `YVYU` | 1 | `RU4(w·2)` | — | — | `stride[0]·h` |
| `NV12`, `NV21` | 2 | `RU4(w)` | `= stride[0]` | — | `offset[1] + stride[0]·cr_h` |
| `I420`, `YV12` | 3 | `RU4(w)` | `RU4(RU2(w)/2)` | `= stride[1]` | `offset[2] + stride[2]·cr_h` |

Зсуви площин для форматів 4:2:0:

```
cr_h      = RU2(h) / 2                      висота кольорової площини
offset[1] = stride[0] · RU2(h)
offset[2] = offset[1] + stride[1] · cr_h    лише для I420 та YV12
```

Чотири байти для `BGRx` не згадано не з недбальства: рядок із чотирибайтових пікселів кратний чотирьом за побудовою, тож округлювати нічого.

**Кадр 1366×768 — три формати поспіль:**

```
BGR    stride[0] = RU4(1366·3) = RU4(4098) = 4100
       size      = 4100 · 768              = 3 148 800

NV12   stride[0] = RU4(1366)              = 1368
       stride[1] = 1368
       offset[1] = 1368 · 768             = 1 050 624
       cr_h      = 768 / 2                =       384
       size      = 1 050 624 + 1368 · 384 = 1 575 936

I420   stride[1] = RU4(RU2(1366)/2) = RU4(683) = 684
       offset[2] = 1 050 624 + 684 · 384       = 1 313 280
       size      = 1 313 280 + 684 · 384       = 1 575 936
```

Тут ховається пастка, на яку натрапляють, коли вирішують «порахувати самому»: **кольоровий крок — це не половина яскравісного**. Округлення застосовують до половини ширини, а не до вже округленого кроку, і на непарних числах результати розходяться.

```
ширина 1362:  stride[0]      = RU4(1362)          = 1364
              stride[0] / 2  =                      682
              справжній stride[1] = RU4(1362/2) = RU4(681) = 684
```

Два байти на рядок — і 384 рядки кольорової площини поїхали.

## GstVideoMeta: коли типові кроки не діють

Типові кроки — це те, що GStreamer вигадав би сам. Реальний буфер, який приїхав від апаратного декодера чи камери через V4L2, розкладено так, як зручно тому залізу, і свою розкладку він несе на собі метаданими.

```c
GstVideoMeta *gst_buffer_get_video_meta      (GstBuffer *buffer);
GstVideoMeta *gst_buffer_get_video_meta_id   (GstBuffer *buffer, gint id);
GstVideoMeta *gst_buffer_add_video_meta      (GstBuffer *buffer, GstVideoFrameFlags flags,
                                              GstVideoFormat format, guint width, guint height);
GstVideoMeta *gst_buffer_add_video_meta_full (GstBuffer *buffer, GstVideoFrameFlags flags,
                                              GstVideoFormat format, guint width, guint height,
                                              guint n_planes,
                                              gsize offset[GST_VIDEO_MAX_PLANES],
                                              gint  stride[GST_VIDEO_MAX_PLANES]);

gboolean gst_video_meta_map              (GstVideoMeta *meta, guint plane, GstMapInfo *info,
                                          gpointer *data, gint *stride, GstMapFlags flags);
gboolean gst_video_meta_unmap            (GstVideoMeta *meta, guint plane, GstMapInfo *info);
gboolean gst_video_meta_set_alignment    (GstVideoMeta *meta, GstVideoAlignment alignment);   /* 1.18 */
gboolean gst_video_meta_get_plane_size   (GstVideoMeta *meta, gsize plane_size[GST_VIDEO_MAX_PLANES]);   /* 1.18 */
gboolean gst_video_meta_get_plane_height (GstVideoMeta *meta, guint plane_height[GST_VIDEO_MAX_PLANES]); /* 1.18 */
```

| Поле `GstVideoMeta` | Тип | Значення |
| --- | --- | --- |
| `buffer` | `GstBuffer *` | буфер, якому належать ці метадані |
| `format` | `GstVideoFormat` | формат кадру |
| `width`, `height` | `guint` | розміри |
| `n_planes` | `guint` | скільки площин насправді |
| `offset[4]` | `gsize` | справжні зсуви площин |
| `stride[4]` | `gint` | справжні кроки |
| `flags` | `GstVideoFrameFlags` | ознаки кадру (поля, порядок полів) |
| `alignment` | `GstVideoAlignment` | запас із чотирьох боків і вирівнювання кроку (1.18) |

Правило одне й воно єдине, що тут треба запам'ятати: **якщо на буфері є `GstVideoMeta`, її `offset` і `stride` переважають над типовими з `GstVideoInfo`**. Кроки з caps — здогад; кроки з метаданих — факт. Ось чому адресу площини не можна рахувати з ширини: ширина є в caps, а вирівнювання — ні.

Дзеркальний бік: метадані на буфері не з'являються самі. Той, хто виділяє буфери, чіпляє їх лише тоді, коли споживач оголосив, що вміє їх читати, — через `gst_query_add_allocation_meta (query, GST_VIDEO_META_API_TYPE, NULL)` у відповіді на запит алокації. Ця домовленість разом із опціями пулу розписана в [контракті буфера й пам'яті](topic:media-vision/buffers-and-memory/api-buffer-memory.md). Не оголосили — і джерело мусить віддавати кадр щільно спакованим, тобто зайвою копією.

## `gst_video_frame_map` проти `gst_buffer_map`

```c
gboolean gst_video_frame_map    (GstVideoFrame *frame, const GstVideoInfo *info,
                                 GstBuffer *buffer, GstMapFlags flags);
gboolean gst_video_frame_map_id (GstVideoFrame *frame, const GstVideoInfo *info,
                                 GstBuffer *buffer, gint id, GstMapFlags flags);
void     gst_video_frame_unmap  (GstVideoFrame *frame);
gboolean gst_video_frame_copy       (GstVideoFrame *dest, const GstVideoFrame *src);
gboolean gst_video_frame_copy_plane (GstVideoFrame *dest, const GstVideoFrame *src, guint plane);
```

| | `gst_buffer_map` | `gst_video_frame_map` |
| --- | --- | --- |
| що дає | один вказівник і довжину | масив вказівників і кроків — на кожну площину |
| знає формат | ні | так, через переданий `GstVideoInfo` |
| читає `GstVideoMeta` | **ні** | **так**, і виправляє нею кроки та зсуви |
| скільки площин | вгадуєте самі | `GST_VIDEO_FRAME_N_PLANES` |
| посилання на буфер | не бере | бере, віддає на `unmap` |
| відповідність | `gst_buffer_unmap` | `gst_video_frame_unmap` |

Перший рядок таблиці й пояснює, чому `gst_buffer_map` на стику з OpenCV — тиха вада. Він поверне `TRUE`, дасть чесний вказівник на початок буфера, і далі ви порахуєте зсув другої площини з ширини — тобто повз метадані, які лежали поруч і мовчали.

`GstVideoFrame` після успішного мапування:

```c
struct _GstVideoFrame {
  GstVideoInfo        info;                          /* копія переданої, виправлена метаданими */
  GstVideoFrameFlags  flags;
  GstBuffer          *buffer;
  gpointer            meta;                          /* GstVideoMeta, якщо була */
  gint                id;
  gpointer            data[GST_VIDEO_MAX_PLANES];
  GstMapInfo          map[GST_VIDEO_MAX_PLANES];
};
```

Поле `info` — саме копія, а не той об'єкт, який ви передали: у ній кроки вже виправлені метаданими буфера. Тому читати їх треба з `frame`, а не з власної `GstVideoInfo`.

| Макрос над `GstVideoFrame *` | Дає |
| --- | --- |
| `GST_VIDEO_FRAME_PLANE_DATA(f,p)` | вказівник на початок площини `p` |
| `GST_VIDEO_FRAME_PLANE_STRIDE(f,p)` | крок площини `p` у байтах |
| `GST_VIDEO_FRAME_PLANE_OFFSET(f,p)` | зсув площини від початку буфера |
| `GST_VIDEO_FRAME_COMP_DATA(f,c)` | вказівник на **першу вибірку компоненти** `c` |
| `GST_VIDEO_FRAME_COMP_STRIDE(f,c)` | крок площини, у якій живе компонента `c` |
| `GST_VIDEO_FRAME_COMP_WIDTH(f,c)`, `..._COMP_HEIGHT(f,c)` | розміри компоненти після субдискретизації |
| `GST_VIDEO_FRAME_COMP_PSTRIDE(f,c)` | байтів між сусідніми вибірками компоненти в рядку |
| `GST_VIDEO_FRAME_N_PLANES(f)`, `..._N_COMPONENTS(f)` | скільки площин і скільки компонент |
| `GST_VIDEO_FRAME_WIDTH(f)`, `..._HEIGHT(f)`, `..._SIZE(f)`, `..._FORMAT(f)` | геометрія й формат |
| `GST_VIDEO_FRAME_IS_INTERLACED(f)`, `..._IS_TFF(f)` | черезрядковість і порядок полів |

Прапорці — звичайні `GstMapFlags` (`GST_MAP_READ`, `GST_MAP_WRITE`) плюс один власний:

| Прапорець | Значення | Дія |
| --- | --- | --- |
| `GST_VIDEO_FRAME_MAP_FLAG_NO_REF` | 65536 | не брати додаткового посилання на буфер (1.6) |

Мінімальний правильний виклик:

```c
GstVideoInfo  info;
GstVideoFrame frame;

if (!gst_video_info_from_caps (&info, caps))
  return GST_FLOW_NOT_NEGOTIATED;

if (!gst_video_frame_map (&frame, &info, buffer, GST_MAP_READ))
  return GST_FLOW_ERROR;

/* … робота з GST_VIDEO_FRAME_PLANE_DATA / PLANE_STRIDE … */

gst_video_frame_unmap (&frame);        /* і на кожному ранньому виході теж */
```

## Площина — це не компонента

Два числа, які плутають щодня: `N_PLANES` і `N_COMPONENTS`. Для NV12 їх два й три відповідно.

```
NV12:  площин 2        (Y) і (UV разом)
       компонент 3     Y, U, V
       COMP_DATA(f,0) = PLANE_DATA(f,0)
       COMP_DATA(f,1) = PLANE_DATA(f,1) + 0     COMP_PSTRIDE(f,1) = 2
       COMP_DATA(f,2) = PLANE_DATA(f,1) + 1     COMP_PSTRIDE(f,2) = 2
```

Практична користь від цієї різниці одна, зате велика. Компонента 1 — це **завжди** U, компонента 2 — **завжди** V, у якій би площині вони не лежали. А I420 і YV12 відрізняються рівно тим, що в YV12 площини U та V поміняно місцями. Тому код, написаний через `PLANE_DATA`, для цих двох форматів мусить мати два різні гілки, а код через `COMP_DATA` — жодної: макроси самі спитають у `finfo`, у якій площині сидить потрібна компонента.

## Бік OpenCV: заголовок над чужою пам'яттю

```cpp
cv::Mat::Mat(int rows, int cols, int type, void* data, size_t step = cv::Mat::AUTO_STEP);
cv::Mat::Mat(cv::Size size, int type, void* data, size_t step = cv::Mat::AUTO_STEP);
```

| Річ | Значення |
| --- | --- |
| `AUTO_STEP` | **0**; означає «рядки лежать щільно», тобто `step[0] = cols · elemSize()` |
| порядок аргументів | `(rows, cols)` — це `(висота, ширина)`; `cv::Size(width, height)` — навпаки |
| копіювання | його немає: конструктор лише запам'ятовує вказівник |
| володіння | його теж немає: [лічильника посилань такий заголовок не має](topic:media-vision/mat-views-no-copy) |
| `step` | у **байтах**, не в пікселях і не в елементах |

```
адреса рядка r        = data + r · step[0]
адреса пікселя (r, c) = data + r · step[0] + c · elemSize()
elemSize()            = channels() · elemSize1()
isContinuous()        ⟺ step[0] == cols · elemSize()  і це не підматриця
```

| Метод | Повертає | Що означає |
| --- | --- | --- |
| `elemSize()` | `size_t` | байтів на один піксель усіма каналами |
| `elemSize1()` | `size_t` | байтів на одну вибірку (за глибиною) |
| `step1()` | `size_t` | `step[0] / elemSize1()` — крок у вибірках |
| `total()` | `size_t` | `rows · cols`; **не** розмір у байтах |
| `isContinuous()` | `bool` | чи можна пройти кадр як один довгий масив |
| `type()`, `depth()`, `channels()` | `int` | опис елемента |

Числові значення типів стануть у пригоді при читанні чужого коду й повідомлень про помилки: `CV_MAKETYPE(depth, cn) = depth + ((cn − 1) << 3)`, звідки `CV_8UC1 = 0`, `CV_8UC2 = 8`, `CV_8UC3 = 16`, `CV_8UC4 = 24`, `CV_16UC1 = 2`.

Несиметричність, через яку `AUTO_STEP` майже завжди хибний саме для кадрів із конвеєра: **власні виділення OpenCV рядків не доповнює ніколи.** Вирівнюється тільки початкова адреса блока, і константа тут одна:

```c
/* modules/core/include/opencv2/core/private.hpp */
#define  CV_MALLOC_ALIGN    64
```

Тобто `Mat`, який OpenCV зробила сама, майже завжди суцільний, а `Mat` над буфером конвеєра — майже ніколи. Звідки взагалі береться вимога кратної адреси, розібрано у [вирівнюванні даних у пам'яті](topic:programming/memory-alignment).

## Таблиця відповідності форматів

Скрізь нижче `w`, `h` — `GST_VIDEO_FRAME_WIDTH/HEIGHT`, `P(p)` — `GST_VIDEO_FRAME_PLANE_DATA(&f, p)`, `S(p)` — `GST_VIDEO_FRAME_PLANE_STRIDE(&f, p)`.

| Формат GStreamer | Площин | Заголовки `cv::Mat` | Як дістати BGR |
| --- | --- | --- | --- |
| `BGR` | 1 | `Mat(h, w, CV_8UC3, P(0), S(0))` | нічого робити не треба |
| `RGB` | 1 | те саме | `cvtColor(src, dst, COLOR_RGB2BGR)` |
| `BGRx`, `BGRA` | 1 | `Mat(h, w, CV_8UC4, P(0), S(0))` | `cvtColor(src, dst, COLOR_BGRA2BGR)` |
| `RGBx`, `RGBA` | 1 | те саме | `COLOR_RGBA2BGR` |
| `GRAY8` | 1 | `Mat(h, w, CV_8UC1, P(0), S(0))` | `COLOR_GRAY2BGR` — здебільшого зайве |
| `GRAY16_LE`, `GRAY16_BE` | 1 | `Mat(h, w, CV_16UC1, P(0), S(0))` | немає прямого коду; спершу масштабувати в 8 біт |
| `YUY2` (він же YUYV) | 1 | `Mat(h, w, CV_8UC2, P(0), S(0))` | `COLOR_YUV2BGR_YUY2` |
| `UYVY` | 1 | те саме | `COLOR_YUV2BGR_UYVY` |
| `YVYU` | 1 | те саме | `COLOR_YUV2BGR_YVYU` |
| `NV12` | 2 | `y(h, w, CV_8UC1, P(0), S(0))`, `uv(h/2, w/2, CV_8UC2, P(1), S(1))` | `cvtColorTwoPlane(y, uv, dst, COLOR_YUV2BGR_NV12)` |
| `NV21` | 2 | те саме | `cvtColorTwoPlane(..., COLOR_YUV2BGR_NV21)` |
| `I420` | 3 | `y`, `u`, `v` — три `CV_8UC1`, кольорові `h/2 × w/2` | `merge({u, v}, uv)` і далі як NV12 |
| `YV12` | 3 | те саме, але через `COMP_DATA`, бо U та V у площинах навпаки | так само |

Коди мають синоніми, і в чужому коді трапляються всі: `COLOR_YUV2BGR_YUY2` = `COLOR_YUV2BGR_YUYV` = `COLOR_YUV2BGR_YUNV`; `COLOR_YUV2BGR_UYVY` = `COLOR_YUV2BGR_Y422` = `COLOR_YUV2BGR_UYNV`; `COLOR_YUV2BGR_I420` = `COLOR_YUV2BGR_IYUV`; `COLOR_YUV420sp2BGR` — це NV21, а `COLOR_YUV420p2BGR` — це YV12.

Про останній рядок таблиці варто сказати окремо, бо це найдешевший спосіб узяти I420 без перепакування всього кадру. `cv::merge` із двох одноканальних матриць робить двоканальну, де U та V чергуються, — а це рівно розкладка кольорової площини NV12. Копіюється при цьому лише хрома: для 1920×1080 це 1 036 800 байтів проти 3 110 400 при перепакуванні цілого кадру.

## Що вимагає `cvtColor` від форматів 4:2:0

```cpp
void cv::cvtColor         (InputArray src, OutputArray dst, int code, int dstCn = 0);
void cv::cvtColorTwoPlane (InputArray src1, InputArray src2, OutputArray dst, int code);
```

`cvtColorTwoPlane` приймає рівно вісім кодів — по чотири на кожен порядок хроми: `COLOR_YUV2BGR_NV12`, `COLOR_YUV2RGB_NV12`, `COLOR_YUV2BGRA_NV12`, `COLOR_YUV2RGBA_NV12` і ті самі чотири з `NV21`. Перший аргумент — площина Y, другий — двоканальна хрома. У поточних збірках 4.x обидві функції мають ще один необов'язковий аргумент `AlgorithmHint hint`, який обирає між точним і швидким наближенням; на розкладку пам'яті він не впливає.

| Шлях | Що приймає | Обмеження |
| --- | --- | --- |
| `cvtColorTwoPlane` | два окремі заголовки зі **своїми** кроками | ширина й висота парні; хрома вдвічі менша за обома вимірами |
| `cvtColor` із кодом `NV12`/`NV21`/`I420`/`YV12` | **один** `CV_8UC1` заввишки `h·3/2` | усі площини в одному блоці, кольорова починається рівно на `step[0]·h`, крок у всіх однаковий |

Другий рядок і є той «високий заголовок», який працює лише за двох умов одночасно. Крок він поважає — адреси всередині рахуються через `step[0]`, — а от зсув другої площини бере як даність, тому апаратний буфер із окремо вирівняними площинами ламає саме його.

І ще одна річ, якої немає в жодній сигнатурі. Перетворення 4:2:0 → BGR в OpenCV зашите на фіксованих коефіцієнтах ITU-R BT.601 з обмеженим діапазоном:

```
/* modules/imgproc/src/color_yuv.simd.hpp */
ITUR_BT_601_CY  = 1220542       int y = max(0, yy − 16) * ITUR_BT_601_CY;
ITUR_BT_601_CUB = 2116026
ITUR_BT_601_CUG = −409993
ITUR_BT_601_CVG = −852492
ITUR_BT_601_CVR = 1673527
ITUR_BT_601_SHIFT = 20
```

Відняте 16 означає, що вхід вважають телевізійним діапазоном 16–235. Поле `colorimetry` з `GstVideoInfo` OpenCV не читає взагалі: кадр із матрицею BT.709 (а це майже все, що знято в HD) вона переведе в BGR за BT.601, і кольори поїдуть — не катастрофічно, але помітно на насичених ділянках. Хочете правильні кольори — або лишіть перетворення конвеєрові, який `colorimetry` знає, або перетворюйте самі. Що саме описують ці матриці, розібрано в [кольорових просторах](topic:physics/color-spaces).

## Готова функція

```cpp
// Кадр із конвеєра → BGR. Заголовки над площинами нічого не копіюють;
// копія відбувається лише всередині cvtColor і merge, де без неї не обійтися.
static bool frame_to_bgr(const GstVideoFrame& f, cv::Mat& bgr)
{
    const int w = GST_VIDEO_FRAME_WIDTH(&f);
    const int h = GST_VIDEO_FRAME_HEIGHT(&f);
    const int cw = GST_VIDEO_FRAME_COMP_WIDTH(&f, 1);    // ширина хроми
    const int ch = GST_VIDEO_FRAME_COMP_HEIGHT(&f, 1);   // висота хроми

    switch (GST_VIDEO_FRAME_FORMAT(&f)) {

    case GST_VIDEO_FORMAT_BGR: {
        cv::Mat src(h, w, CV_8UC3, GST_VIDEO_FRAME_PLANE_DATA(&f, 0),
                                   GST_VIDEO_FRAME_PLANE_STRIDE(&f, 0));
        src.copyTo(bgr);            // без copyTo це позика, що помре на unmap
        return true;
    }
    case GST_VIDEO_FORMAT_BGRx:
    case GST_VIDEO_FORMAT_BGRA: {
        cv::Mat src(h, w, CV_8UC4, GST_VIDEO_FRAME_PLANE_DATA(&f, 0),
                                   GST_VIDEO_FRAME_PLANE_STRIDE(&f, 0));
        cv::cvtColor(src, bgr, cv::COLOR_BGRA2BGR);
        return true;
    }
    case GST_VIDEO_FORMAT_GRAY8: {
        cv::Mat src(h, w, CV_8UC1, GST_VIDEO_FRAME_PLANE_DATA(&f, 0),
                                   GST_VIDEO_FRAME_PLANE_STRIDE(&f, 0));
        cv::cvtColor(src, bgr, cv::COLOR_GRAY2BGR);
        return true;
    }
    case GST_VIDEO_FORMAT_YUY2: {
        cv::Mat src(h, w, CV_8UC2, GST_VIDEO_FRAME_PLANE_DATA(&f, 0),
                                   GST_VIDEO_FRAME_PLANE_STRIDE(&f, 0));
        cv::cvtColor(src, bgr, cv::COLOR_YUV2BGR_YUY2);
        return true;
    }
    case GST_VIDEO_FORMAT_NV12:
    case GST_VIDEO_FORMAT_NV21: {
        cv::Mat y (h,  w,  CV_8UC1, GST_VIDEO_FRAME_PLANE_DATA(&f, 0),
                                    GST_VIDEO_FRAME_PLANE_STRIDE(&f, 0));
        cv::Mat uv(ch, cw, CV_8UC2, GST_VIDEO_FRAME_PLANE_DATA(&f, 1),
                                    GST_VIDEO_FRAME_PLANE_STRIDE(&f, 1));
        cv::cvtColorTwoPlane(y, uv, bgr,
            GST_VIDEO_FRAME_FORMAT(&f) == GST_VIDEO_FORMAT_NV12
                ? cv::COLOR_YUV2BGR_NV12 : cv::COLOR_YUV2BGR_NV21);
        return true;
    }
    case GST_VIDEO_FORMAT_I420:
    case GST_VIDEO_FORMAT_YV12: {
        // COMP, а не PLANE: компонента 1 — завжди U, компонента 2 — завжди V,
        // тому обидва формати проходять цією гілкою без розрізнення.
        cv::Mat y(h,  w,  CV_8UC1, GST_VIDEO_FRAME_COMP_DATA(&f, 0),
                                   GST_VIDEO_FRAME_COMP_STRIDE(&f, 0));
        cv::Mat u(ch, cw, CV_8UC1, GST_VIDEO_FRAME_COMP_DATA(&f, 1),
                                   GST_VIDEO_FRAME_COMP_STRIDE(&f, 1));
        cv::Mat v(ch, cw, CV_8UC1, GST_VIDEO_FRAME_COMP_DATA(&f, 2),
                                   GST_VIDEO_FRAME_COMP_STRIDE(&f, 2));
        cv::Mat uv;
        cv::merge(std::vector<cv::Mat>{u, v}, uv);   // U та V поруч — розкладка NV12
        cv::cvtColorTwoPlane(y, uv, bgr, cv::COLOR_YUV2BGR_NV12);
        return true;
    }
    default:
        return false;               // формат не з нашого списку — хай його візьме videoconvert
    }
}
```

## `cv::VideoCapture` з бекендом GStreamer

Готовий шлях, який робить усе вищеописане всередині.

```cpp
cv::VideoCapture cap("v4l2src device=/dev/video0 ! video/x-raw,format=NV12,width=1280,height=720"
                     " ! videoconvert ! video/x-raw,format=BGR ! appsink drop=true max-buffers=2",
                     cv::CAP_GSTREAMER);              // CAP_GSTREAMER == 1800
```

| Річ | Контракт |
| --- | --- |
| рядок | синтаксис `gst-launch-1.0`, розбирається через `gst_parse_launch` |
| приймач | бекенд шукає в конвеєрі елемент, чиє **ім'я містить** `appsink` або `opencvsink`, і чіпляється до нього |
| caps приймача | ставить сам бекенд; переважно `BGR`, `BGRx`/`BGRA`, `GRAY8`, формати Баєра (`video/x-bayer`) й `image/jpeg`, а як запасний варіант — ширший список `UYVY, YUY2, YVYU, NV12, NV21, YV12, I420, BGRA, RGBA, BGRx, RGBx, GRAY16_LE, GRAY16_BE` |
| `max-buffers` | бекенд ставить 1 — **якщо** у вашому рядку немає підрядка ` max-buffers=` |
| `sync` | у власному конвеєрі бекенд його не чіпає: приймач і далі йде за годинником |
| мапування | усередині — саме `gst_video_frame_map`, тож `GstVideoMeta` бекенд читає правильно |
| що ви отримуєте | **завжди свіжу суцільну матрицю**: `retrieve()` копіює кадр у власний блок без доповнення рядків |

Форма результату за форматом на приймачі: `BGR` → `CV_8UC3`; `GRAY8` → `CV_8UC1`; `BGRA`/`RGBA`/`BGRx`/`RGBx` → `CV_8UC4`; `UYVY`/`YUY2`/`YVYU` → `CV_8UC2`; `GRAY16_*` → `CV_16UC1`; `NV12`/`NV21`/`I420`/`YV12` → одноканальна матриця заввишки `h·3/2`, зібрана щільно; `image/jpeg` — рядок байтів `1 × N` у `CV_8UC1`.

| Властивість | Номер | Поведінка в цьому бекенді |
| --- | --- | --- |
| `CAP_PROP_CONVERT_RGB` | 16 | **нічого не робить**: у `setProperty` і `getProperty` це порожня гілка. Документація каже прямо: для власного конвеєра прапорець ігнорується, тлумачити вихід — ваш клопіт |
| `CAP_PROP_FORMAT` | 8 | загалом по videoio — тип `Mat`, який поверне `retrieve()`; значення −1 (нерозкодований потік) призначене для інших бекендів |
| `CAP_PROP_FRAME_WIDTH/HEIGHT`, `CAP_PROP_FPS` | 3, 4, 5 | читаються з узгоджених caps приймача |

Звідси єдиний робочий спосіб керувати форматом на цьому шляху: **задати його caps-фільтром перед `appsink`** у самому рядку конвеєра, а не властивістю після відкриття. Хочете сирий NV12 — напишіть `! video/x-raw,format=NV12 ! appsink`; хочете BGR — напишіть `format=BGR` і дайте `videoconvert` виконати роботу там, де її ще можна узгодити.

Зворотний бік:

```cpp
cv::VideoWriter out("appsrc ! videoconvert ! x264enc tune=zerolatency ! rtph264pay ! udpsink host=… port=…",
                    cv::CAP_GSTREAMER, 0, 30.0, cv::Size(1280, 720), true);
```

Четвертий аргумент — код `fourcc`; нуль означає «сирі кадри, кодуванням займеться конвеєр». Бекенд оголошує caps `appsrc` сам, за розміром і за `isColor`, і подає кадри як BGR або GRAY8.

## Назад у конвеєр: що мусить збігтися

Коли буфер збирають руками навколо готового `cv::Mat`, звірити треба чотири речі, і кожна ламається окремо.

| Що | Вимога |
| --- | --- |
| формат | тип `Mat` мусить відповідати caps: `CV_8UC3` ↔ `BGR`/`RGB`, `CV_8UC1` ↔ `GRAY8`, `CV_8UC4` ↔ `BGRx`/`BGRA` |
| крок | `gst_buffer_new_wrapped_full` приймає **довжину**, а не крок, — тому або `isContinuous()`, або метадані зі справжніми кроками |
| розмір | елемент нижче за потоком рахуватиме розмір як `GST_VIDEO_INFO_SIZE`, а не як `total() · elemSize()` |
| час життя | буфер переживе вашу функцію, отже блок пікселів мусить пережити буфер |

Третій рядок — той, що дає найгірше падіння, бо помилка виринає в чужому елементі. Числа для щільного `Mat` шириною 1366 у BGR:

```
щільний Mat:            1366 · 3 · 768        = 3 147 264 байти
GST_VIDEO_INFO_SIZE:    RU4(4098) · 768       = 3 148 800 байтів
не вистачає:                                    1 536 байтів
```

Наступний елемент прочитає кадр за типовим кроком 4100 і на останньому рядку вийде за кінець буфера. Виходів два: тримати ширину кратною чотирьом або оголосити свої кроки метаданими —

```c
gsize offset[GST_VIDEO_MAX_PLANES] = { 0, };
gint  stride[GST_VIDEO_MAX_PLANES] = { (gint) img.step[0], };

gst_buffer_add_video_meta_full (buf, GST_VIDEO_FRAME_FLAG_NONE,
                                GST_VIDEO_FORMAT_BGR, img.cols, img.rows,
                                1, offset, stride);
```

— і тоді все, що вміє читати `GstVideoMeta`, візьме кадр як є. Що з цим робить сам `appsrc` і як подавати буфери в потоці, розібрано в [контракті appsink і appsrc](topic:media-vision/appsink-appsrc/api-appsink-appsrc.md).

## Що надрукувати, коли не сходиться

| Симптом | Один рядок, який ставить діагноз |
| --- | --- |
| картинка йде навскіс | `GST_VIDEO_FRAME_PLANE_STRIDE(&f,0)` проти `w · elemSize()` — розбіжність і є нахилом |
| кольорова смуга внизу | `PLANE_OFFSET(&f,1)` проти `PLANE_STRIDE(&f,0) · h` — рівність і є умовою високого заголовка |
| кроки «як у caps», хоча буфер апаратний | `gst_buffer_get_video_meta (buf) == NULL` — метаданих нема, бо їх не просили в запиті алокації |
| кадр із двох різних моментів | шукайте `Mat`, що пережив `gst_video_frame_unmap` |
| сині обличчя | `GST_VIDEO_FRAME_FORMAT(&f)` — там `RGB`, а читаєте як BGR |
| кольори «майже правильні», але тьмяніші | `info.colorimetry` каже BT.709, а `cvtColor` рахує за BT.601 |
