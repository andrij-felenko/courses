# 📋 Інтерфейс сповіщувачів MMU: поля, сигнатури, контракти

Це довідка до наборів зворотних викликів, якими ядро попереджає власника другої таблиці перекладів: що саме кличуть, з-під яких замків, чи вільно там спати й що повертати. Звірено з `include/linux/mmu_notifier.h` та `mm/mmu_notifier.c` ядра 6.16; інтерфейс внутрішньоядерний і рухомий, тож номер версії тут не формальність — сповіщувачі діапазону з'явилися в 5.5, а `invalidate_range` став `arch_invalidate_secondary_tlbs` у 6.6.

## `struct mmu_notifier_ops` — підписка на весь адресний простір

```c
struct mmu_notifier_ops {
        void (*release)(struct mmu_notifier *subscription, struct mm_struct *mm);

        int  (*clear_flush_young)(struct mmu_notifier *subscription, struct mm_struct *mm,
                                  unsigned long start, unsigned long end);
        int  (*clear_young)(struct mmu_notifier *subscription, struct mm_struct *mm,
                            unsigned long start, unsigned long end);
        int  (*test_young)(struct mmu_notifier *subscription, struct mm_struct *mm,
                           unsigned long address);

        int  (*invalidate_range_start)(struct mmu_notifier *subscription,
                                       const struct mmu_notifier_range *range);
        void (*invalidate_range_end)(struct mmu_notifier *subscription,
                                     const struct mmu_notifier_range *range);

        void (*arch_invalidate_secondary_tlbs)(struct mmu_notifier *subscription,
                                               struct mm_struct *mm,
                                               unsigned long start, unsigned long end);

        struct mmu_notifier *(*alloc_notifier)(struct mm_struct *mm);
        void (*free_notifier)(struct mmu_notifier *subscription);
};
```

Жодне поле не обов'язкове: ядро перевіряє покажчик перед викликом, тож набір беруть за потребою.

| виклик | звідки приходить | що ядро вже тримає | сон | повернення |
|---|---|---|---|---|
| `release` | `exit_mmap` або `mmu_notifier_unregister`, завжди до звільнення сторінок | читацька секція SRCU | можна | — |
| `clear_flush_young` | обхід зворотного відображення, коли ядро знімає біт звертання в записі процесора | замок таблиці сторінок | **ні** | ≠ 0, якщо слід звертання був і у вторинних записах |
| `clear_young` | те саме, полегшене: зняти ознаку, але не скидати вторинний TLB | те саме | **ні** | те саме |
| `test_young` | коли треба лише спитати, нічого не міняючи й нічого не розбираючи | те саме | **ні** | ≠ 0, якщо сторінкою користуються |
| `invalidate_range_start` | перед зміною; сторінки ще відображені й мають щонайменше одне посилання | `mmap_lock` і/або замки зворотного відображення | лише коли дозволено прапорцем | `0`, або `-EAGAIN` — **тільки** в неблокуючому режимі |
| `invalidate_range_end` | після зняття записів, скидання TLB і звільнення сторінок | ті самі | так само | — |
| `arch_invalidate_secondary_tlbs` | з архітектурного коду, у точці скидання TLB процесора | спін-замок таблиці сторінок (`ptl`) | **ні** | — |
| `alloc_notifier` | з `mmu_notifier_get`, коли примірника для цього `mm` ще немає | `mmap_lock` на запис | можна | новий сповіщувач або `ERR_PTR` |
| `free_notifier` | з відкладеного SRCU-колбека після останнього `put` | — | **ні** | — |

Три виклики про вік сторінки та `arch_invalidate_secondary_tlbs` ядро робить із-під спін-замка — а це [атомарний контекст](root:sys-unix/kernel-locking), де заснути означає повісити систему: планувальник не має права перемкнути потік, що тримає спін-замок. Отже, ніяких сплячих замків, ніякого чекання на чергу пристрою; усе, що там дозволено, — коротка робота з власними структурами.

Пара `start`/`end` має три правила, які легко проґавити. Перше: між ними підписник не має права **встановлювати** нових відображень у цьому діапазоні — не досить лише зняти наявні. Друге: у неблокуючому режимі відмова `start` подається як `-EAGAIN`, і тоді ядро все одно покличе `end` у **всіх** підписників, які його мають, — бо повідомити конкретного невдаху про власний провал воно не вміє. Звідси третє: хто здатен провалити `start`, той не має права реалізовувати `end` взагалі. Заборона на сон стосується обох викликів пари, не лише першого.

`arch_invalidate_secondary_tlbs` — не доповнення до пари, а альтернатива їй: його реалізує той, чия апаратура ходить у ті самі таблиці, що й процесор, і кому треба скинути лише власний кеш перекладів. Реалізувати обидва механізми водночас — помилка.

