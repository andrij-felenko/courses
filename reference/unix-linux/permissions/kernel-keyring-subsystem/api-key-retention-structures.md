# 📋 Структури даних та системний інтерфейс Kernel Keyring

Ця довідкова вставка містить точний виклад внутрішніх структур даних ядра Linux, масок привілеїв `key_perm_t`, хуків мандатного контролю безпеки LSM, сигнатур системних викликів та параметрів квотування `sysctl`, необхідних для поглибленого розбору розробки підситем безпеки та взаємодії з Kernel Key Retention Service.

## 1. Внутрішні структури даних ядра (`include/linux/key.h`)

Усі об'єкти ключів у ядрі представляються структурою `struct key`. Вона тримає метадані ключа, маску прав, ліміти ресурсів та вказівники на тип і корисне навантаження. Кожен екземпляр аллокується у виділеному кеші ядра slab (`key_jar`) і керується за допомогою підрахунку посилань `refcount_t`.

```c
struct key {
	refcount_t		usage;		/* Лічильник посилань на об'єкт (RCU/atomic) */
	key_serial_t		serial;		/* 32-бітний унікальний додатний ідентифікатор */
	union {
		struct list_head list_link;
		struct assoc_array_ptr *net_node;
	};
	struct key_type		*type;		/* Вказівник на таблицю методів типу ключа */
	struct rw_semaphore	sem;		/* Семафор блокування читання/запису */
	struct key_user		*user;		/* Структура обліку квот пам'яті за UID */
	void			*security;	/* Вказівник на контекст безпеки LSM (SELinux/AppArmor) */
	
	time64_t		expiry;		/* Абсолютний час закінчення дії (0 = безлімітно) */
	time64_t		last_used;	/* Час останнього звернення до ключа */
	
	kuid_t			uid;		/* UID користувача-власника */
	kgid_t			gid;		/* GID групи-власника */
	key_perm_t		perm;		/* 32-бітна маска прав доступу */
	unsigned short		quaitas;	/* Розмір об'єкта в квотах кількості */
	unsigned short		datalen;	/* Довжина корисного навантаження в байтах */
	
	unsigned long		flags;		/* Прапорці стану (KEY_FLAG_REVOKED, KEY_FLAG_DEAD) */
	
	char			*description;	/* Пошуковий текстовий опис (тег) ключа */
	
	union {
		union key_payload payload;	/* Симетричний/асиметричний секретний payload */
		struct assoc_array keys;	/* Дерево посилань на інші ключі (для keyring) */
	};
};
```

Поле `usage` забезпечує безперешкодний RCU-доступ (Read-Copy-Update) під час рекурсивного пошуку ключів у в'язках без захоплення локів на читання. Поле `sem` застосовується лише під час операцій оновлення (`update`) чи анулювання (`revoke`), запобігаючи гонитві даних (data races) між паралельними потоками простору користувача.

Для обліку ресурсоємності та квот пам'яті ядро веде структуру `struct key_user` для кожного UID. Вона зберігається у глобальному червоно-чорному дереві `key_user_tree` ядра під захистом спінлока:

```c
struct key_user {
	struct rb_node		node;
	refcount_t		usage;		/* Кількість утримань даної структури */
	atomic_t		nkeys;		/* Кількість створених ключів цим UID */
	atomic_t		nikeys;		/* Кількість активних ініційованих ключів */
	atomic_t		qnkeys;		/* Кількість ключів, що зараховані в квоту */
	atomic_t		qnbytes;	/* Загальний обсяг байтів payload у квоті */
	kuid_t			uid;		/* Ідентифікатор користувача */
};
```

При додаванні нового ключа ядро виконує атомарні операції `atomic_inc(&user->qnkeys)` та `atomic_add(datalen, &user->qnbytes)`. Якщо підсумкові значення перевищують межу `maxkeys` або `maxbytes`, виклик скасовується і повертає помилку `-EDQUOT`.

Поведінка окремих типів ключів описується структурою `struct key_type`. Кожен новий тип ключів у ядрі реєструється через функцію `register_key_type()` під час ініціалізації відповідного драйвера:

