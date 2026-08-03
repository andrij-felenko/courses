# 📋 Шар сумісности з боку коду ядра: типи, покажчики, точки підключення

Це довідка інтерфейсу, який шар сумісности дає авторові коду ядра: якими типами оголошують 32-бітну форму структури, якою функцією перетворюють покажчик, яким макросом заводять компат-вхід, у яке поле драйвер вішає власний переклад і які числа порівнює фільтр системних викликів. Потрібна вона рівно тоді, коли до вашого коду може дістатися 32-бітний процес, — а це майже будь-який драйвер із власним `ioctl`, будь-який новий виклик, що приймає структуру, і будь-який seccomp-фільтр на x86-64.

## Де що оголошено

| Файл | Що звідти беруть |
| --- | --- |
| `include/linux/compat.h` | `compat_ptr()`, `ptr_to_compat()`, `COMPAT_SYSCALL_DEFINE*`, `in_compat_syscall()`, `struct compat_iovec`, `compat_get_bitmap()`, `get_compat_sigset()` |
| `include/asm-generic/compat.h` | типові `compat_*_t` і сталі `COMPAT_USER_HZ`, `COMPAT_RLIM_INFINITY`, `COMPAT_OFF_T_MAX` |
| `arch/<арх>/include/asm/compat.h` | архітектурні відхилення: інша `compat_ptr()`, інший `__SC_DELOUSE`, `struct compat_stat` |
| `include/vdso/time32.h` · `include/linux/time32.h` | `old_time32_t`, `struct old_timespec32` та перетворювачі до них |
| `include/linux/fs.h` | поле `.compat_ioctl` у `struct file_operations` |
| `fs/ioctl.c` | готова реалізація `compat_ptr_ioctl()` |
| `arch/x86/include/uapi/asm/unistd.h` | `__X32_SYSCALL_BIT` |
| `include/uapi/linux/audit.h` | значення `AUDIT_ARCH_*`, якими фільтр упізнає ABI |

Ключ до всієї таблиці — префікс. `compat_` читається як «форма, яку ця річ має у 32-бітному ABI, побачена з коду 64-бітного ядра». Ім'я в ядрі навмисно не збігається з іменем у програмі: програма пише `size_t`, ядро для тієї самої величини пише `compat_size_t` — і компілятор більше не дасть переплутати два різні числа з однаковою назвою.

## Типи: ширина і знак

Значення в стовпці «ширина» — байти, за загальним `include/asm-generic/compat.h`; архітектура може перевизначити окремий рядок.

| Компат-тип | Основа | Ширина | Рідний відповідник | Ширина рідного |
| --- | --- | --- | --- | --- |
| `compat_int_t` | `s32` | 4 | `int` | 4 |
| `compat_uint_t` | `u32` | 4 | `unsigned int` | 4 |
| `compat_short_t` · `compat_ushort_t` | `s16` · `u16` | 2 | `short` · `unsigned short` | 2 |
| `compat_long_t` | `s32` | 4 | `long` | 8 |
| `compat_ulong_t` | `u32` | 4 | `unsigned long` | 8 |
| `compat_size_t` | `u32` | 4 | `size_t` | 8 |
| `compat_ssize_t` | `s32` | 4 | `ssize_t` | 8 |
| `compat_uptr_t` | `u32` | 4 | `void __user *` | 8 |
| `compat_caddr_t` | `u32` | 4 | адреса «в старому стилі» | 8 |
| `compat_off_t` | `s32` | 4 | `off_t` | 8 |
| `compat_loff_t` | `s64` | 8 | `loff_t` | 8 |
| `compat_ino_t` | `u32` | 4 | `ino_t` | 8 |
| `compat_clock_t` | `s32` | 4 | `__kernel_clock_t` | 8 |
| `compat_mode_t` | `u32` | 4 | `umode_t` | 2 |
| `compat_dev_t` | `u32` | 4 | `dev_t` | 4 |
| `compat_pid_t` | `s32` | 4 | `pid_t` | 4 |
| `compat_key_t` · `compat_timer_t` · `compat_daddr_t` | `s32` | 4 | однойменні | 4 |
| `__compat_uid32_t` · `__compat_gid32_t` | `u32` | 4 | `uid_t` · `gid_t` | 4 |
| `compat_s64` · `compat_u64` | `s64` · `u64` | 8 | `s64` · `u64` | 8 |

