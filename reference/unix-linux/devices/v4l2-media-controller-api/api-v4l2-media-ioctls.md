# 📋 Довідник ioctl-інтерфейсів V4L2 та Media Controller

Цей довідник містить вичерпну технічну специфікацію структур даних, прапорців та системних ioctl-викликів, які утворюють системний ABI підсистем Video4Linux2 (V4L2), Media Controller, V4L2 Subdevice та Media Request API у ядрі Linux.

Усі структури даних у даній специфікації розроблені з урахуванням суворого 64-бітного вирівнювання типів даних (`__u32`, `__u64`, `__s32`). Це гарантує бінарну сумісність (compat ABI) між 32-бітними застосунками простору користувача (наприклад, для архітектур armv7hf чи x86) та 64-бітним ядром Linux (arm64, x86_64) без необхідності виконання дорожчих операцій трансляції в ядрі.

---

## 1. Архітектура кодування та обробки ioctls у ядрі

Системний виклик `ioctl(fd, request, arg)` у ядрі Linux використовує 32-бітний числовий ідентифікатор `request`, кодований за допомогою макросів із заголовочного файла `<asm-generic/ioctl.h>`:

```c
#define _IOC(dir, type, nr, size) \
    (((dir)  << _IOC_DIRSHIFT)  | \
     ((type) << _IOC_TYPESHIFT) | \
     ((nr)   << _IOC_NRSHIFT)   | \
     ((size) << _IOC_SIZESHIFT))
```

Поля коду ioctl діляться на чотири бітові сегменти:
- **Direction (`dir`, 2 біти):** Напрямок передачі даних між користувацьким простором та ядром (`_IOC_NONE`, `_IOC_READ`, `_IOC_WRITE` або `_IOC_READ | _IOC_WRITE`).
- **Size (`size`, 14 бітів):** Розмір структури аргументу у байтах. Ядро використовує це значення для автоматичного копіювання пам'яті через `copy_from_user()` та `copy_to_user()`.
- **Type/Magic (`type`, 8 бітів):** Магічний літерний символ підсистеми (`'v'` для V4L2, `'M'` для Media Controller).
- **Number (`nr`, 8 бітів):** Порядковий номер конкретної команди у підсистемі.

Для спрощення оголошення стандартних викликів ядро надає допоміжні макроси: `_IO(type, nr)`, `_IOR(type, nr, datatype)`, `_IOW(type, nr, datatype)` та `_IOWR(type, nr, datatype)`.

### 1.1. Внутрішня диспетчеризація викликів у драйверах ядра

Усередині ядра Linux кожен драйвер V4L2 та Media Controller реєструє таблиці обробників методів:
- **`struct v4l2_ioctl_ops`:** Таблиця callback-функцій для символьних пристроїв `/dev/videoX`. Підсистема `v4l2-ioctl.c` централізовано перевіряє права доступу, валідує розмір переданих структур та викликає відповідні обробники драйвера (наприклад `.vidioc_s_fmt_vid_cap`, `.vidioc_reqbufs`, `.vidioc_qbuf`).
- **`struct v4l2_subdev_core_ops` / `pad_ops`:** Таблиця callback-функцій для субпристроїв `/dev/v4l2-subdevX`. Центр диспетчеризації `v4l2-subdev.c` передає виклики безпосередньо у драйвери сенсорів або ISP (наприклад `.set_fmt`, `.get_selection`).
- **`struct media_device_ops`:** Таблиця callback-функцій контролера медіа-пристрою `/dev/mediaX` (`mc-device.c`), яка відповідає за маніпуляцію графом топології.

### 1.2. Інваріанти ABI, вирівнювання типів та бінарна сумісність

При взаємодії з ioctl-інтерфейсами мультимедійної підсистеми користувацький простір зобов'язаний дотримуватися таких фундаментальних інваріантів:
1. **Обнулення пам'яті:** Перед викликом будь-якого ioctl всі структури даних повинні бути повністю обнулені (`memset(&str, 0, sizeof(str))` у C або zero-initialization `T str{}` у C++). Це необхідно для гарантії того, що зарезервовані поля (`reserved[...]`) містять нулі і не викликають помилок сумісності у майбутніх версіях ядра.
2. **Суворе 64-бітне вирівнювання:** Вказувачі у структурах V4L2/Media Controller (наприклад `ptr_entities` у `struct media_v2_topology`) передаються як 64-бітні цілі числа (`__u64`), приведені через `uintptr_t`. Це виключає зміщення полів при виконанні 32-бітного коду на 64-бітному ядрі.
3. **Обробка переривань:** Будь-який виклик `ioctl()` може бути перерваний сигналом та повернути `-1` із `errno == EINTR`. Застосунок повинен обгортати виклики у цикл повтору `do { res = ioctl(...); } while (res < 0 && errno == EINTR);`.

---

## 2. Media Controller API (`/dev/mediaX`)

Заголовочний файл ядра: `<linux/media.h>`

Символьний пристрій `/dev/mediaX` слугує шлюзом для опису, дослідження та модифікації апаратного графа мультимедійної системи.

### 2.1. `MEDIA_IOC_DEVICE_INFO`

Виклик `MEDIA_IOC_DEVICE_INFO` дозволяє користувацькому простору дізнатися метадані про контролер медіа-пристрою, назву драйвера ядра, модель апаратури та ревізію шини.

:::tabs
```c
#include <linux/media.h>
#include <sys/ioctl.h>
#include <string.h>
#include <stdio.h>

struct media_device_info dev_info;
memset(&dev_info, 0, sizeof(dev_info));

if (ioctl(media_fd, MEDIA_IOC_DEVICE_INFO, &dev_info) == 0) {
    printf("Driver: %s, Model: %s, Bus: %s\n",
           dev_info.driver, dev_info.model, dev_info.bus_info);
}
```
```cpp
#include <linux/media.h>
#include <sys/ioctl.h>
#include <string_view>
#include <system_error>

// Ініціалізація та безпечне вичитування полів у C++20
media_device_info dev_info{};
if (::ioctl(media_fd, MEDIA_IOC_DEVICE_INFO, &dev_info) < 0) {
    throw std::system_error(errno, std::generic_category(), "MEDIA_IOC_DEVICE_INFO failed");
}

std::string_view driver{dev_info.driver};
std::string_view model{dev_info.model};
std::string_view bus{dev_info.bus_info};
```
:::

#### Опис полів та поведінки
- `driver`: Текстова назва модуля ядра, який зареєстрував контролер (наприклад, `"rkisp1"` або `"sun6i-csi"`).
- `model`: Комерційна назва апаратного блоку або назва плати.
- `serial`: Унікальний серійний номер пристрою у вигляді рядка ASCII.
- `bus_info`: Унікальний системний ідентифікатор пристрою на шині, який збігається зі шляхом у sysfs (наприклад `"platform:rkisp1"` чи `"pci:0000:01:00.0"`).
- `media_version`: Версія підсистеми Media Controller на момент збірки ядра у форматі `KERNEL_VERSION`.
- `hw_revision`: Апаратна версія чипа чи ревізія IP-блоку.
- `driver_version`: Версія модуля драйвера.

