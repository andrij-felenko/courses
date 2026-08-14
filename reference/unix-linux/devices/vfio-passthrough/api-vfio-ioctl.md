# 📋 Інтерфейс ioctl та структури даних підсистеми VFIO

Підсистема VFIO (Virtual Function I/O) надає програмам простору користувача універсальний та безпечний двоуровневий інтерфейс керування апаратними пристроями через системний виклик `ioctl`. Цей довідник містить повноцінний опис програмного контракту ядра Linux: файлові дескриптори, константи, коди системних запитів, структури даних та обробку помилок.

---

## 1. Архітектурна ієрархія файлових дескрипторів

Програмна взаємодія з підсистемою VFIO будується на послідовному відкритті трьох різновидів файлових дескрипторів у просторі користувача. Кожен дескриптор уособлює свій рівень абстракції системних ресурсів.

```
/dev/vfio/vfio (Container FD)
       │
       ├── /dev/vfio/15 (Group FD)
       │         │
       │         └── VFIO_GROUP_GET_DEVICE_FD ──> Device FD (0000:01:00.0)
       │
       └── /dev/vfio/16 (Group FD)
                 │
                 └── VFIO_GROUP_GET_DEVICE_FD ──> Device FD (0000:02:00.0)
```

### 1.1. Контейнерний дескриптор (Container FD)
Створюється через відкриття головного символьного пристрою `/dev/vfio/vfio` за допомогою системного виклику `open(2)`. Контейнер є верховним об'єктом абстракції IOMMU. Він уособлює єдиний домен трансляції адрес IOMMU та спільний простір віртуальних адрес I/O (**IOVA — I/O Virtual Address**). Один контейнер може об'єднувати кілька IOMMU-груп, якщо апаратна конфігурація дозволяє їм ділити спільні таблиці сторінок трансляції IOMMU.

### 1.2. Груповий дескриптор (Group FD)
Створюється відкриттям спеціального пристрою `/dev/vfio/<group_id>`, де `<group_id>` відповідає номеру IOMMU-групи в системі (наприклад `/dev/vfio/15`). Цей дескриптор репрезентує нероздільну апаратну одиницю ізоляції. Файл групи з'являється у файловій системі лише тоді, коли ядро виявило відповідну IOMMU-групу. Відкрити дескриптор можна лише тоді, коли абсолютно всі пристрої цієї групи відв'язані від звичайних драйверів ядра хоста й прив'язані до `vfio-pci` чи не мають драйвера зовсім.

### 1.3. Дескриптор пристрою (Device FD)
На відміну від контейнера та групи, дескриптор пристрою не відкривається прямим шляхом у файловій системі. Процес отримує анонімний дескриптор пристрою через системний виклик `ioctl` над відкритим груповим дескриптором. Дескриптор пристрою дає можливість безпосередньо мапити базові адресні регістри (BAR) у пам'ять процесу через `mmap(2)`, читати та записувати конфігураційний простір PCI через `read(2)`/`write(2)`, а також налаштовувати сигналізацію переривань.

---

## 2. Команди ioctl контейнера (`/dev/vfio/vfio`)

Контейнерний дескриптор обробляє виклики, пов'язані з перевіркою версії підсистеми, вибором бекенду IOMMU та керуванням таблицями трансляції DMA.

| Системна команда ioctl | Тип аргументу | Значення повернення та опис |
| :--- | :--- | :--- |
| `VFIO_GET_API_VERSION` | `NULL` | Повертає ціле число — версію API (поточна версія ядра `VFIO_API_VERSION = 0`). |
| `VFIO_CHECK_EXTENSION` | `unsigned long` | Повертає `1`, якщо вказаний тип IOMMU підтримується ядром, і `0`, якщо ні. |
| `VFIO_SET_IOMMU` | `unsigned long` | Прив'язує обраний тип IOMMU (наприклад `VFIO_TYPE1_IOMMU`) до контейнера. |
| `VFIO_IOMMU_GET_INFO` | `struct vfio_iommu_type1_info*` | Повертає властивості IOMMU-домену (розмір сторінки, підтримувані маски IOVA). |
| `VFIO_IOMMU_MAP_DMA` | `struct vfio_iommu_type1_dma_map*` | Закріплює фізичні сторінки RAM хоста й додає запис трансляції IOVA -> HPA. |
| `VFIO_IOMMU_UNMAP_DMA` | `struct vfio_iommu_type1_dma_unmap*` | Видаляє трансляцію IOVA та розкріплює фізичні сторінки оперативної пам'яті. |

### 2.1. Детальна специфікація структури `vfio_iommu_type1_dma_map`

Для виклику `VFIO_IOMMU_MAP_DMA` користувацький процес повинен заповнити структури даних. Для порівняння наведено специфікацію мовами C та C++:

