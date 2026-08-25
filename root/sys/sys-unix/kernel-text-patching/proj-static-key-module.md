# ⚙️ Модуль зі статичним ключем: п'ять байтів під мікроскопом

Опис механізму звучить переконливо рівно доти, доки не поглянеш на байти. Тут ми зберемо невеликий модуль ядра, який оголошує власний статичний ключ, виставляє в `/sys` перемикач до нього — і сам друкує ті п'ять байтів, що змінюються при перемиканні. Потім подивимося на них ззовні, дизасемблюючи працююче ядро.

## Що має вміти модуль

Потрібні три речі. Ключ, оголошений `DEFINE_STATIC_KEY_FALSE`. Функція з `static_branch_unlikely()` усередині — саме в ній компілятор залишить п'ятибайтовий проміжок. І запис у `/sys`, з якого кличеться `static_branch_enable()`.

Четверте — вміння знайти той проміжок у пам'яті — виглядає як окрема морока, але ядро вже все порахувало за нас. Кожна вставка `static_branch_*` лишає запис у секції `__jump_table`, і при завантаженні модуля ядро складає його записи в `THIS_MODULE->jump_entries`. Звідти `jump_entry_code()` дає точну адресу місця, яке патчиться. Шукати наосліп не доведеться.

```c
// SPDX-License-Identifier: GPL-2.0
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/jump_label.h>
#include <linux/moduleparam.h>

#ifndef CONFIG_JUMP_LABEL
#error "Треба ядро з CONFIG_JUMP_LABEL=y, інакше це буде звичайний if"
#endif

static DEFINE_STATIC_KEY_FALSE(demo_key);

unsigned long demo_arg = 7;
unsigned long demo_hot(unsigned long x);

/* Гаряча функція. noinline і не static — щоб лишилася окремим
 * символом і потрапила в /proc/kallsyms під власним іменем.
 */
noinline unsigned long demo_hot(unsigned long x)
{
        if (static_branch_unlikely(&demo_key))
                return x * 3 + 1;
        return x + 1;
}

/* Показати байти в кожному місці, яке цей модуль патчить. */
static void demo_dump(const char *when)
{
        struct jump_entry *e = THIS_MODULE->jump_entries;
        unsigned int i, n = THIS_MODULE->num_jump_entries;

        for (i = 0; i < n; i++) {
                const u8 *code = (const u8 *)jump_entry_code(&e[i]);

                pr_info("%s: %pS @ %px -> %5ph\n", when, code, code, code);
        }
        pr_info("%s: demo_hot(%lu) = %lu\n", when, demo_arg, demo_hot(demo_arg));
}

static bool enabled;

static int demo_set(const char *val, const struct kernel_param *kp)
{
        bool was = enabled;
        int ret = param_set_bool(val, kp);   /* пише в &enabled */

        if (ret)
                return ret;
        if (enabled == was)
                return 0;

        /* Обидві беруть м'ютекс і cpus_read_lock() — тобто можуть заснути.
         * Тут це безпечно: запис у /sys приходить у контексті процесу.
         */
        if (enabled)
                static_branch_enable(&demo_key);
        else
                static_branch_disable(&demo_key);

        demo_dump(enabled ? "після enable" : "після disable");
        return 0;
}

static const struct kernel_param_ops demo_ops = {
        .set = demo_set,
        .get = param_get_bool,
};
module_param_cb(enabled, &demo_ops, &enabled, 0644);
MODULE_PARM_DESC(enabled, "0/1 — перемкнути статичний ключ");

static int __init demo_init(void)
{
        demo_dump("на старті");
        return 0;
}

static void __exit demo_exit(void) { }

module_init(demo_init);
module_exit(demo_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Статичний ключ під мікроскопом");
```

Два місця в цьому коді варті пояснення. `module_param_cb()` — найдешевший спосіб отримати перемикач у `/sys`: параметр з правами `0644` сам з'являється як `/sys/module/<ім'я>/parameters/enabled`, а наш `.set` перехоплює запис. І `%px` замість звичного `%p`: `%p` віддає **хеш** адреси, з якого нічого не знайдеш, а `%px` друкує справжнє значення. `%5ph` — п'ять байтів у шістнадцятковому вигляді, `%pS` — ім'я символу зі зміщенням.

## Збірка поза деревом ядра

Модуль будується проти вже встановленого ядра — потрібен лише пакунок із заголовками (`linux-headers-$(uname -r)` у Debian, `kernel-devel` у Fedora). [Модулі ядра](topic:sys-unix/kernel-modules) — окрема тема; тут вистачить чотирьох рядків `Makefile` (відступи — табуляції, це `make`):

```makefile
obj-m += statickey_demo.o
KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	$(MAKE) -C $(KDIR) M=$(CURDIR) modules
clean:
	$(MAKE) -C $(KDIR) M=$(CURDIR) clean