```c
struct key_type {
	const char *name;			/* Унікальна назва типу ("user", "logon", "keyring") */
	size_t def_datalen;			/* Розмір payload за замовчуванням */

	/* Методи життєвого циклу */
	int (*preparse)(struct key_preparsed_payload *prep);
	void (*free_preparse)(struct key_preparsed_payload *prep);
	int (*instantiate)(struct key *key, struct key_preparsed_payload *prep);
	int (*update)(struct key *key, struct key_preparsed_payload *prep);
	void (*revoke)(struct key *key);
	void (*destroy)(struct key *key);

	/* Методи пошуку, відображення та зчитання */
	void (*describe)(const struct key *key, struct seq_file *m);
	long (*read)(const struct key *key, char *buffer, size_t buflen);
};
```

Метод `preparse()` перевіряє коректність бінарного формату даних перед виділенням структури `struct key`. Якщо формат хибний, ядро скасовує алокацію без зміни квот користувача. Метод `read()` визначає, чи підтримує даний тип зчитування payload у користувацький буфер (наприклад, у `key_type_logon` цей вказівник дорівнює `NULL`, що унеможливлює витік секрету у user-space).

---

## 2. Маска прав доступу `key_perm_t` та константи

Права доступу до ключа кодуються 32-бітним цілим числом `key_perm_t`, що складається з чотирьох 8-бітних категорій (Possessor, User, Group, Other). Кожна категорія містить 6 бітових прапорів дій.

```text
31        24 23        16 15         8 7          0
+-----------+-----------+-----------+-----------+
| Possessor |   User    |   Group   |   Other   |
+-----------+-----------+-----------+-----------+
```

Розбиття системних бітових констант ядра (`include/linux/key.h`):

```c
/* Права володільця (Possessor) */
#define KEY_POS_VIEW	0x01000000	/* Перегляд метаданих та опису */
#define KEY_POS_READ	0x02000000	/* Зчитання корисного навантаження */
#define KEY_POS_WRITE	0x04000000	/* Оновлення або зміна вмісту */
#define KEY_POS_SEARCH	0x08000000	/* Пошук та прохід крізь в'язку */
#define KEY_POS_LINK	0x10000000	/* Прив'язка до іншої в'язки */
#define KEY_POS_SETATTR	0x20000000	/* Зміна UID/GID, маски прав та expiry */
#define KEY_POS_ALL	0x3f000000	/* Усі маски володільця */

/* Права власника (UID) */
#define KEY_USR_VIEW	0x00010000
#define KEY_USR_READ	0x00020000
#define KEY_USR_WRITE	0x00040000
#define KEY_USR_SEARCH	0x00080000
#define KEY_USR_LINK	0x00100000
#define KEY_USR_SETATTR	0x00200000
#define KEY_USR_ALL	0x003f0000

/* Права групи (GID) */
#define KEY_GRP_VIEW	0x00000100
#define KEY_GRP_READ	0x00000200
#define KEY_GRP_WRITE	0x00000400
#define KEY_GRP_SEARCH	0x00000800
#define KEY_GRP_LINK	0x00001000
#define KEY_GRP_SETATTR	0x00002000
#define KEY_GRP_ALL	0x00003f00

/* Права інших процесів (Other) */
#define KEY_OTH_VIEW	0x00000001
#define KEY_OTH_READ	0x00000002
#define KEY_OTH_WRITE	0x00000004
#define KEY_OTH_SEARCH	0x00000008
#define KEY_OTH_LINK	0x00000010
#define KEY_OTH_SETATTR	0x00000020
#define KEY_OTH_ALL	0x0000003f
```

Під час розрахунку дозволів функція `key_task_permission()` перевіряє статус володіння. Якщо ключ досяжний з кілець нитки, процесу чи сесії, привілеї `KEY_POS_*` поєднуються за допомогою побітового АБО (`|`) з відповідними правами категорій `KEY_USR_*`, `KEY_GRP_*` або `KEY_OTH_*`. Якщо результат побітового І (`&`) із запрошеною маскою не дорівнює нулю, перевірка DAC вважається успішною.

---

## 3. Хуки безпеки LSM (Linux Security Modules)

Окрім перевірки маски `key_perm_t`, ядро виконує розмежування доступу через підсистему LSM (`include/linux/lsm_hooks.h`). Це дозволяє мандатним підсистемам SELinux, AppArmor та Smack накладати додаткові обмеження на основі міток безпеки процесів та ключів.