Рядки поділяються на три класи, і кожен вимагає іншої уваги.

**Ширина збігається** (`compat_int_t`, `compat_pid_t`, `compat_dev_t`). Тип існує не заради перетворення, а заради однаковости запису: коли всі поля структури названо компат-типами, жодне не лишиться поза оглядом, а окрема архітектура зможе перевизначити саме той рядок, який у неї інший.

**Компат-тип вужчий** (`compat_long_t`, `compat_size_t`, `compat_off_t`, `compat_ino_t`). Тут і працює переклад, і тут вирішує знак: `compat_long_t` — знаковий, тож `-1` мусить лишитися `-1` після розширення, а `compat_size_t` — беззнаковий, і його розширюють нулями. Помилка в цьому місці не помітна на малих числах і руйнівна на великих; чому саме — розібрано у [знаковому розширенні](book:programming/sign-extension). Із `compat_off_t` завширшки чотири байти зі знаком випливає `COMPAT_OFF_T_MAX` = `0x7fffffff`: 2 ГіБ мінус один байт, історична межа, заради обходу якої у 32-бітному ABI й з'явилися `stat64`, `_llseek` і `fcntl64`.

**Компат-тип ширший за рідний** — рідкість, але вона є: `compat_mode_t` займає 4 байти, тоді як у ядрі права доступу тримає двобайтовий `umode_t`. Це нагадування, що компат-тип описує не «менше», а «інакше»; ширина рідного типу тут ні до чого. Загальний огляд того, чому розміри цілих у C взагалі не сталі, — у [цілих типах](book:programming/integer-types-c).

Три сталі, які ходять разом із типами:

```
COMPAT_USER_HZ         100          частота, якою 32-бітний ABI рахує тики
COMPAT_RLIM_INFINITY   0xffffffff   «без обмеження» у 32-бітному getrlimit
COMPAT_OFF_T_MAX       0x7fffffff   найбільший зсув, який поміщається в compat_off_t
```

## Вирівнювання, яке несе сам тип

Найтихіша частина контракту — остання пара рядків таблиці. `compat_s64` і `compat_u64` мають ту саму ширину, що й рідні `s64`/`u64`, і все одно оголошені окремо:

```c
#ifdef CONFIG_COMPAT_FOR_U64_ALIGNMENT
typedef s64 __attribute__((aligned(4))) compat_s64;
typedef u64 __attribute__((aligned(4))) compat_u64;
#else
typedef s64 compat_s64;
typedef u64 compat_u64;
#endif
```

Компат-тип несе не лише ширину, а й вимогу [вирівнювання](book:programming/memory-alignment) — правило, за яким компілятор обирає адресу поля всередині структури. На архітектурах, де 32-бітна домовленість ставить восьмибайтове ціле на межу чотирьох байтів (x86 серед них — саме для цього ввімкнено `CONFIG_COMPAT_FOR_U64_ALIGNMENT`), `compat_s64` несе `aligned(4)`, і структура, зібрана з компат-типів, лягає байт у байт так, як її бачить 32-бітна програма. Постав у ту саму структуру звичайний `s64` — і компілятор ядра відсуне його на межу восьми, додавши чотири байти набивки, яких у програмі немає.

Звідси перше практичне правило: **у 32-бітному двійникові структури не має бути жодного рідного типу**. Не тому, що ширина не збіглася б, а тому, що вирівнювання збігтися не зобов'язане.

## Час: чому тут не `compat_`, а `old_*32`

```c
typedef s32 old_time32_t;

struct old_timespec32 {
	old_time32_t	tv_sec;
	s32		tv_nsec;
};

struct old_timeval32 {
	old_time32_t	tv_sec;
	s32		tv_usec;
};

struct old_itimerspec32 {
	struct old_timespec32 it_interval;
	struct old_timespec32 it_value;
};

struct old_utimbuf32 {
	old_time32_t	actime;
	old_time32_t	modtime;
};
```