```

Перед збіркою варто переконатися, що ядро зібране як треба — [конфігурація ядра](topic:sys-unix/kernel-config-and-build) лишається у файлі поруч з образом:

```
$ grep -E 'CONFIG_(JUMP_LABEL|KALLSYMS|PROC_KCORE)=' /boot/config-$(uname -r)
CONFIG_JUMP_LABEL=y
CONFIG_KALLSYMS=y
CONFIG_PROC_KCORE=y
```

Далі — звичайне `make`, `sudo insmod statickey_demo.ko` і `dmesg`:

```
statickey_demo: на старті: demo_hot+0x9/0x1c [statickey_demo] @ ffffffffc0a5e009 -> 0f 1f 44 00 00
statickey_demo: на старті: demo_hot(7) = 8
```

Ось він — п'ятибайтовий `nop`. Тепер перемикач:

```
$ echo 1 | sudo tee /sys/module/statickey_demo/parameters/enabled
```

```
statickey_demo: після enable: demo_hot+0x9/0x1c [statickey_demo] @ ffffffffc0a5e009 -> e9 05 00 00 00
statickey_demo: після enable: demo_hot(7) = 22
```

`0F 1F 44 00 00` стало `E9 05 00 00 00`. Значення теж змінилося з 8 на 22 — гілка справді інша, і ніякої змінної при цьому ніхто не читав.

## Ті самі байти ззовні

Модуль показав себе сам, але цікавіше побачити його очима сторонньої програми. Адресу дає таблиця символів, доступна через [`/proc`](topic:sys-unix/proc-reading-process-and-kernel-state):

```
$ sudo grep -w demo_hot /proc/kallsyms
ffffffffc0a5e000 T demo_hot	[statickey_demo]
```

Без `sudo` тут будуть самі нулі: адреси ядра показують лише тим, хто має `CAP_SYSLOG`. Тепер дизасемблюємо живу пам'ять. `/proc/kcore` — це вся оперативна пам'ять ядра, викладена як звичайний ELF-файл образу пам'яті, і `gdb` читає його без жодних додаткових умовностей:

```
$ sudo gdb -q -c /proc/kcore -ex 'x/5i 0xffffffffc0a5e000' -ex quit
   0xffffffffc0a5e000:	endbr64
   0xffffffffc0a5e004:	nopl   0x0(%rax,%rax,1)
   0xffffffffc0a5e009:	nopl   0x0(%rax,%rax,1)
   0xffffffffc0a5e00e:	lea    0x1(%rdi),%rax
   0xffffffffc0a5e012:	ret
```

Після перемикання:

```
   0xffffffffc0a5e009:	jmp    0xffffffffc0a5e013
   0xffffffffc0a5e00e:	lea    0x1(%rdi),%rax
   0xffffffffc0a5e012:	ret
   0xffffffffc0a5e013:	lea    (%rdi,%rdi,2),%rax
   0xffffffffc0a5e017:	add    $0x1,%rax
   0xffffffffc0a5e01b:	ret
```

Тут одразу видно те, чого не розкажеш словами. Рідкісна гілка (`x * 3 + 1`) лежить **після** `ret`, за межами звичайного шляху виконання — компілятор виніс її з гарячого коду, як йому й веліли. А `jmp` веде саме туди.

Зверніть увагу на зміщення `+0x4`: там теж п'ятибайтовий `nop`, і байти в нього ті самі. Це затертий на `nop` виклик `__fentry__`, точка входу ftrace. Тому шукати статичний ключ візуальним пошуком `nop`-а в дизасемблері марно — адресу треба брати з таблиці, як ми й зробили.

Якщо `/proc/kcore` у вашому дистрибутиві вимкнено або заблоковано режимом lockdown при Secure Boot — нічого страшного: дамп самого модуля вже відповів на те саме питання. (Той-таки Secure Boot, до речі, взагалі відмовиться завантажувати непідписаний модуль.)

## Для порівняння: звичайний прапорець

Щоб побачити, від чого саме нас позбавили, допишіть у модуль другу функцію — таку саму, але на глобальній змінній:

```c
static bool demo_flag;

noinline unsigned long demo_plain(unsigned long x)
{
        if (READ_ONCE(demo_flag))
                return x * 3 + 1;
        return x + 1;
}
```

Дизасемблюйте її так само — і на місці нашого `nop` побачите ось що:

```
   0xffffffffc0a5f009:	cmpb   $0x0,0x1a34(%rip)   # demo_flag
   0xffffffffc0a5f010:	jne    0xffffffffc0a5f017
   0xffffffffc0a5f012:	lea    0x1(%rdi),%rax
   0xffffffffc0a5f016:	ret