:::tabs
```c
struct vfio_iommu_type1_dma_map {
    __u32 argsz;       /* Розмір структури sizeof(struct vfio_iommu_type1_dma_map) */
    __u32 flags;       /* Прапорці прав доступу DMA */
    __u64 vaddr;       /* Віртуальна адреса процесу хоста (HVA — Host Virtual Address) */
    __u64 iova;        /* Бажана віртуальна адреса пристрою (IOVA або GPA) */
    __u64 size;        /* Розмір ділянки пам'яті у байтах (мусить бути кратним розміру сторінки) */
};
```
```cpp
#include <cstdint>
#include <linux/vfio.h>

// В ідіоматичному C++20 структура використовується із сучасними типами та зв'язаною розіменовкою
namespace vfio::api {
    using DmaMapRequest = ::vfio_iommu_type1_dma_map;

    constexpr DmaMapRequest make_dma_map(uint64_t hva, uint64_t iova, uint64_t size, uint32_t flags) noexcept {
        return DmaMapRequest{
            .argsz = sizeof(DmaMapRequest),
            .flags = flags,
            .vaddr = hva,
            .iova = iova,
            .size = size
        };
    }
}
```
:::

Допустимі значення бітових прапорців `flags`:
* `VFIO_DMA_MAP_FLAG_READ` — пристрій має дозвіл читати дані з цієї ділянки пам'яті хоста via DMA.
* `VFIO_DMA_MAP_FLAG_WRITE` — пристрій має дозвіл записувати дані в цю ділянку пам'яті хоста via DMA.

#### Механізм виклику та обробка помилок
Під час виконання `VFIO_IOMMU_MAP_DMA` ядро Linux викликає внутрішню функцію `pin_user_pages()`. Ядро перевіряє, чи не перевищує розмір виділеної пам'яті поточний ліміт `RLIMIT_MEMLOCK` процесу. Якщо ліміт перевищено, `ioctl` повертає помилку `-1` із встановленням `errno = EPERM` або `ENOMEM`. Сторінки маркуються як непридатні для витіснення у swap (pinned memory). Після цього ядро будує апаратні сторінкові таблиці Intel VT-d або AMD-Vi.

---

## 3. Команди ioctl IOMMU-групи (`/dev/vfio/<group_id>`)

Груповий дескриптор керує перевіркою готовності пристроїв та їх прив'язкою до контейнера.

| Системна команда ioctl | Тип аргументу | Значення повернення та опис |
| :--- | :--- | :--- |
| `VFIO_GROUP_GET_STATUS` | `struct vfio_group_status*` | Повертає поточні прапорці стану апаратної IOMMU-групи. |
| `VFIO_GROUP_SET_CONTAINER` | `int *container_fd` | Додає групу до вказаного відкритого контейнера. |
| `VFIO_GROUP_UNSET_CONTAINER`| `int *container_fd` | Від'єднує групу від контейнера. |
| `VFIO_GROUP_GET_DEVICE_FD` | `const char *bdf_name` | Повертає новий файловий дескриптор `device_fd` за PCI BDF адресою. |

### 3.1. Структура `vfio_group_status` та перевірка цілісності

:::tabs
```c
struct vfio_group_status {
    __u32 argsz;       /* Розмір структури sizeof(struct vfio_group_status) */
    __u32 flags;       /* Бітові прапорці стану групи */
};
```
```cpp
#include <cstdint>
#include <linux/vfio.h>

namespace vfio::api {
    using GroupStatus = ::vfio_group_status;

    constexpr GroupStatus make_group_status() noexcept {
        return GroupStatus{
            .argsz = sizeof(GroupStatus),
            .flags = 0
        };
    }
}
```
:::

Значення бітових прапорців:
* `VFIO_GROUP_FLAGS_VIABLE` (1 << 0) — означає, що абсолютно всі пристрої, які входять до цієї IOMMU-групи, безпечно зв'язані з драйверами VFIO або позбавлені драйверів. Якщо прапорець дорівнює `0`, спроба приєднати групу до контейнера поверне помилку `EINVAL`.
* `VFIO_GROUP_FLAGS_CONTAINER_SET` (1 << 1) — вказує, що група вже успішно приєднана до VFIO-контейнера.

---

## 4. Команди ioctl пристрою (`device_fd`)

Дескриптор пристрою надає прямий доступ до регістрів апаратного забезпечення.

