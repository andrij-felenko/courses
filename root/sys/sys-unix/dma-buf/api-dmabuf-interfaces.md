# 📋 Контракт dma-buf: операції експортера й виклики з простору користувача

Це повний перелік того, що зобов'язаний реалізувати драйвер-експортер, що має право викликати драйвер-імпортер і які `ioctl` бачить на дескрипторі звичайна програма: підписи, обов'язковість кожної операції, дисципліна блокування, коди помилок. Довідка потрібна тому, що контракт розкладено по трьох заголовках і двох боках межі ядра, а половина правил тут — не про підписи, а про те, з яким узятим блокуванням дозволено кликати.

Підписи взято з ядра 6.x: `<linux/dma-buf.h>` — бік ядра, однойменний заголовок у складі uapi — `ioctl`-и, `<linux/dma-heap.h>` — купи. Де інтерфейс з'явився недавно, версію вказано окремо.

## Що реалізує експортер

```c
struct dma_buf_ops {
        bool cache_sgt_mapping;
        int  (*attach)(struct dma_buf *, struct dma_buf_attachment *);
        void (*detach)(struct dma_buf *, struct dma_buf_attachment *);
        int  (*pin)(struct dma_buf_attachment *attach);
        void (*unpin)(struct dma_buf_attachment *attach);
        struct sg_table *(*map_dma_buf)(struct dma_buf_attachment *,
                                        enum dma_data_direction);
        void (*unmap_dma_buf)(struct dma_buf_attachment *, struct sg_table *,
                              enum dma_data_direction);
        void (*release)(struct dma_buf *);
        int  (*begin_cpu_access)(struct dma_buf *, enum dma_data_direction);
        int  (*end_cpu_access)(struct dma_buf *, enum dma_data_direction);
        int  (*mmap)(struct dma_buf *, struct vm_area_struct *vma);
        int  (*vmap)(struct dma_buf *dmabuf, struct iosys_map *map);
        void (*vunmap)(struct dma_buf *dmabuf, struct iosys_map *map);
};
```

| Операція | Обов'язкова | Блокування `resv` | Що зобов'язана зробити |
| --- | --- | --- | --- |
| `attach` | ні | ні | прийняти або відкинути нового споживача; єдина точка, де експортер бачить `attach->dev` до того, як хтось попросив адреси |
| `detach` | ні | ні | звільнити свій облік цього приєднання |
| `pin` / `unpin` | парою або жодної | так | закріпити пам'ять на місці, доки живе відображення статичного імпортера |
| `map_dma_buf` | **так** | так | повернути `sg_table` з адресами **для `attach->dev`** — уже пропущений крізь `dma_map_sgtable()`, а не сирий список сторінок |
| `unmap_dma_buf` | **так** | так | розібрати саме те відображення |
| `release` | **так** | — | звільнити пам'ять; кличеться, коли впав останній дескриптор |
| `begin_cpu_access` / `end_cpu_access` | ні | ні | узгодити кеші навколо доступу процесора; за потреби перетягнути буфер у системну пам'ять |
| `mmap` | ні | ні | відобразити буфер у процес; немає — `mmap(2)` на дескриптор дасть `-EINVAL` |
| `vmap` / `vunmap` | ні | так | дати ядру суцільну адресу на весь буфер |

`cache_sgt_mapping` — не операція, а прапорець: якщо він піднятий, ядро саме кешує перше відображення кожного приєднання й не турбує експортера на повторних. Взаємно виключний із динамічністю: разом із `pin`/`unpin` не має сенсу, бо кешоване відображення не переживе переїзду.

`map_dma_buf` повертає `ERR_PTR(-errno)` при невдачі, і `-EINTR` тут законний — виклик має право заснути.

## Створення буфера й дескриптора