`struct old_timespec32` — вісім байтів із вирівнюванням на чотири, тоді як рідна `struct timespec64` займає шістнадцять і вирівнюється на вісім. Перекладають їх готовими функціями, і всі вони повертають `0` або `-EFAULT`:

```c
extern int get_old_timespec32(struct timespec64 *, const void __user *);
extern int put_old_timespec32(const struct timespec64 *, void __user *);
extern int get_old_itimerspec32(struct itimerspec64 *its,
				const struct old_itimerspec32 __user *uits);
extern int put_old_itimerspec32(const struct itimerspec64 *its,
				struct old_itimerspec32 __user *uits);
int get_old_timex32(struct __kernel_timex *, const struct old_timex32 __user *);
int put_old_timex32(struct old_timex32 __user *, const struct __kernel_timex *);
```

Ім'я тут промовисте, і в ньому зміст. Префікс `compat_` доречний лише там, де є два ABI під одним ядром: він означає «чужа форма, яку ми переклали». Вузький час — випадок ширший: він існує ще й на справжньому 32-бітному ядрі, де жодного шару сумісности немає взагалі, а `struct timespec` із чотирибайтовим `tv_sec` є рідною. Тому під час підготовки до 2038 року ці структури назвали `old_*32` — «стара, вузька форма», незалежно від того, хто її читає. Один комплект структур і один комплект перетворювачів обслуговують обидва випадки.

Практичний наслідок: у сучасному дереві не шукайте `compat_time_t` і `struct compat_timespec` — їх немає, а є `old_time32_t` і `struct old_timespec32`.

## Покажчик: `compat_ptr()` і `ptr_to_compat()`

```c
static inline void __user *compat_ptr(compat_uptr_t uptr)
{
	return (void __user *)(unsigned long)uptr;
}

static inline compat_uptr_t ptr_to_compat(void __user *uptr)
{
	return (u32)(unsigned long)uptr;
}
```

Правило нульового розширення тут не окрема дія, а властивість типу: `compat_uptr_t` — це `u32`, беззнакове; при розширенні до `unsigned long` старші біти заповнюються нулями за самим означенням мови. Знакове розширення виникає рівно в ту мить, коли адресу дорогою кладуть у знаковий 32-бітний тип — і саме тому перетворення оформлено функцією, а не приведенням типу вручну.

**Умова: 32-бітна програма передала адресу `0x80000000` — цілком законну верхню половину свого простору.**

```
через compat_ptr():
  (unsigned long)(u32)0x80000000        = 0x0000000080000000   ← адреса програми

уручну, якщо адреса встигла побувати знаковою:
  (unsigned long)(long)(int)0x80000000  = 0xFFFFFFFF80000000   ← половина ядра
```

Другий рядок — це не «на кілька байтів мимо». Це адреса з ядерного діапазону, підставлена звичайним користувачем.

| Архітектура | Тіло `compat_ptr()` | Чому саме так |
| --- | --- | --- |
| x86-64, arm64, ppc64, mips64, sparc64, riscv64 | `(void __user *)(unsigned long)uptr` | 32-бітний ABI адресує всі 4 ГіБ; жодного біта відкидати не можна |
| s390 | `(void __user *)(unsigned long)(uptr & 0x7fffffffUL)` | у режимі сумісности адреса має 31 біт, а старший біт слова несе службове значення й до адреси не належить |

`ptr_to_compat()` — зворотний бік: просте відкидання старших 32 бітів. Безпечне воно лише тому, що ядро вже подбало про передумову — уся пам'ять 32-бітної задачі лежить нижче 4 ГіБ, тож старші біти справді нульові. Викликати `ptr_to_compat()` на адресі, яку ядро видало 64-бітній задачі, — тиха втрата половини адреси без жодного попередження.

## Оголошення компат-виклику: `COMPAT_SYSCALL_DEFINE`

