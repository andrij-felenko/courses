# ⚙️ Латка від нуля: зібрати, увімкнути й навмисно застрягти

Живе латання найпереконливіше виглядає тоді, коли `/proc/cmdline` у вас на очах починає казати щось інше — без перезавантаження й без єдиного зупиненого процесу. Тут ми зберемо модуль-латку, що підміняє одну коротку функцію ядра, простежимо перехід по задачах, а потім свідомо влаштуємо той стан, заради якого існує файл `force`: перехід, що не завершується ніколи.

Мішень — `cmdline_proc_show()` з `fs/proc/cmdline.c`. Усе, що вона робить, — виводить [збережений командний рядок ядра](book:unix-linux/bootloader-and-cmdline) у буфер `seq_file`. Її ж узяв за мішень і приклад у дереві ядра, `samples/livepatch/livepatch-sample.c`, і не випадково: функція коротка, кличеться лише з читання файлу, нічого не тримає й нічого не змінює.

## Чи вміє це ядро

Живе латання не вмикається саме собою — його вирішують під час [збірки ядра](book:unix-linux/kernel-config-and-build), і `.config` лишається поруч з образом:

```
$ grep -E 'CONFIG_(LIVEPATCH|DYNAMIC_FTRACE_WITH|KALLSYMS_ALL|HAVE_RELIABLE_STACKTRACE|TRIM_UNUSED_KSYMS)' /boot/config-$(uname -r)
CONFIG_LIVEPATCH=y
CONFIG_DYNAMIC_FTRACE_WITH_REGS=y
CONFIG_DYNAMIC_FTRACE_WITH_ARGS=y
CONFIG_KALLSYMS_ALL=y
CONFIG_HAVE_RELIABLE_STACKTRACE=y
# CONFIG_TRIM_UNUSED_KSYMS is not set
```

Кожен рядок тут не формальність, а вимога з причиною. `DYNAMIC_FTRACE_WITH_REGS` (або новіший `WITH_ARGS`) потрібен тому, що обробник livepatch мусить дістатися збереженої адреси повернення й підмінити її — звичайного гачка [ftrace](book:unix-linux/ftrace-kernel-tracing) без регістрів для цього замало. `KALLSYMS_ALL` — тому що цілі латка шукає в таблиці символів самого ядра, а без цього прапорця туди потрапляють лише символи коду: імен даних, як-от `saved_command_line`, у ній не буде. `CONFIG_LIVEPATCH` прямо від нього залежить, тож вимкнути його окремо все одно не вийде. `TRIM_UNUSED_KSYMS` мусить бути вимкнений: він викидає з ядра експорти, якими ніхто зі зібраних модулів не користується, а латка приходить пізніше й потребує саме тих, яких на момент збірки ніхто не просив.

Найшвидша перевірка — без `.config` узагалі: тека `/sys/kernel/livepatch` існує тоді й лише тоді, коли підтримка ввімкнена.

## Модуль

Латка — це звичайний [модуль ядра](book:unix-linux/kernel-modules) з новим тілом функції та невеличкою таблицею, що каже, кого воно заступає. Одразу закладемо в неї другий об'єкт — він знадобиться, коли ми навмисно застрягатимемо.

```c
// SPDX-License-Identifier: GPL-2.0
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/livepatch.h>
#include <linux/seq_file.h>
#include <linux/kthread.h>
#include <linux/sched.h>

/* Нове тіло cmdline_proc_show(). Підпис має збігатися ДО КРАПКИ:
 * компілятор його не звірить — .new_func оголошений як void *.
 */
static int livepatch_cmdline_proc_show(struct seq_file *m, void *v)
{
        seq_printf(m, "%s\n", "цю машину залатано наживо");
        return 0;
}

/* Нове тіло victim_loop() з модуля klp_victim (див. нижче). */
static void livepatch_victim_loop(void)
{
        pr_info("нова версія циклу\n");
        while (!kthread_should_stop())
                schedule_timeout_interruptible(HZ);
}

static struct klp_func vmlinux_funcs[] = {
        { .old_name = "cmdline_proc_show",
          .new_func = livepatch_cmdline_proc_show }, { }
};

static struct klp_func victim_funcs[] = {
        { .old_name = "victim_loop",
          .new_func = livepatch_victim_loop }, { }
};

static struct klp_object objs[] = {
        { /* .name = NULL — саме ядро */
          .funcs = vmlinux_funcs },
        { .name  = "klp_victim",       /* ім'я модуля, як у /proc/modules */
          .funcs = victim_funcs },
        { }
};

static struct klp_patch patch = {
        .mod  = THIS_MODULE,
        .objs = objs,
};

static int livepatch_demo_init(void)
{
        return klp_enable_patch(&patch);
}

static void livepatch_demo_exit(void) { }

module_init(livepatch_demo_init);
module_exit(livepatch_demo_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Латка навчальна");
MODULE_INFO(livepatch, "Y");
```

Три речі тут варті окремої уваги.