```c
struct dma_buf_export_info {
        const char *exp_name;            /* ім'я для debugfs і fdinfo */
        struct module *owner;            /* тримає модуль, доки живий буфер */
        const struct dma_buf_ops *ops;
        size_t size;
        int flags;                       /* режим файла: типово O_RDWR */
        struct dma_resv *resv;           /* NULL — ядро заведе власний */
        void *priv;                      /* контекст експортера */
};

#define DEFINE_DMA_BUF_EXPORT_INFO(name)                                \
        struct dma_buf_export_info name = { .exp_name = KBUILD_MODNAME, \
                                         .owner = THIS_MODULE }

struct dma_buf *dma_buf_export(const struct dma_buf_export_info *exp_info);
int             dma_buf_fd(struct dma_buf *dmabuf, int flags);
```

`dma_buf_export()` повертає `ERR_PTR(-EINVAL)` — з `WARN_ON` у журналі — якщо не заповнено `priv`, `ops` або бодай одну з трьох обов'язкових операцій, а також якщо `pin` є без `unpin` чи навпаки. Перевірка навмисно гучна: це помилка програміста, не робочий стан.

```c
DEFINE_DMA_BUF_EXPORT_INFO(info);
info.ops   = &my_ops;
info.size  = len;
info.flags = O_RDWR;
info.priv  = buf;

struct dma_buf *dmabuf = dma_buf_export(&info);
if (IS_ERR(dmabuf))
        return PTR_ERR(dmabuf);

int fd = dma_buf_fd(dmabuf, O_CLOEXEC);
if (fd < 0) {
        dma_buf_put(dmabuf);      /* лише на цій гілці */
        return fd;
}
return fd;                        /* далі посилання належить дескрипторові */
```

Асиметрія в кінці — головна пастка експорту. Успішний `dma_buf_fd()` передає посилання дескрипторові, і `dma_buf_put()` після нього звільнить буфер з-під живого користувача; невдалий не передає нічого, і без `put` буфер лишиться назавжди.

## Виклики імпортера

```c
struct dma_buf *dma_buf_get(int fd);
void            dma_buf_put(struct dma_buf *dmabuf);

struct dma_buf_attachment *dma_buf_attach(struct dma_buf *dmabuf,
                                          struct device *dev);
struct dma_buf_attachment *dma_buf_dynamic_attach(struct dma_buf *dmabuf,
                                          struct device *dev,
                                          const struct dma_buf_attach_ops *importer_ops,
                                          void *importer_priv);
void dma_buf_detach(struct dma_buf *dmabuf, struct dma_buf_attachment *attach);

int  dma_buf_pin(struct dma_buf_attachment *attach);
void dma_buf_unpin(struct dma_buf_attachment *attach);

struct sg_table *dma_buf_map_attachment(struct dma_buf_attachment *,
                                        enum dma_data_direction);
void dma_buf_unmap_attachment(struct dma_buf_attachment *, struct sg_table *,
                              enum dma_data_direction);
struct sg_table *dma_buf_map_attachment_unlocked(struct dma_buf_attachment *,
                                        enum dma_data_direction);
void dma_buf_unmap_attachment_unlocked(struct dma_buf_attachment *,
                                       struct sg_table *,
                                       enum dma_data_direction);

int  dma_buf_begin_cpu_access(struct dma_buf *, enum dma_data_direction dir);
int  dma_buf_end_cpu_access(struct dma_buf *, enum dma_data_direction dir);
int  dma_buf_mmap(struct dma_buf *, struct vm_area_struct *, unsigned long pgoff);

int  dma_buf_vmap(struct dma_buf *dmabuf, struct iosys_map *map);
void dma_buf_vunmap(struct dma_buf *dmabuf, struct iosys_map *map);
int  dma_buf_vmap_unlocked(struct dma_buf *dmabuf, struct iosys_map *map);
void dma_buf_vunmap_unlocked(struct dma_buf *dmabuf, struct iosys_map *map);
```

`dma_buf_get()` повертає `ERR_PTR(-EBADF)` на закритий дескриптор і `ERR_PTR(-EINVAL)` на чинний дескриптор, за яким не dma-buf, — саме так перевіряють, що [дескриптор](root:sys-unix/file-descriptor), прийнятий сокетом чи з `ioctl`, справді той, на що схожий. Напрямок у `map_attachment` — та сама трійка `DMA_TO_DEVICE` / `DMA_FROM_DEVICE` / `DMA_BIDIRECTIONAL` з тим самим значенням для кешів, що й у звичайному [DMA API](root:sys-unix/dma-and-buffers/api-dma-mapping.md); `DMA_NONE` тут беззмістовний.

