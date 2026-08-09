# 📋 SPARSEMEM: параметри збірки, числа архітектур і важелі спостереження

Модель фізичної пам'яті майже не має інтерфейсу для програм — зате має чималу поверхню для того, хто збирає ядро, налагоджує драйвер або дивиться, чому машина не бере нову планку. Тут зібрано цю поверхню: параметри `Kconfig`, числа, з яких виводяться всі інші, поля запису каталогу секцій, функції перетворення «номер кадру ↔ описувач» і файли, якими стан секцій читають із командного рядка. Значення звірені з деревом ядра станом на серпень 2026; де вони помітно мінялися, це названо окремо.

Дві домовленості на весь текст. `pfn` — номер кадру, тобто фізична адреса, поділена на розмір сторінки. Секція — шматок фізичного адресного простору сталого розміру, одиниця, якою SPARSEMEM веде облік; каталог секцій зветься `mem_section[]`.

---

## Частина перша: параметри збірки

Жоден із них сьогодні не обирається вручну на 64-бітовій машині — усі виводяться. Дивитися на них варто не щоб перемкнути, а щоб зрозуміти, у якому режимі працює конкретне ядро.

| параметр | як заданий | що означає |
|---|---|---|
| `CONFIG_SELECT_MEMORY_MODEL` | вмикає архітектура | чи взагалі показувати користувачеві вибір моделі |
| `CONFIG_ARCH_SPARSEMEM_ENABLE` | `bool` без запиту, вмикає архітектура | архітектура вміє SPARSEMEM |
| `CONFIG_ARCH_SPARSEMEM_DEFAULT` | те саме | SPARSEMEM буде обрано за домовленістю |
| `CONFIG_FLATMEM` | `def_bool y`, за `!SPARSEMEM \|\| FLATMEM_MANUAL` | один глобальний масив `mem_map[]` |
| `CONFIG_SPARSEMEM` | `def_bool y`, за `ARCH_SPARSEMEM_ENABLE \|\| SPARSEMEM_MANUAL` | каталог секцій замість одного масиву |
| `CONFIG_SPARSEMEM_EXTREME` | `def_bool y`, за `SPARSEMEM && !SPARSEMEM_STATIC` | каталог дворівневий: листок виділяється на вимогу |
| `CONFIG_SPARSEMEM_VMEMMAP_ENABLE` | `bool` без запиту, вмикає архітектура | архітектура вміє віртуальне вікно описувачів |
| `CONFIG_SPARSEMEM_VMEMMAP` | `def_bool y`, за `SPARSEMEM && SPARSEMEM_VMEMMAP_ENABLE` | описувачі — суцільне відображення, а не набір масивів |
| `CONFIG_HUGETLB_PAGE_OPTIMIZE_VMEMMAP` | `def_bool`, за `ARCH_WANT_OPTIMIZE_HUGETLB_VMEMMAP && SPARSEMEM_VMEMMAP` | код злиття однакових описувачів великих сторінок зібрано в ядро |
| `CONFIG_HUGETLB_PAGE_OPTIMIZE_VMEMMAP_DEFAULT_ON` | `bool` із запитом, типово `n` | те саме злиття ввімкнено вже при завантаженні |
| `CONFIG_ARCH_WANT_OPTIMIZE_DAX_VMEMMAP` | `bool`, вмикає архітектура | те саме, але для діапазонів `ZONE_DEVICE` |
| `CONFIG_ARCH_MHP_MEMMAP_ON_MEMORY_ENABLE` | `bool`, вмикає архітектура | описувачі доданого блока можна класти в нього самого |

Два зауваження, які помітно міняють читання цієї таблиці.

`CONFIG_SPARSEMEM_VMEMMAP` мав запит («Sparse Memory virtual memmap») і його можна було вимкнути руками. У серії Давида Гільденбранда (David Hildenbrand), поданої в серпні 2025-го, запит прибрали: на архітектурах, які вміють vmemmap, він тепер завжди `y`. До того це вже було зроблено для arm64, s390 і x86 поодинці — серія лише поширила правило на loongarch, powerpc, riscv і sparc. Тобто «вимкнути vmemmap і подивитися, чи стане краще» на сучасному ядрі більше не варіант.

