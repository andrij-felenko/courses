# 📋 Інтерфейс модифікаторів DRM: FourCC, UAPI ядра, GBM та Wayland Feedback

Цей довідник містить повний опис структур даних, констант, макросів та функцій інтерфейсу програмування графічного ядра Linux (DRM UAPI), бібліотеки GBM (Mesa) та протоколу Wayland `linux-dmabuf`, які відповідають за опис форматів пікселів та розкладок пам'яті.

## 1. Коди форматів пікселів DRM FourCC

Формати пікселів у підсистемі DRM ядра Linux базуються на чотирисимвольних кодах FourCC (англ. *Four Character Code*). Код пакується у беззнакове 32-бітне ціле число в порядку байтів Little-Endian за допомогою макроса ядра:

```
#define fourcc_code(a, b, c, d) \
    ((uint32_t)(a) | ((uint32_t)(b) << 8) | \
    ((uint32_t)(c) << 16) | ((uint32_t)(d) << 24))
```

Основні константи визначені у файлі заголовків `<drm/drm_fourcc.h>`.

### Порядок байтів і різниця між найменуваннями DRM, CPU та OpenGL

Найменування форматів у DRM FourCC описує розташування бітових полів усередині цілочисельного машинного слова центрального процесора, а не послідовність байтів у пам'яті. На архітектурах із порядком байтів Little-Endian (x86_64, AArch64, RISC-V) молодші біти слова розташовуються за меншими адресами пам'яті. 

Через це виникає термінологічна різниця між підсистемами:
* Формат `DRM_FORMAT_ARGB8888` означає, що при читанні 32-бітного слова `uint32_t` альфа-канал займає біти `[31:24]`, червоний — `[23:16]`, зелений — `[15:8]`, а синій — `[7:0]`.
* У фізичній пам'яті за зростанням байтових адрес це дає послідовність `[Байт 0: Blue, Байт 1: Green, Байт 2: Red, Байт 3: Alpha]`.
* Бібліотеки OpenGL та Vulkan позначають цей самий порядок як `VK_FORMAT_B8G8R8A8_UNORM` або `GL_BGRA`, тоді як графічна бібліотека Cairo та X11 традиційно називають його `CAIRO_FORMAT_ARGB32`.

### Таблиця пакованих форматів RGB

| Константа DRM FourCC | Числове значення FourCC | Опис каналів та глибина | Байти у пам'яті (Little-Endian) | Кількість площин |
| :--- | :--- | :--- | :--- | :--- |
| `DRM_FORMAT_XRGB8888` | `fourcc_code('X','R','2','4')` | 24-бітний колір, 8-бітний ігнорований канал X | `[B0, G1, R2, X3]` | 1 |
| `DRM_FORMAT_ARGB8888` | `fourcc_code('A','R','2','4')` | 32-бітний колір із 8-бітним альфа-каналом | `[B0, G1, R2, A3]` | 1 |
| `DRM_FORMAT_XBGR8888` | `fourcc_code('X','B','2','4')` | 24-бітний колір, зворотний порядок каналів | `[R0, G1, B2, X3]` | 1 |
| `DRM_FORMAT_ABGR8888` | `fourcc_code('A','B','2','4')` | 32-бітний колір, зворотний порядок каналів | `[R0, G1, B2, A3]` | 1 |
| `DRM_FORMAT_RGB565`   | `fourcc_code('R','G','1','6')` | 16-бітний колір (R:5, G:6, B:5 бітів) | `[G:3 B:5, R:5 G:3]` | 1 |
| `DRM_FORMAT_XBGR2101010` | `fourcc_code('X','B','3','0')` | 30-бітний колір (10 бітів/канал, 2 біти X) | Паковані 32 біти | 1 |
| `DRM_FORMAT_ABGR2101010` | `fourcc_code('A','B','3','0')` | 30-бітний колір (10 бітів/канал, 2 біти альфа) | Паковані 32 біти | 1 |

### Таблиця планарних та напівпланарних форматів YUV