Останнє про `release`: він може виконуватися **одночасно** з іншими викликами того самого набору, а в схемі `get`/`put` його взагалі можуть не покликати — лише коли адресний простір розбирають. Надійна точка прибирання там `free_notifier`, а всі вторинні записи мають зникнути ще до `mmu_notifier_put`.

## `struct mmu_notifier_range` — опис зміни

```c
struct mmu_notifier_range {
        struct mm_struct        *mm;
        unsigned long            start;
        unsigned long            end;
        unsigned                 flags;
        enum mmu_notifier_event  event;
        void                    *owner;
};

#define MMU_NOTIFIER_RANGE_BLOCKABLE (1 << 0)

static inline bool mmu_notifier_range_blockable(const struct mmu_notifier_range *range)
{
        return (range->flags & MMU_NOTIFIER_RANGE_BLOCKABLE);
}
```

| поле | вміст |
|---|---|
| `mm` | адресний простір, чиї відображення міняють |
| `start`, `end` | півінтервал віртуальних адрес `[start, end)` |
| `flags` | прапорці виклику; читати їх напряму не треба |
| `event` | причина зміни |
| `owner` | позначка того, хто затіяв зміну; `NULL`, якщо не вказано |

Заповнює структуру той, хто ініціює зміну, — макросом `mmu_notifier_range_init(range, event, flags, mm, start, end)` або `mmu_notifier_range_init_owner(...)`, що додає сьомим аргументом позначку власника. Підписникові з `flags` потрібне одне: `mmu_notifier_range_blockable(range)`. **Відсутність** прапорця означає, що ядро зайшло сюди з місця, де сон заборонений, — типово це прибирач пам'яті після вбивства процесу за браком пам'яті, який мусить рухатися вперед за будь-яку ціну.

## `enum mmu_notifier_event` — чому прийшло скасування

| подія | коли приходить | що з нею робити |
|---|---|---|
| `MMU_NOTIFY_UNMAP` | `munmap()` або переміщення діапазону через `mremap()` | зняти свої записи: відображення зникає |
| `MMU_NOTIFY_CLEAR` | просто очищення запису таблиці — `madvise()`, підміна сторінки іншою тощо | те саме |
| `MMU_NOTIFY_PROTECTION_VMA` | зміна прав на цілу ділянку (`mprotect()`) | нові права видно з прав самої ділянки; перечитувати таблиці процесора не треба |
| `MMU_NOTIFY_PROTECTION_PAGE` | змінився дозвіл на запис для окремих сторінок діапазону | щоб віддзеркалити, доведеться переглянути таблиці процесора — з виклику `end` |
| `MMU_NOTIFY_SOFT_DIRTY` | облік «брудних» сторінок; сторінка й права ті самі | позначити сторінки брудними у себе, щоб записи повз процесор не загубилися |
| `MMU_NOTIFY_RELEASE` | лічильник користувачів `mm` упав до нуля, діапазон більше недоступний (приходить у `invalidate` сповіщувача діапазону) | зняти все негайно |
| `MMU_NOTIFY_MIGRATE` | збирання сторінок для перенесення в пам'ять пристрою | якщо `owner` збігається з власником свого device-private відображення — пропустити |
| `MMU_NOTIFY_EXCLUSIVE` | пристрій більше не матиме ексклюзивного доступу до сторінки | при створенні ексклюзивного діапазону `owner` дорівнює переданому ініціатором, інакше `NULL` |

Обидві останні події існують заради `owner`: драйвер, який сам переносить сторінки, впізнає в скасуванні власну позначку й не розбирає відображення, що він же щойно й будує.

## Реєстрація й час життя

```c
int  mmu_notifier_register(struct mmu_notifier *subscription, struct mm_struct *mm);
int  __mmu_notifier_register(struct mmu_notifier *subscription, struct mm_struct *mm);
void mmu_notifier_unregister(struct mmu_notifier *subscription, struct mm_struct *mm);

struct mmu_notifier *mmu_notifier_get(const struct mmu_notifier_ops *ops, struct mm_struct *mm);
struct mmu_notifier *mmu_notifier_get_locked(const struct mmu_notifier_ops *ops, struct mm_struct *mm);
void mmu_notifier_put(struct mmu_notifier *subscription);
void mmu_notifier_synchronize(void);
```