```

Дев'ять байтів замість п'яти, і серед них — звертання до пам'яті за адресою прапорця та умовний перехід. Цей `cmpb` займе рядок кешу даних, а `jne` — запис у передбачувачі переходів. Обидва ресурси скінченні, і те, що дісталося прапорцеві, не дісталося іншому коду. Статичний ключ прибирає з цього шляху рівно все: лишається `nop`, який процесор пропускає, ні на що не дивлячись.

Другий корисний дослід — поставити `static_branch_unlikely(&demo_key)` ще в одній функції. Цикл у `demo_dump()` не змінюється, але тепер друкує два рядки, і обидва міняються від одного `echo 1`. Це і є суть ключа: одне логічне рішення, скільки завгодно місць у коді, і `static_branch_enable()` обходить їх усі за один пакет правок.

## Три пастки

**Дизасемблювати `.ko` немає сенсу.** `objdump -d statickey_demo.ko` покаже початковий стан — і показуватиме його завжди, скільки б разів ви не перемикали ключ. Файл на диску не міняється ніколи; байти правляться в тій копії, яку `insmod` розмістив у пам'яті ядра. Ба більше, `.ko` — переміщуваний об'єктний файл: адреси в його `__jump_table` ще не остаточні, а власні `.altinstructions` модуля накладаються теж лише при завантаженні. Навіть «початковий» вигляд завантаженого модуля може відрізнятися від файлу.

**Виміряти виграш мікробенчмарком усередині модуля майже неможливо** — і корисно розуміти чому. Різниця між `nop` і передбаченою гілкою — частки наносекунди, тоді як `ktime_get_ns()` коштує десятки, а `rdtsc` із серіалізацією — теж більше за те, що ми міряємо. Прилад важчий за явище. Гірше інше: у тісному циклі прапорець назавжди осідає в кеші першого рівня, а [передбачувач переходів](topic:hw-arch/branch-prediction) вгадує його зі стовідсотковою точністю — тобто звичайний `if` виглядатиме безплатним. Але ж справжня його ціна лежить **не в цьому циклі**: це рядок кешу й запис у передбачувачі, відібрані в іншого коду, і холодне тіло, що розсовує гарячу функцію в кеші інструкцій. Мікробенчмарк моделює рівно ту ситуацію, у якій цих витрат немає. Числа, з якими цей механізм приймали в ядро, отримані інакше — на повному навантаженні цілої системи, за її пропускною здатністю, а не приладом усередині циклу.

**`static_branch_enable()` не можна кликати з атомарного контексту.** Дорогою вниз вона бере `cpus_read_lock()` і м'ютекс таблиці міток, а нижче `text_poke_bp()` бере ще й `text_mutex` і розсилає міжпроцесорні переривання. Будь-що з цього може заснути. Отже: не з обробника переривання, не під спінлоком, не з таймера, не з вимкненим витісненням. При `CONFIG_DEBUG_ATOMIC_SLEEP=y` ядро скаже `BUG: sleeping function called from invalid context`; без нього — тиша, а потім взаємне блокування в найгіршу мить. Треба перемкнути з атомарного контексту — заплануйте `work_struct`. У нашому модулі все зійшлося саме тому, що запис у `/sys` приходить у контексті процесу.

Сюди ж — три дрібниці, на яких спотикаються.

Макроси треба брати **парою**: `DEFINE_STATIC_KEY_FALSE` разом зі `static_branch_unlikely()`, `DEFINE_STATIC_KEY_TRUE` — зі `static_branch_likely()`. Компілятор дивиться саме на цю пару, вирішуючи, що покласти в код при збірці. Збіглася — у типовому стані стоїть `nop`, і гаряча гілка проходить наскрізь. Не збіглася (скажімо, `likely` на ключі-`FALSE`) — код зберуть із `jmp` на місці перевірки, і в найпоширенішому стані ви платитимете перехід замість нічого. Помилка мовчазна: усе працює, просто дарма.

`static_branch_enable()`/`disable()` задають стан прямо й ідемпотентно, а `static_branch_inc()`/`dec()` рахують посилання (кілька підсистем можуть незалежно тримати ключ увімкненим). Змішувати обидві пари на одному ключі не можна — лічильник поїде.

І кожне перемикання — це переривання на всі обчислювальні ядра. Ключ, який доводиться смикати часто, є просто дорогим `if`. Статичний ключ окупається лише там, де читань мільярди, а записів одиниці.