Макросів шість плюс нульовий, за кількістю аргументів: `COMPAT_SYSCALL_DEFINE0(name)` — і далі `COMPAT_SYSCALL_DEFINE1` … `COMPAT_SYSCALL_DEFINE6`, кожен приймає пари «тип, ім'я»:

```c
COMPAT_SYSCALL_DEFINE3(ioctl, unsigned int, fd, unsigned int, cmd,
		       compat_ulong_t, arg)
```

Поруч, у тому самому файлі, стоїть рідна форма:

```c
SYSCALL_DEFINE3(ioctl, unsigned int, fd, unsigned int, cmd,
		unsigned long, arg)
```

Уся різниця — тип третього аргументу. Це і є суть макроса: те саме тіло, оголошене типами іншої домовлености.

Розгортається один рядок у три функції, і кожна має своє призначення.

![Розгортання макроса COMPAT_SYSCALL_DEFINE3 у три функції: псевдонім для таблиці викликів, обгортка з аргументами типу long, у якій спрацьовує звуження, і тіло з оголошеними типами](/reference/unix-linux/foundations/compat-32-on-64/img/macro-expansion.svg)

*Звуження зібрано в середню функцію — далі йдуть уже перевірені значення.*

| Ім'я | Що це | Хто його бачить |
| --- | --- | --- |
| `compat_sys_<name>` | псевдонім (`alias`) без власного тіла, оголошений вашими типами | таблиця системних викликів |
| `__se_compat_sys_<name>` | обгортка, у якої всі аргументи мають тип `long`; тут спрацьовує `__SC_DELOUSE` | вхідний код архітектури |
| `__do_compat_sys_<name>` | `static inline`-тіло з вашими типами — те, що ви написали | лише сам файл |

Ключова частина — `__SC_DELOUSE`, макрос «вичесати аргумент». Загальна версія нічого не робить, крім приведення до оголошеного типу:

```c
#ifndef __SC_DELOUSE
#define __SC_DELOUSE(t,v) ((__force t)(unsigned long)(v))
#endif
```

Версія s390 перевизначає його — і робить це так, що з неї випливають два загальні правила:

```c
#define __TYPE_IS_PTR(t) (!__builtin_types_compatible_p( \
			typeof(0?(__force t)0:0ULL), u64))

#define __SC_DELOUSE(t,v) ({ \
	BUILD_BUG_ON(sizeof(t) > 4 && !__TYPE_IS_PTR(t)); \
	(__force t)(__TYPE_IS_PTR(t) ? ((v) & 0x7fffffff) : (v)); \
})
```

**Перше: кожен аргумент-покажчик компат-виклику проходить через маску сам.** Вам не треба писати жодного рядка — макрос розпізнає покажчик за типом і застосує архітектурне правило. Тому в тілі `__do_compat_sys_*` аргументи-покажчики вже придатні до вжитку.

**Друге: непокажчиковий аргумент, ширший за чотири байти, оголосити не можна.** `BUILD_BUG_ON` зупинить збірку. Це не примха s390, а сама природа 32-бітного входу: аргументи їдуть шістьма реєстрами по чотири байти, і 64-бітне значення в один із них не влазить фізично. Саме звідси беруться компат-виклики, що приймають число двома половинами, — як `_llseek`, у якого зсув у файлі розкладено на `offset_high` і `offset_low`. Добре тут те, що помилка ловиться компілятором, а не на бойовій машині.

Останній крок — реєстрація. У таблиці `arch/x86/entry/syscalls/syscall_32.tbl` рядок виклику має окрему колонку під компат-вхід: заповнена — 32-бітна таблиця веде на `compat_sys_*`, порожня — на звичайний `sys_*`. Компат-обгортку пишуть лише тим викликам, яким вона справді потрібна; для решти обидві таблиці показують на те саме тіло.

## Хто зараз викликає: `in_compat_syscall()`

```c
#ifdef CONFIG_COMPAT
#ifndef in_compat_syscall
static inline bool in_compat_syscall(void) { return is_compat_task(); }
#endif
#else /* !CONFIG_COMPAT */
#define is_compat_task() (0)
#define in_compat_syscall in_compat_syscall
static inline bool in_compat_syscall(void) { return false; }
#endif /* CONFIG_COMPAT */
```