`MODULE_INFO(livepatch, "Y")` — не декоративна позначка, а те, за чим завантажувач модулів упізнає латку. Забудьте цей рядок — і `insmod` поверне `Invalid argument`, а в журналі буде рівно та відповідь, якої заслуговує помилка: `livepatch: module livepatch_demo is not marked as a livepatch module`.

`klp_enable_patch()` кличеться з ініціалізації модуля й тільки звідти. Так зроблено навмисно: якщо ввімкнути латку не вдалося, повернений код помилки просто не дає модулю завантажитися, і в системі не лишається напівживого об'єкта.

Другий об'єкт вказує на модуль, якого зараз у пам'яті немає, — і це нормально. Ядро запам'ятає його й долатає `klp_victim`, щойно той з'явиться. Вихід із модуля порожній: латку вимикають записом у `/sys`, а не вивантаженням.

## Збірка проти свого ядра

Модуль-латка збирається проти заголовків **саме того** ядра, у яке піде, — адреси й розкладка структур у ній прив'язані до конкретної збірки. Потрібен пакунок `linux-headers-$(uname -r)` (Debian) чи `kernel-devel` (Fedora). `Makefile` — чотири рядки, відступи табуляціями:

```makefile
obj-m += livepatch_demo.o klp_victim.o
KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	$(MAKE) -C $(KDIR) M=$(CURDIR) modules
clean:
	$(MAKE) -C $(KDIR) M=$(CURDIR) clean
```

Далі — `make`, `sudo insmod livepatch_demo.ko` і найкоротший дослід у всьому цьому тексті:

```
$ cat /proc/cmdline
BOOT_IMAGE=/vmlinuz-6.12.0 root=/dev/nvme0n1p2 ro quiet
$ sudo insmod livepatch_demo.ko
$ cat /proc/cmdline
цю машину залатано наживо
```

(При Secure Boot непідписаний модуль не завантажиться взагалі — це обмеження підпису, а не livepatch.)

Тепер подивимося, як це виглядало зсередини:

```
$ cat /sys/kernel/livepatch/livepatch_demo/enabled
1
$ cat /sys/kernel/livepatch/livepatch_demo/transition
0
$ dmesg | tail -2
livepatch: 'livepatch_demo': starting patching transition
livepatch: 'livepatch_demo': patching complete
```

`transition` уже нуль, бо перехід завершився швидше, ніж ми встигли набрати команду: жодна задача в системі не сиділа всередині `cmdline_proc_show`, тож усі перемкнулися першим же обходом. Стан кожної задачі окремо видно в `/proc/<pid>/patch_state`, і поза переходом він однаковий у всіх:

```
$ sudo cat /proc/1/patch_state
-1
```

`-1` означає «перехід не триває», `1` — «задача вже на новій версії», `0` — «ще на старій». Ці три числа й будуть нашим приладом.

## Тепер застрягнемо навмисно

Щоб перехід завис, потрібна задача, яка не виходить із латаної функції. Найпростіше зробити її самим — [потоком ядра](book:unix-linux/kernel-threads), увесь життєвий цикл якого проходить усередині одного виклику:

```c
// SPDX-License-Identifier: GPL-2.0
#include <linux/module.h>
#include <linux/kthread.h>
#include <linux/sched.h>

static struct task_struct *victim_thread;

void victim_loop(void);

/* noinline і не static — щоб функція лишилася окремим символом.
 * Уся робота потоку відбувається ВСЕРЕДИНІ неї, тож її кадр лежить
 * на стеку потоку від першої до останньої миті.
 */
noinline void victim_loop(void)
{
        while (!kthread_should_stop())
                schedule_timeout_interruptible(HZ);
}

static int victim_fn(void *unused)
{
        victim_loop();
        return 0;
}

static int __init victim_init(void)
{
        victim_thread = kthread_run(victim_fn, NULL, "klp_victim");
        return PTR_ERR_OR_ZERO(victim_thread);
}

static void __exit victim_exit(void)
{
        kthread_stop(victim_thread);
}

module_init(victim_init);
module_exit(victim_exit);
MODULE_LICENSE("GPL");
```

Порядок важливий: жертва має бути в пам'яті **до** ввімкнення латки. Знімаємо латку (спершу `enabled`, лише потім `rmmod` — вивантажити ввімкнену не можна), і починаємо заново:

```
$ echo 0 | sudo tee /sys/kernel/livepatch/livepatch_demo/enabled
$ sudo rmmod livepatch_demo
$ sudo insmod klp_victim.ko
$ sudo insmod livepatch_demo.ko
$ cat /sys/kernel/livepatch/livepatch_demo/transition
1
$ sleep 60; cat /sys/kernel/livepatch/livepatch_demo/transition
1
```

Ось як виглядає незавершений перехід: `enabled` уже одиниця, `/proc/cmdline` уже підмінений — а `transition` не спадає ні через хвилину, ні через годину. Латка діє для всіх, крім тих, хто ще не перемкнувся; і поки таких є, у системі співіснують обидві версії.

Винуватця шукають за тим самим `patch_state` — це просто перелік задач, у яких стоїть нуль:

```
$ for f in $(sudo grep -l '^0$' /proc/*/patch_state 2>/dev/null); do
>     pid=${f#/proc/}; pid=${pid%/patch_state}
>     echo "$pid $(cat /proc/$pid/comm)"
> done
417 klp_victim
```

Одна задача з тисячі. Причину, з якої вона не перемикається, ядро вміє назвати вголос — треба лише попросити:

```
$ echo -n 'file kernel/livepatch/transition.c +p' | sudo tee /sys/kernel/debug/dynamic_debug/control
$ dmesg | tail -1
livepatch: klp_try_switch_task: klp_victim:417 is sleeping on function victim_loop
```

Це вичерпна відповідь: потік спить усередині латаної функції, його стек містить стару версію, і перемкнути його не можна. Кожні п'ятнадцять секунд ядро будить такі потоки, а звичайним задачам шле підробний сигнал (`livepatch: signaling remaining tasks`) — але наш потік, прокинувшись, повертається в той самий цикл усередині тієї самої функції, і жодне будіння не допоможе.

Правильний вихід — прибрати винуватця, а не перехід:

```
$ sudo rmmod klp_victim
$ cat /sys/kernel/livepatch/livepatch_demo/transition
0
```

Потік завершився, його прапорець зник разом із ним — і перехід дійшов до кінця сам.

Тепер про `force`. Запис одиниці в `/sys/kernel/livepatch/livepatch_demo/force` знімає `TIF_PATCH_PENDING` з усіх задач, і `transition` миттєво стає нулем. Але зверніть увагу, чого при цьому **не** сталося: потік і далі виконує старий код — просто ядро більше про це не знає. Воно щиро вважає, що старої версії не виконує ніхто, а перевірити вже ніяк. Тому плата однозначна: ядро назавжди перестає відпускати посилання на модуль-латку, і `rmmod` після цього не спрацює **ніколи** — до перезавантаження. Пришвидшити нею перехід не можна, можна лише відмовитися від гарантії; за нормальних обставин це не інструмент, а визнання, що машину доведеться перезавантажити.

(Записати `force` можна тільки в латку, що зараз у переході; інакше — `Invalid argument`.)

## Пастки, на яких закінчується ручна збірка

Наш дослід вдався тому, що мішень підібрана під нього. Три речі стають на заваді, щойно мішень справжня.

**Функцію вбудував компілятор.** `insmod` тоді провалюється з `Invalid argument`, а в журналі — `livepatch: symbol 'foo' not found in symbol table`: символу немає, бо тіло розчинилося в тих, хто його кликав. Латати треба вже їх — усіх до одного, і жодна з них не мала помилки. Саме тут ручний спосіб уперше стає непосильним: список викликальників має вирахувати інструмент.

**Функція не трасовна.** Livepatch не пише інструкцій сам, він чіпляється на п'ятибайтовий проміжок, що його [компілятор лишає на вході](book:unix-linux/kernel-text-patching) кожної придатної до трасування функції. Там, де цього проміжку немає — `notrace`, низький код входу в ядро, стартові функції з розділу `__init`, — чіплятися нема за що: `livepatch: failed to find location for function 'foo'`.

**Новому коду потрібен `static`-символ цілі.** Наша латка друкує сталий рядок — і це не лінощі автора взірця, а обхід. Чесна заміна `/proc/cmdline` мусила б прочитати `saved_command_line`, а ця змінна, хоч і глобальна, модулям не експортована. Звичайне [лінкування](book:programming/linking) на ній і зупиниться: `modpost` скаже `"saved_command_line" [livepatch_demo.ko] undefined!`. Те саме — і навіть безнадійніше — з будь-яким [`static`-символом](book:programming/translation-unit) того файлу, який ви латаєте: такого імені лінкувальник не бачить у принципі.

Розв'язання є, але не для рук. Латка несе особливі перерозміщення в секціях `.klp.rela` з символами вигляду `.klp.sym.vmlinux.saved_command_line,0`, які завантажувач модулів розв'язує через таблицю символів ядра; кінцевий нуль — це `sympos`, номер входження на випадок, коли однакове `static`-ім'я трапляється в ядрі кілька разів (той самий номер задають полем `old_sympos` у `klp_func`, коли ядро скаржиться на `unresolvable ambiguity`). Написати такі секції вручну неможливо — їх складає збирач.

Звідси й береться межа цієї вправи. Справжні латки будують інструменти: `kpatch-build` компілює ядро двічі — до й після виправлення, — порівнює об'єктні файли, сам знаходить змінені функції, сам піднімається до викликальників там, де щось вбудовано, і сам породжує `.klp.rela`. У 6.19 те саме приїхало в саме дерево ядра як `klp-build`, переписане поверх `objtool`, який розбирає граф керування й через це знаходить зміни надійніше за порівняння байтів.

Але все, що ці інструменти роблять, вони роблять **до** `insmod`. Модель узгодженості, три числа в `patch_state`, застряглий потік і ціна `force` — усе це лишається рівно таким, як ви щойно бачили руками.
