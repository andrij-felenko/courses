# ⚙️ Пара колбеків cpuhp: перевірити відкат, не вимкнувши жодного ядра процесора

Найчастіша причина, чому код із per-CPU запасом ламається на гарячому підключенні, — його ніхто ніколи не перевіряв: справжнє вимикання ядра процесора зупиняє всю машину, тож на живому сервері його не роблять, а на робочій станції страшно. Але перевіряти й не треба: у sysfs є дві ручки, які проводять ядро процесора крізь ваш стан і навмисне ламають перехід у заданій точці, лишаючи ядро процесора цілком живим. Нижче — робочий [модуль ядра](book:unix-linux/kernel-modules) із per-CPU кешем вільних об'єктів і парою колбеків, а далі — послідовність команд, після якої ви бачите свій `startup`, свій `teardown` і свій відкат у `dmesg`, не втративши жодного такту.

## Задача

Модуль тримає **запас вільних об'єктів на кожному ядрі процесора** — класичну конструкцію, задля якої й існують [змінні per-CPU](book:unix-linux/per-cpu-data): узяти об'єкт зі свого запасу можна без жодного атомарного звертання й без змагання з іншими ядрами. Позаду стоїть спільний пул під звичайним спінлоком — туди йдуть тільки за промахом.

Такий запас зобов'язаний брати участь у протоколі гарячого підключення, і саме тут виникають дві функції:

- **`startup`** — ядро процесора з'явилося, треба наповнити його копію, щоб перше ж звертання не пішло в спільний пул;
- **`teardown`** — ядро процесора гасне, треба злити запас у спільний пул, інакше кілька десятків об'єктів залишаться замкненими в копії, до якої більше ніхто ніколи не зайде.

Довести належить три речі, і жодна не потребує справжнього `offline`:

1. обидва колбеки справді викликаються, причому **на тому самому ядрі процесора**, номер якого їм передали;
2. `teardown` спорожнює запас, і об'єкти опиняються в спільному пулі, а не зникають;
3. коли перехід ламається **вище** за наш стан, машина станів відкочує зроблене й кличе наш `teardown` — тобто гілка відкоту теж робоча.

Мову тут диктує домен: код виконується в ядрі, торкається його структур і збирається тими самими заголовками. Це C.

## Ідея: стан — це пара, а не подія

Механізм не розсилає повідомлень «ядро процесора вмикається» й «ядро процесора вимикається». Він проводить ядро процесора **відрізком пронумерованих станів**, і ви ставите на цьому відрізку свою точку — одразу з двома функціями:

```c
int cpuhp_setup_state(enum cpuhp_state state, const char *name,
                      int (*startup)(unsigned int cpu),
                      int (*teardown)(unsigned int cpu));
```

Перший аргумент — номер. Іменований сталий номер беруть тільки тоді, коли порядок справді важить (кеш розподілювача мусить прокинутися раніше за того, хто з нього виділятиме). Коли не важить — беруть `CPUHP_AP_ONLINE_DYN`, і ядро видає вільний номер із діапазону динамічних станів, повертаючи його **як додатне значення функції**. Звідси перша дрібниця, на якій спотикаються: `cpuhp_setup_state()` повертає `0` для сталого номера й **додатне число** для динамічного, тому перевіряти треба `ret < 0`, а не `ret != 0`.

Друга дрібниця важливіша й одразу пояснює половину подальшого. Реєстрація — це не тільки запис двох вказівників у таблицю: `cpuhp_setup_state()` **тут-таки викликає `startup` для всіх ядер процесора, що вже онлайн**. Тобто ваша структура має бути готова до роботи ще до виклику реєстрації, а сам виклик стоїть останнім рядком ініціалізації. Дзеркально `cpuhp_remove_state()` викликає `teardown` для всіх онлайн-ядер — і тому стоїть **першим** рядком вивантаження.

І третя річ, від якої залежить увесь код нижче. Для стану із секції ONLINE колбек виконує **потік `cpuhp/N`, прибитий до того самого ядра процесора**, номер якого прийшов аргументом. Це видно з коду ядра: `cpuhp_is_ap_state()` вважає «своїми» всі стани, більші за `CPUHP_BRINGUP_CPU`, і для них виклик передають на цільове ядро процесора через його потік. Отже, у нашому `startup` і `teardown` `smp_processor_id()` дорівнює `cpu`, і працювати з `this_cpu_ptr()` законно. Для стану із секції PREPARE це було б неправдою — там колбек біжить на чужому, керівному ядрі процесора, і єдиний правильний доступ — `per_cpu_ptr(&var, cpu)`. Аргумент `cpu` існує саме тому, що припускати «я на ньому» можна не завжди.