Предикатів два, і плутати їх не варто.

| Предикат | Про що каже | Де вірний |
| --- | --- | --- |
| `is_compat_task()` | задача 32-бітна | будь-де, де є `current` |
| `in_compat_syscall()` | **поточний** виклик прийшов компат-входом | лише в контексті системного виклику |

Різниця не педантична. 64-бітна задача має повне право виконати `int 0x80` і потрапити в 32-бітну таблицю: тоді `is_compat_task()` каже «ні», `in_compat_syscall()` — «так», і правильна відповідь для того, хто зараз розбирає аргументи, — саме друга. Тому в коді, що читає дані з простору користувача, беруть `in_compat_syscall()`.

x86 перевизначає загальну реалізацію, щоб урахувати ще й x32:

```c
static inline bool in_compat_syscall(void)
{
	return in_32bit_syscall();       /* in_ia32_syscall() || in_x32_syscall() */
}
#define in_compat_syscall in_compat_syscall	/* override the generic impl */
#define compat_need_64bit_alignment_fixup in_ia32_syscall
```

Останній рядок вартий окремої уваги: `compat_need_64bit_alignment_fixup` відповідає не на питання про ширину, а на питання про розкладку — «чи треба зараз рахувати вирівнювання 64-бітних полів по чотири байти». На x86 це не те саме, що `in_compat_syscall()`: x32 має 32-бітні покажчики, але вирівнює 64-бітні поля по вісім, як рідний ABI. Підсистеми, що складають структури на льоту, питають саме цей предикат.

Найчастіша помилка з обома — питати їх не там. Робочий елемент черги, потік ядра, обробник переривання, зворотний виклик із таймера виконуються не «в чиємусь виклику», і відповідь предиката там довільна. Правило: **розрядність визначають один раз, на вході, і зберігають у власній структурі**; питати згодом уже пізно.

## Драйвер: поле `.compat_ioctl`

```c
struct file_operations {
	...
	long (*unlocked_ioctl) (struct file *, unsigned int, unsigned long);
	long (*compat_ioctl)   (struct file *, unsigned int, unsigned long);
	...
};
```

[Керуючий канал до драйвера](book:unix-linux/ioctl-interface) приймає число-команду й покажчик невідомо на що, тому централізовано перекласти його неможливо — рішення ухвалює автор драйвера. Ось повний перелік випадків.

| Що приймають ваші команди | Що ставити в `.compat_ioctl` |
| --- | --- |
| нічого (аргумент ігнорують) або покажчик на структуру з однаковою розкладкою в обох ABI | `compat_ptr_ioctl` |
| просте ціле замість покажчика | власний обробник: `compat_ptr_ioctl` зіпсував би число маскою s390 |
| структуру, що містить `long`, покажчик, `size_t`, вузький час або 64-бітне поле з іншим вирівнюванням | власний обробник, який читає компат-форму й перекладає її |
| нічого не ставити | 32-бітний процес дістане `-ENOTTY` на будь-якій команді |

Готова реалізація вміщується в чотири рядки:

```c
long compat_ptr_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
	if (!file->f_op->unlocked_ioctl)
		return -ENOIOCTLCMD;

	return file->f_op->unlocked_ioctl(file, cmd, (unsigned long)compat_ptr(arg));
}
```

Уся її робота — прогнати аргумент крізь `compat_ptr()` і віддати рідному обробникові. На всіх архітектурах, крім s390, це тотожність; існує вона саме заради s390 — і саме тому другий рядок таблиці забороняє її для цілих аргументів: маска, нешкідлива для адреси, тихо зітре старший біт числа.

> 🔧 **Навіщо це.** Ці чотири рядки таблиці — увесь ваш вибір, і ухвалюєте ви його не тоді, коли пишете `.compat_ioctl`, а раніше — коли оголошуєте структуру команди. Структура з `long` чи покажчиком усередині прирікає драйвер на власний перекладач, який доведеться супроводжувати вічно й правити щоразу, коли до команди додається поле. Структура з фіксованих типів обходиться одним готовим рядком. Різниця в зусиллях — на роки вперед, а платите ви за неї одним рішенням на початку.