| виклик | умови |
|---|---|
| `mmu_notifier_register` | бере `mmap_lock` на запис сам, тож той, хто кличе, не сміє тримати жодного VM-замка; `mm` має бути живим (`current->mm` або взятий через `get_task_mm()`); усередині бере «легке» посилання на структуру, а не на адресний простір |
| `__mmu_notifier_register` | те саме, але `mmap_lock` на запис уже тримає той, хто кличе |
| `mmu_notifier_unregister` | якщо `release` ще не був — покличе його; після повернення жоден зворотний виклик уже не виконується й не виконуватиметься; може спати |
| `mmu_notifier_get` | знаходить наявний сповіщувач із цим самим `ops` для цього `mm` або створює через `alloc_notifier`; лічильник користувачів усередині; `_locked`-форма вимагає вже взятого `mmap_lock` на запис |
| `mmu_notifier_put` | парний до `get`; на останньому посиланні звільнення йде **асинхронно**, через відкладений колбек, який покличе `free_notifier` |
| `mmu_notifier_synchronize` | чекає, поки ті відкладені звільнення добіжать; модуль **зобов'язаний** покликати це у своєму `__exit`, інакше колбек виконається в уже вивантаженому коді |

Список підписників ядро обходить під [сплячим різновидом RCU](root:sys-unix/rcu-read-copy-update) — читачі не беруть спільного замка й не заважають одне одному, а звільнення відкладається доти, доки всі поточні обходи не завершаться. Звідси й асинхронність `put`, і потреба в `mmu_notifier_synchronize`.

## Інтервальний інтерфейс

```c
struct mmu_interval_notifier_ops {
        bool (*invalidate)(struct mmu_interval_notifier *interval_sub,
                           const struct mmu_notifier_range *range,
                           unsigned long cur_seq);
};

int  mmu_interval_notifier_insert(struct mmu_interval_notifier *interval_sub,
                                  struct mm_struct *mm, unsigned long start,
                                  unsigned long length,
                                  const struct mmu_interval_notifier_ops *ops);
int  mmu_interval_notifier_insert_locked(/* те саме */);
void mmu_interval_notifier_remove(struct mmu_interval_notifier *interval_sub);

unsigned long mmu_interval_read_begin(struct mmu_interval_notifier *interval_sub);
bool mmu_interval_read_retry(struct mmu_interval_notifier *interval_sub, unsigned long seq);
bool mmu_interval_check_retry(struct mmu_interval_notifier *interval_sub, unsigned long seq);
void mmu_interval_set_seq(struct mmu_interval_notifier *interval_sub, unsigned long cur_seq);
```

| виклик | умови |
|---|---|
| `invalidate` (зворотний) | `true` — упорався; `false` — не зміг, дозволено лише в неблокуючому режимі, нагору піде `-EAGAIN`; безумовно кличе `mmu_interval_set_seq` |
| `mmu_interval_notifier_insert` | бере `mmap_lock` на запис сам; після повернення вузол може бути ще не в дереві, тож перше відображення будують лише через `read_begin` |
| `..._insert_locked` | те саме за вже взятого `mmap_lock` на запис |
| `mmu_interval_notifier_remove` | не можна кликати з жодного зворотного виклику; може спати; після повернення викликів більше не буде |
| `mmu_interval_read_begin` | **може заснути**: якщо знецінення саме триває, чекає, поки воно добіжить до кінця; брати **до** читання таблиць процесу |
| `mmu_interval_read_retry` | лише під тим замком драйвера, під яким `invalidate` кличе `set_seq` |
| `mmu_interval_check_retry` | замка не потребує; `true` — надійне свідчення сутички (для раннього виходу з довгої роботи), `false` — ні |
| `mmu_interval_set_seq` | безумовно з `invalidate`, під тим самим замком драйвера |

Вузли складено в [дерево інтервалів](root:sf-algorithms/interval-tree) — структуру, що за діапазоном швидко видає всі відрізки, які з ним перетинаються; тому `invalidate` дістають лише ті підписки, чий проміжок справді зачепило.

Узгодження ж — це [схема з послідовним числом](root:sf-tasks/seqlock): читач бере лічильник до роботи, звіряє після й перечитує все спочатку, якщо число змінилося. Контракт має рівно три умови. `cur_seq`, переданий у `invalidate`, **завжди непарний** — саме непарність позначає «зміна триває», і `read_begin` ніколи не поверне такого числа, бо перечекає. `mmu_interval_set_seq` мусить стояти під тим самим замком, під яким потім кличуть `read_retry`, — інакше перевірка нічого не значить. І звірка, і встановлення відображень мусять бути всередині **одного** взяття цього замка.

## `CONFIG_MMU_NOTIFIER`

Власного питання в `menuconfig` цей параметр не має — його вмикають через `select` ті підсистеми, яким він потрібен: KVM, дзеркалення пам'яті для прискорювачів, IOMMU зі спільною адресацією. Разом із ним автоматично вмикається `INTERVAL_TREE`. Коли параметра немає, зі `struct mm_struct` зникає поле з підписками, а всі виклики `mmu_notifier_*()` стають порожніми inline-заглушками — код, що їх розсипає таблицями сторінок, компілюється без жодної зміни й не коштує нічого. На гарячих шляхах перед розсиланням ядро ще й питає `mm_has_notifiers(mm)`, тож адресний простір без підписників не платить за механізм навіть у ввімкненому ядрі.
