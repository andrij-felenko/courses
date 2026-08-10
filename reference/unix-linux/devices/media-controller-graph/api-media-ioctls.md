# 📋 Медіавузол і пад: команди, структури, константи, помилки

Це повний перелік того, чим програма розмовляє з графом медіапристрою: команди `ioctl` на `/dev/mediaN` і `/dev/v4l-subdevN`, поля кожної структури, таблиці числових констант і коди помилок із їхнім точним значенням. Довідка потрібна тому, що інтерфейс розкладено по трьох заголовках і двох різних вузлах, а більшість реальних збоїв упирається не в підписи, а в те, який саме `errno` про що каже.

Заголовки: `<linux/media.h>` — граф, сутності, зв'язки; `<linux/v4l2-subdev.h>` — пади й формати на них; `<linux/media-bus-format.h>` — коди шини. Значення взято з ядра 6.x; де інтерфейс з'явився пізніше за початковий, версію вказано окремо.

## Команди медіавузла

```c
#define MEDIA_IOC_DEVICE_INFO     _IOWR('|', 0x00, struct media_device_info)
#define MEDIA_IOC_ENUM_ENTITIES   _IOWR('|', 0x01, struct media_entity_desc)
#define MEDIA_IOC_ENUM_LINKS      _IOWR('|', 0x02, struct media_links_enum)
#define MEDIA_IOC_SETUP_LINK      _IOWR('|', 0x03, struct media_link_desc)
#define MEDIA_IOC_G_TOPOLOGY      _IOWR('|', 0x04, struct media_v2_topology)   /* 4.6 */
#define MEDIA_IOC_REQUEST_ALLOC   _IOR ('|', 0x05, int)                        /* 4.20 */

#define MEDIA_REQUEST_IOC_QUEUE   _IO('|', 0x80)   /* на дескрипторі запиту */
#define MEDIA_REQUEST_IOC_REINIT  _IO('|', 0x81)
```

Літера-родина тут `'|'`, а не `'V'`, як у V4L2, — [номер команди](book:unix-linux/ioctl-interface/api-ioctl-encoding.md) кодує ще й розмір структури, тож розширювати ці структури можна лише в зарезервовані поля.

| Команда | Що робить | Куди пишеться відповідь |
| --- | --- | --- |
| `DEVICE_INFO` | ім'я драйвера, модель, версії | вся структура |
| `ENUM_ENTITIES` | одна сутність за її `id` або наступна за ним | вся структура |
| `ENUM_LINKS` | пади однієї сутности й зв'язки, що **виходять** із неї | у два масиви програми |
| `SETUP_LINK` | вмикає або вимикає один зв'язок | нічого, крім `errno` |
| `G_TOPOLOGY` | увесь граф одним викликом | у чотири масиви програми |
| `REQUEST_ALLOC` | заводить [медіазапит](book:unix-linux/media-request-api) — набір параметрів і буфер, які застосуються до одного кадру разом | новий дескриптор в `int` |

## Структури: сутність, пад, зв'язок

```c
struct media_device_info {
        char  driver[16];        /* ім'я драйвера, ASCII з нулем */
        char  model[32];         /* модель, UTF-8 */
        char  serial[40];        /* серійний номер або порожньо */
        char  bus_info[32];      /* розташування: "platform:…", "usb-…" */
        __u32 media_version;     /* версія API, KERNEL_VERSION(a,b,c) */
        __u32 hw_revision;       /* ревізія заліза, формат довільний */
        __u32 driver_version;    /* версія драйвера, KERNEL_VERSION(a,b,c) */
        __u32 reserved[31];
};

struct media_entity_desc {
        __u32 id;                /* задає програма; | MEDIA_ENT_ID_FLAG_NEXT */
        char  name[32];
        __u32 type;              /* насправді функція, MEDIA_ENT_F_* */
        __u32 revision;          /* завжди 0, поле застаріле */
        __u32 flags;             /* MEDIA_ENT_FL_* */
        __u32 group_id;          /* завжди 0, поле застаріле */
        __u16 pads;              /* скільки падів */
        __u16 links;             /* скільки вихідних зв'язків */
        __u32 reserved[4];
        union {
                struct { __u32 major, minor; } dev;   /* номери вузла в /dev */
                __u8 raw[184];
        };
};

struct media_pad_desc {
        __u32 entity;            /* чий це пад */
        __u16 index;             /* номер пада всередині сутности, з 0 */
        __u32 flags;             /* MEDIA_PAD_FL_* */
        __u32 reserved[2];
};

struct media_link_desc {
        struct media_pad_desc source;
        struct media_pad_desc sink;
        __u32 flags;             /* MEDIA_LNK_FL_* */
        __u32 reserved[2];
};

struct media_links_enum {
        __u32 entity;
        struct media_pad_desc  __user *pads;    /* NULL — не заповнювати */
        struct media_link_desc __user *links;
        __u32 reserved[4];
};

#define MEDIA_ENT_ID_FLAG_NEXT   (1U << 31)
```