Поверчувані коди помилок: `EBADF` (недійсний файловий дескриптор), `EFAULT` (недійсний вказівник у просторі користувача), `ENOTTY` (дескриптор не належить медіа-пристрою).

---

### 2.2. `MEDIA_IOC_G_TOPOLOGY`

Отримання повної топології графа в один атомарний виклик. Замінює застарілу послідовність викликів `MEDIA_IOC_ENUM_ENTITIES` та `MEDIA_IOC_ENUM_LINKS`.

:::tabs
```c
#include <linux/media.h>
#include <sys/ioctl.h>
#include <stdlib.h>
#include <string.h>

struct media_v2_topology top;
memset(&top, 0, sizeof(top));

/* 1. Перший виклик з нульовими масивами для вирахування кількості елементів */
if (ioctl(media_fd, MEDIA_IOC_G_TOPOLOGY, &top) < 0) {
    perror("MEDIA_IOC_G_TOPOLOGY count failed");
    return -1;
}

struct media_v2_entity *entities = calloc(top.num_entities, sizeof(*entities));
struct media_v2_pad *pads = calloc(top.num_pads, sizeof(*pads));
struct media_v2_link *links = calloc(top.num_links, sizeof(*links));

top.ptr_entities = (uintptr_t)entities;
top.ptr_pads = (uintptr_t)pads;
top.ptr_links = (uintptr_t)links;

/* 2. Другий виклик для заповнення виділеної пам'яті */
if (ioctl(media_fd, MEDIA_IOC_G_TOPOLOGY, &top) < 0) {
    perror("MEDIA_IOC_G_TOPOLOGY fetch failed");
    free(entities); free(pads); free(links);
    return -1;
}
```
```cpp
#include <linux/media.h>
#include <vector>
#include <sys/ioctl.h>
#include <system_error>

// Двопрохідне атомарне зчитування топології графа у C++
media_v2_topology top{};
if (::ioctl(media_fd, MEDIA_IOC_G_TOPOLOGY, &top) < 0) {
    throw std::system_error(errno, std::generic_category(), "MEDIA_IOC_G_TOPOLOGY initial count failed");
}

std::vector<media_v2_entity> entities(top.num_entities);
std::vector<media_v2_pad> pads(top.num_pads);
std::vector<media_v2_link> links(top.num_links);

top.ptr_entities = reinterpret_cast<uintptr_t>(entities.data());
top.ptr_pads = reinterpret_cast<uintptr_t>(pads.data());
top.ptr_links = reinterpret_cast<uintptr_t>(links.data());

if (::ioctl(media_fd, MEDIA_IOC_G_TOPOLOGY, &top) < 0) {
    throw std::system_error(errno, std::generic_category(), "MEDIA_IOC_G_TOPOLOGY payload fetch failed");
}
```
:::

#### Структури топології
```c
struct media_v2_topology {
    __u64 topology_version; /* Монотонний лічильник версії топології в ядрі */
    __u32 num_entities;     /* Кількість знайдених entities */
    __u32 reserved1;
    __u64 ptr_entities;     /* Вказівник на масив struct media_v2_entity */
    __u32 num_interfaces;   /* Кількість системних інтерфейсів */
    __u32 reserved2;
    __u64 ptr_interfaces;   /* Вказівник на масив struct media_v2_interface */
    __u32 num_pads;         /* Кількість контактних майданчиків (pads) */
    __u32 reserved3;
    __u64 ptr_pads;         /* Вказівник на масив struct media_v2_pad */
    __u32 num_links;        /* Кількість зв'язків (links) */
    __u32 reserved4;
    __u64 ptr_links;        /* Вказівник на масив struct media_v2_link */
};

struct media_v2_entity {
    __u32 id;               /* Унікальний ID entity в системі */
    char name[64];          /* Назва entity (наприклад, "imx219 1-0010") */
    __u32 function;         /* Функціональний тип (MEDIA_ENT_F_CAM_SENSOR, MEDIA_ENT_F_PROC_VIDEO_ISP) */
    __u32 flags;            /* Прапорці стану сутності */
    __u32 reserved[5];
};

struct media_v2_pad {
    __u32 id;               /* Унікальний ID pad у ядрі */
    __u32 entity_id;        /* ID entity, якій належить майданчик */
    __u32 flags;            /* MEDIA_PAD_FL_SINK або MEDIA_PAD_FL_SOURCE */
    __u32 index;            /* Локальний порядковий індекс pad на entity (0, 1, 2...) */
    __u32 reserved[4];
};

struct media_v2_link {
    __u32 id;               /* Унікальний ID зв'язку */
    __u32 source_id;        /* ID джерела (Source Pad ID) */
    __u32 sink_id;          /* ID приймача (Sink Pad ID) */
    __u32 flags;            /* MEDIA_LNK_FL_ENABLED, IMMUTABLE, DYNAMIC */
    __u32 reserved[6];
};
```

#### Прапорці функціональних типів entities (`function`)
- `MEDIA_ENT_F_CAM_SENSOR` (0x00020001) — оптична матриця камери (сенсор).
- `MEDIA_ENT_F_PROC_VIDEO_ISP` (0x00020002) — процесор обробки сигналів зображення (ISP).
- `MEDIA_ENT_F_IO_V4L` (0x00000001) — вузол вводу-виводу V4L2 пам'яті (`/dev/videoX`).
- `MEDIA_ENT_F_VID_IF_BRIDGE` (0x00020003) — міст або приймач серійної шини (наприклад, MIPI CSI-2 Receiver).
- `MEDIA_ENT_F_LENS` (0x00020004) — модуль оптичної лінзи або мотора приводу автофокусу.
- `MEDIA_ENT_F_FLASH` (0x00020005) — світлодіодний або спалаховий контролер освітлення.

#### Прапорці зв'язків (`flags` у `struct media_v2_link`)
- `MEDIA_LNK_FL_ENABLED` (0x00000001) — зв'язок активний, потік даних дозволено.
- `MEDIA_LNK_FL_IMMUTABLE` (0x00000002) — зв'язок жорстко розпаяний в апаратурі; спроба вимкнути поверне `-EINVAL`.
- `MEDIA_LNK_FL_DYNAMIC` (0x00000004) — зв'язок дозволено перемикати під час активного стримінгу кадру.

---

### 2.3. `MEDIA_IOC_SETUP_LINK`

Зміна стану та прапорців зв'язку між контактними майданчиками.

