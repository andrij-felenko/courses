# 📋 Інтерфейс властивостей DRM/KMS та структурування Atomic Commit

Інтерфейс Atomic KMS у просторі користувача реалізовано через бібліотеку `libdrm` (заголовні файли `<xf86drm.h>` та `<xf86drmMode.h>`). В основі Atomic API лежить уніфікована модель «Об'єкт — Властивість» (Object-Property Model). Кожен елемент дисплейного конвеєра ядра репрезентовано як об'єкт DRM із унікальним 32-бітним ідентифікатором (`object_id`). Станом об'єкта керують за допомогою числових властивостей (`property_id`), значеннями яких можуть бути цілі числа, бітові маски, ідентифікатори інших об'єктів або двійкові блоки даних (Blobs).

---

## 1. Типологія властивостей DRM (Property Types)

Властивості в підсистемі DRM поділяються на кілька типів, кожен з яких визначає діапазон та семантику допустимих значень:

1. **Unsigned Integer (Беззнакове ціле):** Пряме 64-бітне число (наприклад, координати `CRTC_X`, `CRTC_Y`).
2. **Signed Integer (Знакове ціле):** Значення зі знаком (наприклад, від'ємні зсуви оверлейних площин).
3. **Boolean:** Прапорець включення або виключення (`0` або `1`, наприклад `ACTIVE` для CRTC чи `VRR_ENABLED`).
4. **Enum (Перелічувальний тип):** Набір фіксованих іменованих констант (наприклад, `type` для площини чи `DPMS` для конектора).
5. **Bitmask (Бітова маска):** Комбінація кількох прапорців (наприклад, можливі кути повороту `rotation`).
6. **Object ID:** Вказівник на інший об'єкт KMS (наприклад, `FB_ID` вказує на фреймбуфер, `CRTC_ID` — на CRTC).
7. **Blob ID:** Ідентифікатор двійкового блоку даних у ядрі (наприклад, `MODE_ID` містить структуру таймінгів розгортки, `EDID` — паспорт монітора).

Властивості також мають прапорці доступу: **Immutable** (незмінна властивість, доступна лише для читання з ядра, як-от `IN_FORMATS` або `type`) та **Mutable** (доступна для запису з простору користувача).

---

## 2. Повна специфікація об'єктів KMS та їхніх властивостей

### 2.1. Об'єкт Plane (Площина сканування)

Площина відповідає за вибірку та первинну колірну обробку піксельних даних з кадрового буфера в пам'яті.

| Назва властивості | Тип | Режим | Опис та семантика значень |
| :--- | :--- | :--- | :--- |
| `FB_ID` | Object ID | Mutable | Ідентифікатор фреймбуфера `drmModeFB2`. Передача `0` вимикає площину та звільняє її апаратний шар. |
| `CRTC_ID` | Object ID | Mutable | Ідентифікатор CRTC, на який проектується площина. Передача `0` від'єднує площину від конвеєра. |
| `CRTC_X`, `CRTC_Y` | Signed Int | Mutable | Координати лівого верхнього кута прямокутника відображення на екрані в пікселях. |
| `CRTC_W`, `CRTC_H` | Unsigned Int | Mutable | Ширина та висота прямокутника відображення на екрані в пікселях. |
| `SRC_X`, `SRC_Y` | Fixed 16.16 | Mutable | Координати кута вибірки з буфера у форматі Q16.16 (значення зсунуте на `<< 16`). |
| `SRC_W`, `SRC_H` | Fixed 16.16 | Mutable | Ширина та висота прямокутника вибірки з буфера у форматі Q16.16 (дозволяє субпіксельний кропінг). |
| `IN_FORMATS` | Blob ID | Immutable | Ідентифікатор блоку даних зі списком підтримуваних DRM-форматів пікселів та модифікаторів макета пам'яті (Layout Modifiers). |
| `type` | Enum | Immutable | Тип площини: `0 = Overlay`, `1 = Primary`, `2 = Cursor`. |
| `rotation` | Bitmask | Mutable | Маска повороту й віддзеркалення: `BIT(0) = ROTATE_0`, `BIT(1) = ROTATE_90`, `BIT(2) = ROTATE_180`, `BIT(3) = ROTATE_270`, `BIT(4) = REFLECT_X`, `BIT(5) = REFLECT_Y`. |
| `COLOR_ENCODING` | Enum | Mutable | Стандарт колірного простору YUV: `ITU-R BT.601 YCbCr` або `ITU-R BT.709 YCbCr`. |
| `COLOR_RANGE` | Enum | Mutable | Динамічний діапазон YUV: `YCbCr limited range` (16-235) або `YCbCr full range` (0-255). |
| `alpha` | Unsigned Int | Mutable | Загальна прозорість площини (Plane Alpha) від `0` (прозоре) до `65535` (повністю покривне). |
| `pixel blend mode` | Enum | Mutable | Алгоритм змішування альфа-каналу: `None`, `Pre-multiplied`, `Coverage`. |
| `IN_FENCE_FD` | Signed Int | Mutable | Файловий дескриптор вхідного фенсу явного синхронізму (Explicit Sync). Драйвер затримує сканування площини до реліза фенсу. |

---

### 2.2. Об'єкт CRTC (Дисплейний контролер)

CRTC відповідає за об'єднання площин, формування кадрової розгортки та підключення генераторів частот (PLL).

| Назва властивості | Тип | Режим | Опис та семантика значень |
| :--- | :--- | :--- | :--- |
| `MODE_ID` | Blob ID | Mutable | Ідентифікатор двійкового блоку даних, що містить структуру `drmModeModeInfo` (параметри розгортки). `0` вимикає розгортку. |
| `ACTIVE` | Boolean | Mutable | `1` — CRTC увімкнений та генерує кадрову розгортку; `0` — CRTC перебуває у стані глибокого енергозбереження. |
| `OUT_FENCE_PTR` | Pointer | Mutable | Вказівник у пам'яті простору користувача (`uint64_t*`), куди ядро записує FD вихідного фенсу (Sync File FD), який сигналізує про завершення сканування поточного кадру. |
| `VRR_ENABLED` | Boolean | Mutable | `1` — увімкнути підтримку змінної частоти оновлення (Variable Refresh Rate / Adaptive-Sync / FreeSync). |
| `DEGAMMA_LUT` | Blob ID | Mutable | Двійковий блок із таблицею зворотного дегаммування пікселів перед змішуванням площин. |
| `DEGAMMA_LUT_SIZE` | Unsigned Int | Immutable | Кількість елементів у таблиці дегаммування, яку підтримує апаратне забезпечення. |
| `CTM` | Blob ID | Mutable | Двійковий блок із матрицею перетворення кольорів 3×3 (Color Transformation Matrix) у форматі Q3.32 для колірної корекції. |
| `GAMMA_LUT` | Blob ID | Mutable | Двійковий блок із таблицею вихідної гамма-корекції після змішування площин. |
| `GAMMA_LUT_SIZE` | Unsigned Int | Immutable | Кількість елементів у таблиці вихідного гаммування. |

---

### 2.3. Об'єкт Connector (Фізичний роз'єм)

Конектор визначає фізичний пристрій виводу, стан підключення та параметри передачі сигналу.

| Назва властивості | Тип | Режим | Опис та семантика значень |
| :--- | :--- | :--- | :--- |
| `CRTC_ID` | Object ID | Mutable | Ідентифікатор CRTC, з якого конектор приймає згенерований потік пікселів. |
| `DPMS` | Enum | Mutable | Режим керування живленням монітора: `0 = On`, `1 = Standby`, `2 = Suspend`, `3 = Off`. |
| `EDID` | Blob ID | Immutable | Двійковий блок із паспортом монітора EDID/CTA-861, зчитаним по шині I2C/DDC. |
| `HDR_OUTPUT_METADATA` | Blob ID | Mutable | Двійковий блок із метаданими статичного HDR (структура `hdr_output_metadata` відповідно до SMPTE ST 2086). |
| `max bpc` | Unsigned Int | Mutable | Максимальна глибина кольору на канал (Bits Per Component): `6`, `8`, `10`, `12` біт. |
| `Colorspace` | Enum | Mutable | Цільовий колірний простір сигналізації: `Default`, `BT2020_RGB`, `BT2020_YCC`, `opRGB`. |
| `content protection` | Enum | Mutable | Стан захисту контенту HDCP: `Undesired`, `Desired`, `Enabled`. |
| `WRITEBACK_FB_ID` | Object ID | Mutable | Ідентифікатор фреймбуфера для конекторів типу Writeback (дозволяє захоплювати відрендерене зображення назад у пам'ять). |

---

## 3. C та C++ API керування атомарними транзакціями у libdrm

### 3.1. Ініціалізація та звільнення контейнера запиту

Атомарна транзакція збирається у спеціальному об'єкті `drmModeAtomicReqPtr`, який представляє проміжний буфер запиту у просторі користувача:

:::tabs
```c
/* C: Ручне створення та звільнення об'єкта запиту */
#include <xf86drm.h>
#include <xf86drmMode.h>

drmModeAtomicReqPtr req = drmModeAtomicAlloc();
if (!req) {
    /* Помилка виділення пам'яті */
}

/* Використання запиту... */

drmModeAtomicFree(req);
```
```cpp
// C++: Управління ресурсом через std::unique_ptr та custom deleter
#include <memory>
#include <stdexcept>
#include <xf86drm.h>
#include <xf86drmMode.h>

struct AtomicReqDeleter {
    void operator()(drmModeAtomicReqPtr req) const noexcept {
        if (req) ::drmModeAtomicFree(req);
    }
};

using AtomicReqPtr = std::unique_ptr<drmModeAtomicReq, AtomicReqDeleter>;

AtomicReqPtr create_atomic_request() {
    AtomicReqPtr req(::drmModeAtomicAlloc());
    if (!req) throw std::bad_alloc();
    return req;
}
```
:::

---

### 3.2. Наповнення запиту змінами властивостей

Додавання кожної зміни стану виконується через уніфікований виклик `drmModeAtomicAddProperty`:

:::tabs
```c
/* C: Прямий виклик libdrm API */
int ret = drmModeAtomicAddProperty(req, object_id, property_id, value);
if (ret < 0) {
    /* Помилка накопичення запиту */
}
```
```cpp
// C++: Безпечний обгортковий метод класу AtomicTransaction
class AtomicTransaction {
    AtomicReqPtr req_;
public:
    AtomicTransaction() : req_(create_atomic_request()) {}

    void add_property(uint32_t obj_id, uint32_t prop_id, uint64_t val) {
        if (::drmModeAtomicAddProperty(req_.get(), obj_id, prop_id, val) < 0) {
            throw std::runtime_error("Не вдалося додати властивість у атомарний запит");
        }
    }
};
```
:::

---

### 3.3. Виконання транзакції через `drmModeAtomicCommit`

Після збірки всіх змін запит передається ядру через один ioctl:

:::tabs
```c
/* C: Прямий ioctl коміт у ядро */
uint32_t flags = DRM_MODE_ATOMIC_NONBLOCK | DRM_MODE_PAGE_FLIP_EVENT;
int ret = drmModeAtomicCommit(fd, req, flags, user_data);
```
```cpp
// C++: Виконання транзакції з поверненням std::expected або винятком
int commit_transaction(int fd, drmModeAtomicReqPtr req, uint32_t flags, void* user_data) {
    int ret = ::drmModeAtomicCommit(fd, req, flags, user_data);
    if (ret < 0) {
        throw std::system_error(-ret, std::generic_category(), "drmModeAtomicCommit failed");
    }
    return ret;
}
```
:::

#### Прапорці `flags` для `drmModeAtomicCommit`:

1. `DRM_MODE_ATOMIC_TEST_ONLY`: Режим «сухого прогону» (dry-run validation). Ядро моделює конфігурацію, перевіряє клоки, смугу пам'яті та ліміти апаратури. Жодні регістри GPU не змінюються. При успіху повертається `0`, при неможливості виконати запит — `-EINVAL` або `-EBUSY`.
2. `DRM_MODE_ATOMIC_NONBLOCK`: Асинхронне (неблокуюче) виконання. Виклик негайно повертає управління, а ядро планує оновлення регістрів GPU на наступному VBlank.
3. `DRM_MODE_ATOMIC_ALLOW_MODESET`: Дозволяє ядру виконувати повну перебудову конвеєра (Full Modeset). Така операція може призводити до тимчасового вимкнення сигналів розгортки (гасіння екрана). Якщо прапорець не встановлено, а конфігурація вимагає перебудови CRTC чи Connector, виклик повертає помилку `-EINVAL`.
4. `DRM_MODE_PAGE_FLIP_EVENT`: Запитує генерування події `DRM_EVENT_FLIP_COMPLETE` у дескриптор `fd` після того, як новий кадр дійсно почне відображатися на моніторі.

---

## 4. Створення та життєвий цикл блоків даних (Property Blobs)

Для передачі складних структур даних (наприклад, відеорежиму `drmModeModeInfo`) використовуються двійкові блоки пам'яті у ядрі:

:::tabs
```c
/* C: Ручне створення та видалення Blob ID */
uint32_t blob_id = 0;
drmModeModeInfo mode_info = /* параметри розгортки */;

if (drmModeCreatePropertyBlob(fd, &mode_info, sizeof(mode_info), &blob_id) == 0) {
    drmModeAtomicAddProperty(req, crtc_id, prop_mode_id, blob_id);
    /* Виконання коміту... */
    drmModeDestroyPropertyBlob(fd, blob_id);
}
```
```cpp
// C++: RAII обгортка для двійкового блоку пам'яті ядра
template <typename T>
class PropertyBlob {
    int fd_;
    uint32_t id_{0};
public:
    PropertyBlob(int fd, const T& data) : fd_(fd) {
        if (::drmModeCreatePropertyBlob(fd_, &data, sizeof(T), &id_) != 0) {
            throw std::runtime_error("Не вдалося створити DRM Property Blob у ядрі");
        }
    }
    ~PropertyBlob() {
        if (id_) ::drmModeDestroyPropertyBlob(fd_, id_);
    }
    [[nodiscard]] uint32_t id() const noexcept { return id_; }
};
```
:::

---

## 5. Диспатчеризація подій VBlank у просторі користувача

При використанні прапорця `DRM_MODE_PAGE_FLIP_EVENT` простір користувача отримує сповіщення про завершення кадрового оновлення через дескриптор `fd`:

:::tabs
```c
/* C: Виклик drmHandleEvent із використанням функціонального коллбека */
drmEventContext evctx = {
    .version = DRM_EVENT_CONTEXT_VERSION,
    .page_flip_handler2 = page_flip_handler
};
drmHandleEvent(fd, &evctx);
```
```cpp
// C++: Лямбда-інтеграція з обробником подій VBlank
drmEventContext evctx{};
evctx.version = DRM_EVENT_CONTEXT_VERSION;
evctx.page_flip_handler2 = [](int fd, unsigned int seq, unsigned int tv_sec, 
                              unsigned int tv_usec, unsigned int crtc_id, void* user_data) {
    auto* listener = static_cast<VBlankListener*>(user_data);
    listener->on_page_flip(seq, crtc_id);
};
::drmHandleEvent(fd, &evctx);
```
:::

Сигнатура 콜бек-функції `page_flip_handler2`:

:::tabs
```c
/* C: Сигнатура кадрового обробника в libdrm */
void page_flip_handler(
    int fd,
    unsigned int sequence,  /* Монотонний лічильник кадрів VBlank */
    unsigned int tv_sec,    /* Секунди за монотонним годинником CLOCK_MONOTONIC */
    unsigned int tv_usec,   /* Мікросекунди за монотонним годинником */
    unsigned int crtc_id,   /* ID CRTC, який завершив розгортку кадру */
    void *user_data         /* Вказівник користувача, переданий у drmModeAtomicCommit */
);
```
```cpp
// C++: Типізований обробник через std::function
using PageFlipHandler = std::function<void(
    int fd,
    unsigned int sequence,
    unsigned int tv_sec,
    unsigned int tv_usec,
    unsigned int crtc_id,
    void* user_data
)>;
```
:::

Отримання події `page_flip_handler2` сигналізує композитору, що попередній фреймбуфер більше не зчитується відеокартою і його можна повторно використовувати для рендерингу наступного кадру.