Перелік сутностей роблять так: беруть `id = MEDIA_ENT_ID_FLAG_NEXT` (тобто «перша, чий номер більший за нуль»), ядро прапорець знімає й повертає першу сутність; далі щоразу підставляють `desc.id | MEDIA_ENT_ID_FLAG_NEXT`, доки не прийде `EINVAL`. Ідентифікатори не щільні й не сталі між увімкненнями — на них не можна покладатися як на іменування.

Масиви для `ENUM_LINKS` розмірює сама програма за полями `pads` і `links` тієї ж сутности, здобутими попереднім `ENUM_ENTITIES`. Важлива несиметричність: ядро віддає лише **вихідні** зв'язки. Щоб зібрати всі ребра графа старим інтерфейсом, доводиться обійти всі сутності по черзі.

У `SETUP_LINK` міняти можна єдине — біт `MEDIA_LNK_FL_ENABLED`; решта полів мусить точно вказувати наявний зв'язок, інакше `EINVAL`.

## Увесь граф одним викликом: G_TOPOLOGY

```c
struct media_v2_entity {
        __u32 id; char name[64]; __u32 function; __u32 flags; __u32 reserved[5];
} __attribute__ ((packed));

struct media_v2_interface {
        __u32 id; __u32 intf_type; __u32 flags; __u32 reserved[9];
        union {
                struct { __u32 major, minor; } devnode;   /* вузол у /dev */
                __u32 raw[16];
        };
} __attribute__ ((packed));

struct media_v2_pad {
        __u32 id; __u32 entity_id; __u32 flags; __u32 index; __u32 reserved[4];
} __attribute__ ((packed));

struct media_v2_link {
        __u32 id; __u32 source_id; __u32 sink_id; __u32 flags; __u32 reserved[6];
} __attribute__ ((packed));

struct media_v2_topology {
        __u64 topology_version;
        __u32 num_entities;   __u32 reserved1;  __u64 ptr_entities;
        __u32 num_interfaces; __u32 reserved2;  __u64 ptr_interfaces;
        __u32 num_pads;       __u32 reserved3;  __u64 ptr_pads;
        __u32 num_links;      __u32 reserved4;  __u64 ptr_links;
} __attribute__ ((packed));
```

Тут `id` — наскрізний для всього графа: пад, сутність та інтерфейс не можуть мати однакового номера, тому в `media_v2_link` два поля `source_id`/`sink_id` описують і зв'язок пад→пад, і прив'язку інтерфейсу до сутности — розрізняють їх за типом у `flags`. Вказівники подано як `__u64` навмисно: так структура однакова для 32- і 64-бітних програм.

Виклик двопрохідний. Нульова структура повертає лічильники, другий прохід — самі дані:

```c
struct media_v2_topology topo;
struct media_v2_entity *ents; struct media_v2_interface *intfs;
struct media_v2_pad *pads;    struct media_v2_link *links;

retry:
        memset(&topo, 0, sizeof(topo));
        if (ioctl(fd, MEDIA_IOC_G_TOPOLOGY, &topo) < 0)   /* лише лічильники */
                return -1;

        ents  = calloc(topo.num_entities,   sizeof(*ents));
        intfs = calloc(topo.num_interfaces, sizeof(*intfs));
        pads  = calloc(topo.num_pads,       sizeof(*pads));
        links = calloc(topo.num_links,      sizeof(*links));

        topo.ptr_entities   = (__u64)(uintptr_t)ents;
        topo.ptr_interfaces = (__u64)(uintptr_t)intfs;
        topo.ptr_pads       = (__u64)(uintptr_t)pads;
        topo.ptr_links      = (__u64)(uintptr_t)links;

        if (ioctl(fd, MEDIA_IOC_G_TOPOLOGY, &topo) < 0) {
                free(ents); free(intfs); free(pads); free(links);
                if (errno == ENOSPC)      /* граф змінився між проходами */
                        goto retry;
                return -1;
        }
```

`topology_version` росте щоразу, коли сутність або зв'язок з'являється чи зникає. Саме він робить `ENOSPC` між двома проходами законним станом, а не збоєм: гаряче під'єднаний субпристрій — звичайна річ, і програма зобов'язана перечитати лічильники, а не здаватися.

## Таблиці констант

Функції сутностей задано трьома основами; програма порівнює `function` (у старому інтерфейсі — `type`) з готовою константою, а не розбирає ім'я по літерах.

```c
#define MEDIA_ENT_F_BASE             0x00000000
#define MEDIA_ENT_F_OLD_BASE         0x00010000   /* сутність із вузлом /dev/videoN */
#define MEDIA_ENT_F_OLD_SUBDEV_BASE  0x00020000   /* сутність-субпристрій */
```

| Константа | Значення | Що це |
| --- | --- | --- |
| `MEDIA_ENT_F_UNKNOWN` | `MEDIA_ENT_F_BASE` | початкове значення; драйвер мусив його замінити |
| `MEDIA_ENT_F_V4L2_SUBDEV_UNKNOWN` | `MEDIA_ENT_F_OLD_SUBDEV_BASE` | те саме для субпристрою, задля сумісности |
| `MEDIA_ENT_F_IO_V4L` | `OLD_BASE + 1` | кінцева точка потоку — вузол `/dev/videoN` |
| `MEDIA_ENT_F_IO_VBI` | `BASE + 0x01002` | те саме для VBI |
| `MEDIA_ENT_F_IO_SWRADIO` | `BASE + 0x01003` | те саме для програмного радіо |
| `MEDIA_ENT_F_IO_DTV` | `BASE + 0x01001` | те саме для цифрового телебачення |
| `MEDIA_ENT_F_CAM_SENSOR` | `OLD_SUBDEV_BASE + 1` | сенсор зображення |
| `MEDIA_ENT_F_FLASH` | `OLD_SUBDEV_BASE + 2` | керування спалахом |
| `MEDIA_ENT_F_LENS` | `OLD_SUBDEV_BASE + 3` | керування оптикою (фокус, діафрагма) |
| `MEDIA_ENT_F_ATV_DECODER` | `OLD_SUBDEV_BASE + 4` | декодер аналогового телесигналу |
| `MEDIA_ENT_F_TUNER` | `OLD_SUBDEV_BASE + 5` | тюнер |
| `MEDIA_ENT_F_VID_IF_BRIDGE` | `BASE + 0x5002` | міст між шинами: приймач CSI-2, HDMI, eDP |
| `MEDIA_ENT_F_VID_MUX` | `BASE + 0x5001` | перемикач кількох входів на один вихід |
| `MEDIA_ENT_F_PROC_VIDEO_ISP` | `BASE + 0x4009` | процесор обробки зображення цілком |
| `MEDIA_ENT_F_PROC_VIDEO_SCALER` | `BASE + 0x4005` | зміна роздільности |
| `MEDIA_ENT_F_PROC_VIDEO_PIXEL_FORMATTER` | `BASE + 0x4002` | розпаковування, обтинання, перепакування пікселів |
| `MEDIA_ENT_F_PROC_VIDEO_PIXEL_ENC_CONV` | `BASE + 0x4003` | перетворення RGB↔YUV↔HSV, демозаїка |
| `MEDIA_ENT_F_PROC_VIDEO_LUT` | `BASE + 0x4004` | таблиця відповідности (гама, криві) |
| `MEDIA_ENT_F_PROC_VIDEO_STATISTICS` | `BASE + 0x4006` | гістограми й зонні середні для експозиції та балансу |
| `MEDIA_ENT_F_PROC_VIDEO_COMPOSER` | `BASE + 0x4001` | складання кількох входів в один кадр |
| `MEDIA_ENT_F_PROC_VIDEO_ENCODER` | `BASE + 0x4007` | стиснення (H.264, HEVC, VPx) |
| `MEDIA_ENT_F_PROC_VIDEO_DECODER` | `BASE + 0x4008` | розтиснення |
| `MEDIA_ENT_F_DTV_DEMOD` | `BASE + 0x00001` | демодулятор цифрового телебачення |
| `MEDIA_ENT_F_TS_DEMUX` | `BASE + 0x00002` | демультиплексор транспортного потоку |
| `MEDIA_ENT_F_AUDIO_CAPTURE` | `BASE + 0x03001` | звуковий вхід тієї самої плати |

