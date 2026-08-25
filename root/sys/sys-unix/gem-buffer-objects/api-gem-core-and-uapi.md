# 📋 Інтерфейс підсистеми GEM: структури ядра, UAPI та ioctl

Підсистема Graphics Execution Manager (GEM) у графічному ядрі Direct Rendering Manager (DRM) надає уніфікований набір структур даних, внутрішніх функцій керування життєвим циклом буферів і системних викликів `ioctl` для простору користувача. Розуміння цих контрактів необхідне для розробки графічних драйверів ядра, медіасерверів, віконних композиторів Wayland та низькорівневих графічних бібліотек Vulkan/OpenGL. Нижче систематизовано ключові типи даних, сигнатури ядра та визначення інтерфейсу користувача (UAPI).

## Базові структури ядра

Головною сутністю підсистеми є структура `struct drm_gem_object`, визначена в заголовковому файлі ядра `<drm/drm_gem.h>`. Вона представляє окремий графічний буфер і вкладається в драйверо-специфічні структури відеопам'яті.

```c
/* include/drm/drm_gem.h */
struct drm_gem_object {
    /** @refcount: Атомарний лічильник посилань ядра */
    struct kref refcount;

    /** @handle_count: Кількість відкритих числових дескрипторів у процесах */
    unsigned handle_count;

    /** @dev: Вказівник на батьківський графічний пристрій DRM */
    struct drm_device *dev;

    /** @filp: Анонімний файл tmpfs/shmem для виділення сторінок пам'яті */
    struct file *filp;

    /** @vma_node: Вузол дерева менеджера фальшивих зміщень mmap */
    struct drm_vma_offset_node vma_node;

    /** @size: Розмір буфера в байтах, вирівняний за межею PAGE_SIZE */
    size_t size;

    /** @funcs: Таблиця віртуальних методів драйвера для цього об'єкта */
    const struct drm_gem_object_funcs *funcs;

    /** @dma_buf: Прив'язаний експортований dma-buf або NULL */
    struct dma_buf *dma_buf;

    /** @import_attach: Вкладення при імпорті буфера з іншого драйвера */
    struct dma_buf_attachment *import_attach;

    /** @resv: Вказівник на об'єкт резервації та огорож синхронізації */
    struct dma_resv *resv;

    /** @_resv: Вбудований локальний об'єкт резервації за замовчуванням */
    struct dma_resv _resv;
};
```

Поле `refcount` відстежує кількість прямих посилань на структуру в адресному просторі ядра. Поки `refcount` більший за нуль, пам'ять під метадані об'єкта гарантовано не буде звільнена.

Поле `handle_count` веде окремий облік того, скільки разів цей об'єкт зареєстровано в таблицях дескрипторів простору користувача. Якщо один процес передає буфер іншому через механізм PRIME або декілька разів імпортує той самий дескриптор у власну таблицю, `handle_count` зростає, сигналізуючи драйверу про необхідність утримувати відповідні зв'язки в інтерфейсі користувача.

Вузол `vma_node` є елементом глобального червоно-чорного дерева менеджера `drm_vma_offset_manager`. Він закріплює за цим буфером унікальний фіктивний діапазон адрес розміром `size`, що усуває конфлікти при паралельному відображенні десятків тисяч буферів через спільний файловий дескриптор пристрою.

Таблиця операцій `struct drm_gem_object_funcs` описує поліморфну поведінку драйвера для конкретного типу графічного об'єкта:

```c
/* include/drm/drm_gem.h */
struct drm_gem_object_funcs {
    /** Звільнення специфічних для драйвера ресурсів при видаленні */
    void (*free)(struct drm_gem_object *obj);

    /** Викликається, коли процес створює новий числовий хендл */
    int (*open)(struct drm_gem_object *obj, struct drm_file *file);

    /** Викликається, коли процес закриває числовий хендл */
    void (*close)(struct drm_gem_object *obj, struct drm_file *file);

    /** Друк діагностичної інформації в debugfs */
    void (*print_info)(struct drm_printer *p, unsigned int indent,
                       const struct drm_gem_object *obj);

    /** Налаштування відображення сторінок VMA при виклику mmap */
    int (*mmap)(struct drm_gem_object *obj, struct vm_area_struct *vma);

    /** Створення scatter-gather таблиці для DMA передачі */
    struct sg_table *(*get_sg_table)(struct drm_gem_object *obj);

    /** Відображення буфера в безперервний простір ядра vmalloc */
    int (*vmap)(struct drm_gem_object *obj, struct iosys_map *map);

    /** Скасування відображення з адресного простору ядра */
    void (*vunmap)(struct drm_gem_object *obj, struct iosys_map *map);

    /** Фіксація фізичних сторінок у пам'яті (заборона витіснення) */
    int (*pin)(struct drm_gem_object *obj);

    /** Дозвіл на витіснення або переміщення сторінок */
    void (*unpin)(struct drm_gem_object *obj);
};
```