Результат — `sg_table`: [список розкиданих шматків](root:hw-arch/scatter-gather), уже в адресах цього пристрою. Обходять `sgt->nents`, і жодного припущення про суцільність робити не можна навіть тоді, коли шматок виявився один.

`dma_buf_vmap()` віддає не вказівник, а помічений вказівник:

```c
struct iosys_map {
        union {
                void __iomem *vaddr_iomem;
                void *vaddr;
        };
        bool is_iomem;
};
```

Причина в тому, що буфер міг опинитися і в системній пам'яті, і у відеопам'яті на іншому кінці шини, а це два різні способи читати той самий діапазон адрес. Тому поле `vaddr` не розіменовують напряму: доступ ведуть помічниками `iosys_map_rd()`, `iosys_map_wr()`, `iosys_map_memcpy_to()`, які самі дивляться на `is_iomem` і обирають між звичайним доступом і `readl`/`memcpy_toio`. Код, що бере `map.vaddr` і працює з ним як зі вказівником, збереться без попередження й розвалиться на першому ж буфері з дискретної карти.

## Блокування: `dma_resv`

У кожного буфера є `dma_resv` — об'єкт, що поєднує блокування буфера й список огорож. Він і є те, чим синхронізуються експортер та імпортери, тож правило «з яким станом блокування кликати» — частина контракту нарівні з підписами.

| Тримати `dma_resv` узятим | Кликати без нього |
| --- | --- |
| `dma_buf_pin`, `dma_buf_unpin` | `dma_buf_attach`, `dma_buf_dynamic_attach`, `dma_buf_detach` |
| `dma_buf_map_attachment`, `dma_buf_unmap_attachment` | `dma_buf_export`, `dma_buf_fd`, `dma_buf_get`, `dma_buf_put` |
| `dma_buf_vmap`, `dma_buf_vunmap` | `dma_buf_begin_cpu_access`, `dma_buf_end_cpu_access`, `dma_buf_mmap` |

Варіанти з суфіксом `_unlocked` беруть блокування самі — це весь зміст суфікса. Вони з'явилися у 6.2, коли підсистему звели до єдиної домовленості; доти кожен драйвер вирішував сам, і саме звідси бралися взаємні заклинювання між графічними драйверами. Новий код, що не тримає блокування з інших міркувань, вживає `_unlocked`.

> 🔧 **Навіщо це.** Блокування взято не для того, щоб захистити лічильник, а щоб приєднання й переїзд не сталися одночасно з відображенням. Тому `move_notify` кличеться саме з узятим `resv` — інакше імпортер міг би отримати адреси рівно в мить, коли буфер уже поїхав, і жодна перевірка після цього не допомогла б. Правила [блокування в ядрі](root:sys-unix/kernel-locking) тут не бюрократія, а єдине, що робить динамічний буфер можливим.

## Динамічне приєднання

```c
struct dma_buf_attach_ops {
        bool allow_peer2peer;
        void (*move_notify)(struct dma_buf_attachment *attach);
};
```

Ці операції передають у `dma_buf_dynamic_attach()`, і вони належать **імпортерові**, а не експортерові. Наявність `move_notify` — обіцянка: «мене можна попередити, тому не закріплюй буфер». Зворотний виклик приходить із узятим `resv`; наявні відображення після нього формально чинні, але вказують на стару домівку, тож імпортер зобов'язаний припинити звернення й перевідобразити якнайшвидше. `allow_peer2peer` дозволяє віддати цьому імпортерові пам'ять без `struct page` — ділянку на іншому пристрої, доступну через шину напряму.

Імпортер без `move_notify` статичний: ядро зобов'язане закріпити буфер `pin`-ом на весь час відображення.

## Що бачить програма на дескрипторі

