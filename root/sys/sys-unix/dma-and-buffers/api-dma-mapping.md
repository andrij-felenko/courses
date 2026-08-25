# 📋 DMA API: підписи, напрямки, атрибути

Це контракт викликів, якими драйвер Linux віддає буфер пристроєві й забирає назад: повні підписи, значення кожного аргумента, таблиця напрямків із тим, що кожен робить із кешем, протокол перевірки невдачі, атрибути й обмеження на пам'ять та контекст виклику. Довідка потрібна тому, що майже кожна помилка цього шару компілюється без жодного попередження, а на x86 ще й не виявляється при випробуванні.

Підписи взято з `<linux/dma-mapping.h>` ядра 6.x; де інтерфейс змінювався недавно, версію вказано окремо.

## Типи й константа невдачі

```c
dma_addr_t                  /* число для регістра пристрою; не вказівник і не фізична адреса */
enum dma_data_direction     /* BIDIRECTIONAL=0, TO_DEVICE=1, FROM_DEVICE=2, NONE=3 */

#define DMA_MAPPING_ERROR   (~(dma_addr_t)0)   /* усі одиниці */
#define DMA_BIT_MASK(n)     /* маска з n молодших одиниць */
```

```c
static inline int dma_mapping_error(struct device *dev, dma_addr_t dma_addr)
{
        debug_dma_mapping_error(dev, dma_addr);
        if (unlikely(dma_addr == DMA_MAPPING_ERROR))
                return -ENOMEM;
        return 0;
}
```

Повертає `0` при успіху й ненульове при невдачі — тобто перевіряють `if (dma_mapping_error(dev, da))`, а не порівнюють `da` з чимось самотужки. Ознакою невдачі не може бути нуль, бо нуль на багатьох шинах — цілком законна адреса, і на системі, де оперативна пам'ять адресується з нуля, перший же успішно відображений буфер виглядав би як помилка. Значення `~0` теж не безкоштовне: воно законне рівно доти, доки жоден пристрій не адресує останній байт свого простору, і саме тому константа належить ядру, а не драйверові.

## Напрямок передачі

Четвертий аргумент кожного відображення — не документація, а вказівка, яку роботу зробити з кешем.

| Напрямок | Хто пише в буфер | Мета при `map` / `sync_for_device` | Мета при `unmap` / `sync_for_cpu` |
| --- | --- | --- | --- |
| `DMA_TO_DEVICE` | процесор | вигнати записане процесором із кеша в пам'ять, щоб пристрій побачив свіже | нічого не потрібно |
| `DMA_FROM_DEVICE` | пристрій | прибрати з кеша брудні рядки ділянки, щоб пізніше не затерли записане пристроєм | знецінити рядки, щоб процесор читав пам'ять, а не свою стару копію |
| `DMA_BIDIRECTIONAL` | обидва | як для `TO_DEVICE` | як для `FROM_DEVICE` |
| `DMA_NONE` | ніхто | не проходить `valid_dma_direction()` → `BUG_ON` у точці входу | — |

