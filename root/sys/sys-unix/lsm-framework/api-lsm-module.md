# 📋 Що саме треба оголосити модулеві LSM

Модуль безпеки не має ні конструктора, ні виклику «зареєструйте мене»: усе, чим він заявляє про себе, — це кілька статичних структур у файлі коду й пара рядків у збірці. Тут вони зібрані повністю: підписи гачків, поля `DEFINE_LSM`, `lsm_blob_sizes`, перемикачі завантаження — і наприкінці найкоротший модуль, який справді ловить дію й повертає відмову. Усе за ядром 6.12; імена й поля з роками змінюються, тож зверятися варто з деревом своєї версії.

## Де що лежить

| Файл | Що звідти беруть |
|---|---|
| `include/linux/lsm_hook_defs.h` | перелік усіх гачків: тип відповіді, типове значення, підпис |
| `include/linux/lsm_hooks.h` | `struct lsm_id`, `struct lsm_info`, `struct lsm_blob_sizes`, `LSM_HOOK_INIT`, `DEFINE_LSM` |
| `include/uapi/linux/lsm.h` | сталі `LSM_ID_*` — єдині номери модулів, видимі назовні |
| `include/linux/lsm_count.h` | `MAX_LSM_COUNT` — скільки гнізд відводить збірка |
| `security/security.c` | `security_add_hooks()`, роздача зсувів, розбір `lsm=` |
| `security/<ім'я>/` | сам модуль: `Kconfig`, `Makefile`, код |

## Підпис гачка

Кожен гачок оголошено одним рядком за сталою формою:

```c
LSM_HOOK(<тип-відповіді>, <типове-значення>, <ім'я>, <аргументи…>)
```

```c
LSM_HOOK(int, 0, ptrace_access_check, struct task_struct *child,
	 unsigned int mode)
LSM_HOOK(int, 0, capable, const struct cred *cred, struct user_namespace *ns,
	 int cap, unsigned int opts)
LSM_HOOK(void, LSM_RET_VOID, bprm_committing_creds,
	 const struct linux_binprm *bprm)
```

Друге поле — відповідь, яку каркас вважає за «нічого не сказано». Воно й ділить гачки на три роди:

| Тип і типове значення | Рід | Що повертати |
|---|---|---|
| `int`, `0` | присуд | `0` — не заперечую; від'ємний errno — відмова, і саме цей код побачить виклик у просторі користувача (`-EACCES`, `-EPERM`). Додатних значень тут не буває |
| `void`, `LSM_RET_VOID` | сповіщення | нічого; кличуть усі модулі по черзі, обірвати обхід нема чим |
| `int`, `-EOPNOTSUPP` | постачання | змістовну відповідь або типову — «мені нема чого сказати» |

Підпис вашої функції має збігатися з оголошеним дослівно. Це не побажання: розбіжність ловить компілятор, бо `LSM_HOOK_INIT` кладе вказівник у поле об'єднання, тип якого породжено з того самого рядка.

## Таблиця гачків і реєстрація

Модуль перелічує свої гачки таблицею пар «ім'я гачка — функція»:

```c
static struct security_hook_list mylsm_hooks[] __ro_after_init = {
	LSM_HOOK_INIT(socket_connect, mylsm_socket_connect),
	LSM_HOOK_INIT(file_open,      mylsm_file_open),
	LSM_HOOK_INIT(task_free,      mylsm_task_free),
};
```

`__ro_after_init` — не прикраса: ядро робить цю ділянку незаписуваною одразу після завантаження, і саме тому таблиця не годиться для чогось, що змінюють на ходу.

Віддають таблицю одним викликом:

```c
extern void security_add_hooks(struct security_hook_list *hooks, int count,
			       const struct lsm_id *lsmid);
```

Кличуть його рівно раз і тільки з `.init`: функція позначена `__init`, а гнізда статичних викликів латають лише на завантаженні. Третій аргумент — паспорт модуля:

```c
struct lsm_id {
	const char *name;
	u64 id;
};
```

`.name` — те саме ім'я, що в `CONFIG_LSM`, у `lsm=`, у `/sys/kernel/security/lsm` і в записах аудиту. `.id` — номер, яким модуль називає себе системним викликам `lsm_list_modules()` і `lsm_get_self_attr()`. Номери роздають при вливанні в дерево ядра й ніколи не перенумеровують: `LSM_ID_CAPABILITY` 100, `SELINUX` 101, `SMACK` 102, `TOMOYO` 103, `APPARMOR` 104, `YAMA` 105, `LOADPIN` 106, `SAFESETID` 107, `LOCKDOWN` 108, `BPF` 109, `LANDLOCK` 110, `IMA` 111, `EVM` 112, `IPE` 113. Стороннього модуля в переліку немає — він живе з `LSM_ID_UNDEF` (0) і тим викликам просто не видний.

## Поля DEFINE_LSM

`DEFINE_LSM(ім'я) = { … }` заповнює одну структуру й кладе її в секцію `.lsm_info.init`:

```c
struct lsm_info {
	const char *name;	/* Required. */
	enum lsm_order order;	/* Optional: default is LSM_ORDER_MUTABLE */
	unsigned long flags;	/* Optional: flags describing LSM */
	int *enabled;		/* Optional: controlled by CONFIG_LSM */
	int (*init)(void);	/* Required. */
	struct lsm_blob_sizes *blobs; /* Optional: for blob sharing. */
};
```

| Поле | Обов'язкове | Значення |
|---|---|---|
| `.name` | так | ім'я модуля в усіх переліках і рядках порядку |
| `.init` | так | єдина точка входу; каркас кличе її раз, у порядку черги. Повертає `0` або від'ємний errno |
| `.order` | ні | `LSM_ORDER_MUTABLE` (0) типово; `LSM_ORDER_FIRST` (−1) віддано `capability`, `LSM_ORDER_LAST` (1) — підсистемі цілісності. Свій модуль лишає типове |
| `.flags` | ні | `LSM_FLAG_EXCLUSIVE` — «зі мною поруч інший виключний не піде»; `LSM_FLAG_LEGACY_MAJOR` — «мене можна назвати старим `security=`» |
| `.enabled` | ні | вказівник на власний `int`-вимикач модуля |
| `.blobs` | ні | апетит на пам'ять при об'єктах |

З `.enabled` є тонкість, через яку його часто ставлять дарма. Якщо поле порожнє, каркас сам підставить туди вказівник на свою сталу `true` чи `false` — залежно від того, чи потрапив модуль у чергу. Власний `int` потрібен лише тоді, коли в модуля є ще й свій перемикач у командному рядку (`selinux=0`, `apparmor=0`): тоді той самий байт бачать і параметр, і каркас.

Є ще `DEFINE_EARLY_LSM()` — та сама структура, але в секцію `.early_lsm_info.init`. Такі модулі каркас піднімає ще раніше за звичайні, до того, як запрацював розподільник пам'яті; поза підсистемою цілісності це майже нікому не потрібно. Обидві секції формує компонувальник, тож і черга кандидатів існує вже в образі ядра — розкладка [ініціалізації підсистем](root:sys-unix/kernel-initcalls) тут ні до чого.

## Скільки просити пам'яті й як її дістати

Апетит оголошують однією структурою, по полю на рід об'єкта:

```c
struct lsm_blob_sizes {
	int lbs_cred;		/* struct cred — облікові дані */
	int lbs_file;		/* struct file — відкритий опис файлу */
	int lbs_ib;		/* об'єкти InfiniBand */
	int lbs_inode;		/* struct inode */
	int lbs_sock;		/* struct sock — сокет із боку ядра */
	int lbs_superblock;	/* змонтована файлова система */
	int lbs_ipc;		/* об'єкт System V IPC */
	int lbs_key;		/* ключ у зв'язці ядра */
	int lbs_msg_msg;	/* окреме повідомлення черги */
	int lbs_perf_event;	/* подія perf */
	int lbs_task;		/* struct task_struct */
	int lbs_xattr_count;	/* НЕ байти — кількість комірок під xattr */
	int lbs_tun_dev;	/* пристрій TUN/TAP */
	int lbs_bdev;		/* блоковий пристрій */
};
```