```c
#define MEDIA_ENT_FL_DEFAULT       (1U << 0)   /* типова сутність своєї функції */
#define MEDIA_ENT_FL_CONNECTOR     (1U << 1)   /* не блок, а рознім на платі */

#define MEDIA_PAD_FL_SINK          (1U << 0)   /* вхід: пад приймає дані */
#define MEDIA_PAD_FL_SOURCE        (1U << 1)   /* вихід: пад віддає дані */
#define MEDIA_PAD_FL_MUST_CONNECT  (1U << 2)   /* без увімкненого зв'язку не запуститься */

#define MEDIA_LNK_FL_ENABLED       (1U << 0)   /* дані течуть; єдине, що можна міняти */
#define MEDIA_LNK_FL_IMMUTABLE     (1U << 1)   /* розведено в кремнії, завжди ввімкнено */
#define MEDIA_LNK_FL_DYNAMIC       (1U << 2)   /* можна перемикати під час знімання */

#define MEDIA_LNK_FL_LINK_TYPE     (0xf << 28)          /* маска типу зв'язку */
#  define MEDIA_LNK_FL_DATA_LINK      (0U << 28)        /* пад → пад */
#  define MEDIA_LNK_FL_INTERFACE_LINK (1U << 28)        /* інтерфейс → сутність */
#  define MEDIA_LNK_FL_ANCILLARY_LINK (2U << 28)        /* фізичний зв'язок, 6.1 */
```

Пад завжди рівно одного напрямку: `SINK` і `SOURCE` разом — помилка драйвера. `IMMUTABLE` без `ENABLED` теж беззмістовний і забороняється при реєстрації.

Тип зв'язку вибирають маскою `flags & MEDIA_LNK_FL_LINK_TYPE`, і цей крок пропускати не можна: `G_TOPOLOGY` віддає в одному масиві всі три роди. Зв'язок-інтерфейс — це відповідь на питання «через який вузол у `/dev` говорити до цієї сутности»; пари `major`/`minor` з `media_v2_interface` шукають у `/sys/dev/char/<major>:<minor>` або зіставляють із `stat()` вузла. Допоміжний зв'язок (`ANCILLARY`) описує не потік даних, а фізичну спорідненість — так до сенсора прив'язують його оптику.

Інтерфейси називають, куди ведуть: `MEDIA_INTF_T_V4L_VIDEO` (`/dev/videoN`), `MEDIA_INTF_T_V4L_SUBDEV` (`/dev/v4l-subdevN`), `MEDIA_INTF_T_V4L_VBI`, `MEDIA_INTF_T_V4L_SWRADIO`, `MEDIA_INTF_T_V4L_TOUCH`, родини `MEDIA_INTF_T_DVB_*` і `MEDIA_INTF_T_ALSA_*`.

## Виклики на паді субпристрою

Ці команди йдуть на `/dev/v4l-subdevN` і в кожній є поле `pad` — бо вузол один, а падів у сутности кілька.