:::tabs
```c
#include <linux/media.h>
#include <sys/ioctl.h>
#include <string.h>

struct media_link_desc link_cmd;
memset(&link_cmd, 0, sizeof(link_cmd));

link_cmd.source.entity = source_entity_id;
link_cmd.source.index = source_pad_index;
link_cmd.source.flags = MEDIA_PAD_FL_SOURCE;

link_cmd.sink.entity = sink_entity_id;
link_cmd.sink.index = sink_pad_index;
link_cmd.sink.flags = MEDIA_PAD_FL_SINK;

link_cmd.flags = MEDIA_LNK_FL_ENABLED; /* Активація зв'язку */

if (ioctl(media_fd, MEDIA_IOC_SETUP_LINK, &link_cmd) < 0) {
    /* Обробка помилки мофіфікації зв'язку */
}
```
```cpp
#include <linux/media.h>
#include <sys/ioctl.h>
#include <system_error>

media_link_desc link_cmd{};
link_cmd.source.entity = source_entity_id;
link_cmd.source.index = source_pad_index;
link_cmd.source.flags = MEDIA_PAD_FL_SOURCE;

link_cmd.sink.entity = sink_entity_id;
link_cmd.sink.index = sink_pad_index;
link_cmd.sink.flags = MEDIA_PAD_FL_SINK;

link_cmd.flags = MEDIA_LNK_FL_ENABLED;

if (::ioctl(media_fd, MEDIA_IOC_SETUP_LINK, &link_cmd) < 0) {
    throw std::system_error(errno, std::generic_category(), "MEDIA_IOC_SETUP_LINK failed");
}
```
:::

Поверчувані коди помилок:
- `EBUSY`: Зв'язок намагаються змінити під час активного відеопотоку на апаратурі, яка не підтримує `MEDIA_LNK_FL_DYNAMIC`.
- `EINVAL`: Вказано неіснуючий майданчик, неіснуючу entity або спроба з'єднати майданчики одного типу (наприклад, Sink з Sink).
- `EPERM`: Спроба вимкнути зв'язок з прапорцем `MEDIA_LNK_FL_IMMUTABLE`.

---

## 3. V4L2 Subdevice API (`/dev/v4l2-subdevX`)

Заголовочний файл ядра: `<linux/v4l2-subdev.h>`

Файли `/dev/v4l2-subdevX` надають доступ до налаштувань конкретних апаратних блоків у графі (сенсор, CSI-2, ISP).

### 3.1. `VIDIOC_SUBDEV_G_FMT` / `VIDIOC_SUBDEV_S_FMT`

Зчитування та встановлення шинного формату (Media Bus Format) на окремому майданчику субпристрою.

:::tabs
```c
#include <linux/v4l2-subdev.h>
#include <sys/ioctl.h>
#include <string.h>

struct v4l2_subdev_format subfmt;
memset(&subfmt, 0, sizeof(subfmt));

subfmt.which = V4L2_SUBDEV_FORMAT_ACTIVE;
subfmt.pad = 0; /* Source pad */
subfmt.format.width = 1920;
subfmt.format.height = 1080;
subfmt.format.code = MEDIA_BUS_FMT_SBGGR10_1X10; /* 10-bit Bayer RAW */
subfmt.format.field = V4L2_FIELD_NONE;
subfmt.format.colorspace = V4L2_COLORSPACE_RAW;

if (ioctl(subdev_fd, VIDIOC_SUBDEV_S_FMT, &subfmt) < 0) {
    /* Обробка помилки встановлення формату субпристрою */
}
```
```cpp
#include <linux/v4l2-subdev.h>
#include <sys/ioctl.h>
#include <system_error>

v4l2_subdev_format subfmt{};
subfmt.which = V4L2_SUBDEV_FORMAT_ACTIVE;
subfmt.pad = 0; // Source pad
subfmt.format.width = 1920;
subfmt.format.height = 1080;
subfmt.format.code = MEDIA_BUS_FMT_SBGGR10_1X10; // 10-bit Bayer RAW
subfmt.format.field = V4L2_FIELD_NONE;
subfmt.format.colorspace = V4L2_COLORSPACE_RAW;

if (::ioctl(subdev_fd, VIDIOC_SUBDEV_S_FMT, &subfmt) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_SUBDEV_S_FMT failed");
}
```
:::

#### Поля та константи
- `which`:
  - `V4L2_SUBDEV_FORMAT_TRY` (0) — випробування конфігурації у підготовчому контексті ядра (`v4l2_subdev_state`) без зміни регістрів обладнання.
  - `V4L2_SUBDEV_FORMAT_ACTIVE` (1) — застосування формату безпосередньо до фізичних регістрів апаратури.
- `code`: Задає спосіб упаковки пікселів у фізичній шині. Поширені коди:
  - `MEDIA_BUS_FMT_SBGGR10_1X10` (0x3007) — 10-бітний Bayer BGGR, 10 біт за такт.
  - `MEDIA_BUS_FMT_YUYV8_1X16` (0x200d) — YUV 4:2:2 з 16-бітною паралельною шиною.
  - `MEDIA_BUS_FMT_UYVY8_2X8` (0x2006) — YUV 4:2:2 передається за 2 такти по 8 біт.
  - `MEDIA_BUS_FMT_RGB888_1X24` (0x100a) — 24-бітне неспрямоване RGB.

---

### 3.2. `VIDIOC_SUBDEV_G_SELECTION` / `VIDIOC_SUBDEV_S_SELECTION`

Керування прямокутниками кадрування (Crop) та масштабування (Compose) всередині субпристрою.

:::tabs
```c
#include <linux/v4l2-subdev.h>
#include <sys/ioctl.h>
#include <string.h>

struct v4l2_subdev_selection sel;
memset(&sel, 0, sizeof(sel));

sel.which = V4L2_SUBDEV_FORMAT_ACTIVE;
sel.pad = 0; /* Sink pad */
sel.target = V4L2_SEL_TGT_CROP;
sel.flags = V4L2_SEL_FLAG_LE; /* Менше або дорівнює вихідній області */
sel.r.left = 0;
sel.r.top = 0;
sel.r.width = 1920;
sel.r.height = 1080;

if (ioctl(subdev_fd, VIDIOC_SUBDEV_S_SELECTION, &sel) < 0) {
    /* Обробка помилки прямокутника вибору */
}
```
```cpp
#include <linux/v4l2-subdev.h>
#include <sys/ioctl.h>
#include <system_error>

v4l2_subdev_selection sel{};
sel.which = V4L2_SUBDEV_FORMAT_ACTIVE;
sel.pad = 0; // Sink pad
sel.target = V4L2_SEL_TGT_CROP;
sel.flags = V4L2_SEL_FLAG_LE;
sel.r.left = 0;
sel.r.top = 0;
sel.r.width = 1920;
sel.r.height = 1080;

if (::ioctl(subdev_fd, VIDIOC_SUBDEV_S_SELECTION, &sel) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_SUBDEV_S_SELECTION failed");
}
```
:::

#### Цілі вибору (`target`)
- `V4L2_SEL_TGT_CROP` (0x0000) — вирізання прямокутної області з вхідного кадру на Sink Pad.
- `V4L2_SEL_TGT_CROP_BOUNDS` (0x0002) — гранично припустимі межі вирізання для даного майданчика.
- `V4L2_SEL_TGT_COMPOSE` (0x0100) — розміщення вирізаної області на вихідному полотні Source Pad (масштабування).
- `V4L2_SEL_TGT_COMPOSE_BOUNDS` (0x0102) — межі масштабування полотна.

---

### 3.3. `VIDIOC_SUBDEV_ENUM_MBUS_CODE` та `VIDIOC_SUBDEV_G_FRAME_INTERVAL`

