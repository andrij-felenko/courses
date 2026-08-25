# 🧾 Інтерфейс memblock: структури, виклики, прапорці, параметри завантаження

Це перелік імен, якими ранній розподільник пам'яті ядра Linux керується зсередини й показує себе назовні: поля структур, сигнатури функцій, значення прапорців діапазону та параметри командного рядка, що змінюють його поведінку. Усе звірено з Linux 6.16 (`include/linux/memblock.h`, `mm/memblock.c`); де інтерфейс змінився недавно, стара форма названа окремо.

## Структури

```c
struct memblock_region {
        phys_addr_t base;             /* початок діапазону */
        phys_addr_t size;             /* довжина в байтах */
        enum memblock_flags flags;    /* властивості діапазону */
#ifdef CONFIG_NUMA
        int nid;                      /* вузол NUMA */
#endif
};

struct memblock_type {
        unsigned long cnt;            /* скільки записів зайнято */
        unsigned long max;            /* скільки вміщає масив зараз */
        phys_addr_t total_size;       /* сума size усіх записів */
        struct memblock_region *regions;
        char *name;                   /* "memory" | "reserved" | "physmem" */
};

struct memblock {
        bool bottom_up;               /* напрям пошуку вільного вікна */
        phys_addr_t current_limit;    /* стеля адрес для виділень */
        struct memblock_type memory;  /* що взагалі існує */
        struct memblock_type reserved;/* що вже комусь належить */
};
```

Глобальний примірник `struct memblock memblock` стартує з `.bottom_up = false` і `.current_limit = MEMBLOCK_ALLOC_ANYWHERE`; обидва масиви показують на статичні `memblock_memory_init_regions` і `memblock_reserved_init_regions` розміром `INIT_MEMBLOCK_REGIONS` — це 128, і архітектура має право перевизначити окремо `INIT_MEMBLOCK_MEMORY_REGIONS` та `INIT_MEMBLOCK_RESERVED_REGIONS`.

Поле `nid` існує лише за `CONFIG_NUMA`; читають його через `memblock_get_region_node()`, який без NUMA завжди віддає нуль. Сам поділ пам'яті на вузли з різною ціною доступу описано окремо — [NUMA](root:hw-arch/numa).

Третій тип, `physmem`, — окрема глобальна змінна, а не поле `struct memblock`; існує лише за `CONFIG_HAVE_MEMBLOCK_PHYS_MAP` і зберігає карту прошивки такою, якою її дали, тоді як `memory` вже обрізали параметри командного рядка. Стартовий розмір — `INIT_PHYSMEM_REGIONS`, тобто 4 записи.

## Наповнення карти

| Виклик | Дія |
| --- | --- |
| `int memblock_add(phys_addr_t base, phys_addr_t size)` | додати діапазон у `memory` без вузла й прапорців |
| `int memblock_add_node(phys_addr_t base, phys_addr_t size, int nid, enum memblock_flags flags)` | те саме з вузлом і прапорцями |
| `int memblock_remove(phys_addr_t base, phys_addr_t size)` | викинути діапазон із `memory`: для ядра цієї пам'яті більше немає |
| `int memblock_reserve(phys_addr_t base, phys_addr_t size)` | позначити діапазон зайнятим у `reserved` |
| `int memblock_reserve_kern(phys_addr_t base, phys_addr_t size)` | те саме плюс `MEMBLOCK_RSRV_KERN` |
| `int memblock_set_node(phys_addr_t base, phys_addr_t size, struct memblock_type *type, int nid)` | приписати діапазон вузлові; масив передають явно — `&memblock.memory` |
| `int memblock_mark_nomap / memblock_clear_nomap / memblock_mark_mirror(phys_addr_t base, phys_addr_t size)` | поставити чи зняти прапорець на вже наявному діапазоні |
| `int memblock_reserved_mark_noinit(phys_addr_t base, phys_addr_t size)` | те саме для `MEMBLOCK_RSRV_NOINIT` |

Усі повертають 0 або `-ENOMEM`, і єдина причина відмови — не вдалося розсунути масив. Меж наявних записів вони не бояться: діапазон, що перетинає сусідів, розрізає їх, а суміжні з однаковими властивостями зливаються назад.

У 6.12 `memblock_reserve()` ще був звичайною функцією. У 6.16 це інлайн-обгортка над `__memblock_reserve(base, size, NUMA_NO_NODE, 0)` — саме вона й дала змогу з'явитися парному `memblock_reserve_kern()`.

## Виділення