```c
#define VIDIOC_SUBDEV_ENUM_MBUS_CODE  _IOWR('V',  2, struct v4l2_subdev_mbus_code_enum)
#define VIDIOC_SUBDEV_G_FMT           _IOWR('V',  4, struct v4l2_subdev_format)
#define VIDIOC_SUBDEV_S_FMT           _IOWR('V',  5, struct v4l2_subdev_format)
#define VIDIOC_SUBDEV_G_SELECTION     _IOWR('V', 61, struct v4l2_subdev_selection)
#define VIDIOC_SUBDEV_S_SELECTION     _IOWR('V', 62, struct v4l2_subdev_selection)
#define VIDIOC_SUBDEV_ENUM_FRAME_SIZE _IOWR('V', 74, struct v4l2_subdev_frame_size_enum)

struct v4l2_subdev_format {
        __u32 which;                       /* TRY або ACTIVE */
        __u32 pad;
        struct v4l2_mbus_framefmt format;  /* width, height, code, field,
                                              colorspace, ycbcr_enc,
                                              quantization, xfer_func */
        __u32 stream;                      /* 6.3: номер потоку в паді */
        __u32 reserved[7];
};

struct v4l2_subdev_selection {
        __u32 which; __u32 pad; __u32 target; __u32 flags;
        struct v4l2_rect r;                /* left, top, width, height */
        __u32 stream; __u32 reserved[7];
};

struct v4l2_subdev_mbus_code_enum {
        __u32 pad; __u32 index; __u32 code; __u32 which;
        __u32 flags; __u32 stream; __u32 reserved[6];
};

struct v4l2_subdev_frame_size_enum {
        __u32 index; __u32 pad; __u32 code;
        __u32 min_width, max_width, min_height, max_height;
        __u32 which; __u32 stream; __u32 reserved[7];
};

enum v4l2_subdev_format_whence {
        V4L2_SUBDEV_FORMAT_TRY    = 0,
        V4L2_SUBDEV_FORMAT_ACTIVE = 1,
};
```

`TRY` не чіпає залізо: драйвер підправляє поданий формат під свої обмеження й повертає, що вийшло б. Стан цих спроб живе **у відкритому дескрипторі**, а не в пристрої, — тож два процеси не заважають одне одному й після `close()` від спроб не лишається сліду.

Прямокутники беруть цілями `target`: `V4L2_SEL_TGT_CROP` — що саме зчитати з входу, `CROP_BOUNDS` — межі, в яких це дозволено, `CROP_DEFAULT` — типовий прямокутник, `NATIVE_SIZE` — фізичний розмір матриці; `COMPOSE`, `COMPOSE_BOUNDS`, `COMPOSE_DEFAULT` — куди покласти результат на виході. Прапорці `V4L2_SEL_FLAG_GE` і `V4L2_SEL_FLAG_LE` кажуть драйверові, у який бік округляти, коли точний прямокутник неможливий.

Промацування можливостей пада — два вкладені переліки, обидва закінчуються `EINVAL`:

```c
struct v4l2_subdev_mbus_code_enum mc = {
        .pad = 0, .index = 0, .which = V4L2_SUBDEV_FORMAT_ACTIVE,
};
while (ioctl(sd, VIDIOC_SUBDEV_ENUM_MBUS_CODE, &mc) == 0) {
        struct v4l2_subdev_frame_size_enum fs = {
                .pad = 0, .index = 0, .code = mc.code,
                .which = V4L2_SUBDEV_FORMAT_ACTIVE,
        };
        while (ioctl(sd, VIDIOC_SUBDEV_ENUM_FRAME_SIZE, &fs) == 0) {
                printf("0x%04x  %ux%u … %ux%u\n", mc.code,
                       fs.min_width, fs.min_height, fs.max_width, fs.max_height);
                fs.index++;
        }
        mc.index++;
}
```

## Коди шини MEDIA_BUS_FMT_*

