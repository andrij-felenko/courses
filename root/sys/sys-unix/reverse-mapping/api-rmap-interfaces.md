# 📋 Довідка по rmap: структури, поля, функції й замки

Це перелік того, з чого в ядрі Linux зібрано зворотне відображення: які поля має `struct anon_vma` і `struct anon_vma_chain`, як молодші біти вказівника `folio->mapping` кодують три різні світи, з чого складається `struct rmap_walk_control`, які функції ведуть облік відображень і — головне — якого замка кожна з них вимагає від того, хто її кличе. Ця остання таблиця тут найважливіша: у цьому місці ядра не той замок коштує не повільності, а взаємного блокування або мовчазного псування чужої пам'яті.

**Це не ABI.** Усе нижче — внутрішні інтерфейси ядра. На них не поширюється правило «не ламати простір користувача» ([що саме заморожено](root:sys-unix/kernel-abi-stability) — окрема тема): імена, підписи, самі поля структур міняються між випусками, і кожна така зміна — звичайна рутина, а не подія. За опорну точку тут узято **6.12 LTS**; місця, де дерево вже поїхало далі, помічено окремо, а наприкінці зібрано перелік зсувів. Перед тим як писати код, звіряйте кожен підпис із деревом **свого** ядра — `git grep -n 'folio_add_anon_rmap_ptes' include/linux/rmap.h` дасть відповідь швидше за будь-яку статтю.

## Куди вказує folio->mapping

Одне поле відповідає на питання «якому об'єктові належить ця сторінка», і відповідей у нього чотири — причому одна з них до зворотного відображення стосунку не має. Розрізняють їх два молодші біти самого вказівника: структури, на які він може вказувати, вирівняні щонайменше на чотири байти, тож ці біти в чесній адресі однаково нульові й вільні під прапорці.

```c
/* include/linux/page-flags.h, ядра до 6.16 включно */
#define PAGE_MAPPING_ANON       0x1
#define PAGE_MAPPING_MOVABLE    0x2
#define PAGE_MAPPING_KSM        (PAGE_MAPPING_ANON | PAGE_MAPPING_MOVABLE)
#define PAGE_MAPPING_FLAGS      (PAGE_MAPPING_ANON | PAGE_MAPPING_MOVABLE)
```

| Молодші біти | Куди насправді веде `mapping` | Хто це перевіряє |
| --- | --- | --- |
| `00` | `struct address_space` інода — або `NULL` у сторінки, що нікому не належить | `folio_mapping()` |
| `01` — лише `ANON` | `struct anon_vma` | `folio_test_anon()` |
| `10` — лише `MOVABLE` | `struct movable_operations` не-LRU рухомої сторінки (кулька драйвера балона, `zsmalloc`); до зворотного відображення стосунку не має | `__folio_test_movable()` |
| `11` — `KSM` | вузол стабільного дерева [механізму злиття однакових сторінок](root:sys-unix/ksm-page-merging), а не `anon_vma` | `folio_test_ksm()` |

Дістати вказівник із поля — це відняти прапорці, і саме так це записано в коді:

```c
anon_mapping = (unsigned long)READ_ONCE(folio->mapping);
if ((anon_mapping & PAGE_MAPPING_FLAGS) != PAGE_MAPPING_ANON)
        return NULL;                    /* не анонімна — не наш випадок */
anon_vma = (struct anon_vma *)(anon_mapping - PAGE_MAPPING_ANON);
```

**Умова.** Зі знімка пам'яті прочитано `folio->mapping = 0xffff888104a3c001`, сторінка не належить кешеві плит.

```
mapping                       =  0xffff888104a3c001
mapping & 0x3                 =  0x1        → лише PAGE_MAPPING_ANON
адреса структури              =  0xffff888104a3c001 − 1  =  0xffff888104a3c000
висновок                      :  за адресою лежить struct anon_vma
```