| Виклик | Що повертає | Занулює | Межі пошуку |
| --- | --- | --- | --- |
| `void *memblock_alloc(size, align)` | віртуальну адресу прямого відображення | так | `0 … current_limit` |
| `void *memblock_alloc_or_panic(size, align)` | те саме | так | те саме |
| `void *memblock_alloc_low(size, align)` | віртуальну адресу | так | `0 … ARCH_LOW_ADDRESS_LIMIT` |
| `void *memblock_alloc_node(size, align, nid)` | віртуальну адресу | так | з наданням переваги вузлу `nid` |
| `void *memblock_alloc_try_nid(size, align, min_addr, max_addr, nid)` | віртуальну адресу | так | задані явно |
| `void *memblock_alloc_raw / memblock_alloc_try_nid_raw(…)` | віртуальну адресу | **ні** | як у відповідника |
| `phys_addr_t memblock_phys_alloc(size, align)` | фізичну адресу | ні | `0 … current_limit` |
| `phys_addr_t memblock_phys_alloc_range(size, align, start, end)` | фізичну адресу | ні | задані явно |
| `phys_addr_t memblock_phys_alloc_try_nid(size, align, nid)` | фізичну адресу | ні | з наданням переваги вузлу |
| `phys_addr_t memblock_alloc_range_nid(size, align, start, end, nid, bool exact_nid)` | фізичну адресу | ні | задані явно; `exact_nid` забороняє відступ на інші вузли |

Три сталі задають межі: `MEMBLOCK_LOW_LIMIT` (0) — «знизу без обмежень», `MEMBLOCK_ALLOC_ACCESSIBLE` (0 у ролі верхньої межі) — «доти, доки дотягується `current_limit`», `MEMBLOCK_ALLOC_ANYWHERE` (`~(phys_addr_t)0`) — «стелі немає».

Невдача не зупиняє ядро: «віртуальні» виклики віддають `NULL`, «фізичні» — нуль. Перевіряти обов'язково, і саме щоб не писати цю перевірку щоразу вручну, з'явився макрос `memblock_alloc_or_panic()` — він зупиняє ядро сам і друкує ім'я викликача.

## Звільнення й кінець доби

| Виклик | Коли |
| --- | --- |
| `void memblock_free(void *ptr, size_t size)` | за віртуальною адресою, до передачі естафети |
| `int memblock_phys_free(phys_addr_t base, phys_addr_t size)` | за фізичною, до передачі естафети |
| `void memblock_free_late(phys_addr_t base, phys_addr_t size)` | після передачі: сторінки йдуть уже [розподільникові сторінок](root:sys-unix/physical-page-allocator) |
| `void memblock_free_all(void)` | одноразова передача естафети цілком |

Оголошення `memblock_free_all()` з публічного заголовка прибрали: у 6.12 воно ще в `include/linux/memblock.h`, у 6.16 — у внутрішньому `mm/internal.h`, бо єдиний законний викликач — `mm_core_init()`.

## Режим роботи й запитання до карти

| Виклик | Дія |
| --- | --- |
| `void memblock_allow_resize(void)` | з цієї миті масиви дозволено подвоювати |
| `void memblock_set_bottom_up(bool enable)` | напрям пошуку вільного вікна |
| `void memblock_set_current_limit(phys_addr_t limit)` | стеля адрес для наступних виділень |
| `bool memblock_is_region_memory(phys_addr_t base, phys_addr_t size)` | чи діапазон **цілком** лежить у `memory` |
| `bool memblock_is_region_reserved(phys_addr_t base, phys_addr_t size)` | чи діапазон **бодай частково** зачіпає `reserved` |
| `bool memblock_is_memory / memblock_is_map_memory / memblock_is_reserved(phys_addr_t addr)` | те саме для однієї адреси |
| `phys_addr_t memblock_start_of_DRAM / memblock_end_of_DRAM / memblock_phys_mem_size / memblock_reserved_size(void)` | підсумкові числа |
| `void memblock_dump_all(void)` | надрукувати обидва масиви |

Несиметричність двох перевірок навмисна й легко ловить необережного: «пам'ять» питають на повне вкладення, «зайнятість» — на будь-який перетин. Обидві відповіді потрібні саме в такому вигляді, бо перша дозволяє користуватися діапазоном, а друга забороняє.

## Ітератори

```c
u64 i;
phys_addr_t start, end;

/* усе придатне, крім від'єднуваного та знайденого драйверами */
for_each_mem_range(i, &start, &end)
        pr_info("RAM %pa..%pa\n", &start, &end);

/* вільне = memory мінус reserved, з фільтром за вузлом і прапорцями */
for_each_free_mem_range(i, NUMA_NO_NODE, MEMBLOCK_NONE, &start, &end, NULL)
        pr_info("free %pa..%pa\n", &start, &end);
```

Обидва — обгортки над `__for_each_mem_range()`, який крутить `__next_mem_range()`: нижні 32 біти лічильника `i` індексують перший масив, верхні — проміжки між записами другого. Кінець діапазону виключний, тобто вікно це `start ≤ x < end`. Зворотні напрями — `for_each_mem_range_rev()` і `for_each_free_mem_range_reverse()`; обхід по номерах кадрів на кожен вузол — `for_each_mem_pfn_range(i, nid, &spfn, &epfn, &out_nid)`.

Важлива подробиця саме `for_each_mem_range()`: він мовчки пропускає діапазони з `MEMBLOCK_HOTPLUG` і `MEMBLOCK_DRIVER_MANAGED` — це вшито в означення макроса, а не в аргументи.

## Прапорці діапазону