Для драйверів інтегрованих відеочипів та SoC у ядрі реалізовано стандартну обгортку `struct drm_gem_shmem_object` (`<drm/drm_gem_shmem_helper.h>`), яка автоматизує роботу з анонімними сторінками ОЗП:

```c
/* include/drm/drm_gem_shmem_helper.h */
struct drm_gem_shmem_object {
    struct drm_gem_object base;
    struct mutex pages_lock;
    struct page **pages;
    unsigned int pages_use_count;
    atomic_t pages_pin_count;
    struct sg_table *sgt;
    struct iosys_map map;
    unsigned int vaddr_use_count;
    bool is_iomem;
};
```

М'ютекс `pages_lock` захищає масив фізичних сторінок `pages` від стану перегонів при одночасному виклику сторінкового збою `fault()` з боку процесора та DMA-прив'язки з боку графічного прискорювача. Лічильник `pages_pin_count` гарантує, що під час активного апаратного сканування або рендерингу підсистема керування пам'яттю ядра не скине ці сторінки у swap-простір.

## Функції ядра для керування GEM-об'єктами

Підсистема DRM експортує набір допоміжних функцій для маніпуляції життєвим циклом об'єктів, таблицями хендлів та синхронізацією:

| Функція ядра | Опис призначення та контракт використання |
| :--- | :--- |
| `int drm_gem_object_init(struct drm_device *dev, struct drm_gem_object *obj, size_t size)` | Ініціалізує базові поля структури, встановлює розмір, початковий лічильник `kref = 1`, створює анонімний файл tmpfs та ініціалізує об'єкт резервації `_resv`. |
| `void drm_gem_object_release(struct drm_gem_object *obj)` | Звільняє системні ресурси (tmpfs файл, вузол vma_node, блокування), викликається перед остаточною деалокацією обгортки драйвера. |
| `void drm_gem_object_get(struct drm_gem_object *obj)` | Атомарно збільшує лічильник посилань `refcount` на одиницю при передачі покажчика в інші структури ядра. |
| `void drm_gem_object_put(struct drm_gem_object *obj)` | Зменшує `refcount`. Коли лічильник досягає нуля, автоматично викликає метод `funcs->free` або загальний деструктор. |
| `int drm_gem_handle_create(struct drm_file *file_priv, struct drm_gem_object *obj, uint32_t *handle)` | Реєструє об'єкт у таблиці xarray/idr відкритого дескриптора процесу, повертає новий 32-бітний числовий хендл та збільшує `kref`. |
| `int drm_gem_handle_delete(struct drm_file *file_priv, uint32_t handle)` | Видаляє хендл із таблиці процесу, викликає метод `funcs->close` та зменшує лічильник посилань об'єкта. |
| `struct drm_gem_object *drm_gem_object_lookup(struct drm_file *file_priv, uint32_t handle)` | Знаходить об'єкт за числовим хендлом у контексті процесу та повертає покажчик з інкрементованим `kref`. |
| `int drm_gem_create_mmap_offset(struct drm_gem_object *obj)` | Виділяє унікальний числовий діапазон у просторі `drm_vma_offset_manager` для подальшого виклику `mmap`. |
| `void drm_gem_free_mmap_offset(struct drm_gem_object *obj)` | Звільняє фальшиве зміщення з менеджера VMA при остаточному видаленні буфера. |
| `int drm_gem_prime_handle_to_fd(struct drm_device *dev, struct drm_file *file_priv, uint32_t handle, uint32_t flags, int *prime_fd)` | Експортує GEM-буфер, створюючи об'єкт `struct dma_buf` і новий файловий дескриптор PRIME у процесі. |
| `int drm_gem_prime_fd_to_handle(struct drm_device *dev, struct drm_file *file_priv, int prime_fd, uint32_t *handle)` | Імпортує переданий дескриптор dma-buf у локальну таблицю дескрипторів процесу, створюючи числовий хендл. |

Кожна з цих функцій суворо регулює правила володіння ресурсами. Наприклад, успішний виклик `drm_gem_object_lookup()` зобов'язує розробника драйвера викликати `drm_gem_object_put()` після завершення обробки запиту, щоб уникнути витоку пам'яті в ядрі.

## Інтерфейс користувача (DRM UAPI ioctl)

Простір користувача взаємодіє з підсистемою GEM через системні виклики `ioctl` над відкритим файловим дескриптором вузла `/dev/dri/cardX` (головний вузол KMS/керування) або `/dev/dri/renderD128` (вузол прямого рендерингу).

### 1. Виділення неперервного лінійного буфера (Dumb Buffer)