| Системна команда ioctl | Тип аргументу | Значення повернення та опис |
| :--- | :--- | :--- |
| `VFIO_DEVICE_GET_INFO` | `struct vfio_device_info*` | Повертає кількість доступних регіонів (BAR) та векторів переривань. |
| `VFIO_DEVICE_GET_REGION_INFO` | `struct vfio_region_info*` | Зчитує детальні геометричні параметри регіону (розмір, зсув, прапорці). |
| `VFIO_DEVICE_GET_IRQ_INFO` | `struct vfio_irq_info*` | Зчитує параметри конкретного типу переривань (INTx, MSI, MSI-X). |
| `VFIO_DEVICE_SET_IRQS` | `struct vfio_irq_set*` | Підключає або вимикає генерацію переривань на дескриптори `eventfd`. |
| `VFIO_DEVICE_RESET` | `NULL` | Ініціює апаратне скидання пристрою (PCI Function Level Reset — FLR). |

### 4.1. Індекси регіонів PCI та структура `vfio_region_info`

Для PCI/PCIe пристроїв ядро виділяє стандартні індекси регіонів:
* `VFIO_PCI_BAR0_REGION_INDEX` (0) .. `VFIO_PCI_BAR5_REGION_INDEX` (5) — Базові адресні регістри (BAR0–BAR5).
* `VFIO_PCI_ROM_REGION_INDEX` (6) — Пам'ять Expansion ROM пристрою.
* `VFIO_PCI_CONFIG_REGION_INDEX` (7) — Конфігураційний простір PCI (PCI Configuration Space, 256 байтів для PCI, 4 КБ для PCIe).
* `VFIO_PCI_VGA_REGION_INDEX` (8) — Регіон сумісності VGA MMIO/IO.

:::tabs
```c
struct vfio_region_info {
    __u32 argsz;       /* Розмір структури */
    __u32 flags;       /* Властивості регіону (VFIO_REGION_INFO_FLAG_READ, WRITE, MMAP) */
    __u32 index;       /* Індекс регіону (наприклад VFIO_PCI_BAR0_REGION_INDEX) */
    __u32 cap_offset;  /* Зсув до додаткових розширень (capabilities) */
    __u64 size;        /* Розмір регіону у байтах */
    __u64 offset;      /* Зсув у файлі device_fd для виклику mmap() */
};
```
```cpp
#include <cstdint>
#include <linux/vfio.h>

namespace vfio::api {
    using RegionInfo = ::vfio_region_info;

    constexpr RegionInfo make_region_info(uint32_t index) noexcept {
        return RegionInfo{
            .argsz = sizeof(RegionInfo),
            .flags = 0,
            .index = index,
            .cap_offset = 0,
            .size = 0,
            .offset = 0
        };
    }
}
```
:::

Якщо `flags` містить `VFIO_REGION_INFO_FLAG_MMAP`, процес може виконати `mmap()` за вказаним зсувом `offset` для отримання прямого покажчика в оперативну пам'ять хоста на MMIO-регістри пристрою.

### 4.2. Налаштування переривань через `struct vfio_irq_set`

Переривання пристрою передаються у простір користувача через механізм `eventfd(2)`. Для налаштування використовується структура:

:::tabs
```c
struct vfio_irq_set {
    __u32 argsz;       /* Загальний розмір структури + розширення data[] */
    __u32 flags;       /* Прапорці дії та типу даних */
    __u32 index;       /* Індекс переривання (VFIO_PCI_INTX_IRQ_INDEX, VFIO_PCI_MSI_IRQ_INDEX, VFIO_PCI_MSIX_IRQ_INDEX) */
    __u32 start;       /* Початковий вектор (зазвичай 0) */
    __u32 count;       /* Кількість векторів */
    __u8  data[];      /* Масив файлових дескрипторів eventfd */
};
```
```cpp
#include <cstdint>
#include <linux/vfio.h>

namespace vfio::api {
    using IrqSet = ::vfio_irq_set;

    constexpr IrqSet make_irq_set(uint32_t index, uint32_t start, uint32_t count, uint32_t flags) noexcept {
        return IrqSet{
            .argsz = sizeof(IrqSet) + count * sizeof(int),
            .flags = flags,
            .index = index,
            .start = start,
            .count = count
        };
    }
}
```
:::

Прапорці керування перериваннями `flags`:
* `VFIO_IRQ_SET_DATA_EVENTFD` — масив `data[]` містить масив цілих чисел `int fd[]`, які є файловими дескрипторами `eventfd`.
* `VFIO_IRQ_SET_ACTION_TRIGGER` — пов'язує генерацію переривання пристроєм із сигналізацією у відповідний `eventfd`.
* `VFIO_IRQ_SET_ACTION_MASK` / `UNMASK` — маскує або розмасковує вказані вектори переривань.

Коли пристрій генерує переривання MSI-X, ядро Linux перехоплює його й викликає `eventfd_signal()`. В результаті дескриптор `eventfd` у просторі користувача стає доступним для читання, або пробуджує цикл очікування `epoll_wait()`, надаючи можливість користувацькому драйверу миттєво відреагувати на подію заліза.