| Ім'я | Значення | Що означає | Як зветься у debugfs |
| --- | --- | --- | --- |
| `MEMBLOCK_NONE` | 0x0 | без особливостей | `NONE` |
| `MEMBLOCK_HOTPLUG` | 0x1 | ділянку можна від'єднати на ходу | `HOTPLUG` |
| `MEMBLOCK_MIRROR` | 0x2 | апаратно дзеркалена пам'ять | `MIRROR` |
| `MEMBLOCK_NOMAP` | 0x4 | не додавати в пряме відображення ядра | `NOMAP` |
| `MEMBLOCK_DRIVER_MANAGED` | 0x8 | пам'ять, про яку знає лише драйвер | `DRV_MNG` |
| `MEMBLOCK_RSRV_NOINIT` | 0x10 | не ініціалізувати `struct page` для цих кадрів | `RSV_NIT` |
| `MEMBLOCK_RSRV_KERN` | 0x20 | резервування зробило саме ядро | `RSV_KERN` |
| `MEMBLOCK_KHO_SCRATCH` | 0x40 | робоча пам'ять для передавання стану через kexec | `KHO_SCRATCH` |

Останні два в 6.12 ще відсутні й з'явилися пізніше. Значення — окремі біти, але в записі діапазону їх зберігають як набір, а `debugfs` друкує лише перший знайдений.

## Параметри командного рядка

Усе, що нижче, ядро розбирає ще в добу `memblock`, тож дописують це в [рядок параметрів завантажувача](root:sys-unix/bootloader-and-cmdline), а не в `/proc`.

| Параметр | Що робить |
| --- | --- |
| `memblock=debug` | вмикає `memblock_debug`: кожне додавання, резервування й виділення потрапляє в журнал |
| `mem=nn[KMG]` | викидає з `memory` усе вище `nn` — пам'ять просто зникає |
| `memmap=nn[KMG]@ss[KMG]` | оголошує ділянку звичайною RAM |
| `memmap=nn[KMG]#ss` / `$ss` / `!ss` | оголошує її даними ACPI / зарезервованою / стійкою пам'яттю |
| `memmap=exactmap` | стирає карту прошивки цілком: далі всю карту описують наступними `memmap=` |
| `crashkernel=size[@offset]`, `size,high`, `size,low`, `range1:size1,range2:size2[@offset]` | резервує суцільну ділянку під [аварійне ядро](root:sys-unix/kexec-and-kdump) |
| `hugepagesz=`, `hugepages=N` | резервує [великі сторінки](root:sys-unix/huge-pages-tlb-reach) наперед — гігантські (1 ГіБ) інакше зібрати вже не вийде |

## Мінімальний хід архітектурного коду

```c
/* 1. перекласти карту прошивки в memory */
for (i = 0; i < e820_table->nr_entries; i++) {
        struct e820_entry *e = &e820_table->entries[i];

        if (e->type == E820_TYPE_RAM)
                memblock_add(e->addr, e->size);
}

/* 2. назвати вголос усе зайняте */
memblock_reserve(__pa_symbol(_text), __pa_symbol(_end) - __pa_symbol(_text));

/* 3. підняти стелю до реально відображеної пам'яті й дозволити ріст масивів */
memblock_set_current_limit(max_pfn_mapped << PAGE_SHIFT);
memblock_allow_resize();

/* 4. виділяти */
u32 *tbl = memblock_alloc(nr * sizeof(*tbl), SMP_CACHE_BYTES);
if (!tbl)
        panic("немає ранньої пам'яті під таблицю\n");
```

Порядок тут не косметичний: `memblock_allow_resize()` до підняття стелі означає, що подвоєному масивові нікуди лягти, а виділення до `memblock_reserve()` образу ядра просто віддасть пам'ять, у якій це ядро лежить.

## Що видно назовні

За `CONFIG_DEBUG_FS` `__initcall` створює каталог `/sys/kernel/debug/memblock` із двома файлами на читання (права 0444) — `memory` і `reserved`. Формат рядка — номер запису, межі включно, вузол (або `x`, якщо вузол не заданий) і назва прапорця:

```
   0: 0x0000000000001000..0x000000000009efff    x NONE
   1: 0x0000000000100000..0x00000000bffdffff    0 NONE
```

`memblock=debug` пише інакше — через `pr_info()` і з довжиною діапазону окремим числом:

```
 memory.cnt  = 0x2
 memory[0x0]	[0x0000000000001000-0x000000000009efff], 0x000000000009e000 bytes flags: 0x0
```

Там же видно й обидві події зростання масивів: успішну — `memblock: %s is doubled to %ld at [%pa-%pa]`, і фатальну — `memblock: cannot resize %s array`, після якої ядро зупиняється.

Чи будуть ці файли осмислені після завантаження, вирішує `CONFIG_ARCH_KEEP_MEMBLOCK`. Без нього `__init_memblock` розкривається в `__meminit`, а `memblock_discard()` викидає масиви разом з іншим кодом ініціалізації; з ним `__init_memblock` порожній, `memblock_discard()` нічого не робить, і масиви живуть далі. Обирають цей параметр архітектури, яким і через годину роботи треба питати «чи це взагалі пам'ять» — зокрема arm64 і powerpc.