Планарні формати розділяють компоненти яскравості (Y) та колірності (U/V) на окремі масиви пам'яті. У напівпланарних форматах (NV12, P010) колірні компоненти U і V чергуються в межах єдиної другої площини, що вдвічі знижує кількість апаратних транзакцій читання пам'яті.

| Константа DRM FourCC | Код FourCC | Субдискретизація | Структура площин пам'яті | Площин |
| :--- | :--- | :--- | :--- | :--- |
| `DRM_FORMAT_NV12` | `fourcc_code('N','V','1','2')` | 4:2:0 YUV | Площина 0: Y (W×H); Площина 1: перемежовані UV (W×H/2) | 2 |
| `DRM_FORMAT_NV21` | `fourcc_code('N','V','2','1')` | 4:2:0 YUV | Площина 0: Y (W×H); Площина 1: перемежовані VU (W×H/2) | 2 |
| `DRM_FORMAT_YUV420` | `fourcc_code('Y','U','1','2')` | 4:2:0 YUV | Площина 0: Y (W×H); Площина 1: U (W/2×H/2); Площина 2: V (W/2×H/2) | 3 |
| `DRM_FORMAT_P010` | `fourcc_code('P','0','1','0')` | 4:2:0 YUV HDR | 10-бітний у 16-бітному слові; Площина 0: Y; Площина 1: UV | 2 |

## 2. 64-бітне кодування модифікаторів DRM

Модифікатор формату зберігається у 64-бітному полі `uint64_t modifier`. Старші 8 бітів (біти 63..56) містять ідентифікатор виробника, а молодші 56 бітів (біти 55..0) — драйверо-специфічний опис геометрії блоків та стиснення.

```
+-------------------+---------------------------------------------------------+
| Vendor ID (8 біт) | Код розкладки, тайлінгу та метаданих виробника (56 біт)  |
| Біти 63 .. 56     | Біти 55 .. 0                                            |
+-------------------+---------------------------------------------------------+
```

Такий поділ гарантує абсолютну ізоляцію просторів числових значень між різними компаніями: жоден вендорний модифікатор Intel не зможе випадково збігтися за значенням із модифікатором AMD чи Arm.

### Макроси формування та виділення виробника

```
#define DRM_FORMAT_MOD_VENDOR_NONE    0
#define DRM_FORMAT_MOD_VENDOR_INTEL   0x01
#define DRM_FORMAT_MOD_VENDOR_AMD     0x02
#define DRM_FORMAT_MOD_VENDOR_NVIDIA  0x03
#define DRM_FORMAT_MOD_VENDOR_SAMSUNG 0x04
#define DRM_FORMAT_MOD_VENDOR_QCOM    0x05
#define DRM_FORMAT_MOD_VENDOR_VIVANTE 0x06
#define DRM_FORMAT_MOD_VENDOR_BROADCOM 0x07
#define DRM_FORMAT_MOD_VENDOR_ARM     0x08
#define DRM_FORMAT_MOD_VENDOR_ALLWINNER 0x09
#define DRM_FORMAT_MOD_VENDOR_AMLOGIC 0x0a

#define fourcc_mod_code(vendor, val) \
    ((((uint64_t)DRM_FORMAT_MOD_VENDOR_##vendor) << 56) | \
     ((val) & 0x00ffffffffffffffULL))

#define fourcc_mod_is_vendor(val, vendor) \
    (fourcc_mod_get_vendor(val) == DRM_FORMAT_MOD_VENDOR_##vendor)

#define fourcc_mod_get_vendor(val) \
    (((val) >> 56) & 0xff)
```

### Універсальні стандартизовані модифікатори

* `DRM_FORMAT_MOD_INVALID`: значення `((1ULL << 56) - 1)` (`0x00ffffffffffffffULL`). Позначає невалідний або невідомий модифікатор. Використовується програмами як запит до драйвера обрати неявну розкладку самостійно. Передача цього значення у системний виклик `ADDFB2` із прапорцем `DRM_MODE_FB_MODIFIERS` заборонена й повертає помилку `-EINVAL`.
* `DRM_FORMAT_MOD_LINEAR`: значення `0ULL` (`fourcc_mod_code(NONE, 0)`). Гарантує суцільний растровий порядок рядків пам'яті (крок рядка `pitch` байтів, без тайлінгу та стиснення). Дозволяє прямий доступ процесора через `mmap()`.