## Модуль

```c
// SPDX-License-Identifier: GPL-2.0
/* cpucache.c — per-CPU запас об'єктів і пара колбеків гарячого підключення */
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/cpu.h>
#include <linux/cpuhotplug.h>
#include <linux/debugfs.h>
#include <linux/init.h>
#include <linux/kstrtox.h>
#include <linux/local_lock.h>
#include <linux/module.h>
#include <linux/percpu.h>
#include <linux/seq_file.h>
#include <linux/slab.h>
#include <linux/spinlock.h>

#define WANT 8            /* скільки об'єктів тримає запас одного ядра процесора */

struct obj {
        struct obj *next;
};

/* ── спільний пул: один на систему, під звичайним спінлоком ─────────── */
static DEFINE_SPINLOCK(pool_lock);
static struct obj *pool_head;
static unsigned long pool_size;

static void obj_list_free(struct obj *list)
{
        while (list) {
                struct obj *o = list;

                list = o->next;
                kfree(o);
        }
}

static void pool_push(struct obj *o)
{
        spin_lock(&pool_lock);
        o->next = pool_head;
        pool_head = o;
        pool_size++;
        spin_unlock(&pool_lock);
}

static struct obj *pool_pop(void)
{
        struct obj *o;

        spin_lock(&pool_lock);
        o = pool_head;
        if (o) {
                pool_head = o->next;
                pool_size--;
        }
        spin_unlock(&pool_lock);

        return o ? o : kmalloc(sizeof(*o), GFP_KERNEL);
}

/* ── запас на кожному ядрі процесора ────────────────────────────────── */
struct cache {
        local_lock_t  lock;
        struct obj   *head;
        unsigned int  count;
        unsigned long hits, misses, filled, drained;
};

static DEFINE_PER_CPU(struct cache, cache) = {
        .lock = INIT_LOCAL_LOCK(lock),
};

static struct obj *obj_get(void)
{
        struct cache *c;
        struct obj *o;

        local_lock(&cache.lock);
        c = this_cpu_ptr(&cache);
        o = c->head;
        if (o) {
                c->head = o->next;
                c->count--;
                c->hits++;
        } else {
                c->misses++;
        }
        local_unlock(&cache.lock);

        return o ? o : pool_pop();   /* у пул ідемо вже без замка: там можна заснути */
}

static void obj_put(struct obj *o)
{
        struct cache *c;
        bool kept;

        local_lock(&cache.lock);
        c = this_cpu_ptr(&cache);
        kept = c->count < WANT;
        if (kept) {
                o->next = c->head;
                c->head = o;
                c->count++;
        }
        local_unlock(&cache.lock);

        if (!kept)
                pool_push(o);        /* запас повний — назад у спільний пул */
}

/* ── пара колбеків ──────────────────────────────────────────────────── */
static enum cpuhp_state hp_state;
static bool fail_startup;            /* debugfs: наступний startup упаде один раз */

static int cache_cpu_online(unsigned int cpu)
{
        struct obj *batch = NULL, *o;
        struct cache *c;
        unsigned int have, need, i, n;

        /* потік cpuhp/N прибитий до свого ядра процесора, тож це законно */
        WARN_ON_ONCE(cpu != smp_processor_id());

        if (READ_ONCE(fail_startup)) {
                WRITE_ONCE(fail_startup, false);
                pr_info("startup  cpu=%u навмисно повертає -ENOMEM\n", cpu);
                return -ENOMEM;
        }

        local_lock(&cache.lock);
        have = this_cpu_ptr(&cache)->count;
        local_unlock(&cache.lock);

        /* НЕ «додати WANT», а «доповнити ДО WANT»: після відкоту цей колбек
         * приходить на копію, яку ніхто не спорожнив */
        need = (have < WANT) ? WANT - have : 0;

        for (i = 0; i < need; i++) {          /* виділяємо ДО замка: тут можна спати */
                o = kmalloc(sizeof(*o), GFP_KERNEL);
                if (!o) {
                        obj_list_free(batch); /* прибрати за собою й чесно впасти */
                        return -ENOMEM;
                }
                o->next = batch;
                batch = o;
        }

        local_lock(&cache.lock);
        c = this_cpu_ptr(&cache);
        while (batch && c->count < WANT) {
                o = batch;
                batch = o->next;
                o->next = c->head;
                c->head = o;
                c->count++;
        }
        n = c->count;
        c->filled++;
        local_unlock(&cache.lock);

        obj_list_free(batch);                 /* зайве, якщо лишилося */
        pr_info("startup  cpu=%u count=%u (біжу на cpu%d)\n",
                cpu, n, smp_processor_id());
        return 0;
}

static int cache_cpu_offline(unsigned int cpu)
{
        struct obj *list, *o;
        struct cache *c;
        unsigned long n = 0;

        WARN_ON_ONCE(cpu != smp_processor_id());

        local_lock(&cache.lock);
        c = this_cpu_ptr(&cache);
        list = c->head;              /* забираємо весь список одним рухом */
        c->head = NULL;
        c->count = 0;
        local_unlock(&cache.lock);

        while (list) {               /* і аж потім, без замка, роздаємо в пул */
                o = list;
                list = o->next;
                pool_push(o);
                n++;
        }

        this_cpu_add(cache.drained, n);
        pr_info("teardown cpu=%u злито %lu, у пулі %lu\n",
                cpu, n, READ_ONCE(pool_size));
        return 0;                    /* teardown не має права не вдатися */
}

/* ── вітрина: підсумок за possible, а не за online ──────────────────── */
static int stats_show(struct seq_file *m, void *v)
{
        unsigned long hits = 0, misses = 0, drained = 0;
        unsigned int cpu;

        seq_puts(m, "cpu  online  count  hits  misses  filled  drained\n");
        for_each_possible_cpu(cpu) {
                struct cache *c = per_cpu_ptr(&cache, cpu);

                seq_printf(m, "%3u  %6d  %5u  %4lu  %6lu  %6lu  %7lu\n",
                           cpu, cpu_online(cpu), c->count,
                           c->hits, c->misses, c->filled, c->drained);
                hits += c->hits;
                misses += c->misses;
                drained += c->drained;
        }
        seq_printf(m, "разом: hits %lu, misses %lu, drained %lu, у пулі %lu\n",
                   hits, misses, drained, READ_ONCE(pool_size));
        return 0;
}
DEFINE_SHOW_ATTRIBUTE(stats);

static ssize_t churn_write(struct file *f, const char __user *ubuf,
                           size_t count, loff_t *ppos)
{
        unsigned int n, i;
        int ret = kstrtouint_from_user(ubuf, count, 10, &n);

        if (ret)
                return ret;

        for (i = 0; i < n; i++) {
                struct obj *o = obj_get();

                if (!o)
                        return -ENOMEM;
                obj_put(o);
        }
        return count;
}

static const struct file_operations churn_fops = {
        .owner  = THIS_MODULE,
        .write  = churn_write,
        .llseek = noop_llseek,
};

static struct dentry *dir;

static int __init cpucache_init(void)
{
        int ret;

        dir = debugfs_create_dir("cpucache", NULL);
        debugfs_create_file("stats", 0444, dir, NULL, &stats_fops);
        debugfs_create_file("churn", 0200, dir, NULL, &churn_fops);
        debugfs_create_bool("fail_startup", 0644, dir, &fail_startup);

        /* реєстрація — ОСТАННІМ рядком: вона одразу кличе startup
         * на всіх ядрах процесора, що вже онлайн */
        ret = cpuhp_setup_state(CPUHP_AP_ONLINE_DYN, "cpucache:online",
                                cache_cpu_online, cache_cpu_offline);
        if (ret < 0) {               /* саме < 0: динамічний номер додатний */
                debugfs_remove_recursive(dir);
                return ret;
        }
        hp_state = ret;
        pr_info("узято динамічний стан %d\n", hp_state);
        return 0;
}

static void __exit cpucache_exit(void)
{
        cpuhp_remove_state(hp_state);   /* ПЕРШИМ: зливає всі запаси в пул */
        debugfs_remove_recursive(dir);
        obj_list_free(pool_head);       /* і аж тепер звільняти пам'ять */
        pool_head = NULL;
        pool_size = 0;
        pr_info("вивантажено\n");
}

module_init(cpucache_init);
module_exit(cpucache_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Per-CPU запас об'єктів із парою колбеків cpuhp");
```