Основні інтерфейсні хуки:
- `int security_key_alloc(struct key *key, const struct cred *cred, unsigned long flags);` — Викликається під час алокації ключа для створення непрозорого контексту безпеки `key->security` та привласнення метки SELinux/AppArmor на основі облікових даних `cred`.
- `void security_key_free(struct key *key);` — Викликається при вивантаженні `struct key` для звільнення пам'яті структури `key->security`.
- `int security_key_permission(key_ref_t key_ref, const struct cred *cred, enum key_need_perm need_perm);` — Викликається перед кожною операцією над ключем. Перевіряє, чи дозволяє активна мандатна політика даному суб'єкту `cred` здійснювати дію `need_perm` над об'єктом ключа.
- `int security_key_getsecurity(struct key *key, char **_buffer);` — Експортує текстове представлення контексту безпеки ключа у простір користувача (наприклад, `system_u:object_r:user_key_t:s0`).

При блокуванні операції мандатним контролем LSM системний виклик повертає помилку `-EACCES`, а у системний аудит `auditd` записується відповідне повідомлення про порушення мандатної політики.

---

## 4. Системні виклики та коди операцій `keyctl`

Інтерфейс взаємодії між користувацьким простором та ядром реалізовано через три системні виклики: `add_key()`, `request_key()` та `keyctl()`.

### `add_key()`

Під час виклику системної функції додавання ключа ядро виконує послідовну процедуру перевірки квот, пошуку та ініціалізації об'єкта `struct key`:
1. **Пошук цільової в'язки:** Ядро знаходить уповноважену в'язку за її `keyring_id` та перевіряє дозвіл `KEY_POS_WRITE` або `KEY_USR_WRITE` у поточного процесу.
2. **Пошук наявного ключа:** У цільовій в'язці здійснюється пошук ключа з однаковим типом `type` та описом `description`. Якщо такий ключ існує і його тип підтримує метод `update()`, ядро перевіряє нові дані через `preparse()`, оновлює payload під блокуванням `key->sem` та коригує квоту `qnbytes` у `struct key_user`.
3. **Аллокація та ініціалізація нового ключа:** Якщо ключ відсутній, ядро перевіряє ліміти `maxkeys` та `maxbytes` для UID. При дотриманні квот виділяється структура `struct key` із кешу `key_jar`, їй присвоюється унікальний 32-бітний `key_serial_t`, викликаються методи `preparse()` та `instantiate()`, створюється контекст безпеки LSM через `security_key_alloc()`, після чого посилання додається у дерево в'язки.

Сигнатура системного виклику:

```c
key_serial_t add_key(const char *type,
                     const char *description,
                     const void *payload,
                     size_t plen,
                     key_serial_t keyring_id);
```

### `request_key()`

Механізм запиту ключа поєднує рекурсивний пошук у просторі ядра та динамічний виклик у простір користувача:
1. **Ієрархічний пошук у ядрі:** Ядро виконує послідовний обхід приєднаних в'язок процесу — нитки (`@t`), процесу (`@p`), сесії (`@s`) та користувача (`@u`/`@us`). Для кожної в'язки перевіряється дозвіл `Search`. Якщо готовий та ініціалізований ключ знайдено, ядро збільшує лічильник `usage` і повертає його серійний номер.
2. **Ініціація Upcall:** Якщо ключ не знайдено і параметр `callout_info` не дорівнює `NULL`, ядро створює тимчасовий неініціалізований ключ у `dest_keyring` та переходить у режим очікування. За допомогою механізму `call_usermodehelper` ядро запускає процес простору користувача `/sbin/request-key`.
3. **Заповнення секрету:** Користувацький помічник отримує повноваження через `KEYCTL_ASSUME_AUTHORITY`, отримує або згенеровує секретний payload і викликає `KEYCTL_INSTANTIATE` (або `KEYCTL_REJECT` при помилці), що розблоковує заснулий системний виклик `request_key()`.

Сигнатура системного виклику:

```c
key_serial_t request_key(const char *type,
                         const char *description,
                         const char *callout_info,
                         key_serial_t dest_keyring);
```

### `keyctl()`