У таблиці навмисно записано мету, а не інструкцію: конкретну операцію обирає архітектура. На arm64 `arch_sync_dma_for_device()` завжди робить `clean` (запис брудних рядків у пам'ять — цього досить і щоб пристрій побачив свіже, і щоб рядки перестали бути брудними), а `arch_sync_dma_for_cpu()` знецінює все, крім `DMA_TO_DEVICE`. На arm32 `clean` і `invalidate` розведено за напрямком. Драйвер має право спиратися лише на мету з таблиці.

На платформі, де контролер пам'яті сам стежить за кешами процесора — про це є стаття [когерентність кеша і DMA](root:hw-arch/cache-coherency-dma), — усі ці операції порожні: `dma_dev_need_sync()` повертає хибу, і виклики стають нічим. Тому напрямок, поставлений навмання, на x86 не проявиться ніяк.

> 🔧 **Навіщо це.** `DMA_BIDIRECTIONAL` виглядає безпечним вибором «про всяк випадок», але він не лише дорожчий удвічі — він приховує помилку. Буфер, оголошений двонапрямним, дозволяє процесорові прочитати те, що він сам туди записав, навіть якщо пристрій нічого не писав; випробування пройде, а на іншій платформі виявиться, що напрямок не збігається з дійсністю. Ставлять точний напрямок, і `dma-debug` при `CONFIG_DMA_API_DEBUG=y` перевіряє, що `unmap` і `sync` називають той самий.

## Межа адресації пристрою

```c
int dma_set_mask(struct device *dev, u64 mask);            /* потокові відображення */
int dma_set_coherent_mask(struct device *dev, u64 mask);   /* узгоджені виділення */
u64 dma_get_required_mask(struct device *dev);             /* яка маска покрила б усю пам'ять */

static inline int dma_set_mask_and_coherent(struct device *dev, u64 mask)
{
        int rc = dma_set_mask(dev, mask);
        if (rc == 0)
                dma_set_coherent_mask(dev, mask);
        return rc;
}
```

Кличуть один раз при під'єднанні пристрою, **до** першого відображення. Повертають нуль при успіху; ненульове означає, що платформа такої вузької маски не витягує, і драйвер мусить відмовитися від DMA, а не працювати далі.

| Наслідок маски | Що робить ядро |
| --- | --- |
| буфер у межах маски | звичайне відображення |
| буфер поза межами, є [IOMMU](root:hw-arch/iommu) | адресу видає таблиця перекладу — вона в межах маски за побудовою |
| буфер поза межами, IOMMU немає | тихо підставляє буфер із нижньої пам'яті й копіює вміст туди й назад (swiotlb) |
| маска не задана взагалі | ядро припускає 32 біти |

Остання пастка відома: `dma_set_mask_and_coherent(dev, DMA_BIT_MASK(64))` не може провалитися, тож поширений візерунок «спробувати 64, при невдачі відкотитися на 32» — мертвий код.

## Узгоджена пам'ять

```c
void *dma_alloc_attrs(struct device *dev, size_t size, dma_addr_t *dma_handle,
                      gfp_t flag, unsigned long attrs);
void  dma_free_attrs(struct device *dev, size_t size, void *cpu_addr,
                     dma_addr_t dma_handle, unsigned long attrs);

static inline void *dma_alloc_coherent(struct device *dev, size_t size,
                                       dma_addr_t *dma_handle, gfp_t gfp);
#define dma_free_coherent(d, s, c, h)  dma_free_attrs(d, s, c, h, 0)

static inline void *dma_alloc_wc(struct device *dev, size_t size,
                                 dma_addr_t *dma_addr, gfp_t gfp);  /* + WRITE_COMBINE */
```

Виклик повертає **два** значення: адресу для процесора (як результат) і адресу для пристрою (через `dma_handle`). Обидві вирівняні на найменший порядок сторінок, не менший за `size` — тож запит на 60 КіБ гарантовано не перетне межу 64 КіБ, чого вимагає частина контролерів.

Для дрібних однакових шматочків узгодженої пам'яті є окремий розподільник, який не марнує сторінку на кожен:

```c
struct dma_pool *dma_pool_create(const char *name, struct device *dev,
                                 size_t size, size_t align, size_t boundary);
void *dma_pool_alloc(struct dma_pool *pool, gfp_t flags, dma_addr_t *handle);
void  dma_pool_free(struct dma_pool *pool, void *vaddr, dma_addr_t handle);
void  dma_pool_destroy(struct dma_pool *pool);
```

`boundary` — межа, яку жоден виданий шматок не має права перетнути (`0` знімає вимогу).

## Потокові відображення

```c
dma_addr_t dma_map_single_attrs(struct device *dev, void *ptr, size_t size,
                                enum dma_data_direction dir, unsigned long attrs);
void       dma_unmap_single_attrs(struct device *dev, dma_addr_t addr, size_t size,
                                  enum dma_data_direction dir, unsigned long attrs);

dma_addr_t dma_map_page_attrs(struct device *dev, struct page *page, size_t offset,
                              size_t size, enum dma_data_direction dir,
                              unsigned long attrs);
void       dma_unmap_page_attrs(struct device *dev, dma_addr_t addr, size_t size,
                                enum dma_data_direction dir, unsigned long attrs);

#define dma_map_single(d, a, s, r)     dma_map_single_attrs(d, a, s, r, 0)
#define dma_unmap_single(d, a, s, r)   dma_unmap_single_attrs(d, a, s, r, 0)
#define dma_map_page(d, p, o, s, r)    dma_map_page_attrs(d, p, o, s, r, 0)
#define dma_unmap_page(d, a, s, r)     dma_unmap_page_attrs(d, a, s, r, 0)
```

`dma_map_single` бере адресу ядра, `dma_map_page` — пару «сторінка плюс зсув»: це єдиний спосіб віддати пристроєві сторінку, для якої немає постійної адреси в ядрі, і саме через нього проходять сторінки з простору користувача. Аргументи `unmap` мусять збігатися з аргументами `map` до останнього числа — на платформі з підмінними буферами саме за ними ядро знаходить, звідки копіювати назад.

## Списки сегментів

```c
unsigned int dma_map_sg_attrs(struct device *dev, struct scatterlist *sg, int nents,
                              enum dma_data_direction dir, unsigned long attrs);
void         dma_unmap_sg_attrs(struct device *dev, struct scatterlist *sg, int nents,
                                enum dma_data_direction dir, unsigned long attrs);

int  dma_map_sgtable(struct device *dev, struct sg_table *sgt,
                     enum dma_data_direction dir, unsigned long attrs);
void dma_unmap_sgtable(struct device *dev, struct sg_table *sgt,
                       enum dma_data_direction dir, unsigned long attrs);

#define dma_map_sg(d, s, n, r)    dma_map_sg_attrs(d, s, n, r, 0)
#define dma_unmap_sg(d, s, n, r)  dma_unmap_sg_attrs(d, s, n, r, 0)
```

Тут два різні протоколи помилки, і плутати їх не можна.

| Виклик | Успіх | Невдача | Скільки сегментів обходити | Що передавати в `unmap` |
| --- | --- | --- | --- | --- |
| `dma_map_sg` | повернене число > 0 | **`0`** — `dma_mapping_error` тут не вживають | повернене число | **початкове** `nents`, не повернене |
| `dma_map_sgtable` | `0` | від'ємний `errno` (`-EIO`, `-ENOMEM`, `-EREMOTEIO`) | `sgt->nents` | `sgt` — рахунок бере з `orig_nents` сам |

Причина розбіжності — в тому, що відображених сегментів може стати **менше**, ніж було: IOMMU вміє зшити сусідні фізичні сторінки в один неперервний діапазон. Старий інтерфейс мусив вертати цю нову кількість замість коду помилки, тому нуль і став ознакою невдачі. `dma_map_sgtable` (від 5.10) тримає обидва числа в самій структурі: `orig_nents` — скільки записів у списку, `nents` — скільки з них має адреси для пристрою. Обходити треба `nents`, звільняти — за `orig_nents`; у новому коді беруть саме цю форму.

## Синхронізація без розбирання відображення

```c
void dma_sync_single_for_cpu(struct device *dev, dma_addr_t addr, size_t size,
                             enum dma_data_direction dir);
void dma_sync_single_for_device(struct device *dev, dma_addr_t addr, size_t size,
                                enum dma_data_direction dir);
void dma_sync_sg_for_cpu(struct device *dev, struct scatterlist *sg, int nelems,
                         enum dma_data_direction dir);
void dma_sync_sg_for_device(struct device *dev, struct scatterlist *sg, int nelems,
                            enum dma_data_direction dir);
void dma_sync_sgtable_for_cpu(struct device *dev, struct sg_table *sgt,
                              enum dma_data_direction dir);
void dma_sync_sgtable_for_device(struct device *dev, struct sg_table *sgt,
                                 enum dma_data_direction dir);
```

Потрібні тоді й лише тоді, коли процесор хоче торкнутися буфера, який усе ще відображений — типово при повторному вжитку того самого буфера в кільці. `..._for_cpu` викликають **перед** читанням, `..._for_device` — **після** запису; напрямок мусить бути той самий, що при відображенні. Синхронізація відображення не знімає: буфер лишається чинним, поки не буде `unmap`.

## Той самий буфер у просторі користувача

```c
int dma_mmap_attrs(struct device *dev, struct vm_area_struct *vma, void *cpu_addr,
                   dma_addr_t dma_addr, size_t size, unsigned long attrs);

#define dma_mmap_coherent(d, v, c, h, s)  dma_mmap_attrs(d, v, c, h, s, 0)
static inline int dma_mmap_wc(struct device *dev, struct vm_area_struct *vma,
                              void *cpu_addr, dma_addr_t dma_addr, size_t size);
```

Кличуть з обробника `.mmap` файлу пристрою — про сам механізм є стаття [mmap](root:sys-unix/mmap-model). `cpu_addr` і `dma_addr` мусять бути тією самою парою, яку повернуло `dma_alloc_coherent`; атрибути мусять збігатися з атрибутами виділення, інакше програма дістане ділянку з іншими властивостями кешування, ніж ядро. Повертає `0` або від'ємний `errno`. Для передачі буфера не програмі, а іншому драйверові, цей шлях не годиться — там окремий інтерфейс [dma-buf](root:sys-unix/dma-buf).

## Атрибути

Останній аргумент `*_attrs` — побітове «або» з таких прапорців.

| Атрибут | Значення | Коли доречний |
| --- | --- | --- |
| `DMA_ATTR_WRITE_COMBINE` | `1UL << 2` | буфер, у який процесор лише лінійно пише й ніколи не читає: кадр для дисплея, вершини для графічного процесора. Записи збираються в пачки замість окремих транзакцій шини |
| `DMA_ATTR_NO_KERNEL_MAPPING` | `1UL << 4` | великий буфер, якого ядро не торкається — його лише віддають назовні або пристроєві. Заощаджує адресний простір ядра, а на 32 бітах це справжній дефіцит |
| `DMA_ATTR_WEAK_ORDERING` | `1UL << 1` | пристрій не потребує, щоб його доступи до буфера лягали в порядку видачі; дозволяє залізу переставляти їх місцями |
| `DMA_ATTR_SKIP_CPU_SYNC` | `1UL << 5` | той самий фізичний буфер відображають на кілька пристроїв: кеш узгоджують один раз, решта відображень пропускають операцію |
| `DMA_ATTR_FORCE_CONTIGUOUS` | `1UL << 6` | контролер не вміє збирати передачу зі списку — ділянка мусить бути суцільною фізично, а не лише в адресах шини |
| `DMA_ATTR_NO_WARN` | `1UL << 8` | невдале виділення — очікуваний робочий випадок, а не поламка; гасить попередження в журналі |

`DMA_ATTR_SKIP_CPU_SYNC` — найнебезпечніший із них: він знімає саме той захист, заради якого існує напрямок, і покладає узгодження кеша на драйвер. `DMA_ATTR_WEAK_ORDERING` не заміняє [бар'єрів пам'яті](root:hw-arch/memory-barrier-instructions) з боку процесора — він про порядок доступів пристрою, не про порядок записів процесора.

## Звідки брати буфер і звідки кликати

| Джерело пам'яті | Годиться для потокового відображення |
| --- | --- |
| [`kmalloc`, `kmem_cache_alloc`](root:sys-unix/kernel-memory-slab) | так |
| сторінки з [розподільника фізичних сторінок](root:sys-unix/physical-page-allocator) | так, через `dma_map_page` |
| стек ядра | **ні** — може бути поза досяжною зоною й ділити кеш-рядок із сусідніми змінними |
| [`vmalloc`, `kvmalloc`](root:sys-unix/vmalloc-kernel-mappings) | **ні** — фізично не суцільне |
| статичні дані модуля, образ ядра | **ні** |
| результат `kmap` | **ні** |

Вирівнювання. Ділянка має починатися й закінчуватися на межі кеш-рядка, інакше знецінення зачепить чужі дані в спільному рядку. Розмір рядка дає `dma_get_cache_alignment()` (це `ARCH_DMA_MINALIGN`). Історично `kmalloc` вирівнював **кожен** об'єкт на цю межу, але на arm64 це коштувало 128 байтів на будь-який дріб'язок, тому там числа розвели: `ARCH_DMA_MINALIGN` лишився `128`, а `ARCH_KMALLOC_MINALIGN` став `8`. Наслідок практичний: дрібний буфер із `kmalloc` тепер може виявитися невирівняним, і для некогерентного пристрою ядро мовчки підмінить його власним — правильно, але повільно.

| Виклик | З обробника переривання |
| --- | --- |
| `dma_map_*`, `dma_unmap_*`, `dma_sync_*` | так |
| `dma_alloc_coherent` | так, але тільки з `GFP_ATOMIC` |
| `dma_free_coherent`, `dma_pool_create`, `dma_pool_destroy` | **ні** |
| `dma_pool_alloc`, `dma_pool_free` | так |
| `dma_mmap_*` | ні — це шлях із системного виклику |

Межа проходить рівно там, де виклик може заснути; що саме вважається обробником переривання й чому там не можна спати, розібрано в статті про [переривання й нижні половини](root:sys-unix/interrupts-bottom-halves).

## Мінімальний повний виклик

```c
/* один раз, при під'єднанні */
if (dma_set_mask_and_coherent(dev, DMA_BIT_MASK(64)))
        return -EIO;

/* на кожну передачу */
dma_addr_t da = dma_map_single(dev, buf, len, DMA_TO_DEVICE);
if (dma_mapping_error(dev, da))
        return -ENOMEM;

start_transfer(dev, da, len);           /* адресу — в регістр пристрою */
wait_for_completion(&done);             /* прокидається обробник переривання */

dma_unmap_single(dev, da, len, DMA_TO_DEVICE);   /* аргументи ті самі, що при map */
```

Чотири рядки, у яких немає жодної арифметики над адресами, — і це головна властивість інтерфейсу, а не випадковість.