Перелічення підтримуваних шинних форматів та керування частотою кадрів на субпристроях.

:::tabs
```c
#include <linux/v4l2-subdev.h>
#include <sys/ioctl.h>
#include <stdio.h>
#include <string.h>

struct v4l2_subdev_mbus_code_enum code_enum;
memset(&code_enum, 0, sizeof(code_enum));
code_enum.pad = 0;
code_enum.which = V4L2_SUBDEV_FORMAT_ACTIVE;

while (ioctl(subdev_fd, VIDIOC_SUBDEV_ENUM_MBUS_CODE, &code_enum) == 0) {
    printf("Supported mbus code[%u]: 0x%04x\n", code_enum.index, code_enum.code);
    code_enum.index++;
}
```
```cpp
#include <linux/v4l2-subdev.h>
#include <sys/ioctl.h>
#include <iostream>
#include <vector>

std::vector<uint32_t> mbus_codes;
v4l2_subdev_mbus_code_enum code_enum{};
code_enum.pad = 0;
code_enum.which = V4L2_SUBDEV_FORMAT_ACTIVE;

while (::ioctl(subdev_fd, VIDIOC_SUBDEV_ENUM_MBUS_CODE, &code_enum) == 0) {
    mbus_codes.push_back(code_enum.code);
    code_enum.index++;
}
```
:::

---

## 4. V4L2 Buffer Management API (`/dev/videoX`)

Заголовочний файл ядра: `<linux/videodev2.h>`

Слугує для конфігурування режимів захоплення, виділення та обміну буферами пам'яті між ядром та користувацьким простором.

### 4.1. `VIDIOC_QUERYCAP` та `VIDIOC_S_FMT`

Перевірка можливостей пристрою та налаштування піксельного формату кадру у системній пам'яті.

:::tabs
```c
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <string.h>
#include <stdio.h>

struct v4l2_capability cap;
memset(&cap, 0, sizeof(cap));
if (ioctl(video_fd, VIDIOC_QUERYCAP, &cap) < 0) {
    perror("VIDIOC_QUERYCAP failed");
    return -1;
}

struct v4l2_format fmt;
memset(&fmt, 0, sizeof(fmt));
fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
fmt.fmt.pix.width = 1920;
fmt.fmt.pix.height = 1080;
fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_UYVY;
fmt.fmt.pix.field = V4L2_FIELD_NONE;

if (ioctl(video_fd, VIDIOC_S_FMT, &fmt) < 0) {
    perror("VIDIOC_S_FMT failed");
    return -1;
}
```
```cpp
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <system_error>

v4l2_capability cap{};
if (::ioctl(video_fd, VIDIOC_QUERYCAP, &cap) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_QUERYCAP failed");
}

v4l2_format fmt{};
fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
fmt.fmt.pix.width = 1920;
fmt.fmt.pix.height = 1080;
fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_UYVY;
fmt.fmt.pix.field = V4L2_FIELD_NONE;

if (::ioctl(video_fd, VIDIOC_S_FMT, &fmt) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_S_FMT failed");
}
```
:::

---

### 4.2. Multi-planar API (`V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE`)

Для апаратних відеоконтролерів, які зберігають площини коду (наприклад Y, U, V у рознесених масивах ОЗП чи NV12 у двох площинах Y та UV), V4L2 використовує Multi-planar API.

:::tabs
```c
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <string.h>

struct v4l2_format mp_fmt;
memset(&mp_fmt, 0, sizeof(mp_fmt));
mp_fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
mp_fmt.fmt.pix_mp.width = 1920;
mp_fmt.fmt.pix_mp.height = 1080;
mp_fmt.fmt.pix_mp.pixelformat = V4L2_PIX_FMT_NV12;
mp_fmt.fmt.pix_mp.field = V4L2_FIELD_NONE;
mp_fmt.fmt.pix_mp.num_planes = 2;

if (ioctl(video_fd, VIDIOC_S_FMT, &mp_fmt) < 0) {
    /* Обробка помилки multi-planar формату */
}
```
```cpp
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <system_error>

v4l2_format mp_fmt{};
mp_fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
mp_fmt.fmt.pix_mp.width = 1920;
mp_fmt.fmt.pix_mp.height = 1080;
mp_fmt.fmt.pix_mp.pixelformat = V4L2_PIX_FMT_NV12;
mp_fmt.fmt.pix_mp.field = V4L2_FIELD_NONE;
mp_fmt.fmt.pix_mp.num_planes = 2;

if (::ioctl(video_fd, VIDIOC_S_FMT, &mp_fmt) < 0) {
    throw std::system_error(errno, std::generic_category(), "Multi-planar S_FMT failed");
}
```
:::

При роботі з `MPLANE` у `struct v4l2_buffer` поле `m.planes` має містити вказівник на масив структур `struct v4l2_plane`, розмір якого відповідає `num_planes`.

---

### 4.3. `VIDIOC_REQBUFS`

Ініціалізація внутрішньої черги буферів Videobuf2 (`vb2_queue`).

:::tabs
```c
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <string.h>

struct v4l2_requestbuffers req;
memset(&req, 0, sizeof(req));
req.count = 4;
req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
req.memory = V4L2_MEMORY_MMAP;

if (ioctl(video_fd, VIDIOC_REQBUFS, &req) < 0) {
    /* Обробка помилки виділення буферів */
}
```
```cpp
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <system_error>

v4l2_requestbuffers req{};
req.count = 4;
req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
req.memory = V4L2_MEMORY_MMAP;

if (::ioctl(video_fd, VIDIOC_REQBUFS, &req) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_REQBUFS failed");
}
```
:::

#### Режими пам'яті (`memory`)
- `V4L2_MEMORY_MMAP` (1) — Пам'ять виділяється драйвером ядра. Користувач отримує зміщення `offset` і відображає її через `mmap()`.
- `V4L2_MEMORY_USERPTR` (2) — Пам'ять виділяється користувачем через `posix_memalign()`.
- `V4L2_MEMORY_DMABUF` (3) — Пам'ять імпортується у вигляді дескрипторів DMA-BUF від іншого драйвера (наприклад GPU або DRM).

Очищення та звільнення буферів ядра здійснюється викликом `VIDIOC_REQBUFS` із значенням `req.count = 0`.

---

### 4.4. `VIDIOC_EXPBUF`

Експорт виділеного буфера V4L2 у вигляд дескриптора DMA-BUF для Zero-Copy обміну.

:::tabs
```c
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <string.h>

struct v4l2_exportbuffer exp;
memset(&exp, 0, sizeof(exp));
exp.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
exp.index = 0; /* Перший буфер */
exp.flags = O_CLOEXEC | O_RDWR;

if (ioctl(video_fd, VIDIOC_EXPBUF, &exp) == 0) {
    int dmabuf_fd = exp.fd; /* Дескриптор для передачі в DRM або GPU */
}
```
```cpp
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <system_error>

v4l2_exportbuffer exp{};
exp.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
exp.index = 0; // Перший буфер
exp.flags = O_CLOEXEC | O_RDWR;

if (::ioctl(video_fd, VIDIOC_EXPBUF, &exp) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_EXPBUF failed");
}
int dmabuf_fd = exp.fd;
```
:::