`CONFIG_SPARSEMEM_VMEMMAP_PREINIT` (разом з `ARCH_WANT_HUGETLB_VMEMMAP_PREINIT`) — внутрішній параметр без запиту, що з'явився 2025 року для одного вузького випадку: великі сторінки, замовлені ще в рядку ядра, дістають уже злитий vmemmap одразу, замість того щоб виділити описувачі й негайно їх звільнити.

Побачити, що вийшло на конкретній машині ([де ядро тримає свою конфігурацію й що з неї видно вже після завантаження](book:unix-linux/kernel-config-and-build): `.config` збірки або той самий текст, вкладений в образ і доступний як `/proc/config.gz`):

```sh
$ zgrep -E '^CONFIG_(FLATMEM|SPARSEMEM|HUGETLB_PAGE_OPT)' /proc/config.gz
CONFIG_FLATMEM_MANUAL is not set
CONFIG_SPARSEMEM_MANUAL=y
CONFIG_SPARSEMEM=y
CONFIG_SPARSEMEM_EXTREME=y
CONFIG_SPARSEMEM_VMEMMAP_ENABLE=y
CONFIG_SPARSEMEM_VMEMMAP=y
CONFIG_HUGETLB_PAGE_OPTIMIZE_VMEMMAP=y
```

---

## Частина друга: числа архітектури

Архітектура задає рівно два числа. `MAX_PHYSMEM_BITS` — справжня ширина фізичної адреси, яку тримає апаратура. `SECTION_SIZE_BITS` — вибір людини: наскільки дрібно різати адресний простір. Решта виводиться:

```
PA_SECTION_SHIFT        = SECTION_SIZE_BITS
PFN_SECTION_SHIFT       = SECTION_SIZE_BITS − PAGE_SHIFT
PAGES_PER_SECTION       = 1 << PFN_SECTION_SHIFT
PAGE_SECTION_MASK       = ~(PAGES_PER_SECTION − 1)
SECTIONS_SHIFT          = MAX_PHYSMEM_BITS − SECTION_SIZE_BITS
NR_MEM_SECTIONS         = 1 << SECTIONS_SHIFT
SECTIONS_PER_ROOT       = PAGE_SIZE ÷ sizeof(struct mem_section)

SUBSECTION_SHIFT        = 21                       ← 2 МіБ, однаково всюди
PFN_SUBSECTION_SHIFT    = SUBSECTION_SHIFT − PAGE_SHIFT
PAGES_PER_SUBSECTION    = 1 << PFN_SUBSECTION_SHIFT
SUBSECTIONS_PER_SECTION = 1 << (SECTION_SIZE_BITS − SUBSECTION_SHIFT)

номер секції            = pfn >> PFN_SECTION_SHIFT      (pfn_to_section_nr)
перший кадр секції      = nr  << PFN_SECTION_SHIFT      (section_nr_to_pfn)
```

| архітектура | сторінка | `SECTION_SIZE_BITS` | секція | кадрів у секції | масив секції | `MAX_PHYSMEM_BITS` |
|---|---|---|---|---|---|---|
| x86-64, 4 рівні | 4 КіБ | 27 | 128 МіБ | 32768 | 2 МіБ | 46 |
| x86-64, 5 рівнів | 4 КіБ | 27 | 128 МіБ | 32768 | 2 МіБ | 52 |
| arm64 | 4 КіБ | 27 | 128 МіБ | 32768 | 2 МіБ | `CONFIG_ARM64_PA_BITS` (звично 48) |
| arm64 | 16 КіБ | 27 | 128 МіБ | 8192 | 512 КіБ | те саме |
| arm64 | 64 КіБ | 29 | 512 МіБ | 8192 | 512 КіБ | те саме |
| riscv, 64 біти | 4 КіБ | 27 | 128 МіБ | 32768 | 2 МіБ | 56 |
| s390 | 4 КіБ | 27 | 128 МіБ | 32768 | 2 МіБ | `CONFIG_MAX_PHYSMEM_BITS` |
| powerpc | 4 / 64 КіБ | 24 | 16 МіБ | 4096 / 256 | 256 КіБ / 16 КіБ | залежить від MMU |
| x86-32 з PAE | 4 КіБ | 29 | 512 МіБ | 131072 | 8 МіБ | 36 |
| x86-32 без PAE | 4 КіБ | 26 | 64 МіБ | 16384 | 1 МіБ | 32 |