Обрамлення доступу процесора — `DMA_BUF_IOCTL_SYNC`, один [ioctl](root:sys-unix/ioctl-interface) із однією структурою.

```c
struct dma_buf_sync { __u64 flags; };

#define DMA_BUF_SYNC_READ   (1 << 0)
#define DMA_BUF_SYNC_WRITE  (2 << 0)
#define DMA_BUF_SYNC_RW     (DMA_BUF_SYNC_READ | DMA_BUF_SYNC_WRITE)
#define DMA_BUF_SYNC_START  (0 << 2)      /* нуль — не прапорець, а його відсутність */
#define DMA_BUF_SYNC_END    (1 << 2)
#define DMA_BUF_SYNC_VALID_FLAGS_MASK  (DMA_BUF_SYNC_RW | DMA_BUF_SYNC_END)

#define DMA_BUF_BASE        'b'
#define DMA_BUF_IOCTL_SYNC  _IOW(DMA_BUF_BASE, 0, struct dma_buf_sync)
```

`DMA_BUF_SYNC_START` дорівнює нулю: початок доступу — це просто виклик без `END`. Писати його все одно варто, бо парність `START`/`END` у коді видно очима, а її відсутність — ні.

| `flags & DMA_BUF_SYNC_RW` | Напрямок усередині ядра | На що чекає `START` |
| --- | --- | --- |
| `READ` | `DMA_FROM_DEVICE` | лише на огорожу записувача |
| `WRITE` | `DMA_TO_DEVICE` | на всіх: і записувача, і читачів |
| `RW` | `DMA_BIDIRECTIONAL` | на всіх |
| `0` | — | `-EINVAL` |

| Помилка | Причина | Що робити |
| --- | --- | --- |
| `EINVAL` | біт поза `VALID_FLAGS_MASK` або порожнє поле напрямку | виправити виклик |
| `EFAULT` | структуру не вдалося прочитати з простору користувача | виправити виклик |
| `EAGAIN`, `EINTR` | очікування огорож перервано | **повторити той самий виклик** |

Останній рядок — не дрібниця. `START` чекає на огорожі, а чекання переривне; код, що перевіряє лише `ret == 0`, зрідка проскакує в буфер, у який ще пише пристрій. Тому виклик обгортають циклом.

**Назва буфера** — для обліку, і тільки:

```c
#define DMA_BUF_NAME_LEN     32           /* разом із нульовим байтом */
#define DMA_BUF_SET_NAME     _IOW(DMA_BUF_BASE, 1, const char *)
#define DMA_BUF_SET_NAME_A   _IOW(DMA_BUF_BASE, 1, __u32)
#define DMA_BUF_SET_NAME_B   _IOW(DMA_BUF_BASE, 1, __u64)
```

Три імені однієї команди — слід давньої помилки. Розмір типу входить у число `ioctl`, а `const char *` має різний розмір у 32- і 64-бітних програмах, тож початковий `DMA_BUF_SET_NAME` розгортався у два різні числа залежно від того, хто компілювався. Варіанти `_A` і `_B` фіксують обидва явно, і ядро приймає їх усі. Назва довша за межу відкидається.

**Явні огорожі** — від 6.0:

```c
struct dma_buf_export_sync_file { __u32 flags; __s32 fd; };
struct dma_buf_import_sync_file { __u32 flags; __s32 fd; };

#define DMA_BUF_IOCTL_EXPORT_SYNC_FILE _IOWR(DMA_BUF_BASE, 2, struct dma_buf_export_sync_file)
#define DMA_BUF_IOCTL_IMPORT_SYNC_FILE _IOW(DMA_BUF_BASE, 3, struct dma_buf_import_sync_file)
```

`flags` тут — та сама пара `DMA_BUF_SYNC_READ`/`WRITE` і з тим самим сенсом. Експорт знімає з буфера **знімок** наявних огорож і повертає їх окремим дескриптором `sync_file` у полі `fd`: замість чекати зараз, програма забирає право почекати пізніше. Імпорт робить зворотне — вкладає огорожі з поданого `sync_file` у `dma_resv` буфера, щоб їх побачили ті, хто синхронізується неявно. Пара потрібна саме для зшивання двох світів: явного, де чекає програма, і неявного, де чекають драйвери. Механіка самих огорож — окрема тема: [огорожі й sync_file](root:sys-unix/dma-fence-sync).