---

### 4.5. `VIDIOC_QBUF` / `VIDIOC_DQBUF` та `VIDIOC_STREAMON` / `VIDIOC_STREAMOFF`

Постановка буфера у чергу апаратури, запуск стримінгу DMA, вилучення заповненого кадру та зупинка потоку.

:::tabs
```c
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <string.h>

/* 1. Постановка буфера в чергу ядра */
struct v4l2_buffer buf;
memset(&buf, 0, sizeof(buf));
buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
buf.memory = V4L2_MEMORY_MMAP;
buf.index = 0;

if (ioctl(video_fd, VIDIOC_QBUF, &buf) < 0) {
    /* Обробка помилки QBUF */
}

/* 2. Запуск відеопотоку */
enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
if (ioctl(video_fd, VIDIOC_STREAMON, &type) < 0) {
    /* Обробка помилки STREAMON */
}

/* 3. Вилучення готового кадру */
struct v4l2_buffer dqbuf;
memset(&dqbuf, 0, sizeof(dqbuf));
dqbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
dqbuf.memory = V4L2_MEMORY_MMAP;

if (ioctl(video_fd, VIDIOC_DQBUF, &dqbuf) == 0) {
    uint32_t frame_seq = dqbuf.sequence;
    uint32_t payload_bytes = dqbuf.bytesused;
}

/* 4. Зупинка відеопотоку */
ioctl(video_fd, VIDIOC_STREAMOFF, &type);
```
```cpp
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <system_error>

v4l2_buffer buf{};
buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
buf.memory = V4L2_MEMORY_MMAP;
buf.index = 0;

if (::ioctl(video_fd, VIDIOC_QBUF, &buf) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_QBUF failed");
}

v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
if (::ioctl(video_fd, VIDIOC_STREAMON, &type) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_STREAMON failed");
}

v4l2_buffer dqbuf{};
dqbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
dqbuf.memory = V4L2_MEMORY_MMAP;

if (::ioctl(video_fd, VIDIOC_DQBUF, &dqbuf) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_DQBUF failed");
}

uint32_t frame_seq = dqbuf.sequence;
uint32_t payload_bytes = dqbuf.bytesused;

::ioctl(video_fd, VIDIOC_STREAMOFF, &type);
```
:::

#### Поля структури `struct v4l2_buffer`
- `index`: Індекс буфера в кільцевій черзі (0 .. `count`-1).
- `bytesused`: Кількість записаних байтів у буфері (заповнюється ядром при `DQBUF`).
- `flags`: Прапорці стану буфера:
  - `V4L2_BUF_FLAG_MAPPED` (0x0001) — буфер відображено через `mmap()`.
  - `V4L2_BUF_FLAG_QUEUED` (0x0002) — буфер перебуває у черзі ядра на обробку.
  - `V4L2_BUF_FLAG_DONE` (0x0004) — обробку буфера завершено апаратурою, можна викликати `DQBUF`.
  - `V4L2_BUF_FLAG_ERROR` (0x0040) — кадр захоплено з непереборною апаратною помилкою (наприклад, CRC error на шині MIPI CSI-2).
- `sequence`: Монотонний лічильник номерів кадрів від моменту виклику `STREAMON`.
- `timestamp`: Системна позначка часу захоплення кадру (`struct timeval`).
- `request_fd`: Файловий дескриптор об'єкта запиту при використанні Media Request API.

---

## 5. Розширені API: V4L2 Control API, Events API та Media Request API

### 5.1. V4L2 Control API та атомарні розширені контроли

Заголовочний файл ядра: `<linux/videodev2.h>`

Слугує для налаштування динамічних параметрів зображення (експозиція, підсилення, баланс білого, дзеркальне відображення).

:::tabs
```c
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <string.h>

struct v4l2_ext_control ext_ctrls[2];
memset(ext_ctrls, 0, sizeof(ext_ctrls));

ext_ctrls[0].id = V4L2_CID_EXPOSURE;
ext_ctrls[0].value = 250;

ext_ctrls[1].id = V4L2_CID_ANALOGUE_GAIN;
ext_ctrls[1].value = 16;

struct v4l2_ext_controls ctrls;
memset(&ctrls, 0, sizeof(ctrls));
ctrls.ctrl_class = V4L2_CTRL_CLASS_USER;
ctrls.count = 2;
ctrls.controls = ext_ctrls;

if (ioctl(video_fd, VIDIOC_S_EXT_CTRLS, &ctrls) < 0) {
    /* Обробка помилки атомарного встановлення кластера контролів */
}
```
```cpp
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <array>
#include <system_error>

std::array<v4l2_ext_control, 2> ext_ctrls{};
ext_ctrls[0].id = V4L2_CID_EXPOSURE;
ext_ctrls[0].value = 250;

ext_ctrls[1].id = V4L2_CID_ANALOGUE_GAIN;
ext_ctrls[1].value = 16;

v4l2_ext_controls ctrls{};
ctrls.ctrl_class = V4L2_CTRL_CLASS_USER;
ctrls.count = static_cast<uint32_t>(ext_ctrls.size());
ctrls.controls = ext_ctrls.data();

if (::ioctl(video_fd, VIDIOC_S_EXT_CTRLS, &ctrls) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_S_EXT_CTRLS failed");
}
```
:::

---

### 5.2. Асинхронний подійний фреймворк V4L2 (Events API)

Підсистема V4L2 підтримує асинхронне сповіщення користувацького простору про зміни стану пристрою (динамічна зміна роздільної здатності кадру, зміна значення controls під дією 3A-алгоритмів).

:::tabs
```c
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <string.h>

/* 1. Підписка на подію зміни джерела (Source Change) */
struct v4l2_event_subscription sub;
memset(&sub, 0, sizeof(sub));
sub.type = V4L2_EVENT_SOURCE_CHANGE;

if (ioctl(video_fd, VIDIOC_SUBSCRIBE_EVENT, &sub) < 0) {
    /* Обробка помилки підписки */
}

/* 2. Отримання події з черги ядра */
struct v4l2_event ev;
memset(&ev, 0, sizeof(ev));
if (ioctl(video_fd, VIDIOC_DQEVENT, &ev) == 0) {
    if (ev.type == V4L2_EVENT_SOURCE_CHANGE) {
        printf("Source resolution change event received!\n");
    }
}
```
```cpp
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <system_error>

v4l2_event_subscription sub{};
sub.type = V4L2_EVENT_SOURCE_CHANGE;

if (::ioctl(video_fd, VIDIOC_SUBSCRIBE_EVENT, &sub) < 0) {
    throw std::system_error(errno, std::generic_category(), "SUBSCRIBE_EVENT failed");
}

v4l2_event ev{};
if (::ioctl(video_fd, VIDIOC_DQEVENT, &ev) == 0) {
    if (ev.type == V4L2_EVENT_SOURCE_CHANGE) {
        // Обробка асинхронної зміни конфігурації
    }
}
```
:::

---

### 5.3. Media Request API

Заголовочний файл ядра: `<linux/media.h>`