### Ключові вендорні модифікатори

#### Модифікатори Intel (`<drm/drm_fourcc.h>`)
* `I915_FORMAT_MOD_X_TILED`: `fourcc_mod_code(INTEL, 1)` — тайли 512×8 байтів (4 КБ). Традиційний тайлінг для 2D/3D та дисплея на старих платформах.
* `I915_FORMAT_MOD_Y_TILED`: `fourcc_mod_code(INTEL, 2)` — тайли 128×32 байти (4 КБ). Оптимізовано для 3D-шейдерів і текстурування (покоління Gen6–Gen11).
* `I915_FORMAT_MOD_Yf_TILED`: `fourcc_mod_code(INTEL, 3)` — тайли з кривою Гільберта / Z-порядком для покращення просторової локальності.
* `I915_FORMAT_MOD_Y_TILED_CCS`: `fourcc_mod_code(INTEL, 4)` — Y-Tile з допоміжною площиною стиснення кольору (Render Decompression) для чипів Skylake/Kaby Lake.
* `I915_FORMAT_MOD_Y_TILED_GEN12_RC_CCS`: `fourcc_mod_code(INTEL, 6)` — стиснення кольору для архітектури Intel Xe (Tiger Lake).
* `I915_FORMAT_MOD_4_TILED`: `fourcc_mod_code(INTEL, 9)` — тайлінг Tile4 (новий базовий тайлінг поколінь DG2 / Meteor Lake / Lunar Lake).
* `I915_FORMAT_MOD_4_TILED_DG2_RC_CCS`: `fourcc_mod_code(INTEL, 10)` — Tile4 зі стисненням Render Compression для дискретних GPU Intel Arc.
* `I915_FORMAT_MOD_4_TILED_MTL_RC_CCS`: `fourcc_mod_code(INTEL, 13)` — Tile4 зі стисненням для інтегрованих систем Meteor Lake.

#### Модифікатори Arm AFBC (Arm FrameBuffer Compression)
Arm кодує розмір суперблока стиснення у молодших бітах модифікатора та використовує бітові прапорці для ввімкнення розширених режимів:
* `AFBC_FORMAT_MOD_BLOCK_SIZE_16x16`: `fourcc_mod_code(ARM, 1)` — стиснення блоками 16×16 пікселів.
* `AFBC_FORMAT_MOD_BLOCK_SIZE_32x8`: `fourcc_mod_code(ARM, 2)` — оптимізовано для широких горизонтальних вікон.
* Додаткові бітові маски Arm AFBC (накладаються через бітове `|`):
  * `AFBC_FORMAT_MOD_YTR` (`1ULL << 4`): оборотна трансформація колірного простору RGB у YUV для підвищення коефіцієнта стиснення.
  * `AFBC_FORMAT_MOD_SPARSE` (`1ULL << 5`): підтримка незаповнених проміжків пам'яті (розріджені блоки).
  * `AFBC_FORMAT_MOD_CBR` (`1ULL << 6`): режим фіксованого бітрейту (Constant Bitrate) для гарантії пропускної здатності.
  * `AFBC_FORMAT_MOD_SPLIT_BLOCK` (`1ULL << 7`): роздільне стиснення каналів кольору.