Одне застереження, через яке ловлять помилки при читанні дампів: у сторінки, відданої під кеш плит, цих полів **немає взагалі** — розподільник [кешу об'єктів ядра](root:sys-unix/kernel-memory-slab) вживає ті самі байти `struct page` під власний стан. Перевірка `folio_test_slab()` мусить іти першою, інакше всі три прапорці читаються з чужих даних.

**Зсув від 6.17.** Прапорці перейменували, і зміст бітів змінився: `PAGE_MAPPING_MOVABLE` зник, бо не-LRU рухомі сторінки переїхали на окремий тип сторінки (`PG_movable_ops`), а біт `0x2` дістав нове ім'я й нову роль — він осмислений лише разом із `ANON`.

```c
/* include/linux/page-flags.h, від 6.17 */
#define FOLIO_MAPPING_ANON      0x1
#define FOLIO_MAPPING_ANON_KSM  0x2
#define FOLIO_MAPPING_KSM       (FOLIO_MAPPING_ANON | FOLIO_MAPPING_ANON_KSM)
#define FOLIO_MAPPING_FLAGS     (FOLIO_MAPPING_ANON | FOLIO_MAPPING_ANON_KSM)
```

## struct anon_vma: спільна точка збору

```c
/* include/linux/rmap.h */
struct anon_vma {
        struct anon_vma        *root;             /* корінь дерева; у корені — сам на себе */
        struct rw_semaphore     rwsem;            /* справжній замок — тільки в корені */
        atomic_t                refcount;
        unsigned long           num_children;
        unsigned long           num_active_vmas;
        struct anon_vma        *parent;
        struct rb_root_cached   rb_root;          /* дерево інтервалів ребер */
};
```

| Поле | Що означає | Хто його береже |
| --- | --- | --- |
| `root` | корінь дерева об'єктів, що виросло з розгалужень; замок беруть **завжди** за цим вказівником, а не за своїм `rwsem` | не міняється після створення |
| `rwsem` | читання-запис на дерево ребер; фактично працює лише примірник у корені | сам собою |
| `refcount` | лічильник посилань; піднімають ті, хто не має гарантії, що ділянка проживе всю операцію | атомарний |
| `num_children` | скільки об'єктів мають `parent`, рівний цьому, **включно з ним самим** | `rwsem` кореня |
| `num_active_vmas` | скільки ділянок мають `vma->anon_vma`, рівний цьому | `rwsem` кореня |
| `parent` | об'єкт, від якого цей відгалузився | не міняється після створення |
| `rb_root` | дерево інтервалів усіх ребер, приписаних до цього об'єкта | `rwsem` кореня |

Два лічильники — не статистика, а вхід у єдине правило: коли `anon_vma_clone` бачить об'єкт, у якого `num_active_vmas == 0` і `num_children < 2`, він **не заводить новий**, а віддає нащадкові цей. Саме це не дає ланцюжкові послідовних розгалужень рости квадратично. Корінь при цьому ніколи не перевикористовується: він посилається сам на себе як на предка, тож його `num_children` завжди щонайменше одиниця.

`rb_root_cached` — це [червоно-чорне дерево](root:sf-algorithms/red-black-tree) з окремо збереженим лівим краєм, доповнене до [дерева інтервалів](root:sf-algorithms/interval-tree): кожен вузол додатково носить найбільший кінець відрізка в своєму піддереві, і саме це дозволяє відсікати цілі гілки при запиті «які ребра накривають задане зміщення».

> 🔧 **Навіщо це.** Поле `root` — найчастіша причина «незрозумілих» заклинань у власному коді, що чіпає анонімні ділянки. Замок у дереві об'єктів один на все дерево, і живе він у корені; помічники `anon_vma_lock_read/write` самі туди йдуть, а ось прямий `down_read(&anon_vma->rwsem)` за власним примірником компілюється, працює на однопроцесній машині й розвалюється під навантаженням, бо два учасники беруть **різні** семафори, вважаючи, що беруть один.

## struct anon_vma_chain: ребро, вписане у два індекси

```c
struct anon_vma_chain {
        struct vm_area_struct  *vma;
        struct anon_vma        *anon_vma;
        struct list_head        same_vma;         /* ланка в списку ділянки */
        struct rb_node          rb;               /* вузол у дереві об'єкта */
        unsigned long           rb_subtree_last;  /* доповнення дерева інтервалів */
#ifdef CONFIG_DEBUG_VM_RB
        unsigned long           cached_vma_start, cached_vma_last;
#endif
};
```

Уся сіль структури в тому, що одне ребро «ділянка ↔ об'єкт» стоїть одночасно у двох різних індексах і відповідає на два протилежні питання.

| Поле | Індекс, у якому воно стоїть | Питання, на яке відповідає | Замок |
| --- | --- | --- | --- |
| `same_vma` | плаский список `vma->anon_vma_chain` | «до яких об'єктів приписана ця ділянка» | `mmap_lock` і замок таблиці сторінок |
| `rb` · `rb_subtree_last` | дерево інтервалів `anon_vma->rb_root` | «які ділянки приписані до цього об'єкта й накривають задане зміщення» | `anon_vma->root->rwsem` |

Звідси й асиметрія в цінах. Перше питання виникає при розборі ділянки (`unlink_anon_vmas`, злиття, розділення) і завжди має короткий список — стільки елементів, скільки предків у ділянки. Друге виникає на кожному обході зворотного відображення й мусить бути швидким при тисячах ділянок, тому там дерево, а не список.

Поля `cached_vma_start` і `cached_vma_last` існують лише при `CONFIG_DEBUG_VM_RB` (див. [конфігурацію ядра](root:sys-unix/kernel-config-and-build)) і потрібні одному: перевіряти, що доповнення дерева не розійшлося з дійсними межами ділянки. У бойовій збірці їх немає, тож `sizeof(struct anon_vma_chain)` між збірками різний — не закладайтеся на число.

## Ключ обходу: адреса з зміщення

Обидва дерева — і `i_mmap` інода, і `rb_root` об'єкта — індексуються **зміщенням у сторінках**, а не адресами. Переклад в адресу робить одна функція:

```c
/* mm/internal.h */
static inline unsigned long vma_address(struct vm_area_struct *vma,
                                        pgoff_t pgoff, unsigned long nr_pages);
/* повертає -EFAULT, якщо жодна сторінка діапазону не потрапляє в ділянку */
```

Її поведінка на краю має значення для будь-якого власного обходу: якщо початок діапазону лежить **до** початку ділянки, але хвіст усе-таки в неї заходить, повертається `vma->vm_start`, а не помилка. Великий folio, що звисає з початку ділянки, обхід тому не пропускає.

## struct rmap_walk_control і сам обхід

```c
struct rmap_walk_control {
        void *arg;
        bool  try_lock;
        bool  contended;
        bool (*rmap_one)(struct folio *folio, struct vm_area_struct *vma,
                         unsigned long addr, void *arg);
        int  (*done)(struct folio *folio);
        struct anon_vma *(*anon_lock)(struct folio *folio,
                                      struct rmap_walk_control *rwc);
        bool (*invalid_vma)(struct vm_area_struct *vma, void *arg);
};

void rmap_walk(struct folio *folio, struct rmap_walk_control *rwc);
void rmap_walk_locked(struct folio *folio, struct rmap_walk_control *rwc);
```

| Поле | Обов'язкове | Зміст |
| --- | --- | --- |
| `arg` | ні | передається без змін у `rmap_one` та `invalid_vma`; звичайно вказівник на власний накопичувач |
| `try_lock` | ні | «не чекати на замку»: якщо `trylock` не вдався, обхід не блокується, а відступає |
| `contended` | ні | заповнює **обхід**: `true` означає, що відступили саме через зайнятий замок, а не через порожній результат |
| `rmap_one` | **так** | те, що робиться з кожною знайденою парою «ділянка, адреса»; повернути `false` — припинити обхід |
| `done` | ні | перевіряється після кожного `rmap_one`; ненульове повернення завершує обхід достроково |
| `anon_lock` | ні | власний спосіб узяти замок анонімного об'єкта; типово `folio_lock_anon_vma_read` |
| `invalid_vma` | ні | відсіювання нецікавих ділянок **до** виклику `rmap_one` |

Розрізнення `rmap_one` і `done` неочевидне, а різниця істотна: `rmap_one` каже «мені більше нічого не треба», а `done` — «мета досягнута, дивитися далі нема сенсу». Витіснення ставить у `done` перевірку `folio_not_mapped`: щойно лічильник відображень упав до нуля, обхід зупиняється, навіть якщо в дереві лишилися ділянки.

`rmap_walk` сам вибирає, куди йти:

| Вид folio | Куди веде обхід | Що обходить | Чого вимагає |
| --- | --- | --- | --- |
| `folio_test_ksm()` | `rmap_walk_ksm` (`mm/ksm.c`) | ланцюжок `rmap_item` вузла стабільного дерева, а для кожного — усе дерево його `anon_vma` **цілком**, без відсікання за зміщенням | замок folio |
| `folio_test_anon()` | `rmap_walk_anon` | ребра `anon_vma->rb_root` у діапазоні зміщень folio | замок анонімного об'єкта бере сам |
| решта | `rmap_walk_file` | ділянки `mapping->i_mmap` у діапазоні зміщень folio | замок folio (перевіряється `VM_BUG_ON_FOLIO`) |

`rmap_walk_locked` робить те саме, але виходить із того, що потрібний замок уже в руках викликача; на злитій сторінці він просто падає — підтримки KSM у ньому немає.

Мінімальний робочий обхід — порахувати, у скількох ділянках folio видно, і надрукувати адресу в кожній:

```c
struct mapper_scan {
        unsigned int count;
};

static bool report_one(struct folio *folio, struct vm_area_struct *vma,
                       unsigned long addr, void *arg)
{
        struct mapper_scan *s = arg;

        s->count++;
        pr_info("rmap: mm=%p addr=%#lx %s\n",
                vma->vm_mm, addr, vma->vm_file ? "file" : "anon");
        return true;                     /* далі, до кінця дерева */
}

static void who_maps(struct folio *folio)
{
        struct mapper_scan scan = { .count = 0 };
        struct rmap_walk_control rwc = {
                .arg       = &scan,
                .rmap_one  = report_one,
                .anon_lock = folio_lock_anon_vma_read,
                .try_lock  = true,       /* під тиском краще відступити */
        };

        folio_lock(folio);               /* обов'язково для файлових і злитих */
        rmap_walk(folio, &rwc);
        folio_unlock(folio);

        if (rwc.contended)
                pr_info("rmap: lock contended, list incomplete\n");
        else
                pr_info("rmap: %u mappings total\n", scan.count);
}
```

Цей код збирається **лише всередині дерева ядра**. `rmap_walk` не експортований: у `mm/rmap.c` з усього переліку назовні відкрито тільки `folio_mkclean` і `make_device_exclusive_range`, обидва через `EXPORT_SYMBOL_GPL`. Із [завантажуваного модуля](root:sys-unix/kernel-modules) обхід не покличеш — і це свідоме рішення, а не недогляд.

## Облік відображень: хто додає і хто знімає

Функції обліку не ходять деревами — вони правлять лічильники й прапорці folio в мить, коли запис таблиці сторінок з'являється або зникає. Ім'я кожної складене за одним шаблоном: `folio_<дія>_<вид>_rmap_<рівень>`.

```c
void folio_add_new_anon_rmap(struct folio *, struct vm_area_struct *,
                             unsigned long address, rmap_t flags);
void folio_add_anon_rmap_ptes(struct folio *, struct page *, int nr_pages,
                              struct vm_area_struct *, unsigned long address,
                              rmap_t flags);
void folio_add_anon_rmap_pmd(struct folio *, struct page *,
                             struct vm_area_struct *, unsigned long address,
                             rmap_t flags);
void folio_add_file_rmap_ptes(struct folio *, struct page *, int nr_pages,
                              struct vm_area_struct *);
void folio_add_file_rmap_pmd(struct folio *, struct page *,
                             struct vm_area_struct *);
void folio_remove_rmap_ptes(struct folio *, struct page *, int nr_pages,
                            struct vm_area_struct *);
void folio_remove_rmap_pmd(struct folio *, struct page *,
                           struct vm_area_struct *);
void folio_move_anon_rmap(struct folio *, struct vm_area_struct *);

/* однослівні форми — макроси-обгортки з nr_pages = 1 */
#define folio_add_anon_rmap_pte(folio, page, vma, address, flags)  \
        folio_add_anon_rmap_ptes(folio, page, 1, vma, address, flags)
#define folio_add_file_rmap_pte(folio, page, vma)   folio_add_file_rmap_ptes(folio, page, 1, vma)
#define folio_remove_rmap_pte(folio, page, vma)     folio_remove_rmap_ptes(folio, page, 1, vma)
```

| Функція | Коли кличуть | Особливість |
| --- | --- | --- |
| `folio_add_new_anon_rmap` | сторінка щойно народилася в цій ділянці й більше ніде не відображена | обходиться без «збільшити й перевірити»: лічильник просто встановлюють, бо перегонів ще нема. Замок folio потрібен лише тоді, коли folio не позначено як виключне |
| `folio_add_anon_rmap_ptes` | відображення **вже наявної** анонімної сторінки: збій свопу, перенесення, спільна після розгалуження сторінка | вимагає замка folio: між установленням `mapping` і перевіркою `index` не має влізти перетворення на злиту сторінку |
| `folio_add_file_rmap_ptes` | відображення сторінки кешу файлу | замка folio не потребує: `mapping` файлової сторінки не міняється під ногами |
| `folio_remove_rmap_ptes` | знято `nr_pages` записів | тут же знімається `mlock` і, коли лічильник упав до нуля, оновлюється статистика вузла |
| `folio_move_anon_rmap` | сторінка після копіювання при записі лишилася в одного процесу — її переводять під його власний `anon_vma`, щоб обхід більше не перебирав батька й сусідів | вимагає замка folio й пише `mapping` одним `WRITE_ONCE` разом із бітом `ANON`: читач ніколи не побачить нового вказівника без прапорця |

`nr_pages` — не прикраса. Пакетний виклик замінює `n` окремих атомарних операцій над лічильником folio на одну, і для великого folio це різниця в порядок на гарячому шляху.

Прапорців `rmap_t`, які приймає анонімна гілка, усього два:

```c
typedef int __bitwise rmap_t;
#define RMAP_NONE       ((__force rmap_t)0)   /* сторінка, можливо, спільна */
#define RMAP_EXCLUSIVE  ((__force rmap_t)BIT(0))  /* належить рівно одному процесові */
```

`RMAP_EXCLUSIVE` — це обіцянка, з якої потім живе [копіювання при записі](root:sf-os/copy-on-write): позначену так сторінку при збої запису можна віддати без копіювання. Обіцянка знімається, щойно сторінка стає спільною, і саме тому родина `folio_try_dup_anon_rmap_*` при розгалуженні може повернути помилку, а не просто збільшити лічильник.

**Зсув після 6.12.** Додано `pud`-рівень (`folio_add_file_rmap_pud`, `folio_remove_rmap_pud`), а внутрішній `enum rmap_level` із значеннями `RMAP_LEVEL_PTE/PMD` замінено на спільний `enum pgtable_level` із `PGTABLE_LEVEL_PTE/PMD/PUD`. Це внутрішня кухня `mm/rmap.c`, але вона трапляється в стеках викликів і в патчах.

## Споживачі обходу

Усі вони — тонкі обгортки: складають `rmap_walk_control`, кличуть `rmap_walk`, розбирають накопичене.

```c
void try_to_unmap(struct folio *, enum ttu_flags flags);
void try_to_migrate(struct folio *folio, enum ttu_flags flags);
int  folio_referenced(struct folio *, int is_locked,
                      struct mem_cgroup *memcg, unsigned long *vm_flags);
int  folio_mkclean(struct folio *);
```

| Функція | Що робить її `rmap_one` | Які поля заповнює | Що повертає |
| --- | --- | --- | --- |
| `try_to_unmap` | прибирає запис таблиці, лишаючи позначку свопу або просто звільняючи; так працює [витіснення](root:sys-unix/swap-and-reclaim) | `done = folio_not_mapped`, `anon_lock` | нічого; викликач сам перевіряє `folio_mapped()` |
| `try_to_migrate` | ставить на місце записів спеціальні позначки перенесення, за якими інший процесор чекатиме | те саме + `invalid_vma`, що пропускає тимчасову ділянку `exec` | нічого |
| `folio_referenced` | збирає й скидає апаратний біт звернення, накопичує `vm_flags` усіх ділянок | `try_lock = true`, `invalid_vma`, `anon_lock` | кількість відображень зі зверненням, або **`-1`**, якщо відступили через зайнятий замок |
| `folio_mkclean` | знімає біт запису в усіх спільних відображеннях | `invalid_vma`, що пропускає все без `VM_SHARED` | скільки записів очищено |

Повернення `-1` з `folio_referenced` — єдине місце в цьому переліку, де зайнятість замка видно назовні як окреме значення. Витіснення тлумачить його не як «звернень не було», а як «спитати не вдалося», і відкладає сторінку замість того, щоб помилково визнати її холодною.

`enum ttu_flags` керує тим, що саме роблять `try_to_unmap` і `try_to_migrate`:

| Прапорець | Значення | Дія |
| --- | --- | --- |
| `TTU_SPLIT_HUGE_PMD` | `0x4` | розділити відображення рівня PMD на окремі записи ([великі сторінки](root:sys-unix/huge-pages-tlb-reach)) |
| `TTU_IGNORE_MLOCK` | `0x8` | знімати відображення й у замкненій у пам'яті ділянці |
| `TTU_SYNC` | `0x10` | не покладатися на швидкі перевірки: обхід має бути точним, бо за ним звіряють лічильники |
| `TTU_HWPOISON` | `0x20` | ставити на місце записів позначку зіпсованої пам'яті |
| `TTU_BATCH_FLUSH` | `0x40` | не скидати [буфер трансляції](root:sys-unix/tlb-shootdown) на кожному записі; викликач зробить один спільний скид наприкінці |
| `TTU_RMAP_LOCKED` | `0x80` | замок зворотного відображення вже взято — іти через `rmap_walk_locked` |

`try_to_migrate` приймає лише набір `TTU_RMAP_LOCKED | TTU_SPLIT_HUGE_PMD | TTU_SYNC | TTU_BATCH_FLUSH`; на будь-якому іншому прапорці він друкує попередження й повертається, нічого не зробивши. Спроба «заодно» передати туди `TTU_IGNORE_MLOCK` мовчки з'їдає весь виклик.

## Життєвий цикл anon_vma

```c
static inline int anon_vma_prepare(struct vm_area_struct *vma);   /* швидкий шлях */
int  __anon_vma_prepare(struct vm_area_struct *vma);              /* повільний */
int  anon_vma_clone(struct vm_area_struct *dst, struct vm_area_struct *src);
int  anon_vma_fork(struct vm_area_struct *vma, struct vm_area_struct *pvma);
void unlink_anon_vmas(struct vm_area_struct *vma);
static inline void anon_vma_merge(struct vm_area_struct *vma,
                                  struct vm_area_struct *next);
```

| Функція | Хто кличе | Що робить | Повернення |
| --- | --- | --- | --- |
| `anon_vma_prepare` | обробник [збою сторінки](root:sf-os/page-fault) перед першим записом в анонімну ділянку | якщо `vma->anon_vma` уже є — нічого; інакше йде в повільний шлях | `0` або `-ENOMEM` |
| `__anon_vma_prepare` | лише `anon_vma_prepare` | шукає придатний об'єкт у сусідньої ділянки (частий випадок після `mprotect`, що розрізав одну ділянку надвоє), інакше заводить новий | `0` або `-ENOMEM` |
| `anon_vma_clone` | розділення, злиття, розширення ділянки, копіювання при `mremap`, і `anon_vma_fork` | приписує `dst` до **всіх** об'єктів, до яких приписано `src` | `0` або `-ENOMEM` |
| `anon_vma_fork` | `fork` — по ділянці на кожну ділянку батька | спершу `anon_vma_clone`, потім (якщо не вдалося перевикористати) власний новий об'єкт для сторінок, доторканих після розгалуження | `0` або `-ENOMEM` |
| `unlink_anon_vmas` | знищення ділянки, відкат помилок | знімає всі ребра ділянки й прибирає осиротілі об'єкти | нічого |
| `anon_vma_merge` | злиття двох сусідніх ділянок | звичайний `unlink_anon_vmas(next)` з перевіркою, що об'єкт у них справді спільний | нічого |

Правило перевикористання, заради якого існують два лічильники, записане в `anon_vma_clone` буквально так: перевикористати чужий об'єкт, якщо `dst` ще не має свого, `src` має, і при цьому в кандидата `num_children < 2` та `num_active_vmas == 0`. Читається це як «об'єкт уже нічий і має щонайбільше одного нащадка» — тобто вироджений ланцюжок розгалужень згортається на місці, а справді розгалужене дерево лишається деревом.

`anon_vma_fork` тихо повертає `0`, якщо в батьківської ділянки `anon_vma` немає взагалі: ділянка, у яку жодного разу не писали, нічого не успадковує — і не платить.

## Замки: що беруть і в якому порядку

Помічники семафора всі до одного працюють із `anon_vma->root->rwsem`, а не зі своїм примірником:

```c
static inline void anon_vma_lock_write(struct anon_vma *anon_vma)
{
        down_write(&anon_vma->root->rwsem);
}
/* так само anon_vma_unlock_write, anon_vma_lock_read, anon_vma_unlock_read,
   anon_vma_trylock_write, anon_vma_trylock_read */
```

Для файлової гілки роль того самого замка грає `mapping->i_mmap_rwsem` із парою `i_mmap_lock_read` / `i_mmap_trylock_read` (`include/linux/fs.h`).

Дістати анонімний об'єкт зі сторінки, коли його будь-якої миті можуть звільнити, уміють дві функції:

```c
struct anon_vma *folio_get_anon_vma(struct folio *folio);
struct anon_vma *folio_lock_anon_vma_read(struct folio *folio,
                                          struct rmap_walk_control *rwc);
```

Обидві читають `folio->mapping` під RCU, перевіряють прапорці, підіймають `refcount` через `atomic_inc_not_zero` і **повторно** перевіряють, що folio досі відображене. Ця друга перевірка й тримає всю конструкцію: пам'ять під `anon_vma` береться з кеша з прапорцем `SLAB_TYPESAFE_BY_RCU`, тобто слот може бути перевикористаний одразу, але **тільки під структуру того самого типу** — читання з нього безпечне, просто відповідь може виявитися чужою. Без [RCU](root:sys-unix/rcu-read-copy-update) і цієї пари перевірок обхід читав би звільнену пам'ять.

`folio_lock_anon_vma_read` додатково намагається взяти замок одним `trylock` на швидкому шляху, а при невдачі — або блокується, або, коли стоїть `rwc->try_lock`, ставить `rwc->contended = true` і повертає `NULL`.

**Порядок замків — жорсткий і однаковий для всієї підсистеми пам'яті.** Ось той його шматок, що стосується зворотного відображення (повний перелік — у шапці `mm/rmap.c`):

```
inode->i_rwsem                       (при записі чи вкороченні файлу)
  mm->mmap_lock
    mapping->invalidate_lock
      folio_lock
        mapping->i_mmap_rwsem
          anon_vma->rwsem
            mm->page_table_lock  або  pte_lock
              swap_lock
                i_pages lock
```

Практичних наслідків із цієї драбини три, і кожен ловить свою помилку.

**Перший.** `i_mmap_rwsem` і `anon_vma->rwsem` стоять на сусідніх щаблях у такому порядку — тому код, що тримає замок анонімного об'єкта, не сміє брати замок дерева ділянок інода. Обхід цього й не робить: він або файловий, або анонімний, ніколи не обидва.

**Другий.** Замок folio стоїть **вище** за обидва, тож брати його всередині `rmap_one` не можна — а взяти його наперед у викликача обов'язково там, де це вимагають `try_to_unmap`, `folio_mkclean` і файлова гілка обходу.

**Третій.** Замок таблиці сторінок — найнижчий; його бере вже `page_vma_mapped_walk` усередині `rmap_one` і лишає у `pvmw->ptl`. Свій `spin_lock` на таблицю до входу в обхід — прямий шлях до заклинання.

Окремим рядком у тій самій шапці записано виняток: обробка апаратної помилки пам'яті (`collect_procs_anon`) бере `anon_vma->rwsem` або `i_mmap_rwsem` **перед** `tasklist_lock`, а вже за ним — замок таблиці. Це не суперечність, а окрема гілка ієрархії, яку не змішують із першою.

## Яка функція якого замка вимагає

Стовпці читаються так: **«так»** — викликач мусить тримати замок до виклику; **«бере сам»** — функція візьме й відпустить його всередині; **«—»** — не бере і не вимагає.

| Функція | замок folio | `mmap_lock` | `i_mmap_rwsem` / `anon_vma` rwsem | замок таблиці сторінок | може спати |
| --- | --- | --- | --- | --- | --- |
| `anon_vma_prepare` · `__anon_vma_prepare` | — | **так** (перевіряється `mmap_assert_locked`) | бере сам, на запис | — | **так** |
| `anon_vma_clone` · `anon_vma_fork` | — | **так**, обох просторів | бере сам, на запис | — | **так** |
| `unlink_anon_vmas` | — | **так** | бере сам, на запис | — | **так** |
| `folio_add_new_anon_rmap` | лише якщо folio не виключне | — | — | **так** | ні |
| `folio_add_anon_rmap_ptes` · `_pmd` | **так** | — | — | **так** | ні |
| `folio_add_file_rmap_ptes` · `_pmd` | — | — | — | **так** | ні |
| `folio_remove_rmap_ptes` · `_pmd` | — | — | — | **так** | ні |
| `folio_move_anon_rmap` | **так** | — | — | **так** | ні |
| `rmap_walk` (файлова гілка й KSM) | **так** | — | бере сам, на читання | — | **так** |
| `rmap_walk` (анонімна гілка) | наполегливо радять | — | бере сам, на читання | — | **так** |
| `rmap_walk_locked` | **так** | — | **так**, уже взято | — | **так** |
| `try_to_unmap` · `try_to_migrate` | **так** | — | бере сам (або `TTU_RMAP_LOCKED`) | бере `page_vma_mapped_walk` | **так** |
| `folio_referenced` | бере сам, якщо треба | — | бере сам, `trylock` | бере `page_vma_mapped_walk` | **так** |
| `folio_mkclean` | **так** (`BUG_ON` інакше) | — | бере сам | бере `page_vma_mapped_walk` | **так** |
| `folio_get_anon_vma` · `folio_lock_anon_vma_read` | радять тримати | — | друга бере на читання | — | **так** |

Рядок «наполегливо радять» для анонімної гілки не є формальністю: без замка folio поле `mapping` може змінитися просто під час обходу — саме тому `folio_lock_anon_vma_read` перевіряє `anon_vma->root` повторно вже після взяття замка й починає спочатку, якщо він змінився.

Останній стовпець важить не менше за решту: жодну з цих функцій не можна кликати з контексту, де спати не можна. Усе, що бере `rw_semaphore`, — а це весь обхід — розраховане на контекст процесу з дозволеним засинанням ([замки в ядрі](root:sys-unix/kernel-locking)).

## Що вже поїхало: зсуви між версіями

| Було | Стало | Коли |
| --- | --- | --- |
| `PAGE_MAPPING_ANON` · `PAGE_MAPPING_MOVABLE` · `PAGE_MAPPING_KSM` | `FOLIO_MAPPING_ANON` · `FOLIO_MAPPING_ANON_KSM` · `FOLIO_MAPPING_KSM` | 6.17 |
| `PAGE_MAPPING_MOVABLE` як окремий стан `mapping` | прапорець типу сторінки `PG_movable_ops` | 6.17 |
| `PAGE_MAPPING_DAX_SHARED` — окремий стан для fsdax | прибрано | 6.15 |
| `enum rmap_level` (`RMAP_LEVEL_PTE`/`PMD`) | `enum pgtable_level` (`PGTABLE_LEVEL_PTE`/`PMD`/`PUD`) | після 6.12 |
| немає `pud`-рівня | `folio_add_file_rmap_pud` · `folio_remove_rmap_pud` | після 6.12 |
| `folio_referenced(..., unsigned long *vm_flags)` | `folio_referenced(..., vm_flags_t *vm_flags)` | після 6.12 |
| `page_add_anon_rmap` · `page_remove_rmap` (посторінкові) | родина `folio_*_rmap_*` з `nr_pages` | 6.8 |
| `struct anon_vma.degree` — один лічильник на все | пара `num_children` + `num_active_vmas` | 6.0 |

Ця таблиця не повна й не може бути повною — вона тут заради темпу, який показує. Від 6.0 до 6.17 змінилося геть усе: імена констант, склад полів, підписи, розбиття на рівні таблиць сторінок. Тому єдина чесна порада замість переліку — три команди в дереві свого ядра:

```
git grep -n 'struct anon_vma {' include/linux/rmap.h
git grep -n 'FOLIO_MAPPING_\|PAGE_MAPPING_' include/linux/page-flags.h
sed -n '/Lock ordering in mm/,/^ \*\//p' mm/rmap.c
```

Третя з них друкує чинну для цього дерева ієрархію замків. Вона незмінно точніша за будь-який зовнішній переказ — включно з цим.