Два місця тут варті окремої уваги, бо саме вони відрізняють робочий колбек від такого, що падає раз на місяць.

**Виділення стоїть поза замком.** `local_lock` на звичайному ядрі вимикає витіснення, а `kmalloc(GFP_KERNEL)` має право заснути — заснути з вимкненим витісненням означає повісити ядро процесора. Тому `startup` спершу набирає партію об'єктів у власний список, а тоді одним коротким проходом під замком вставляє їх у запас. Дзеркально `teardown` спершу забирає ввесь список під замком, а роздає його в спільний пул уже без замка. Правило загальне: **під замком роблять тільки перечеплення вказівників**, усе, що може заснути чи довго тривати, — назовні. Детальніше про те, які саме контексти дозволяють сон, — [замки в ядрі й атомарний контекст](book:unix-linux/kernel-locking). Одне припущення тут варто назвати вголос: у цей запас ходять лише з контексту процесу, тому спільний пул захищено звичайним `spin_lock()`, а по пам'ять ходять із `GFP_KERNEL`. Хто чіпатиме запас із softirq чи обробника переривання, мусить перейти на `spin_lock_irqsave()` і `GFP_ATOMIC` — але сам протокол гарячого підключення від цього не міняється ані на рядок.

**`startup` доповнює до `WANT`, а не додає `WANT`.** Спокуса написати «виділити вісім і причепити» велика, і на дорозі вгору вона працює бездоганно. Ламається вона на зірваному переході: машина станів кличе колбеки там, де прохід обірвався, і копія, яку ваш `teardown` не встиг (або не мав нагоди) спорожнити, лишається наповненою — а `startup` до неї ще може прийти. При «додати вісім» запас у такому разі росте щоразу, а `WANT` перестає бути межею. Нижче ми подивимося на обидва випадки з оболонки: і коли копію спорожнили, і коли ні.