#### Модифікатори AMD (`<drm/drm_fourcc.h>`)
AMD пакує параметри мікроархітектури (версію тайлінгу, банк пам'яті, конфігурацію конвеєрів) через макрос `AMD_FMT_MOD_SET(TILE_VERSION, TILE)`:
* `AMD_FMT_MOD_TILE_GFX9_64K_S`: тайли розміром 64 КБ зі стандартною просторовою розкладкою (Standard 64K).
* `AMD_FMT_MOD_TILE_GFX9_64K_D`: тайли 64 КБ для поверхонь відображення (Display 64K).
* Бітові поля DCC (Delta Color Compression):
  * `AMD_FMT_MOD_DCC`: увімкнення поверхні стиснення метаданих DCC.
  * `AMD_FMT_MOD_DCC_RETILE`: спеціальний режим перетайлінгу для одночасного сканування контролером дисплея DCN.

#### Модифікатори NVIDIA
* `DRM_FORMAT_MOD_NVIDIA_BLOCK_LINEAR_2D(height, kind, gen)`: формує модифікатор блочно-лінійної розкладки архітектур Kepler, Maxwell, Pascal, Volta, Turing, Ampere та Ada Lovelace (GOB — Group of Bytes по 512 байтів).

## 3. Структури DRM UAPI ядра Linux

### Структура реєстрації кадрового буфера `drm_mode_fb_cmd2`

Структура передається у системний виклик `ioctl(drm_fd, DRM_IOCTL_MODE_ADDFB2, &cmd)`:

```
struct drm_mode_fb_cmd2 {
    uint32_t fb_id;          /* Вихідне поле: унікальний числовий ID кадрового буфера */
    uint32_t width;          /* Ширина буфера в пікселях */
    uint32_t height;         /* Висота буфера в пікселях */
    uint32_t pixel_format;   /* 32-бітний код DRM FourCC (наприклад, DRM_FORMAT_ARGB8888) */
    uint32_t flags;          /* Прапорці конфігурації (DRM_MODE_FB_*) */

    uint32_t handles[4];     /* GEM-хендли пам'яті для кожної з площин (до 4 площин) */
    uint32_t pitches[4];     /* Крок рядка (stride) у байтах для кожної площини */
    uint32_t offsets[4];     /* Зміщення площини від початку відповідного GEM-об'єкта */
    uint64_t modifier[4];    /* 64-бітний DRM Format Modifier для кожної площини */
};
```

Прапорці конфігурації `flags`:
* `DRM_MODE_FB_INTERLACED` (`0x01`): буфер містить черезрядкову розгортку.
* `DRM_MODE_FB_MODIFIERS` (`0x02`): поле `modifier[4]` містить дійсні 64-бітні модифікатори розкладки. Якщо прапорець відсутній, ядро трактує буфер як неявний або лінійний.

#### Коди помилок системного виклику ADDFB2

* `-EINVAL`: непідтримуваний FourCC, некоректне вирівнювання `offsets` або `pitches`, неприпустиме значення модифікатора (`DRM_FORMAT_MOD_INVALID` із прапорцем `DRM_MODE_FB_MODIFIERS`), або різні модифікатори для площин одного буфера.
* `-ENOSPC`: розмір виділеного GEM-об'єкта менший за область, яку покриває геометрія площин разом із метаданими.
* `-ERANGE`: ширина або висота перевищують апаратні ліміти контролера дисплея.
* `-EOPNOTSUPP`: драйвер не підтримує роботу з модифікаторами або не реалізує атомарний інтерфейс.

### Властивість площини `IN_FORMATS` та бінарний блоб

Кожна площина DRM KMS (`struct drm_plane`) публікує незмінну властивість `IN_FORMATS`. Вона вказує на бінарний об'єкт блобу `struct drm_format_modifier_blob`:

```
struct drm_format_modifier_blob {
    uint32_t version;         /* Версія структури блобу (зазвичай 1) */
    uint32_t flags;           /* Зарезервовано */
    uint32_t count_formats;   /* Кількість підтримуваних FourCC-форматів */
    uint32_t formats_offset;  /* Зміщення до масиву uint32_t formats[] */
    uint32_t count_modifiers; /* Кількість 64-бітних модифікаторів */
    uint32_t modifiers_offset;/* Зміщення до масиву struct drm_format_modifier[] */
};

struct drm_format_modifier {
    uint64_t formats;         /* Бітова маска індексів форматів (індекси з масиву formats[]) */
    uint32_t offset;          /* Зміщення у бітовій масці (для підтримки понад 64 форматів) */
    uint32_t pad;             /* Вирівнювання */
    uint64_t modifier;        /* 64-бітне числове значення модифікатора */
};
```

#### Алгоритм розбору блобу `IN_FORMATS` у просторі користувача

Щоб з'ясувати, які модифікатори дозволені для конкретного FourCC:
1. Простір користувача отримує ідентифікатор блобу властивості `IN_FORMATS` через `drmModeObjectGetProperties()`.
2. Викликає `drmModeGetPropertyBlob()`, отримуючи покажчик на заповнену структуру `struct drm_format_modifier_blob`.
3. Знаходить масив форматів: `const uint32_t *formats = (const uint32_t *)((const char *)blob + blob->formats_offset)`.
4. Знаходить індекс `idx` шуканого формату (наприклад, `DRM_FORMAT_XRGB8888`) у масиві `formats`.
5. Перебирає модифікатори: `const struct drm_format_modifier *mods = (const struct drm_format_modifier *)((const char *)blob + blob->modifiers_offset)`.
6. Модифікатор `mods[i]` підтримується для цього формату, якщо встановлено відповідний біт: `(mods[i].formats & (1ULL << (idx - mods[i].offset))) != 0` за умови, що `idx >= mods[i].offset` і `idx < mods[i].offset + 64`.

## 4. Інтерфейс бібліотеки Generic Buffer Management (GBM)

Функції бібліотеки `libgbm` для роботи з модифікаторами:

```
/* Створення буфера із заданим переліком дозволених модифікаторів */
struct gbm_bo *gbm_bo_create_with_modifiers2(
    struct gbm_device *gbm,
    uint32_t width,
    uint32_t height,
    uint32_t format,
    const uint64_t *modifiers,
    const unsigned int count,
    uint32_t flags
);

/* Отримання обраного драйвером модифікатора */
uint64_t gbm_bo_get_modifier(struct gbm_bo *bo);

/* Отримання кількості фізичних площин буфера (разом із aux-площинами) */
int gbm_bo_get_plane_count(struct gbm_bo *bo);

/* Експорт файлового дескриптора dma-buf для конкретної площини */
int gbm_bo_get_fd_for_plane(struct gbm_bo *bo, int plane);

/* Отримання кроку рядка в байтах для площини */
uint32_t gbm_bo_get_stride_for_plane(struct gbm_bo *bo, int plane);

/* Отримання байтового зміщення площини */
uint32_t gbm_bo_get_offset(struct gbm_bo *bo, int plane);
```

## 5. Протокол Wayland Feedback (`wp_linux_dmabuf_feedback_v1`)

Протокол зворотного зв'язку Wayland передає клієнту таблицю підтримуваних форматів та транші пріоритетів (tranches):

1. **`main_device`:** передає шлях або `dev_t` ідентифікатор основного графічного вузла рендерингу (наприклад, `/dev/dri/renderD128`). Клієнт зобов'язаний відкрити саме цей пристрій для виділення спільних буферів.
2. **`format_table`:** передає дескриптор спільної пам'яті `shm_pool`, що містить масив записів `struct dmabuf_feedback_format`:
   ```
   struct dmabuf_feedback_format {
       uint32_t format;    /* Код FourCC */
       uint32_t padding;
       uint64_t modifier;  /* 64-бітний модифікатор */
   };
   ```
   Клієнт відображає цю таблицю у пам'ять за допомогою `mmap()` і використовує її як глобальний довідник пар «формат-модифікатор».
3. **`tranche_target_device`:** вказує цільовий пристрій для конкретного траншу (наприклад, дискретний GPU або контролер дисплея).
4. **`tranche_formats`:** передає бінарний масив 16-бітних індексів, що посилаються на записи в таблиці `format_table`. Індекси розташовані в порядку спадання пріоритету (найшвидший апаратний тайлінг іде першим).
5. **`tranche_flags`:** прапорець `WP_LINUX_DMABUF_FEEDBACK_V1_TRANCHE_FLAGS_SCANOUT` (`0x01`) свідчить, що транш оптимізовано для прямого апаратного сканування дисплейною площиною KMS (Zero-Copy Direct Scanout). Клієнт повинен віддати перевагу модифікаторам із цього траншу для повноекранних ігор та мультимедійних плеєрів.