Найважливіше в цій структурі — не поля, а те, що каркас робить із ними на завантаженні:

```c
static void __init lsm_set_blob_size(int *need, int *lbs)
{
	int offset;

	if (*need <= 0)
		return;

	offset = ALIGN(*lbs, sizeof(void *));
	*lbs = offset + *need;
	*need = offset;
}
```

Останній рядок і є весь контракт: **поле, куди ви записали потрібний розмір, каркас перезаписує вашим зсувом**. До ініціалізації там байти, після неї — адреса всередині спільного шматка. Тому доступ до своїх даних завжди має один вигляд:

```c
static inline struct demolsm_task *demolsm_task(const struct task_struct *t)
{
	return t->security + demolsm_blob_sizes.lbs_task;
}
```

Три речі, про які мовчить сама структура:

- Структура апетиту має бути `__ro_after_init` — після роздачі зсувів вона стає таблицею адрес, і запис у неї означав би зсув чужих даних під ногами.
- Поле, залишене нулем, пам'яті не дає, а зсув у ньому лишається нулем — читання «за своїм зсувом» мовчки віддасть чужі байти. Не просили — не читайте.
- Блоб інода перед першим модулем дістає ще й `sizeof(struct rcu_head)`: інод звільняють відкладено, [через RCU](root:sys-unix/rcu-read-copy-update), і місце під службовий заголовок каркас відрізає собі сам. А `lbs_xattr_count` рахує не байти, а комірки в масиві [розширених атрибутів](root:sys-unix/acl-and-xattr), які модуль хоче покласти на щойно створений файл; зсув там теж у комірках.

## Перемикачі завантаження

| Перемикач | Де задають | Що робить |
|---|---|---|
| `CONFIG_LSM="…"` | збірка, `security/Kconfig` | черга типово, вшита в образ |
| `lsm=…` | [командний рядок ядра](root:sys-unix/bootloader-and-cmdline) | заміняє список **цілком** |
| `security=<ім'я>` | командний рядок | старий спосіб: вимикає всі інші модулі з `LSM_FLAG_LEGACY_MAJOR`, черги не міняє |
| `lsm.debug` | командний рядок | друкує в журнал старту, як складалася черга і кого відсіяли |
| `selinux=0`, `apparmor=0`, … | командний рядок | власний вимикач модуля крізь `.enabled` |
| `/sys/kernel/security/lsm` | читання на живій системі | підсумкова черга в порядку обходу |

Типове значення в 6.12, коли дистрибутив нічого не обрав:

```
landlock,lockdown,yama,loadpin,safesetid,selinux,smack,tomoyo,apparmor,ipe,bpf
```

Два правила поверх списку. Модулі з `LSM_ORDER_FIRST` і `LSM_ORDER_LAST` працюють завжди, якщо зібрані, — у списку їх шукати не треба. Модуль, якого в списку немає, не вимикається якось особливо: його `.init` просто ніколи не кличуть.

## Найкоротший модуль, який справді працює

Три файли в `security/demolsm/`. Спершу сам код — один обмежувальний гачок, який забороняє непривілейованим процесам вихідні з'єднання:

```c
// security/demolsm/demolsm.c
// SPDX-License-Identifier: GPL-2.0
#define pr_fmt(fmt) "demolsm: " fmt

#include <linux/cred.h>
#include <linux/lsm_hooks.h>
#include <linux/net.h>
#include <linux/sched.h>
#include <linux/socket.h>
#include <uapi/linux/lsm.h>

static int demolsm_socket_connect(struct socket *sock,
				  struct sockaddr *address, int addrlen)
{
	if (address->sa_family != AF_INET && address->sa_family != AF_INET6)
		return 0;
	if (uid_eq(current_euid(), GLOBAL_ROOT_UID))
		return 0;

	pr_info("connect заборонено, pid %d\n", current->pid);
	return -EPERM;
}

static struct security_hook_list demolsm_hooks[] __ro_after_init = {
	LSM_HOOK_INIT(socket_connect, demolsm_socket_connect),
};

static const struct lsm_id demolsm_lsmid = {
	.name = "demolsm",
	.id   = LSM_ID_UNDEF,	/* свій номер дають лише при вливанні в дерево */
};

static int __init demolsm_init(void)
{
	security_add_hooks(demolsm_hooks, ARRAY_SIZE(demolsm_hooks),
			   &demolsm_lsmid);
	pr_info("піднято\n");
	return 0;
}

DEFINE_LSM(demolsm) = {
	.name = "demolsm",
	.init = demolsm_init,
};
```

```makefile
# security/demolsm/Makefile
# SPDX-License-Identifier: GPL-2.0
obj-$(CONFIG_SECURITY_DEMOLSM) += demolsm.o
```

```
# security/demolsm/Kconfig
config SECURITY_DEMOLSM
	bool "Demo LSM: заборона вихідних з'єднань непривілейованим"
	depends on SECURITY && NET
	default n
```

Далі — чотири правки поза текою модуля. Дві очевидні: `source "security/demolsm/Kconfig"` до `security/Kconfig` і `obj-$(CONFIG_SECURITY_DEMOLSM) += demolsm/` до `security/Makefile`. Третя — ім'я модуля в `CONFIG_LSM`, інакше `.init` ніхто не покличе.

Четверта неочевидна, і без неї ядро впаде на завантаженні. Від 6.12 гнізда під гачки виділяють на збірці, а їхню кількість рахує препроцесор за жорстким переліком відомих модулів у `include/linux/lsm_count.h`. Про сторонній модуль там нічого не знають, гнізда закінчаться, і `lsm_static_call_init()` завершиться панікою про вичерпані гнізда під гачки. Тож у той файл треба дописати свій блок за спільним зразком і додати `DEMOLSM_ENABLED` до переліку в `MAX_LSM_COUNT`:

```c
#if IS_ENABLED(CONFIG_SECURITY_DEMOLSM)
#define DEMOLSM_ENABLED 1,
#else
#define DEMOLSM_ENABLED
#endif
```

Далі [збирають ядро](root:sys-unix/kernel-config-and-build) як звичайно й перевіряють:

```
$ cat /sys/kernel/security/lsm
capability,demolsm

$ curl -sS http://127.0.0.1/
curl: (7) Failed to connect: Operation not permitted

$ sudo dmesg | tail -1
demolsm: connect заборонено, pid 3412
```

Якщо в першому рядку модуля немає — далі шукати марно. Причин рівно три: імені немає в черзі, `.init` повернув помилку, або модуль вимкнено виключністю; котра саме — покаже завантаження з `lsm.debug`.

## Найчастіші помилки

| Симптом | Причина |
|---|---|
| паніка на завантаженні: гнізда під гачки вичерпано | свій `CONFIG_` не додано до `lsm_count.h` |
| `panic: Too many LSMs registered.` | той самий недорахунок, але вперся в `MAX_LSM_COUNT` уже в `security_add_hooks()` |
| модуля немає в `/sys/kernel/security/lsm` | імені немає в `CONFIG_LSM` чи `lsm=`, або витіснив виключний |
| у блобі сміття | поле апетиту лишили нулем, а читають за ним як за зсувом |
| гачок ніколи не спрацьовує | попередній у черзі вже відмовив, або класична перевірка відмовила ще до гачка |
| помилка компіляції в `LSM_HOOK_INIT` | підпис функції розійшовся з `lsm_hook_defs.h` |