Для виділення базових буферів сканування дисплея використовується узагальнений механізм dumb-буферів:

```c
/* include/uapi/drm/drm_mode.h */
#define DRM_IOCTL_MODE_CREATE_DUMB DRM_IOWR(0xB2, struct drm_mode_create_dumb)
#define DRM_IOCTL_MODE_MAP_DUMB    DRM_IOWR(0xB3, struct drm_mode_map_dumb)
#define DRM_IOCTL_MODE_DESTROY_DUMB DRM_IOWR(0xB4, struct drm_mode_destroy_dumb)

struct drm_mode_create_dumb {
    __u32 height;      /* Вхід: висота в пікселях */
    __u32 width;       /* Вхід: ширина в пікселях */
    __u32 bpp;         /* Вхід: глибина кольору (біт на піксель, наприклад 32) */
    __u32 flags;       /* Вхід: службові прапорці (зазвичай 0) */
    __u32 handle;      /* Вихід: призначений числовий хендл GEM */
    __u32 pitch;       /* Вихід: довжина рядка в байтах із вирівнюванням */
    __u64 size;        /* Вихід: повний виділений розмір буфера в байтах */
};

struct drm_mode_map_dumb {
    __u32 handle;      /* Вхід: числовий хендл GEM-об'єкта */
    __u32 pad;         /* Вирівнювання структури */
    __u64 offset;      /* Вихід: фальшиве зміщення (fake offset) для mmap */
};

struct drm_mode_destroy_dumb {
    __u32 handle;      /* Вхід: числовий хендл буфера для знищення */
};
```

При виклику `DRM_IOCTL_MODE_CREATE_DUMB` ядро самостійно обчислює необхідне апаратне вирівнювання рядків (поле `pitch`) та загальний розмір (`size`), округлений до цілої кількості сторінок пам'яті. Повернений `handle` є валідним виключно в межах того файлового дескриптора, через який надійшов запит.

Виклик `DRM_IOCTL_MODE_MAP_DUMB` не виконує прямого виділення віртуальної пам'яті процесу, а повертає 64-бітне фальшиве зміщення `offset`. Програма передає це зміщення в системний виклик `mmap()`, де ядро використовує його як ключ для пошуку структури `drm_gem_object`.

### 2. Спільне використання буферів (PRIME)

Експорт та імпорт пам'яті здійснюються за допомогою уніфікованих системних викликів PRIME (`<drm/drm.h>`):

```c
/* include/uapi/drm/drm.h */
#define DRM_IOCTL_PRIME_HANDLE_TO_FD DRM_IOWR(0x2D, struct drm_prime_handle)
#define DRM_IOCTL_PRIME_FD_TO_HANDLE DRM_IOWR(0x2E, struct drm_prime_handle)

struct drm_prime_handle {
    __u32 handle;      /* Хендл GEM (вхід при експорті, вихід при імпорті) */
    __u32 flags;       /* Прапорці дескриптора: DRM_CLOEXEC | DRM_RDWR */
    __s32 fd;          /* Файловий дескриптор dma-buf (вихід при експорті, вхід при імпорті) */
};
```

Прапорець `DRM_CLOEXEC` гарантує, що отриманий дескриптор автоматично закриється при виконанні системного виклику `execve`, запобігаючи несанкціонованому витоку доступу до буфера у дочірні процеси. Прапорець `DRM_RDWR` запитує повні права доступу на читання та запис для імпортованого буфера.

### 3. Закриття дескриптора GEM

Коли процес завершує роботу з буфером, виділеним через спеціалізований драйверний ioctl, він викликає універсальний системний виклик закриття хендла:

```c
/* include/uapi/drm/drm.h */
#define DRM_IOCTL_GEM_CLOSE DRM_IOW(0x09, struct drm_gem_close)

struct drm_gem_close {
    __u32 handle;      /* Числовий хендл, що підлягає видаленню */
    __u32 pad;
};
```

Виклик `DRM_IOCTL_GEM_CLOSE` деактивує числовий ідентифікатор у контексті процесу. Якщо цей буфер не використовується іншими процесами та не прив'язаний до активного сканування екрана KMS, ядро ініціює повне видалення фізичних сторінок пам'яті.

## Синхронізація: механізм dma_resv ядра

Кожен GEM-об'єкт містить структуру `struct dma_resv`, що координує асинхронні операції читання та запису обладнання. Керування об'єктом резервації здійснюється через функції ядра (`<linux/dma-resv.h>`):

```c
/* Блокування об'єкта резервації перед модифікацією списку огорож */
void dma_resv_lock(struct dma_resv *obj, struct ww_acquire_ctx *ctx);
void dma_resv_unlock(struct dma_resv *obj);

/* Додавання огорожі асинхронної операції */
int dma_resv_add_fence(struct dma_resv *obj, struct dma_fence *fence,
                       enum dma_resv_usage usage);
```