Масив секції рахований для `sizeof(struct page) = 64`. На x86-64 у файлі `arch/x86/include/asm/sparsemem.h` `MAX_PHYSMEM_BITS` — не стала, а вираз `pgtable_l5_enabled() ? 52 : 46`: те саме ядро на машині з п'ятирівневими таблицями адресує в шістдесят чотири рази більший простір.

Значення 27 на arm64 з'явилося не одразу: до ядра 5.12 (2021) секція там була 2³⁰, тобто цілий гігабайт, і саме стільки становила найдрібніша одиниця гарячого додавання.

**Порахуймо x86-64 із чотирирівневими таблицями до кінця — саме звідси беруться всі числа, які видно в системі:**

```
SECTION_SIZE_BITS    = 27          → секція 2²⁷ = 128 МіБ
PFN_SECTION_SHIFT    = 27 − 12     = 15
PAGES_PER_SECTION    = 2¹⁵         = 32768 кадрів
масив однієї секції  = 32768 × 64 Б = 2 МіБ  ← рівно один запис PMD

MAX_PHYSMEM_BITS     = 46          → 64 ТіБ фізичних адрес
NR_MEM_SECTIONS      = 2⁴⁶⁻²⁷ = 2¹⁹ = 524288
sizeof(mem_section)  = 16 Б        (два слова, без CONFIG_PAGE_EXTENSION)
каталог одним шматком = 524288 × 16 Б = 8 МіБ

SECTIONS_PER_ROOT    = 4096 ÷ 16   = 256 секцій = 32 ГіБ адрес на листок
верхній масив        = 524288 ÷ 256 = 2048 покажчиків × 8 Б = 16 КіБ
машина з 64 ГіБ поспіль → 16 КіБ + два листки по 4 КіБ = 24 КіБ

SUBSECTIONS_PER_SECTION = 2²⁷⁻²¹   = 64  ← мапа підсекцій в одному слові
```

Вісім мегабайтів проти двадцяти чотирьох кілобайтів — це і є вся суть `SPARSEMEM_EXTREME`, і саме тому він `def_bool y`. З п'ятирівневими таблицями розрив ще більший: `NR_MEM_SECTIONS` = 2²⁵, суцільний каталог важив би 512 МіБ.

---

## Частина третя: запис каталогу

```c
struct mem_section {
        unsigned long section_mem_map;
        struct mem_section_usage *usage;
#ifdef CONFIG_PAGE_EXTENSION
        struct page_ext *page_ext;
        unsigned long pad;
#endif
};

struct mem_section_usage {
        struct rcu_head rcu;
#ifdef CONFIG_SPARSEMEM_VMEMMAP
        DECLARE_BITMAP(subsection_map, SUBSECTIONS_PER_SECTION);
#endif
        unsigned long pageblock_flags[0];
};
```

Слово `section_mem_map` служить двом різним речам у різні моменти життя секції.

![Слово section_mem_map: молодші біти — прапорці, старші — спершу номер вузла, потім зміщена адреса масиву](/reference/unix-linux/memory/sparsemem-and-vmemmap/img/section-word.svg)

*`sparse_early_nid()` читає старші біти як номер вузла — але тільки доти, доки їх не затерла адреса масиву.*

Прапорці лежать у молодших бітах, а їхні номери задає перелік, тож залежать від конфігурації — покладатися варто на макроси, не на числа:

| прапорець | що означає |
|---|---|
| `SECTION_MARKED_PRESENT` | у діапазоні секції прошивка оголосила пам'ять |
| `SECTION_HAS_MEM_MAP` | масив описувачів для секції вже заведено |
| `SECTION_IS_ONLINE` | секція в роботі: її сторінки віддано розподільникові |
| `SECTION_IS_EARLY` | секція заведена при завантаженні, а не гарячим додаванням |
| `SECTION_TAINT_ZONE_DEVICE` | у секції є сторінки `ZONE_DEVICE` (лише за `CONFIG_ZONE_DEVICE`) |
| `SECTION_IS_VMEMMAP_PREINIT` | vmemmap секції заповнено наперед (лише за `CONFIG_SPARSEMEM_VMEMMAP_PREINIT`) |
| `SECTION_MAP_LAST_BIT` | не прапорець, а межа: перший біт, який уже належить адресі |