## Збірка

Модуль збирає система збирання ядра — вона знає прапорці, заголовки й ABI саме тієї версії, у яку модуль потім вантажать. `Makefile` поруч із `cpucache.c`:

```makefile
obj-m := cpucache.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	$(MAKE) -C $(KDIR) M=$(CURDIR) modules

clean:
	$(MAKE) -C $(KDIR) M=$(CURDIR) clean
```

`KDIR` вказує на заголовки поточного ядра (пакет `linux-headers-$(uname -r)` або `kernel-devel`); звідки береться це дерево — [збирання й конфігурація ядра](book:unix-linux/kernel-config-and-build).

```sh
$ make
$ sudo insmod cpucache.ko
$ sudo dmesg | tail -5
cpucache: startup  cpu=0 count=8 (біжу на cpu0)
cpucache: startup  cpu=1 count=8 (біжу на cpu1)
cpucache: startup  cpu=2 count=8 (біжу на cpu2)
cpucache: startup  cpu=3 count=8 (біжу на cpu3)
cpucache: узято динамічний стан 220
```

Перше спостереження безкоштовне: рядки з'явилися ще до того, як ми чогось торкнулися. `cpuhp_setup_state()` пройшла всіма онлайн-ядрами процесора й покликала `startup` на кожному — і в дужках видно, що номер, який прийшов аргументом, збігається з номером ядра процесора, що виконує код.

Погоняймо кеш, щоб числа перестали бути нулями:

```sh
$ for i in 0 1 2 3; do taskset -c $i sh -c 'echo 1000 > /sys/kernel/debug/cpucache/churn'; done
$ cat /sys/kernel/debug/cpucache/stats
cpu  online  count  hits  misses  filled  drained
  0       1      8  1000       0       1        0
  1       1      8  1000       0       1        0
  2       1      8  1000       0       1        0
  3       1      8  1000       0       1        0
разом: hits 4000, misses 0, drained 0, у пулі 0
```

