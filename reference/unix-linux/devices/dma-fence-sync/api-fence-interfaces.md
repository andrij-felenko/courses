# 📋 Контракт огорож: dma_fence, sync_file і властивості атомарної заявки

Тут зібрано точні імена, поля, номери викликів і повернені значення, якими огорожі описані в коді — з боку ядра й з боку програми. Біля кожного пункту стоїть версія ядра, у якій він з'явився; версії перевірені прямо по дереву — символ є в теґу `vX.Y` і його немає в попередньому теґу.

## Об'єкт у ядрі: `struct dma_fence`

```c
/* include/linux/dma-fence.h — під цим іменем з v4.10 (доти struct fence) */
struct dma_fence {
    spinlock_t                 *lock;   /* спільний із чергою, що сигналізує */
    const struct dma_fence_ops *ops;
    union {                             /* три стадії життя, ніколи разом    */
        struct list_head cb_list;       /* доки не спрацювала: спостерігачі  */
        ktime_t          timestamp;     /* після падіння: мить сигналу       */
        struct rcu_head  rcu;           /* після звільнення                  */
    };
    u64            context;   /* ідентифікатор апаратної черги */
    u64            seqno;     /* місце в цій черзі             */
    unsigned long  flags;
    struct kref    refcount;
    int            error;     /* 0 або від'ємний errno */
};
```

Об'єднання (`union`) — не економія на дрібницях, а твердження: доки огорожа не спрацювала, часу сигналу ще немає, а доки на неї хтось дивиться, звільняти нічого. Три поля не можуть знадобитися одночасно.