Системний виклик `keyctl()` діє як єдиний мультиплексований інтерфейс керування ключами ядра. Механізм його диспетчеризації працює так:
1. **Дешифрування коду операції:** Диспетчер ядра `sys_keyctl()` приймає перший аргумент `operation` і перевіряє його за таблицею допустимих команд керування.
2. **Розпакування аргументів та авторизація:** Залежно від коду `operation` ядро зчитує змінні позиційні параметри (ідентифікатори ключів, буфери payload, маски прав `key_perm_t` чи таймаути), знаходить відповідні об'єкти `struct key` в RCU-дереві та перевіряє привілеї через `key_task_permission()` та LSM-хук `security_key_permission()`.
3. **Маршрутизація до обробника:** Диспетчер передає виконання конкретній внутрішній функції підсистеми (наприклад, `keyctl_update_key()`, `keyctl_revoke_key()`, `keyctl_read_key()` або `keyctl_set_timeout()`), повертаючи результат або код помилки у простір користувача.

Сигнатура системного виклику:

```c
long keyctl(int operation, ...);
```

Список стандартних констант операцій `operation` (`include/uapi/linux/keyctl.h`):

```c
#define KEYCTL_GET_KEYRING_ID		0	/* Повернути ID спеціальної в'язки */
#define KEYCTL_JOIN_SESSION_KEYRING	1	/* Створити або приєднатися до сесійної в'язки */
#define KEYCTL_UPDATE			2	/* Оновити payload ключа */
#define KEYCTL_REVOKE			3	/* Анулювати ключ */
#define KEYCTL_CHOWN			4	/* Змінити власника UID/GID */
#define KEYCTL_SETPERM			5	/* Змінити маску key_perm_t */
#define KEYCTL_DESCRIBE			6	/* Зчитати текстовий опис ключа */
#define KEYCTL_CLEAR			7	/* Очистити вміст в'язки */
#define KEYCTL_LINK			8	/* Прив'язати ключ до в'язки */
#define KEYCTL_UNLINK			9	/* Видалити посилання з в'язки */
#define KEYCTL_SEARCH			10	/* Пошук ключа у в'язках */
#define KEYCTL_READ			11	/* Зчитати payload у буфер */
#define KEYCTL_INSTANTIATE		12	/* Ініціалізувати ключ під час upcall */
#define KEYCTL_NEGATE			13	/* Відхилити створення ключа в upcall */
#define KEYCTL_SETPTR_TIMEOUT		14	/* Встановити таймер згасання (TTL у секундах) */
#define KEYCTL_ASSUME_AUTHORITY		15	/* Встановити повноваження ініціалізації upcall */
#define KEYCTL_GET_SECURITY		17	/* Отримати текстову мітку LSM */
#define KEYCTL_INVALIDATE		21	/* Негайно знищити ключ з пам'яті */
#define KEYCTL_RESTRICT_KEYRING		29	/* Встановити обмеження на додавання ключів до в'язки */
```

---

## 5. Системні квоти та помилки системних викликів

Керування ресурсами оперативної пам'яті ядра здійснюється через інтерфейси `sysctl` у каталозі `/proc/sys/kernel/keys/`:

| Файл у `sysctl` | Значення | Опис |
| :--- | :--- | :--- |
| `maxkeys` | `200` | Максимальна кількість ключів для одного ненульового UID |
| `maxbytes` | `20000` | Максимальний обсяг байтів payload для одного ненульового UID |
| `root_maxkeys` | `1000000` | Максимальна кількість ключів для UID 0 (root) |
| `root_maxbytes` | `25000000` | Максимальний обсяг байтів payload для UID 0 (root) |

Типові коди помилок системних викликів підсистеми ключів (`errno`):

- **`-ENOKEY`:** Ключ не знайдено або до нього немає доступу `Search`.
- **`-EKEYREVOKED`:** Ключ було анульовано операцією `KEYCTL_REVOKE`.
- **`-EKEYEXPIRED`:** Термін дії ключа вичерпано (`expiry` в минулому).
- **`-EKEYREJECTED`:** Ключ було позначено як відхилений під час upcall.
- **`-EDQUOT`:** Перевищено системну квоту `maxkeys` або `maxbytes` для даного UID.
- **`-EACCES`:** Відмовлено в доступі на рівні маски прав `key_perm_t` або мандатної політики LSM.
- **`-EOPNOTSUPP`:** Операція не підтримується для даного типу ключа (наприклад, спроба зчитати `logon` ключ).