Питають їх не безпосередньо, а через маленькі вбудовані функції з `include/linux/mmzone.h`:

| функція | що питає |
|---|---|
| `__pfn_to_section(pfn)` | запис каталогу за номером кадру; `NULL`, якщо листка немає |
| `__nr_to_section(nr)` | те саме за номером секції |
| `present_section(ms)`, `present_section_nr(nr)` | `SECTION_MARKED_PRESENT` |
| `valid_section(ms)`, `valid_section_nr(nr)` | `SECTION_HAS_MEM_MAP` |
| `early_section(ms)` | `SECTION_IS_EARLY` |
| `online_section(ms)`, `online_section_nr(nr)` | `SECTION_IS_ONLINE` |
| `online_device_section(ms)` | `SECTION_IS_ONLINE` і `SECTION_TAINT_ZONE_DEVICE` одночасно |
| `pfn_section_valid(ms, pfn)` | біт цієї підсекції в `usage->subsection_map` |
| `__section_mem_map_addr(ms)` | `section_mem_map & SECTION_MAP_MASK` — сама адреса, без прапорців |

---

## Частина четверта: перетворення

Три моделі — три різні визначення однієї пари макросів, `include/asm-generic/memory_model.h`:

```c
/* CONFIG_FLATMEM */
#define __pfn_to_page(pfn)   (mem_map + ((pfn) - ARCH_PFN_OFFSET))
#define __page_to_pfn(page)  ((unsigned long)((page) - mem_map) + ARCH_PFN_OFFSET)

/* CONFIG_SPARSEMEM_VMEMMAP */
#define __pfn_to_page(pfn)   (vmemmap + (pfn))
#define __page_to_pfn(page)  (unsigned long)((page) - vmemmap)

/* CONFIG_SPARSEMEM — обидва напрямки складніші за один вираз, тому це
   інструкції-вирази GCC; тут наведено те, що вони роблять по суті */
#define __pfn_to_page(pfn)   ({ struct mem_section *__s = __pfn_to_section(pfn); \
                                __section_mem_map_addr(__s) + (pfn); })
#define __page_to_pfn(pg)    ({ int __sec = memdesc_section((pg)->flags);        \
                                (unsigned long)((pg) - __section_mem_map_addr(   \
                                        __nr_to_section(__sec))); })
```

Функція `memdesc_section()` у зворотному напрямку — та, що дістає номер секції з бітів `page->flags`; донедавна вона звалася `page_to_section()`.

Ім'я `vmemmap` — макрос архітектури, і його визначення варте погляду:

| архітектура | `vmemmap` | зауваження |
|---|---|---|
| x86-64, 4 рівні | `(struct page *)vmemmap_base`, типово `0xffffea0000000000`, вікно 1 ТіБ | з `CONFIG_RANDOMIZE_MEMORY` база не стала, тому це змінна, а не константа |
| x86-64, 5 рівнів | `0xffd4000000000000`, вікно 0.5 ПіБ | |
| arm64 | `(struct page *)VMEMMAP_START − (memstart_addr >> PAGE_SHIFT)` | базу заздалегідь зменшено на перший кадр, тож віднімання назад лишається чистим |

Функція, без якої весь цей апарат небезпечний:

```c
static inline int pfn_valid(unsigned long pfn)
{
        struct mem_section *ms;
        int ret;

        if (PHYS_PFN(PFN_PHYS(pfn)) != pfn)          /* номер не влазить у фізичну адресу */
                return 0;
        if (pfn_to_section_nr(pfn) >= NR_MEM_SECTIONS)
                return 0;
        ms = __pfn_to_section(pfn);
        rcu_read_lock_sched();
        if (!valid_section(ms)) {
                rcu_read_unlock_sched();
                return 0;
        }
        /* рання секція заповнена цілком; у пізньої питаємо конкретну підсекцію */
        ret = early_section(ms) || pfn_section_valid(ms, pfn);
        rcu_read_unlock_sched();
        return ret;
}
```