Дозволяє зв'язувати конфігураційні зміни кадр-в-кадр із відповідними буферами пам'яті.

:::tabs
```c
#include <linux/media.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <stdio.h>

int req_fd = -1;
if (ioctl(media_fd, MEDIA_IOC_REQUEST_ALLOC, &req_fd) < 0) {
    perror("MEDIA_IOC_REQUEST_ALLOC помилка");
}

/* Відправка запиту у чергу */
if (ioctl(req_fd, MEDIA_REQUEST_IOC_QUEUE) < 0) {
    perror("MEDIA_REQUEST_IOC_QUEUE помилка");
}

/* Скидання стану об'єкта запиту */
ioctl(req_fd, MEDIA_REQUEST_IOC_REINIT);
close(req_fd);
```
```cpp
#include <linux/media.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <system_error>

int req_fd = -1;
if (::ioctl(media_fd, MEDIA_IOC_REQUEST_ALLOC, &req_fd) < 0) {
    throw std::system_error(errno, std::generic_category(), "REQUEST_ALLOC failed");
}

if (::ioctl(req_fd, MEDIA_REQUEST_IOC_QUEUE) < 0) {
    ::close(req_fd);
    throw std::system_error(errno, std::generic_category(), "REQUEST_QUEUE failed");
}

::ioctl(req_fd, MEDIA_REQUEST_IOC_REINIT);
::close(req_fd);
```
:::

#### Системні виклики над `req_fd`
- `ioctl(req_fd, MEDIA_REQUEST_IOC_QUEUE)` — Відправка накопиченого запиту з налаштуваннями controls та буфером кадру в апаратну чергу ядра.
- `ioctl(req_fd, MEDIA_REQUEST_IOC_REINIT)` — Скидання стану об'єкта запиту для його повторного використання в наступному циклі кадрів.

---

## 6. Системні коди помилок та крайові випадки

Виклики `ioctl()` підсистеми V4L2 та Media Controller у разі помилки повертають `-1` та встановлюють змінну `errno`. Нижче наведено зведену матрицю системних кодов помилок:

| Код помилки | Назва в POSIX | Типові причини виникнення у V4L2 / Media Controller |
|---|---|---|
| `EBUSY` | Device or resource busy | Спроба зміни формату (`VIDIOC_S_FMT`) або зв'язку (`MEDIA_IOC_SETUP_LINK`) під час активного відеопотоку (`STREAMON`). |
| `EINVAL` | Invalid argument | Передано невідомий `type`, некоректні розміри кадру, неіснуючі індекси pads чи несумісний `memory` режим. |
| `EAGAIN` | Resource temporarily unavailable | Неблокуючий режим відкриття (`O_NONBLOCK`): у черзі при `VIDIOC_DQBUF` немає жодного готового кадру. |
| `EPIPE` | Broken pipe | При `VIDIOC_STREAMON`: граф Media Controller не залікований або розрив у форматах шини між сусідніми pads. |
| `ENOMEM` | Cannot allocate memory | Ядро не змогло виділити фізично неперервну пам'ять (CMA) при `VIDIOC_REQBUFS`. |
| `ENOTTY` | Inappropriate ioctl for device | Файловий дескриптор відкритий для символьного пристрою, який не підтримує дану категорію ioctl. |
| `EFAULT` | Bad address | Передано недійсний користувацький вказівник у структурі (наприклад `ptr_entities == NULL`). |
| `ENODEV` | No such device | Апаратний пристрій було відключено від системи (наприклад USB-вебкамеру витягнуто з роз'єму). |
| `EPERM` | Operation not permitted | Спроба модифікувати зв'язок з прапорцем `MEDIA_LNK_FL_IMMUTABLE`. |

---

## 7. Життєвий цикл буферів у фреймворку Videobuf2 (vb2)

Усі операції з пам'яттю V4L2 проходять через внутрішній фреймворк ядра **Videobuf2 (vb2)**. Кожен буфер у черзі проходить чітку послідовність станів:

```
 [ Unallocated ]
        │  (VIDIOC_REQBUFS)
        ▼
 [ DEQUEUED ] ──────(VIDIOC_QBUF)──────► [ QUEUED ]
        ▲                                     │  (Hardware DMA Start)
        │                                     ▼
 [ DQBUF ] ◄───────(DMA Finished)─────── [ ACTIVE ]
```

1. **`DEQUEUED`:** Буфер виділений в ОЗП, але належить користувацькому простору. Процес може читати/писати дані у масив.
2. **`QUEUED`:** Буфер переданий ядру через `VIDIOC_QBUF` і поміщений у внутрішню чергу драйвера. Доступ ЦП до пам'яті заборонено.
3. **`ACTIVE`:** Буфер переданий безпосередньо у DMA-контролер апаратури для запису поточного кадру.
4. **`DONE`:** Апаратура згенерувала переривання завершення кадру. Буфер повернувся у чергу готовності і очікує виклику `VIDIOC_DQBUF`.

При експорті буфера у DMA-BUF через `VIDIOC_EXPBUF` ядро створює прив'язку `struct dma_buf` до внутрішньої сторінки пам'яті `struct page`. У разі прямого прочитання пам'яті з боку ЦП необхідно забезпечити синхронізацію кєш-пам'яті L1/L2 через системний виклик `ioctl(dmabuf_fd, DMABUF_IOCTL_SYNC, &sync_arg)`.

---

## 8. Механізм апаратного узгодження форматів (Format Negotiation)

Підсистема Media Controller вимагає строгого узгодження форматів шини на кожному етапі мультимедійного конвеєра. Процес конфігурування графа виконується у такому чіткому порядку:

1. **Конфігурація сенсора камери (`/dev/v4l2-subdev0`):** Застосунок встановлює бажаний шинний формат (`MEDIA_BUS_FMT_SBGGR10_1X10` або `MEDIA_BUS_FMT_UYVY8_2X8`) та роздільну здатність на джерельному майданчику (Source Pad 0).
2. **Конфігурація приймача CSI-2 (`/dev/v4l2-subdev1`):** Застосунок передає той самий шинний формат на вхідний Sink Pad 0 приймача CSI-2. Драйвер приймача автоматично узгоджує внутрішній формат на своєму Source Pad 1 у підготовчому контексті `v4l2_subdev_state`.
3. **Конфігурація процесора ISP (`/dev/v4l2-subdev2`):** На Sink Pad ISP передається сирий Bayer RAW формат від CSI-2, а на Source Pad ISP налаштовується формат YUV 4:2:2 чи YUV 4:2:0.
4. **Конфігурація DMA-вузла V4L2 (`/dev/video0`):** Застосунок відкриває пристрій захоплення та викликає `VIDIOC_S_FMT` із піксельним форматом (наприклад `V4L2_PIX_FMT_UYVY` чи `V4L2_PIX_FMT_NV12`), який відповідає вихідному шинному формату Source Pad ISP.

Спроба викликати `VIDIOC_STREAMON` при незбігу форматів між підключеними майданчиками або при вимкнених зв'язках поверне помилку `EPIPE` ("Broken pipe").

---

## 9. Аналіз часових характеристик та системних затримок (Latency & Profiling)

При побудові високонавантажених відеопотоків у реальному часі критичним фактором є аналіз затримок на кожному виклику ioctl:

1. **`VIDIOC_REQBUFS`:** Одноразовий важкий виклик. Залежно від типу аллокатора ядра (CMA або Scatter-Gather), виділення неперервного фізичного блоку пам'яті під чотири буфери 4K може тривати від 2 до 15 мілісекунд через необхідність виконання дефрагментації сторінок пам'яті ОЗП.
2. **`VIDIOC_EXPBUF`:** Легковажний виклик (~5–15 мікросекунд). Створює анонімний `dma_buf` файл та експортує дескриптор.
3. **`VIDIOC_QBUF` / `VIDIOC_DQBUF`:** Високочастотні операції цикла стримінгу (~1–3 мікросекунди). Вони не виконують копіювання пам'яті, а лише переставляють вказівники на `struct vb2_buffer` у списку готовності та оновлюють стани апаратних регістрів.
4. **`poll()`:** Час очікування визначається виключно кадровою частотою сенсора (наприклад 33.3 мс для 30 FPS чи 16.6 мс для 60 FPS).

Точна оцінка міжкадрових затримок реалізується аналізом поля `timestamp` у структурі `v4l2_buffer`. Ядро заповнює це поле значенням системного монотонного годинника `CLOCK_MONOTONIC` у момент генерування переривання апаратурою, що виключає вплив затримок виклику `DQBUF` у користувацькому просторі.

---

## 10. Повний розширений приклад конфігурування графа та обробки потоку

Нижче наведено повні та готові до компіляції приклади конфігурування графа Media Controller, виділення буферів, експорту DMA-BUF та читання кадрів з обробкою неблокуючого виклику `poll()`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <poll.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/media.h>
#include <linux/v4l2-subdev.h>
#include <linux/videodev2.h>

#define BUF_COUNT 4

struct buffer_entry {
    void *start;
    size_t length;
    int dbuf_fd;
};

int main(void) {
    int media_fd = -1, subdev_fd = -1, video_fd = -1;
    struct buffer_entry buffers[BUF_COUNT];
    memset(buffers, 0, sizeof(buffers));

    /* 1. Відкриття media-контролера та зчитування топології */
    media_fd = open("/dev/media0", O_RDWR);
    if (media_fd < 0) {
        perror("open /dev/media0 failed");
        return EXIT_FAILURE;
    }

    struct media_device_info minfo;
    memset(&minfo, 0, sizeof(minfo));
    if (ioctl(media_fd, MEDIA_IOC_DEVICE_INFO, &minfo) < 0) {
        perror("MEDIA_IOC_DEVICE_INFO failed");
        goto cleanup;
    }
    printf("[C] Connected to media dev: %s (%s)\n", minfo.driver, minfo.model);

    /* 2. Налаштування субпристрою */
    subdev_fd = open("/dev/v4l2-subdev0", O_RDWR);
    if (subdev_fd < 0) {
        perror("open /dev/v4l2-subdev0 failed");
        goto cleanup;
    }

    struct v4l2_subdev_format sfmt;
    memset(&sfmt, 0, sizeof(sfmt));
    sfmt.pad = 0;
    sfmt.which = V4L2_SUBDEV_FORMAT_ACTIVE;
    sfmt.format.width = 1920;
    sfmt.format.height = 1080;
    sfmt.format.code = MEDIA_BUS_FMT_UYVY8_2X8;
    sfmt.format.field = V4L2_FIELD_NONE;

    if (ioctl(subdev_fd, VIDIOC_SUBDEV_S_FMT, &sfmt) < 0) {
        perror("VIDIOC_SUBDEV_S_FMT failed");
        goto cleanup;
    }

    /* 3. Налаштування вузла захоплення /dev/video0 */
    video_fd = open("/dev/video0", O_RDWR | O_NONBLOCK);
    if (video_fd < 0) {
        perror("open /dev/video0 failed");
        goto cleanup;
    }

    struct v4l2_format vfmt;
    memset(&vfmt, 0, sizeof(vfmt));
    vfmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    vfmt.fmt.pix.width = 1920;
    vfmt.fmt.pix.height = 1080;
    vfmt.fmt.pix.pixelformat = V4L2_PIX_FMT_UYVY;
    vfmt.fmt.pix.field = V4L2_FIELD_NONE;

    if (ioctl(video_fd, VIDIOC_S_FMT, &vfmt) < 0) {
        perror("VIDIOC_S_FMT failed");
        goto cleanup;
    }

    /* 4. Запит буферів у ядра */
    struct v4l2_requestbuffers req;
    memset(&req, 0, sizeof(req));
    req.count = BUF_COUNT;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;

    if (ioctl(video_fd, VIDIOC_REQBUFS, &req) < 0) {
        perror("VIDIOC_REQBUFS failed");
        goto cleanup;
    }

    for (size_t i = 0; i < req.count; ++i) {
        struct v4l2_buffer buf;
        memset(&buf, 0, sizeof(buf));
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;

        if (ioctl(video_fd, VIDIOC_QUERYBUF, &buf) < 0) {
            perror("VIDIOC_QUERYBUF failed");
            goto cleanup;
        }

        buffers[i].length = buf.length;
        buffers[i].start = mmap(NULL, buf.length, PROT_READ | PROT_WRITE,
                                MAP_SHARED, video_fd, buf.m.offset);
        if (buffers[i].start == MAP_FAILED) {
            perror("mmap failed");
            goto cleanup;
        }

        struct v4l2_exportbuffer expbuf;
        memset(&expbuf, 0, sizeof(expbuf));
        expbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        expbuf.index = i;
        expbuf.flags = O_CLOEXEC | O_RDWR;

        if (ioctl(video_fd, VIDIOC_EXPBUF, &expbuf) < 0) {
            perror("VIDIOC_EXPBUF failed");
            goto cleanup;
        }
        buffers[i].dbuf_fd = expbuf.fd;
    }

    /* 5. Запуск потоку та зчитування одного кадру через poll */
    for (size_t i = 0; i < req.count; ++i) {
        struct v4l2_buffer buf;
        memset(&buf, 0, sizeof(buf));
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;
        ioctl(video_fd, VIDIOC_QBUF, &buf);
    }

    enum v4l2_buf_type stype = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if (ioctl(video_fd, VIDIOC_STREAMON, &stype) < 0) {
        perror("VIDIOC_STREAMON failed");
        goto cleanup;
    }

    struct pollfd pfd;
    pfd.fd = video_fd;
    pfd.events = POLLIN;

    int poll_res = poll(&pfd, 1, 2000); /* Очікування 2 секунди */
    if (poll_res > 0 && (pfd.revents & POLLIN)) {
        struct v4l2_buffer dqbuf;
        memset(&dqbuf, 0, sizeof(dqbuf));
        dqbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        dqbuf.memory = V4L2_MEMORY_MMAP;

        if (ioctl(video_fd, VIDIOC_DQBUF, &dqbuf) == 0) {
            printf("[C] Captured frame seq %u, size %u bytes\n", dqbuf.sequence, dqbuf.bytesused);
        }
    } else {
        printf("[C] Poll timeout or error\n");
    }

    ioctl(video_fd, VIDIOC_STREAMOFF, &stype);

cleanup:
    for (size_t i = 0; i < BUF_COUNT; ++i) {
        if (buffers[i].dbuf_fd >= 0) close(buffers[i].dbuf_fd);
        if (buffers[i].start && buffers[i].start != MAP_FAILED) {
            munmap(buffers[i].start, buffers[i].length);
        }
    }
    if (video_fd >= 0) close(video_fd);
    if (subdev_fd >= 0) close(subdev_fd);
    if (media_fd >= 0) close(media_fd);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/media.h>
#include <linux/v4l2-subdev.h>
#include <linux/videodev2.h>

class ScopedFd {
    int fd_{-1};
public:
    explicit ScopedFd(int fd = -1) : fd_(fd) {}
    ~ScopedFd() { reset(); }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;

    ScopedFd(ScopedFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

class MmappedBuffer {
    void* start_{MAP_FAILED};
    size_t length_{0};
    ScopedFd dbuf_fd_;

public:
    MmappedBuffer() = default;
    MmappedBuffer(void* start, size_t length, ScopedFd dbuf_fd)
        : start_(start), length_(length), dbuf_fd_(std::move(dbuf_fd)) {}

    ~MmappedBuffer() {
        if (start_ != MAP_FAILED && start_ != nullptr) {
            ::munmap(start_, length_);
        }
    }

    MmappedBuffer(const MmappedBuffer&) = delete;
    MmappedBuffer& operator=(const MmappedBuffer&) = delete;

    MmappedBuffer(MmappedBuffer&&) noexcept = default;
    MmappedBuffer& operator=(MmappedBuffer&&) noexcept = default;

    [[nodiscard]] void* data() const noexcept { return start_; }
    [[nodiscard]] size_t size() const noexcept { return length_; }
    [[nodiscard]] int dmabuf_fd() const noexcept { return dbuf_fd_.get(); }
};

class MediaIoctlPipeline {
    ScopedFd media_fd_;
    ScopedFd subdev_fd_;
    ScopedFd video_fd_;
    std::vector<MmappedBuffer> buffers_;

    static void check_ioctl(int res, const std::string& msg) {
        if (res < 0) {
            throw std::system_error(errno, std::generic_category(), msg);
        }
    }

public:
    void init(const std::string& media_dev, const std::string& subdev_dev, const std::string& video_dev) {
        media_fd_.reset(::open(media_dev.c_str(), O_RDWR));
        check_ioctl(media_fd_.valid() ? 0 : -1, "Open " + media_dev);

        subdev_fd_.reset(::open(subdev_dev.c_str(), O_RDWR));
        check_ioctl(subdev_fd_.valid() ? 0 : -1, "Open " + subdev_dev);

        video_fd_.reset(::open(video_dev.c_str(), O_RDWR | O_NONBLOCK));
        check_ioctl(video_fd_.valid() ? 0 : -1, "Open " + video_dev);
    }

    void configure_pipeline() {
        v4l2_subdev_format sfmt{};
        sfmt.pad = 0;
        sfmt.which = V4L2_SUBDEV_FORMAT_ACTIVE;
        sfmt.format.width = 1920;
        sfmt.format.height = 1080;
        sfmt.format.code = MEDIA_BUS_FMT_UYVY8_2X8;
        sfmt.format.field = V4L2_FIELD_NONE;
        check_ioctl(::ioctl(subdev_fd_.get(), VIDIOC_SUBDEV_S_FMT, &sfmt), "VIDIOC_SUBDEV_S_FMT");

        v4l2_format vfmt{};
        vfmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        vfmt.fmt.pix.width = 1920;
        vfmt.fmt.pix.height = 1080;
        vfmt.fmt.pix.pixelformat = V4L2_PIX_FMT_UYVY;
        vfmt.fmt.pix.field = V4L2_FIELD_NONE;
        check_ioctl(::ioctl(video_fd_.get(), VIDIOC_S_FMT, &vfmt), "VIDIOC_S_FMT");

        v4l2_requestbuffers req{};
        req.count = 4;
        req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        req.memory = V4L2_MEMORY_MMAP;
        check_ioctl(::ioctl(video_fd_.get(), VIDIOC_REQBUFS, &req), "VIDIOC_REQBUFS");

        buffers_.reserve(req.count);

        for (uint32_t i = 0; i < req.count; ++i) {
            v4l2_buffer buf{};
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            buf.memory = V4L2_MEMORY_MMAP;
            buf.index = i;
            check_ioctl(::ioctl(video_fd_.get(), VIDIOC_QUERYBUF, &buf), "VIDIOC_QUERYBUF");

            void* ptr = ::mmap(nullptr, buf.length, PROT_READ | PROT_WRITE, MAP_SHARED, video_fd_.get(), buf.m.offset);
            if (ptr == MAP_FAILED) {
                throw std::system_error(errno, std::generic_category(), "mmap failed");
            }

            v4l2_exportbuffer expbuf{};
            expbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            expbuf.index = i;
            expbuf.flags = O_CLOEXEC | O_RDWR;
            check_ioctl(::ioctl(video_fd_.get(), VIDIOC_EXPBUF, &expbuf), "VIDIOC_EXPBUF");

            buffers_.emplace_back(ptr, buf.length, ScopedFd(expbuf.fd));
        }
    }

    void stream_one_frame() {
        for (uint32_t i = 0; i < buffers_.size(); ++i) {
            v4l2_buffer buf{};
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            buf.memory = V4L2_MEMORY_MMAP;
            buf.index = i;
            check_ioctl(::ioctl(video_fd_.get(), VIDIOC_QBUF, &buf), "VIDIOC_QBUF");
        }

        v4l2_buf_type stype = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        check_ioctl(::ioctl(video_fd_.get(), VIDIOC_STREAMON, &stype), "VIDIOC_STREAMON");

        pollfd pfd{};
        pfd.fd = video_fd_.get();
        pfd.events = POLLIN;

        int poll_res = ::poll(&pfd, 1, 2000);
        if (poll_res > 0 && (pfd.revents & POLLIN)) {
            v4l2_buffer dqbuf{};
            dqbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            dqbuf.memory = V4L2_MEMORY_MMAP;
            check_ioctl(::ioctl(video_fd_.get(), VIDIOC_DQBUF, &dqbuf), "VIDIOC_DQBUF");

            std::cout << "[C++] Frame sequence: " << dqbuf.sequence << ", payload: " << dqbuf.bytesused << " bytes\n";
        } else {
            std::cerr << "[C++] Timeout waiting for frame\n";
        }

        check_ioctl(::ioctl(video_fd_.get(), VIDIOC_STREAMOFF, &stype), "VIDIOC_STREAMOFF");
    }
};

int main() {
    try {
        MediaIoctlPipeline app;
        app.init("/dev/media0", "/dev/v4l2-subdev0", "/dev/video0");
        app.configure_pipeline();
        app.stream_one_frame();
    } catch (const std::exception& ex) {
        std::cerr << "Pipeline error: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::