**Відображення** — звичайний [`mmap`](root:sys-unix/mmap-model) на дескриптор, зі зсувом `0` і довжиною не більшою за розмір буфера. Якщо експортер не реалізував `.mmap`, виклик повертає `-EINVAL` — і це той самий код, що й на «дескриптор узагалі не dma-buf», тож розрізняти ці два випадки доводиться не за помилкою, а за походженням дескриптора.

## Виділення з купи

```c
struct dma_heap_allocation_data {
        __u64 len;
        __u32 fd;                 /* заповнює ядро */
        __u32 fd_flags;
        __u64 heap_flags;
};

#define DMA_HEAP_VALID_FD_FLAGS    (O_CLOEXEC | O_ACCMODE)
#define DMA_HEAP_VALID_HEAP_FLAGS  (0ULL)
#define DMA_HEAP_IOC_MAGIC         'H'
#define DMA_HEAP_IOCTL_ALLOC       _IOWR(DMA_HEAP_IOC_MAGIC, 0x0, \
                                         struct dma_heap_allocation_data)
```

Купи (від 5.6) — символьні пристрої в `/dev/dma_heap/`; типово там є `system` і, якщо ядро зібрано з резервованою ділянкою, `cma`. `heap_flags` мусить бути нулем: поле заведено на майбутнє й перевіряється строго. Повний виклик, від виділення до безпечного доступу процесором:

```c
int heap = open("/dev/dma_heap/system", O_RDONLY | O_CLOEXEC);
struct dma_heap_allocation_data a = {
        .len        = 4 << 20,
        .fd_flags   = O_RDWR | O_CLOEXEC,
        .heap_flags = 0,
};
if (ioctl(heap, DMA_HEAP_IOCTL_ALLOC, &a) < 0)
        return -1;
close(heap);                      /* буфер живе своїм дескриптором a.fd */

void *p = mmap(NULL, a.len, PROT_READ | PROT_WRITE, MAP_SHARED, a.fd, 0);

struct dma_buf_sync s = { .flags = DMA_BUF_SYNC_START | DMA_BUF_SYNC_WRITE };
while (ioctl(a.fd, DMA_BUF_IOCTL_SYNC, &s) < 0 && (errno == EINTR || errno == EAGAIN))
        ;
memset(p, 0, a.len);
s.flags = DMA_BUF_SYNC_END | DMA_BUF_SYNC_WRITE;
while (ioctl(a.fd, DMA_BUF_IOCTL_SYNC, &s) < 0 && (errno == EINTR || errno == EAGAIN))
        ;
```

Дескриптор `a.fd` уже придатний до всього: віддати драйверові, надіслати іншому процесові [сокетом домену Unix](root:sys-unix/unix-domain-sockets), закрити.

## Де подивитися на живі буфери

| Джерело | Що показує |
| --- | --- |
| `/sys/kernel/debug/dma_buf/bufinfo` | усі буфери системи: розмір, `exp_name`, назву, номер inode, лічильник посилань і перелік **приєднаних пристроїв** |
| `/proc/<pid>/fdinfo/<fd>` | той самий буфер із боку процесу: `size`, `count`, `exp_name`, `name` |

`bufinfo` доступний лише з `CONFIG_DMA_SHARED_BUFFER` і змонтованим debugfs, і читати його може тільки привілейований користувач. Це єдине місце, де видно **перелік приєднань**, — а отже, єдиний спосіб відповісти на питання «хто ще тримає цей кадр», коли пам'ять не звільняється. У `fdinfo` лічильник виведено на одиницю меншим за внутрішній: віднято тимчасове посилання, яке procfs бере на файл, поки друкує цей рядок, — тож видно те саме число, що й без спостерігача.