Жодного промаху: запас наповнили в `startup`, і по спільний пул ніхто не пішов — власне, заради цього per-CPU кеші й існують. Про `taskset` і про те, чому [прив'язка](book:unix-linux/cpu-affinity) тут обов'язкова, довго говорити не варто: без неї планувальник рознесе цикл по ядрах як йому зручно, і числа в стовпчиках будуть випадкові.

## Перевірка без жодного offline

Тепер найцікавіше. Усе, що діялося досі, — це дорога вгору. Дорога вниз і відкат перевіряються тими самими файлами, якими ядро перевіряє саме себе.

### Знайти свій номер

```sh
$ grep cpucache /sys/devices/system/cpu/hotplug/states
220: cpucache:online
$ tail -2 /sys/devices/system/cpu/hotplug/states
232: sched:active
233: online
$ cat /sys/devices/system/cpu/cpu3/hotplug/state
233
```

`states` перелічує ввесь відрізок — усі стани, у яких хоч хтось зареєстрував колбек, разом із номерами й іменами. Файл `cpuN/hotplug/state` каже, де саме зараз стоїть це ядро процесора: `233` — найправіша точка, `CPUHP_ONLINE`.

Числа тут — не сталий інтерфейс. Стани нумерує перелічуваний тип у заголовку ядра, тож номер міняється від версії до версії й від конфігурації до конфігурації, а динамічний номер залежить ще й від того, скільки модулів попросили його раніше. У скрипт зашивають не число, а пошук за іменем.

### Провести ядро процесора крізь свій стан

Файл `target` приймає номер і **веде ядро процесора туди**:

```sh
$ echo 219 | sudo tee /sys/devices/system/cpu/cpu3/hotplug/target
$ cat /sys/devices/system/cpu/cpu3/hotplug/state
219
$ sudo dmesg | tail -1
cpucache: teardown cpu=3 злито 8, у пулі 8
```

Ядро процесора при цьому нікуди не поділося: воно й далі виконує код, приймає переривання й тримає задачі — усе, що з ним сталося, це скасування колбеків із номерами вище за 219. Наш `teardown` серед них.

Тут ховається межа, на якій легко проколотися. Ціль `219`, а не `220` — і не тому, що так зручніше. Машина станів іде вниз, доки поточний стан **більший** за ціль, тож дійшовши до цілі, вона зупиняється **на ній**, і колбек самої цілі не скасовують. Написали б `220` — і `teardown` нашого стану не викликався б узагалі. Це прямо видно у власному трасувальному виводі з документації ядра: після спуску до цілі `140` дорога назад починається з кроку `141`, тобто стан `140` вниз не проходили. Саму фразу в документації сформульовано так, що вона наводить на протилежний висновок; вивід трасування в тому ж абзаці розсуджує це однозначно.

Стан підтверджує вітрина: запас третього ядра процесора порожній, об'єкти в пулі, лічильник злитого виріс.

```sh
$ cat /sys/kernel/debug/cpucache/stats
cpu  online  count  hits  misses  filled  drained
  0       1      8  1000       0       1        0
  1       1      8  1000       0       1        0
  2       1      8  1000       0       1        0
  3       1      0  1000       0       1        8
разом: hits 4000, misses 0, drained 8, у пулі 8
```

Зверніть увагу на стовпчик `online`: третє ядро процесора там і далі одиниця. Ми пройшли крізь свій стан, не вимкнувши ядра процесора — рівно те, чого хотіли. Назад:

```sh
$ echo 233 | sudo tee /sys/devices/system/cpu/cpu3/hotplug/target
$ sudo dmesg | tail -1
cpucache: startup  cpu=3 count=8 (біжу на cpu3)
```

### Зламати перехід навмисне

Другий файл, `fail`, озброює **одноразову підставну помилку** в заданому стані. Механіка проста й варта того, щоб її знати точно: перед тим як покликати колбек стану, ядро дивиться, чи не озброєно цей номер, і якщо озброєно — скидає озброєння й повертає `-EAGAIN` **замість виклику**. Далі спрацьовує звичайний відкат.

Озброїмо стан **вище** за наш і пройдімо знизу вгору:

```sh
$ echo 219 | sudo tee /sys/devices/system/cpu/cpu3/hotplug/target   # спускаємось
$ echo 232 | sudo tee /sys/devices/system/cpu/cpu3/hotplug/fail     # ламаємо sched:active
$ echo 233 | sudo tee /sys/devices/system/cpu/cpu3/hotplug/target
tee: /sys/devices/system/cpu/cpu3/hotplug/target: Resource temporarily unavailable
$ cat /sys/devices/system/cpu/cpu3/hotplug/state
219
$ sudo dmesg | tail -3
cpucache: teardown cpu=3 злито 8, у пулі 16
cpucache: startup  cpu=3 count=8 (біжу на cpu3)
cpucache: teardown cpu=3 злито 8, у пулі 24
```

Ось воно все, у трьох рядках. Спуск покликав наш `teardown`. Підйом дійшов до `220`, покликав наш `startup` — запас наповнився. На `232` підставилася помилка, і машина станів пішла назад, скасовуючи все, що встигла зробити, — зокрема й наш стан, звідки третій рядок. Ядро процесора лишилося там, звідки вирушало, а `tee` чесно повідомив `EAGAIN`.

![Дві панелі. Ліворуч драбина станів і стрілка teardown униз від 233 до 220 із поясненням, що на цілі 219 машина зупиняється й колбек самої цілі не скасовують. Праворуч та сама драбина, стан 232 позначено як озброєний fail, стрілка startup угору від 219 до 232 і стрілка відкоту вниз, із поясненням, що наш teardown кличуть під час відкоту, а запис у target повертає EAGAIN](/reference/unix-linux/processes/cpu-hotplug/img/target-and-fail.svg)

*Ліва панель — звичайний прохід крізь свій стан; права — навмисна поломка вище за свій стан, після якої відкат проходить крізь нього ще раз.*

Тепер згадаймо, чому `startup` доповнює запас до `WANT`, а не додає `WANT`. У цій послідовності його викликали на копію, яку щойно спорожнили, — усе гладко. А тепер озброїмо `fail` на **своєму** стані й спустімося:

```sh
$ echo 233 | sudo tee /sys/devices/system/cpu/cpu3/hotplug/target    # вертаємось нагору
$ echo 220 | sudo tee /sys/devices/system/cpu/cpu3/hotplug/fail
$ echo 219 | sudo tee /sys/devices/system/cpu/cpu3/hotplug/target
tee: /sys/devices/system/cpu/cpu3/hotplug/target: Resource temporarily unavailable
$ cat /sys/devices/system/cpu/cpu3/hotplug/state
233
$ sudo dmesg | tail -1
cpucache: startup  cpu=3 count=8 (біжу на cpu3)    # рядок від підйому вище, нового немає
```

Спуск дійшов до `220`, і замість нашого `teardown` підставилася помилка — тобто запас **лишився повним**. Далі найцікавіше: машина станів не вважає наш стан пройденим униз і веде ядро процесора назад угору **з наступного стану**, не кличучи нашого `startup`, — нового рядка в `dmesg` не з'явилося, а ядро процесора знову стоїть на `233`. У `stats` `count` і далі `8`, `drained` не змінився. Копія лишилася наповненою, хоч крізь неї щойно намагалися пройти вниз, — і саме тому колбек мусить бути ідемпотентним: він може прийти і на спорожнену копію, і на таку, а «додати вісім» дало б у другому випадку шістнадцять, потім двадцять чотири.

### Своя гілка помилки — окремий важіль

І одразу застереження, без якого ця перевірка створює хибне відчуття покриття. Файл `fail` **не викликає ваш колбек**: він підставляє помилку замість виклику. Тобто він перевіряє, як на вашу відмову реагують сусіди й машина станів, — але ваш власний `return -ENOMEM` разом із прибиранням за собою (`obj_list_free(batch)`) не виконується жодного разу. Щоб пройти саме цю гілку, потрібен власний важіль; у модулі це `fail_startup` у debugfs:

```sh
$ echo 219 | sudo tee /sys/devices/system/cpu/cpu3/hotplug/target
$ echo 1   | sudo tee /sys/kernel/debug/cpucache/fail_startup
$ echo 233 | sudo tee /sys/devices/system/cpu/cpu3/hotplug/target
tee: /sys/devices/system/cpu/cpu3/hotplug/target: Cannot allocate memory
$ sudo dmesg | tail -1
cpucache: startup  cpu=3 навмисно повертає -ENOMEM
```

Помилка інша — `ENOMEM` замість `EAGAIN`, — і це не косметика: значення, яке повернув **ваш** код, доїжджає до простору користувача цілим. Саме такий вигляд має чесна відмова, і саме її має побачити той, хто пише `echo 1 > online` на машині без пам'яті.

## Пастки

**`cpuhp_setup_state()` з колбека — миттєве заклинення.** Реєстрація бере `cpus_read_lock()`, а ваш колбек виконується тоді, коли операція гарячої зміни вже тримає `cpus_write_lock()`. Читач під власним письменником не пройде ніколи, і машина стане намертво — без oops, без повідомлення, просто мовчазне зависання. Для такого випадку є `cpuhp_setup_state_cpuslocked()` та `cpuhp_remove_state_nocalls_cpuslocked()`: суфікс каже «замок уже мій, удруге не бери». Те саме стосується будь-чого, що всередині чіпає цей замок, — `cpu_up()`, `cpu_down()`, обходів під `cpus_read_lock()`.

**Сон у секції STARTING.** Стани між `CPUHP_AP_IDLE_DEAD` і `CPUHP_AP_ONLINE` виконуються на самому ядрі процесора з вимкненими перериваннями. Жодного `kmalloc(GFP_KERNEL)`, `mutex_lock()`, `wait_event()`. Приємно, що sysfs тут прикриває від половини помилок сам: спроба озброїти `fail` на атомарному стані повертає `EINVAL`, бо відкочувати там нікуди. Але вибір стану лишається на вас — і 99 % кодів, що тримають запас, мають брати `CPUHP_AP_ONLINE_DYN`, а не лізти нижче.

**`for_each_possible_cpu` проти `for_each_online_cpu`.** У `stats_show()` обхід за `possible` — і це не перестрахування. Пам'ять під `DEFINE_PER_CPU` виділено за `possible` на все життя системи, тож у копії вимкненого ядра процесора лежать його останні числа: `hits`, `misses`, `drained`. Обхід за `online` мовчки викинув би їх із суми, і після кількох гарячих змін підсумок почав би зменшуватися. Правило симетричне й тримається одним рядком: **лічильники збирають за possible, роботу роздають за online** — а роздають ще й під `cpus_read_lock()`, щоб маска не змінилася між перевіркою й дією.

**Вивантаження без зняття стану.** Приберіть `cpuhp_remove_state()` з `cpucache_exit()` — і `rmmod` пройде без жодного слова. Таблиця станів у ядрі й далі триматиме вказівники на `cache_cpu_online` та `cache_cpu_offline`, а пам'яті під цим кодом уже не буде. Найближче засинання ноутбука (а воно вимикає всі ядра процесора, крім завантажувального) стрибне за цими вказівниками — і машина впаде так, що в звіті не буде жодної згадки про ваш модуль, бо його вже немає. Із цього ж випливає й порядок усередині `exit`: `cpuhp_remove_state()` **першим**, звільнення пам'яті **після** нього, бо він зобов'язаний спершу прогнати `teardown` по всіх онлайн-ядрах процесора — і саме звідти прилетять останні об'єкти.

**`teardown`, що повертає помилку.** У колбека є тип `int`, і спокуса чогось не вдатися велика. Не варто: коли `cpuhp_remove_state()` розсилає `teardown` під час вивантаження модуля, ненульова відповідь ловиться `BUG_ON()` просто на місці. Логіка тверда — ядро процесора вже приречене, скасовувати скасування нікуди. `teardown` мусить уміти впоратися завжди; якщо для прибирання треба щось, що може не вдатися, це «щось» готують у `startup`.

**Номер стану — не константа.** Ані `220` з наших виводів, ані `232` не є частиною жодної домовленості. Динамічний номер залежить від того, скільки модулів попросили його до вас, тому й у скриптах перевірки, і в тестах його щоразу шукають за іменем у `states`. Той самий скрипт на іншому ядрі з іншою конфігурацією знайде інше число — і це нормально.

І остання, приємна дрібниця для тих, хто дійшов сюди: увесь цей шлях видно й у трасуванні. Увімкніть точки `cpuhp:cpuhp_enter` та `cpuhp:cpuhp_exit` — і кожен крок відрізка з іменем функції й кодом повернення ляже в кільцевий буфер, разом із тим, який саме потік його виконував. Про самі точки й [ftrace](book:unix-linux/ftrace-kernel-tracing) — окремо, але для перевірки колбека цих двох вистачає з головою: там видно і порядок, і те, на якому ядрі процесора що бігло, і де саме зірвався перехід.