Для запобігання взаємним блокуванням (англ. *deadlocks*), коли кілька паралельних черг GPU намагаються заблокувати однаковий набір буферів у різному порядку, `dma_resv` використовує спеціальний алгоритм м'ютексів очікування-поранення (англ. *Wound-Wait mutex*, `ww_mutex`). Контекст захоплення `ww_acquire_ctx` відстежує пріоритети транзакцій і примусово відкочує блокування молодшої транзакції у разі виникнення циклічної залежності.

Типи використання (`enum dma_resv_usage`):
* `DMA_RESV_USAGE_WRITE`: ексклюзивна огорожа запису (наприклад, виконання фрагментного шейдера GPU, що формує пікселі буфера);
* `DMA_RESV_USAGE_READ`: спільні огорожі читання (одночасний показ на дисплеї KMS, кодування відео або читання іншим клієнтом);
* `DMA_RESV_USAGE_BOOKKEEP`: внутрішній облік драйвера для контролю пам'яті без блокування звичайних читачів і записувачів.

## Явна синхронізація через drm_syncobj

Сучасні графічні API нового покоління (Vulkan, Direct3D 12) та композитори Wayland підтримують механізм явної синхронізації (англ. *explicit synchronization*) за допомогою об'єктів `drm_syncobj` (`<drm/drm.h>`):

```c
#define DRM_IOCTL_SYNCOBJ_CREATE        DRM_IOWR(0xBF, struct drm_syncobj_create)
#define DRM_IOCTL_SYNCOBJ_DESTROY       DRM_IOWR(0xC0, struct drm_syncobj_destroy)
#define DRM_IOCTL_SYNCOBJ_HANDLE_TO_FD  DRM_IOWR(0xC1, struct drm_syncobj_handle)
#define DRM_IOCTL_SYNCOBJ_FD_TO_HANDLE  DRM_IOWR(0xC2, struct drm_syncobj_handle)
#define DRM_IOCTL_SYNCOBJ_WAIT          DRM_IOWR(0xC3, struct drm_syncobj_wait)
#define DRM_IOCTL_SYNCOBJ_TIMELINE_WAIT DRM_IOWR(0xCA, struct drm_syncobj_timeline_wait)
```

Об'єкт `drm_syncobj` інкапсулює асинхронну огорожу `struct dma_fence` або 64-бітну часову шкалу (англ. *timeline points*). Програма в просторі користувача може передати дескриптор `syncobj` разом із пакетом команд, дозволяючи GPU очікувати сигналу завершення попередньої стадії без потреби блокування всього GEM-об'єкта на рівні ядра.

## Діагностика та трасування GEM у debugfs

Стан активних GEM-буферів ядра доступний для діагностики через віртуальну файлову систему `debugfs`:

* `/sys/kernel/debug/dri/0/gem_names`: таблиця глобальних експортованих імен буферів;
* `/sys/kernel/debug/dri/0/clients`: перелік відкритих файлових дескрипторів клієнтів із кількістю виділених буферів і споживанням пам'яті;
* `/sys/kernel/debug/dri/0/amdgpu_gem_info` або `/sys/kernel/debug/dri/0/i915_gem_objects`: детальна інформація драйвера про розміщення буферів у доменах VRAM, GTT та системного ОЗП.

Підсистема ядра також підтримує системні точки трасування `tracepoints` (`drm:drm_gem_open`, `drm:drm_gem_put`, `dma_fence:dma_fence_emit`), які можна аналізувати в реальному часі за допомогою інструментів `perf` або `ftrace` для виявлення затримок рендерингу та втрачених кадрів.

## Коди помилок системних викликів GEM

| Код помилки | Типова причина виникнення |
| :--- | :--- |
| `EINVAL` | Некоректні параметри виділення (нульова ширина/висота, непідтримувана глибина `bpp`, невірні прапорці) або недійсне зміщення `mmap`. |
| `ENOENT` | Заданий числовий хендл `handle` не існує в просторі імен відкритого `drm_file` поточного процесу. |
| `ENOMEM` | Недостатньо вільної відеопам'яті (VRAM) або системного ОЗП для задоволення запиту виділення буфера. |
| `EBUSY` | Буфер заблокований тривалою апаратною операцією або утримується в режимі монопольного використання. |
| `EACCES` | Спроба експорту або імпорту буфера з дескриптора без відповідних прав читання/запису (`PROT_READ`/`PROT_WRITE`). |
| `EOPNOTSUPP` | Драйвер пристрою не підтримує запитану операцію (наприклад, виклик `DRM_IOCTL_MODE_CREATE_DUMB` на суто обчислювальному вузлі `accel`). |