Правила, за якими структура команди виходить однаковою в обох ABI:

- лише типи фіксованої ширини — `__u8`, `__u16`, `__u32`, `__u64` та знакові `__s*`; ніколи `long`, `size_t`, `time_t`, `enum` чи справжній покажчик;
- 64-бітне поле оголошувати як `__aligned_u64` — це `__u64 __attribute__((aligned(8)))` з `include/uapi/linux/types.h`; тоді воно вирівнюється по вісім в обох ABI;
- покажчик усередині структури передавати як `__aligned_u64`, а в драйвері перетворювати макросом `u64_to_user_ptr()`;
- набивку писати явно окремим полем і занулювати її, а не покладатися на компілятор.

Найкоротший робочий приклад — структура, драйвер і підключення:

```c
/* uapi-заголовок драйвера */
struct widget_cfg {
	__u32		channel;
	__u32		_pad;		/* явна набивка до межі 8 */
	__aligned_u64	window_ns;	/* вирівнювання 8 в ОБОХ ABI */
};

#define WIDGET_SET_CFG _IOW('W', 1, struct widget_cfg)

/* драйвер */
static long widget_ioctl(struct file *f, unsigned int cmd, unsigned long arg)
{
	struct widget_cfg cfg;

	if (cmd != WIDGET_SET_CFG)
		return -ENOTTY;
	if (copy_from_user(&cfg, (void __user *)arg, sizeof(cfg)))
		return -EFAULT;
	if (cfg._pad)			/* набивка мусить бути нульова */
		return -EINVAL;

	return widget_apply(&cfg);
}

static const struct file_operations widget_fops = {
	.owner		= THIS_MODULE,
	.unlocked_ioctl	= widget_ioctl,
	.compat_ioctl	= compat_ptr_ioctl,
};
```

Без `_pad` і `__aligned_u64` те саме поле `window_ns` стало б на зсув 4 у 32-бітній збірці й на зсув 8 у 64-бітній: розмір структури 12 проти 16, і драйвер читав би сміття, зміщене на чотири байти.

## x32: біт усередині номера

```c
/*
 * x32 syscall flag bit.  Some user programs expect syscall NR macros
 * and __X32_SYSCALL_BIT to have type int, even though syscall numbers
 * are, for practical purposes, unsigned long.
 */
#define __X32_SYSCALL_BIT	0x40000000
```

| Питання | Відповідь |
| --- | --- |
| Як виглядає номер x32-виклику | номер x86-64 з увімкненим бітом 30: `read` = 0 стає `0x40000000` |
| Хто його знімає | вхідний код, перш ніж індексувати таблицю: `nr & ~__X32_SYSCALL_BIT` |
| Як дізнатися зсередини ядра | `in_x32_syscall()` — читає `orig_ax` задачі й перевіряє біт |
| Де живуть виклики, яким потрібен переклад структур | окремим блоком у кінці `arch/x86/entry/syscalls/syscall_64.tbl`, позначені як `x32` |
| Що бачить seccomp | `arch` = `AUDIT_ARCH_X86_64`, а біт лишається в номері |

Останній рядок — головна пастка фільтрів на x86-64: власного значення `AUDIT_ARCH_*` у x32 немає, і за полем `arch` він не відрізняється від рідного ABI.

## Фільтр: `struct seccomp_data` і `AUDIT_ARCH_*`

```c
/**
 * struct seccomp_data - the format the BPF program executes over.
 * @nr: the system call number
 * @arch: indicates system call convention as an AUDIT_ARCH_* value
 *        as defined in <linux/audit.h>.
 * @instruction_pointer: at the time of the system call.
 * @args: up to 6 system call arguments always stored as 64-bit values
 *        regardless of the architecture.
 */
struct seccomp_data {
	int nr;
	__u32 arch;
	__u64 instruction_pointer;
	__u64 args[6];
};
```

Програма-фільтр читає це не за іменами полів, а за зсувами, тож зсуви теж є частиною контракту:

| Поле | Зсув | Ширина |
| --- | --- | --- |
| `nr` | 0 | 4 |
| `arch` | 4 | 4 |
| `instruction_pointer` | 8 | 8 |
| `args[0]` … `args[5]` | 16, 24, 32, 40, 48, 56 | по 8 |

Аргументи фільтр бачить уже розширеними до восьми байтів незалежно від ABI — тобто після того, як вхідний код звузив реєстри й свідомо доповнив старші половини. Своїх, «сирих» 32 бітів фільтр не бачить ніколи.

Значення `arch` складається з номера машини ELF і двох прапорців:

```
__AUDIT_ARCH_64BIT                   0x80000000
__AUDIT_ARCH_LE                      0x40000000
__AUDIT_ARCH_CONVENTION_MIPS64_N32   0x20000000
```

| Константа | Складники | Число |
| --- | --- | --- |
| `AUDIT_ARCH_I386` | `EM_386` (3) + LE | `0x40000003` |
| `AUDIT_ARCH_X86_64` | `EM_X86_64` (62) + 64BIT + LE | `0xC000003E` |
| `AUDIT_ARCH_ARM` | `EM_ARM` (40) + LE | `0x40000028` |
| `AUDIT_ARCH_AARCH64` | `EM_AARCH64` (183) + 64BIT + LE | `0xC00000B7` |
| `AUDIT_ARCH_S390` | `EM_S390` (22) | `0x00000016` |
| `AUDIT_ARCH_S390X` | `EM_S390` (22) + 64BIT | `0x80000016` |
| `AUDIT_ARCH_RISCV32` | `EM_RISCV` (243) + LE | `0x400000F3` |
| `AUDIT_ARCH_RISCV64` | `EM_RISCV` (243) + 64BIT + LE | `0xC00000F3` |

Звідси й форма правильного початку [фільтра системних викликів](book:unix-linux/seccomp-filtering): дві перевірки, обидві перед будь-яким номером.

```c
struct sock_filter filter[] = {
	/* 0 */ BPF_STMT(BPF_LD | BPF_W | BPF_ABS,
			 offsetof(struct seccomp_data, arch)),
	/* 1 */ BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
	/* 2 */ BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

	/* 3 */ BPF_STMT(BPF_LD | BPF_W | BPF_ABS,
			 offsetof(struct seccomp_data, nr)),
	/* 4 */ BPF_JUMP(BPF_JMP | BPF_JGE | BPF_K, __X32_SYSCALL_BIT, 0, 1),
	/* 5 */ BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

	/* 6 */ /* лише тут можна порівнювати самі номери викликів */
	        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
};
```

Числа `1, 0` та `0, 1` у переходах — це «скільки інструкцій пропустити, якщо так» і «скільки, якщо ні». Інструкція 1 пропускає повернення-вбивство, коли ABI очікуваний; інструкція 4 навпаки: номер, не менший за `0x40000000`, веде на вбивство.

Перша перевірка закриває 64-бітний процес, який виконав `int 0x80` і потрапив у 32-бітну таблицю, де ті самі номери означають інші виклики. Друга закриває x32, який має те саме значення `arch` і зсунуті номери. Фільтр, що починається одразу з номера, не робить ані першого, ані другого — і не забороняє нічого.

## Як переконатися, що структура однакова в обох ABI

Питання розв'язується компілятором, а не оглядом коду. Достатньо покласти в сам uapi-заголовок твердження про розмір і зсуви — тоді розбіжність виявиться при збірці, а не в звіті про помилку:

```c
static_assert(sizeof(struct widget_cfg) == 16);
static_assert(offsetof(struct widget_cfg, channel)   == 0);
static_assert(offsetof(struct widget_cfg, window_ns) == 8);
```

І зібрати заголовок двічі — обидві збірки мусять пройти мовчки:

```
gcc -m64 -c check.c
gcc -m32 -c check.c
```

Якщо друга падає, ви щойно зловили ту саму розбіжність зсувів, яку інакше знайшов би користувач 32-бітної програми — на роки пізніше й у значно неприємніший спосіб.