Код шини описує не байти в пам'яті, а сигнал на дротах між двома блоками, тому це окремий простір чисел, а не [формат пікселів](book:algorithms/pixel-formats) `V4L2_PIX_FMT_*`. Ім'я читають так: колірна модель, біти на складник, далі `NXM` — скільки тактів шини (`N`) якої ширини (`M`) припадає на один піксель. `UYVY8_2X8` — два восьмибітні такти на піксель, `UYVY8_1X16` — той самий піксель одним шістнадцятибітним словом; це різні коди, бо це різна розводка.

| Діапазон | Родина | Приклади |
| --- | --- | --- |
| `0x1xxx` | RGB | `RGB565_1X16` = 0x1017, `RGB888_1X24` = 0x100a |
| `0x2xxx` | YUV і сіре | `UYVY8_2X8` = 0x2006, `UYVY8_1X16` = 0x200f, `YUYV8_1X16` = 0x2011, `Y8_1X8` = 0x2001, `Y10_1X10` = 0x200a |
| `0x3xxx` | Bayer | `SBGGR8_1X8` = 0x3001, `SGRBG10_1X10` = 0x300a, `SRGGB10_1X10` = 0x300f, `SBGGR12_1X12` = 0x3008 |
| `0x4xxx` | стиснене | `JPEG_1X8` = 0x4001 |
| `0x5xxx` | власні коди виробників | — |
| `0x6xxx` | HSV | — |
| `0x7xxx` | метадані | `METADATA_FIXED` = 0x7001 |

Літери в Bayer-кодах — порядок кольорового фільтра в лівому верхньому куті (`SGRBG` — зелений-червоний, синій-зелений), і він зміщується, коли міняють прямокутник обтинання на непарну кількість рядків чи стовпців. Окремо стоїть `MEDIA_BUS_FMT_FIXED` = 0x0001 — «формат не налаштовується», для зв'язків, де вибирати нема з чого.

## Помилки і що кожна означає

| Код | Звідки й чому | Що робити |
| --- | --- | --- |
| `EPIPE` | `VIDIOC_STREAMON`: перевірка `link_validate` побачила різні `width`, `height` або `code` на двох кінцях увімкненого зв'язку | вирівняти формат уздовж усього тракту, пад за падом |
| `ENOLINK` | `VIDIOC_STREAMON`: у тракті є пад із `MUST_CONNECT` без жодного ввімкненого зв'язку | увімкнути відсутню ланку |
| `EBUSY` | `SETUP_LINK`: у пада-приймача вже є ввімкнений зв'язок, або йде потік, а зв'язок не `DYNAMIC`; `S_FMT`/`S_SELECTION`: пад зайнятий потоком; `STREAMON`: пад уже в іншому конвеєрі | вимкнути суперника або зупинити потік |
| `EINVAL` | неіснуюча сутність, пад чи зв'язок; спроба змінити `IMMUTABLE`; `index` за межами переліку; непідтримані `which` або `target` | у переліках це нормальний кінець, не збій |
| `EPERM` | `S_FMT`/`S_SELECTION` з `ACTIVE` на субпристрої, відкритому лише для читання | працювати з `TRY` або відкрити вузол на запис |
| `ENOSPC` | `G_TOPOLOGY`: масиви менші за фактичну кількість або граф змінився між проходами | перечитати лічильники й повторити |
| `ENOTTY` | `REQUEST_ALLOC`: драйвер не вміє запитів | обійтися без них |
| `ENOENT`, `EIO` | `MEDIA_REQUEST_IOC_QUEUE`: у запиті немає жодного буфера; залізо в поганому стані | додати буфер; перезапустити потік |

> 🔧 **Навіщо це.** `EPIPE` не каже, який саме зв'язок не збігся, — а ядро це знає й пише в журнал. Обидві перевірки, і зіставлення форматів, і `MUST_CONNECT`, ведуть діагностику через `dev_dbg`, тобто мовчать, доки їх не ввімкнути: `echo -n 'file mc-entity.c +p' > /sys/kernel/debug/dynamic_debug/control` і те саме для `v4l2-subdev.c`. Після цього `dmesg` показує рядок із іменами обох сутностей, номерами падів і тим, що саме розійшлося — ширина, висота чи код. Це різниця між годиною перебору `media-ctl` і одним рядком.