| прапорець у `flags` | значення |
|---|---|
| `DMA_FENCE_FLAG_SIGNALED_BIT` | спрацювала; ставиться рівно раз |
| `DMA_FENCE_FLAG_TIMESTAMP_BIT` | у `timestamp` лежить мить сигналу |
| `DMA_FENCE_FLAG_ENABLE_SIGNAL_BIT` | програмну сигналізацію ввімкнено (з'явився перший спостерігач) |
| `DMA_FENCE_FLAG_USER_BITS` | звідси й вище — біти, вільні для драйвера |

## `struct dma_fence_ops`: що зобов'язаний дати драйвер

| поле | обов'язкове | сигнатура | вимоги до виклику |
|---|---|---|---|
| `get_driver_name` | так | `const char *(*)(struct dma_fence *)` | зовуть із налагоджувального друку, зокрема з атомарного контексту: без сну й без замків |
| `get_timeline_name` | так | `const char *(*)(struct dma_fence *)` | те саме; ім'я черги, а не окремої порції роботи |
| `enable_signaling` | ні | `bool (*)(struct dma_fence *)` | зовуть із `fence->lock` і вимкненими перериваннями; повертає `false`, якщо огорожа вже впала |
| `signaled` | ні | `bool (*)(struct dma_fence *)` | швидка перевірка без сну; має право повернути `false` для вже спрацьованої |
| `wait` | ні, застаріле | `signed long (*)(struct dma_fence *, bool intr, signed long timeout)` | без нього діє `dma_fence_default_wait()` — новим драйверам своє не потрібне |
| `release` | ні | `void (*)(struct dma_fence *)` | може виконатися в контексті переривання; звільняти через `dma_fence_free()` |
| `set_deadline` | ні, з v6.4 | `void (*)(struct dma_fence *, ktime_t)` | підказка про бажаний строк; без сну, зовуть багато разів |

Крім зворотних викликів, у структурі є поле `use_64bit_seqno` (з v5.2): коли воно `false`, номери порівнюються 32-бітною арифметикою з обгортанням, коли `true` — повними 64 бітами. Шкалам потрібне друге.

## Виклики над огорожею

| виклик | повертає | контекст |
|---|---|---|
| `void dma_fence_init(f, ops, lock, context, seqno)` | — | лічильник посилань стає 1 |
| `u64 dma_fence_context_alloc(unsigned num)` | початок діапазону контекстів | раз на чергу, не на порцію роботи |
| `signed long dma_fence_wait_timeout(f, bool intr, signed long timeout)` | залишок таймауту в тиках, `0` — вийшов час, `-ERESTARTSYS` — перервано сигналом | спить; таймаут у тиках ядра |
| `signed long dma_fence_wait(f, bool intr)` | `0` — дочекалися, `-ERESTARTSYS` — перервано | обгортка з `MAX_SCHEDULE_TIMEOUT` |
| `int dma_fence_add_callback(f, cb, func)` | `0` — додано, **`-ENOENT` — уже спрацювала**, `-EINVAL` — помилка | зворотний виклик виконається в атомарному контексті або в контексті переривання |
| `bool dma_fence_remove_callback(f, cb)` | `true` — знято до спрацювання | після `false` виклик уже стався або от-от станеться |
| `int dma_fence_signal(f)` | `0`, або від'ємне, якщо огорожа вже спрацювала | бере `fence->lock`, гасить переривання і звідти ж кличе всіх спостерігачів |
| `int dma_fence_signal_locked(f)` | те саме | замок уже в руках у того, хто кличе |
| `void dma_fence_set_error(f, int error)` | — | лише **до** сигналу, лише від'ємний `errno` |
| `bool dma_fence_is_signaled(f)` | стан | дешева перевірка |
| `void dma_fence_set_deadline(f, ktime_t)` | — | з v6.4; абсолютна мить за монотонним годинником |
| `bool dma_fence_begin_signalling(void)` / `dma_fence_end_signalling(bool)` | ознака вкладеності | з v5.9, лише під `CONFIG_LOCKDEP`: позначає критичну секцію сигналізації |

> 🔧 **Навіщо це.** Два рядки цієї таблиці мовчки псують код. Перший — `-ENOENT` від `dma_fence_add_callback()`: коли огорожа вже впала, зворотний виклик **не станеться ніколи**, і той, хто перевіряє тільки на `< 0`, чекатиме вічно замість того, щоб одразу зробити свою роботу. Другий — порядок `dma_fence_set_error()` перед `dma_fence_signal()`: після сигналу позначку помилки ставити пізно, бо спостерігачі вже прокинулися й уже прочитали `error` як нуль. Обидва місця не падають на стенді — вони дають зависання чи мовчазно зіпсований кадр у чужого користувача.

Зворотні виклики виконуються там, де сталася сигналізація, — часто в обробнику переривання. Усе, що вони роблять, мусить бути дозволене в атомарному контексті: жодного сну, жодного виділення пам'яті, замки лише з тих, які [ядро дозволяє брати з перерваного контексту](book:unix-linux/kernel-locking) — тобто спінлоки, а не мʼютекси.

## `dma_resv`: список огорож усередині буфера

```c
/* include/linux/dma-resv.h — цей вигляд із v5.19 */
enum dma_resv_usage {
    DMA_RESV_USAGE_KERNEL,     /* переїзд буфера, робота самого ядра */
    DMA_RESV_USAGE_WRITE,      /* запис, поданий із простору користувача */
    DMA_RESV_USAGE_READ,       /* читання, подане з простору користувача */
    DMA_RESV_USAGE_BOOKKEEP,   /* облік: неявно на це не чекають        */
};
```

Порядок `KERNEL < WRITE < READ < BOOKKEEP`, і правило одне: **коли в резервації просять огорожі одного рівня, разом із ними повертаються огорожі всіх нижчих**. Звідси випливає підміна, на якій легко спіткнутися: рівень, який ви називаєте при очікуванні, — це не ваш намір, а верхня межа того, що вас обходить.

| маю намір | називаю рівень | дочекаюся |
|---|---|---|
| читати буфер | `DMA_RESV_USAGE_WRITE` | `KERNEL` + `WRITE` |
| писати в буфер | `DMA_RESV_USAGE_READ` | `KERNEL` + `WRITE` + `READ` |
| синхронізуватися самому | `DMA_RESV_USAGE_KERNEL` | лише `KERNEL` |

Саме цю інверсію робить помічник `dma_resv_usage_rw(bool write)`: для запису він віддає `DMA_RESV_USAGE_READ`, для читання — `DMA_RESV_USAGE_WRITE`.

| виклик | призначення |
|---|---|
| `int dma_resv_reserve_fences(obj, unsigned int num)` | заздалегідь виділити місце під `num` огорож — щоб на шляху сигналізації нічого не виділялося |
| `void dma_resv_add_fence(obj, fence, usage)` | додати огорожу з позначкою; замок резервації має бути в руках |
| `long dma_resv_wait_timeout(obj, usage, bool intr, unsigned long timeout)` | дочекатися всього рівня `usage` й нижче |
| `bool dma_resv_test_signaled(obj, usage)` | перевірити без сну |
| `int dma_resv_get_singleton(obj, usage, struct dma_fence **out)` | згорнути весь рівень в одну огорожу |
| `dma_resv_for_each_fence(cursor, obj, usage, fence)` | обхід списку |
| `int dma_resv_lock(obj, struct ww_acquire_ctx *ctx)` / `dma_resv_unlock(obj)` | замок типу ww-mutex; `ctx` потрібен, коли беруть кілька буферів одразу, інакше зустрічні захоплення заклиняться |

До v5.19 замість позначок були окремі `dma_resv_add_excl_fence()` і `dma_resv_add_shared_fence()`; у старих драйверах вони ще трапляються.

## `sync_file`: огорожа як дескриптор

Усередині ядра (з v4.7) потрібні рівно два виклики:

```c
struct sync_file *sync_file_create(struct dma_fence *fence); /* бере СВОЄ посилання */
struct dma_fence *sync_file_get_fence(int fd);   /* нове посилання або NULL;
                                                    звільняти dma_fence_put() */
/* віддати назовні: */
int fd = get_unused_fd_flags(O_CLOEXEC);
fd_install(fd, sync_file->file);
```

З боку програми це звичайний [файловий дескриптор](book:unix-linux/file-descriptor): `poll()` віддає `POLLIN`, коли огорожа спрацювала, тож чекати на неї можна в спільному циклі подій разом із сокетами й таймерами ([select, poll, epoll](book:unix-linux/select-poll-epoll)). Помилки `poll()` не показує — спрацьована з помилкою виглядає готовою; справжній стан дає лише `SYNC_IOC_FILE_INFO`.

```c
/* include/uapi/linux/sync_file.h;  SYNC_IOC_MAGIC == '>' */
struct sync_merge_data { char name[32]; __s32 fd2; __s32 fence;
                         __u32 flags; __u32 pad; };
struct sync_fence_info { char obj_name[32]; char driver_name[32];
                         __s32 status; __u32 flags; __u64 timestamp_ns; };
struct sync_file_info  { char name[32]; __s32 status; __u32 flags;
                         __u32 num_fences; __u32 pad; __u64 sync_fence_info; };
struct sync_set_deadline { __u64 deadline_ns; __u64 pad; };
```

| виклик [ioctl](book:unix-linux/ioctl-interface) | номер і структура | з версії | як уживати |
|---|---|---|---|
| `SYNC_IOC_MERGE` | `_IOWR('>', 3, struct sync_merge_data)` | v4.7 | `fd2` — другий дескриптор, у `fence` повертається новий; вхідні лишаються відкритими, закривати їх вам |
| `SYNC_IOC_FILE_INFO` | `_IOWR('>', 4, struct sync_file_info)` | v4.7 | два проходи: спершу з `num_fences = 0` дізнатися кількість, потім із масивом за вказівником `sync_fence_info` |
| `SYNC_IOC_SET_DEADLINE` | `_IOW('>', 5, struct sync_set_deadline)` | v6.8 | `deadline_ns` — абсолютна мить за `CLOCK_MONOTONIC` ([час у ядрі](book:unix-linux/kernel-timekeeping)) |

`status` у `sync_file_info` і `sync_fence_info`: `0` — ще працює, `1` — спрацювала, від'ємне — спрацювала з помилкою. Поля `flags` і `pad` мусять бути нульові, інакше `-EINVAL`.

## Міст із [dma-buf](book:unix-linux/dma-buf) у явну синхронізацію

```c
/* include/uapi/linux/dma-buf.h;  DMA_BUF_BASE == 'b' */
struct dma_buf_export_sync_file { __u32 flags; __s32 fd; };
struct dma_buf_import_sync_file { __u32 flags; __s32 fd; };
```

| виклик | номер і структура | з версії |
|---|---|---|
| `DMA_BUF_IOCTL_EXPORT_SYNC_FILE` | `_IOWR('b', 2, struct dma_buf_export_sync_file)` | v6.0 |
| `DMA_BUF_IOCTL_IMPORT_SYNC_FILE` | `_IOW('b', 3, struct dma_buf_import_sync_file)` | v6.0 |

`flags` в обох — `DMA_BUF_SYNC_READ`, `DMA_BUF_SYNC_WRITE` або `DMA_BUF_SYNC_RW`; порожній набір і будь-який зайвий біт дають `-EINVAL`. А от значення прапорців у двох викликах різне, і це навмисно.

- **Вивантаження** розуміє прапорець як намір: `READ` означає «збираюся читати», тож ядро віддає рівень `WRITE` — самих записувачів. `WRITE` або `RW` означає «збираюся писати», і ядро віддає рівень `READ` — геть усе. Якщо чекати немає на що, повертається завжди готова огорожа-заглушка, а не помилка, тож дескриптор ви отримаєте в будь-якому разі.
- **Завантаження** розуміє прапорець буквально: `WRITE` кладе огорожу з позначкою `DMA_RESV_USAGE_WRITE`, `READ` — із позначкою `DMA_RESV_USAGE_READ`. Злиту огорожу ядро перед тим розкладає на складники й додає їх поодинці.

## Властивості атомарної заявки [DRM](book:unix-linux/drm-kms)

Обидві з'явилися у v4.10.

| властивість | на чому | тип | зміст |
|---|---|---|---|
| `IN_FENCE_FD` | площина | знаковий діапазон, `-1 … INT_MAX` | дескриптор `sync_file`, якого ядро дочекається, перш ніж показати вміст цієї площини; `-1` — чекати нема на що. Дескриптор лишається вашим, ядро його не закриває |
| `OUT_FENCE_PTR` | контролер (CRTC) | діапазон `__u64` | **вказівник** на ваше `__s32`, куди ядро запише номер нового дескриптора; огорожа спрацює після справжнього перемикання кадру |

Особливості, які виявляються не одразу: при `DRM_MODE_ATOMIC_TEST_ONLY` вхідна огорожа лише перевіряється на справність, а у вихідне поле лягає `-1`; те саме `-1` там опиниться, якщо заявку відхилено з будь-якої причини. Поєднати `DRM_MODE_ATOMIC_TEST_ONLY` з `DRM_MODE_PAGE_FLIP_EVENT` не можна — не буває приміряння з подією про виконання.

## `drm_syncobj`: комірка, яку можна перезаряджати

| виклик | номер | структура | з версії |
|---|---|---|---|
| `DRM_IOCTL_SYNCOBJ_CREATE` | `0xBF` | `drm_syncobj_create { __u32 handle, flags; }` | v4.13 |
| `DRM_IOCTL_SYNCOBJ_DESTROY` | `0xC0` | `drm_syncobj_destroy { __u32 handle, pad; }` | v4.13 |
| `DRM_IOCTL_SYNCOBJ_HANDLE_TO_FD` | `0xC1` | `drm_syncobj_handle` | v4.13 |
| `DRM_IOCTL_SYNCOBJ_FD_TO_HANDLE` | `0xC2` | `drm_syncobj_handle` | v4.13 |
| `DRM_IOCTL_SYNCOBJ_WAIT` | `0xC3` | `drm_syncobj_wait` | v4.14 |
| `DRM_IOCTL_SYNCOBJ_RESET` | `0xC4` | `drm_syncobj_array` | v4.14 |
| `DRM_IOCTL_SYNCOBJ_SIGNAL` | `0xC5` | `drm_syncobj_array` | v4.14 |
| `DRM_IOCTL_SYNCOBJ_TIMELINE_WAIT` | `0xCA` | `drm_syncobj_timeline_wait` | v5.2 |
| `DRM_IOCTL_SYNCOBJ_QUERY` | `0xCB` | `drm_syncobj_timeline_array` | v5.2 |
| `DRM_IOCTL_SYNCOBJ_TRANSFER` | `0xCC` | `drm_syncobj_transfer` | v5.2 |
| `DRM_IOCTL_SYNCOBJ_TIMELINE_SIGNAL` | `0xCD` | `drm_syncobj_timeline_array` | v5.2 |

Дескриптором об'єкт передається у двох різних значеннях, і плутати їх не можна:

```c
struct drm_syncobj_handle { __u32 handle; __u32 flags; __s32 fd; __u32 pad; };

#define DRM_SYNCOBJ_HANDLE_TO_FD_FLAGS_EXPORT_SYNC_FILE (1 << 0)  /* v4.14 */
#define DRM_SYNCOBJ_FD_TO_HANDLE_FLAGS_IMPORT_SYNC_FILE (1 << 0)  /* v4.14 */
```

Без прапорця дескриптор — це **сам об'єкт-комірка**: інший процес, отримавши його, бачитиме й майбутні перезарядки. З прапорцем через дескриптор ходить **лише поточний вміст комірки** у вигляді звичайного `sync_file`, тобто знімок однієї огорожі.

Групові виклики беруть не одну комірку, а масив; шкальні — ще й масив позначок до нього:

```c
struct drm_syncobj_create { __u32 handle; __u32 flags; };
#define DRM_SYNCOBJ_CREATE_SIGNALED (1 << 0)   /* народитися вже спрацьованим */

struct drm_syncobj_array          { __u64 handles; __u32 count_handles, pad; };
struct drm_syncobj_timeline_array { __u64 handles; __u64 points;
                                    __u32 count_handles, flags; };
```

`RESET` спорожняє комірки, `SIGNAL` кладе в них уже спрацьовану огорожу — обидва рятують, коли робота так і не була подана, а чекачі вже є. `QUERY` віддає поточну позначку кожної шкали, `TRANSFER` переносить огорожу з однієї комірки або позначки в іншу, не чекаючи на неї.

```c
struct drm_syncobj_timeline_wait {   /* v5.2 */
    __u64 handles;        /* масив дескрипторів об'єктів */
    __u64 points;         /* по позначці шкали на кожен  */
    __s64 timeout_nsec;   /* абсолютний час за CLOCK_MONOTONIC */
    __u32 count_handles, flags, first_signaled, pad;
    __u64 deadline_nsec;  /* v6.8 */
};

#define DRM_SYNCOBJ_WAIT_FLAGS_WAIT_ALL        (1 << 0)  /* v4.14 */
#define DRM_SYNCOBJ_WAIT_FLAGS_WAIT_FOR_SUBMIT (1 << 1)  /* v4.14 */
#define DRM_SYNCOBJ_WAIT_FLAGS_WAIT_AVAILABLE  (1 << 2)  /* v5.2  */
#define DRM_SYNCOBJ_WAIT_FLAGS_WAIT_DEADLINE   (1 << 3)  /* v6.8  */
```

`WAIT_FOR_SUBMIT` — саме той прапорець, задля якого шкали й заводили: без нього очікування на порожню комірку одразу дає `-EINVAL`, з ним очікувач засинає й прокидається, коли роботу подадуть пізніше. `WAIT_AVAILABLE` зупиняє чекача не на завершенні, а на появі огорожі в комірці. `WAIT_DEADLINE` перетворює `deadline_nsec` на підказку тому, хто сигналізуватиме, — те саме, що `SYNC_IOC_SET_DEADLINE` робить для окремого дескриптора, і не випадково обидва прийшли одним випуском.