Обхід під `rcu_read_lock_sched()` не декоративний: `usage` разом із мапою підсекцій звільняється через RCU, бо секцію можуть вилучати паралельно з читанням.

Питання, які легко переплутати, і чим на кожне відповідати:

| питання | відповідь |
|---|---|
| чи є за цим номером описувач | `pfn_valid(pfn)` |
| чи описувач іще й у робочому стані | `pfn_to_online_page(pfn)` з `<linux/memory_hotplug.h>` — `struct page *` або `NULL` |
| чи це оперативна пам'ять, а не вікно пристрою | `pfn_valid` цього не питає; дивитися `/proc/iomem` або `page_is_ram()` |
| чи ця сторінка нікуди не зникне під руками | ні `pfn_valid`, ні `pfn_to_online_page` не тримають посилання — треба [брати сторінку в облік перед передачею пристроєві](book:unix-linux/page-pinning-gup): `pin_user_pages()` піднімає лічильник і забороняє переносити кадр |

Мінімальний робочий модуль, який друкує стан секції за номером кадру (символ `mem_section` експортований, тож `__pfn_to_section()` доступний і поза ядром — [як збирається й вантажиться модуль](book:unix-linux/kernel-modules): окремий об'єктний файл, який вставляють у працююче ядро й лінкують з його символами):

```c
#include <linux/mm.h>
#include <linux/mmzone.h>
#include <linux/memory_hotplug.h>

static void describe_pfn(unsigned long pfn)
{
        struct mem_section *ms;
        struct page *pg;

        if (!pfn_valid(pfn)) {
                pr_info("pfn %lu: описувача немає\n", pfn);
                return;   /* pfn_to_page() тут поклав би ядро */
        }
        ms = __pfn_to_section(pfn);
        pg = pfn_to_online_page(pfn);         /* NULL, якщо секція не в роботі */

        pr_info("pfn %lu  секція %lu  present=%d early=%d online=%d  page=%px\n",
                pfn, pfn_to_section_nr(pfn),
                !!present_section(ms), !!early_section(ms), !!online_section(ms), pg);
}
```

| симптом | причина |
|---|---|
| падіння ядра на адресі всередині вікна vmemmap | `pfn_to_page()` на номер із діри, без `pfn_valid()` |
| `pfn_valid()` каже «так», а сторінка не в розподільнику | секція наявна, але блок переведено в `offline` — питати треба `pfn_to_online_page()` |
| `pfn_valid()` каже «так» на діапазон пристрою | це `ZONE_DEVICE`: описувачі є, звичайної пам'яті немає |
| перевірка минула, а кадр під час роботи поїхав | описувач не закріплено; `pfn_valid()` — це не посилання |

---

## Частина п'ята: що видно з командного рядка

Секцій самих собою в `/sys` немає — назовні виходить укрупнена одиниця, блок пам'яті, і кожен блок є ціле число секцій. Тека `/sys/devices/system/memory/` ([як пристрої й підсистеми взагалі показані в sysfs](book:unix-linux/sysfs-device-model): дерево тек, де кожен файл — одне значення, читане й часто записуване):

| файл | доступ | що |
|---|---|---|
| `block_size_bytes` | ч | розмір блока в байтах, **шістнадцятковим без префікса** |
| `auto_online_blocks` | ч/з | у який стан ставити нові блоки: `offline`, `online`, `online_kernel`, `online_movable` |
| `probe` | з | оголосити блок за фізичною адресою вручну (де архітектура це вміє) |
| `memoryX/state` | ч/з | читається як `online`, `offline`, `going-offline`; пишеться одним із чотирьох станів вище |
| `memoryX/online` | ч/з | те саме спрощено: `0` або `1` |
| `memoryX/valid_zones` | ч | у якій зоні блок опинився (є за `CONFIG_MEMORY_HOTREMOVE`) |
| `memoryX/phys_index` | ч | номер блока |
| `memoryX/removable` | ч | легасі: колись натякало, чи блок узагалі знімний |
| `memoryX/phys_device` | ч | легасі, використовував лише s390 |

Розмір блока архітектура обирає сама, і x86-64 тут поводиться не так, як решта:

```
типово (arm64, riscv, s390): 1 << SECTION_SIZE_BITS  = розмір секції

x86-64, probe_memory_block_size():
    пам'яті менше за 64 ГіБ      → 128 МіБ
    пам'яті 64 ГіБ і більше      → до 2 ГіБ, з підказки прошивки або стелі,
                                    далі вдвічі меншає, доки не збіжиться
                                    з вирівнюванням кінця пам'яті
```

```sh
$ cat /sys/devices/system/memory/block_size_bytes
8000000
$ echo $(( 0x$(cat /sys/devices/system/memory/block_size_bytes) / 1024 / 1024 ))
128
$ cat /sys/devices/system/memory/memory*/state | sort | uniq -c
    511 online
      1 offline
```

Шістнадцяткове `8000000` — це 128 МіБ; переплутати його з десятковим числом легко, а помилка виходить у шістдесят разів.

---

## Частина шоста: перемикачі, що міняють поведінку

| важіль | де живе | значення | типове |
|---|---|---|---|
| `hugetlb_free_vmemmap=` | рядок ядра | `on`, `off` | `off`, або `on` за `CONFIG_HUGETLB_PAGE_OPTIMIZE_VMEMMAP_DEFAULT_ON=y` |
| `vm.hugetlb_optimize_vmemmap` | `sysctl` | `0`, `1` | успадковує стан попереднього |
| `memory_hotplug.memmap_on_memory` | рядок ядра; далі `/sys/module/memory_hotplug/parameters/memmap_on_memory` (права `0444` — лише читання) | `Y`, `N`, `force` | `N` |
| `memory_hotplug.online_policy` | те саме, права `0644` | `contig-zones`, `auto-movable` | `contig-zones` |
| `memory_hotplug.auto_movable_ratio` | те саме | стеля відношення рухомої пам'яті до нерухомої, у відсотках | `301` |
| `memory_hotplug.auto_movable_numa_aware` | те саме | `Y`, `N` | `Y` |

Злиття описувачів великих сторінок (HVO) має три властивості, через які його регулярно вмикають марно. Воно діє **лише на сторінки, виділені після ввімкнення**: уже набраний пул лишається як був. Воно недоступне, коли `sizeof(struct page)` не є степенем двійки. І воно робить виділення та звільнення великої сторінки приблизно вдвічі повільнішими, бо описувачі доводиться щоразу розводити й зводити назад. Скільки саме пам'яті це повертає й на чому — у [важелях пулу великих сторінок і прозорих великих сторінок](book:unix-linux/huge-pages/api-huge-page-interfaces.md); ключ `vm.hugetlb_optimize_vmemmap` живе там же, серед решти [параметрів, які ядро віддає через `sysctl`](book:unix-linux/sysctl-tunables).

`force` у `memmap_on_memory` — не синонім «увімкнено». Звичайне `Y` вимагає, щоб описувачі рівно вкладалися в кратне число сторінок доданого блока, і мовчки відмовляється, коли не вкладаються; `force` наказує класти їх туди в будь-якому разі, і саме опис параметра в ядрі попереджає, що це може змарнувати пам'ять. Взаємодія з HVO однобічна: описувачі, взяті з самого доданого блока, злити вже не можна, а решта vmemmap цього ж блока злиттю піддається.

Два останні важелі стосуються не моделі пам'яті, а того, куди потрапляє додана пам'ять, — але без них картина не сходиться: блок, який приїхав у `ZONE_NORMAL`, майже напевно вже не вимкнеться, бо ядро розкладе в ньому нерухомі об'єкти. Що з цим робить політика `auto-movable`, коли її варто вмикати й чому вилучення пам'яті — задача принципово важча за додавання, розібрано в [гарячому додаванні й вилученні пам'яті](book:unix-linux/memory-hotplug): ядро вміє брати нові діапазони фізичної пам'яті на ходу, блоками, і переводити їх у робочий стан або назад. Окремий випадок — [постійна пам'ять як пристрій](book:unix-linux/persistent-memory-devices): її простори імен ніхто не рівняв на 128 МіБ, і саме заради них у vmemmap існує крок у 2 МіБ.
