# 📋 Довідник структур та функцій API підсистеми I²C/SMBus

Підсистема I²C та SMBus ядра Linux визначає чіткий набір структур даних, прапорців функціональності, допоміжних функцій життєвого циклу та системних викликів. Усі вони зосереджені в системних заголовних файлах ядра `include/linux/i2c.h`, `include/linux/i2c-smbus.h`, `include/uapi/linux/i2c.h` та `include/uapi/linux/i2c-dev.h`. Цей довідник систематизує внутрішній програмний інтерфейс ядра для розробників драйверів хост-контролерів та клієнтських мікросхем, а також користувацький інтерфейс керування через символьні пристрої `/dev/i2c-N`.

## 1. Головні структури ядра для драйверів

### 1.1. `struct i2c_adapter` — представлення хост-контролера шини

Структура `struct i2c_adapter` інкапсулює окремий фізичний контролер шини I²C/SMBus (апаратний блок SoC, PCI-хост або програмний GPIO bit-banging):

```c
struct i2c_adapter {
	struct module *owner;
	unsigned int class;
	const struct i2c_algorithm *algo;
	void *algo_data;

	const struct i2c_lock_operations *lock_ops;
	struct rt_mutex bus_lock;
	struct rt_mutex mux_lock;

	int timeout;
	int retries;
	struct device dev;

	int nr;
	char name[48];
	struct completion dev_released;

	struct mutex userspace_clients_lock;
	struct list_head userspace_clients;

	struct i2c_bus_recovery_info *bus_recovery_info;
	const struct i2c_adapter_quirks *quirks;
};
```

Призначення ключових полів:
- `algo` — вказівник на таблицю операцій низькорівневої передачі даних між процесором та шиною.
- `nr` — числовий індекс шини в системі. Він визначає назву символьного вузла `/dev/i2c-nr` та шлях у дереві sysfs `/sys/bus/i2c/devices/i2c-nr`.
- `bus_lock` — м'ютекс взаємного виключення, що гарантує неподільність складних складених транзакцій та виключає стан гонитви між різними клієнтами на одній шині.
- `timeout` — граничний час очікування відповіді апаратного контролера у системних квантах часу (джифісах).
- `retries` — кількість повторних апаратних спроб виконання транзакції при отриманні негативного підтвердження NACK від веденого пристрою.
- `bus_recovery_info` — структура з колбеками відновлення застряглої шини шляхом примусової зміни стану пінів та генерації імпульсів тактування.
- `quirks` — опис апаратних обмежень контролера (максимальна довжина одного повідомлення, заборона Repeated START тощо).

### 1.2. `struct i2c_algorithm` — таблиця методів доступу до шини

Визначає механізми фізичної передачі бітів лініями шини:

```c
struct i2c_algorithm {
	int (*master_xfer)(struct i2c_adapter *adap, struct i2c_msg *msgs,
			   int num);
	int (*master_xfer_atomic)(struct i2c_adapter *adap,
				  struct i2c_msg *msgs, int num);
	int (*smbus_xfer)(struct i2c_adapter *adap, u16 addr,
			  unsigned short flags, char read_write,
			  u8 command, int size, union i2c_smbus_data *data);
	int (*smbus_xfer_atomic)(struct i2c_adapter *adap, u16 addr,
				 unsigned short flags, char read_write,
				 u8 command, int size, union i2c_smbus_data *data);
	u32 (*functionality)(struct i2c_adapter *adap);
	int (*reg_slave)(struct i2c_client *client);
	int (*unreg_slave)(struct i2c_client *client);
};
```

Опис методів:
- `master_xfer` — передача масиву сирих транзакцій I²C `struct i2c_msg`. Повертає кількість успішно переданих повідомлень або від'ємний код помилки (`-EIO`, `-ENXIO`, `-ETIMEDOUT`).
- `master_xfer_atomic` — неблокуючий варіант передачі для контекстів із вимкненими перериваннями (під час збереження дампа panic або аварійного перезавантаження).
- `smbus_xfer` — виконання апаратної команди SMBus (використовується контролерами, які не вміють генерувати довільні I²C-послідовності, зокрема чипсетами Intel PCH/i801).
- `functionality` — повертає бітову маску можливостей шини (`I2C_FUNC_*`).
- `reg_slave` / `unreg_slave` — реєстрація локального процесора як веденого пристрою на шині (I2C Target/Slave mode).

### 1.3. `struct i2c_client` — опис підключеного пристрою

Представляє конкретну мікросхему, підключену до шини:

```c
struct i2c_client {
	unsigned short flags;
	unsigned short addr;
	char name[I2C_NAME_SIZE];
	struct i2c_adapter *adapter;
	struct device dev;
	int init_irq;
	int irq;
	struct list_head detected;
};
```

Ключові поля:
- `addr` — 7-бітна (або 10-бітна) адреса пристрою на шині без урахування біта R/W (наприклад, `0x68` для годинника RTC, `0x76` для датчика тиску).
- `flags` — бітові прапорці стану (`I2C_CLIENT_TEN` для 10-бітної адреси, `I2C_CLIENT_PEC` для контролю помилок SMBus PEC, `I2C_CLIENT_SLAVE` для режиму веденого).
- `adapter` — вказівник на адаптер шини, до якої фізично приєднано мікросхему.
- `irq` — номер системного переривання, призначеного лінії тривоги чи готовності сенсора.
- `dev` — вбудований об'єкт базової моделі пристроїв Linux.

### 1.4. `struct i2c_driver` — драйвер класу пристроїв

Визначає програмну логіку керування пристроєм:

```c
struct i2c_driver {
	unsigned int class;
	int (*probe)(struct i2c_client *client);
	void (*remove)(struct i2c_client *client);
	void (*shutdown)(struct i2c_client *client);
	void (*alert)(struct i2c_client *client, enum i2c_alert_protocol protocol,
		      unsigned int data);

	int (*detect)(struct i2c_client *client, struct i2c_board_info *info);
	const unsigned short *address_list;
	struct list_head clients;

	struct device_driver driver;
	const struct i2c_device_id *id_table;
};
```

Опис елементів:
- `probe` — вызывается ядром під час успішного збігу пристрою та драйвера для налаштування регістрів та реєстрації в спеціалізованих підсистемах (`hwmon`, `iio`, `input`, `rtc`).
- `remove` — викликається при відключенні пристрою або вивантаженні модуля для звільнення виділених пам'яті та ліній IRQ.
- `driver.of_match_table` — таблиця збігу з вузлами дерева пристроїв Device Tree (`struct of_device_id`).
- `driver.acpi_match_table` — таблиця збігу з об'єктами таблиць ACPI DSDT/SSDT (`struct acpi_device_id`).
- `id_table` — таблиця текстових ідентифікаторів пристроїв (`struct i2c_device_id`).
- `detect` та `address_list` — інфраструктура автовиявлення мікросхем шляхом послідовного зондування адрес.

### 1.5. `struct i2c_bus_recovery_info` — конфігурація відновлення шини

Описує механізм виведення шини зі стану аварійного блокування:

```c
struct i2c_bus_recovery_info {
	int (*recover_bus)(struct i2c_adapter *adap);
	int (*get_scl)(struct i2c_adapter *adap);
	void (*set_scl)(struct i2c_adapter *adap, int val);
	int (*get_sda)(struct i2c_adapter *adap);
	void (*set_sda)(struct i2c_adapter *adap, int val);
	int (*get_bus_free)(struct i2c_adapter *adap);
	void (*prepare_recovery)(struct i2c_adapter *adap);
	void (*unprepare_recovery)(struct i2c_adapter *adap);
	struct pinctrl *pinctrl;
	struct pinctrl_state *pins_default;
	struct pinctrl_state *pins_gpio;
};
```

- `prepare_recovery` — перемикає функціональні виводи SoC з апаратного контролера I²C у режим GPIO через підсистему `pinctrl`.
- `set_scl` / `get_sda` — функції маніпуляції лініями для надсилання 9 тактів SCL з метою вивільнення застряглого біта SDA.
- `unprepare_recovery` — повертає виводи SoC у вихідний стан апаратного контролера.

---

## 2. Функції життєвого циклу підсистеми

### 2.1. Реєстрація адаптерів та драйверів

- `int i2c_add_adapter(struct i2c_adapter *adap)`  
  Реєструє хост-контролер шини в ядрі з динамічним виділенням наступного вільного номера `nr`.
- `int i2c_add_numbered_adapter(struct i2c_adapter *adap)`  
  Реєструє контролер зі строго фіксованим номером `adap->nr`, заданим конфігурацією платформи або аліасом у Device Tree.
- `void i2c_del_adapter(struct i2c_adapter *adap)`  
  Видаляє адаптер шини, автоматично звільняючи всі підключені до нього дочірні клієнтські пристрої `i2c_client`.
- `int i2c_register_driver(struct module *owner, struct i2c_driver *driver)`  
  Реєструє драйвер пристрою в підсистемі та запускає перевірку наявності відповідних клієнтів на всіх зареєстрованих шинах.
- `void i2c_del_driver(struct i2c_driver *driver)`  
  Видаляє драйвер, попередньо викликаючи метод `remove()` для кожного зв'язаного з ним пристрою.
- `module_i2c_driver(driver_struct)`  
  Допоміжний макрос, який розгортається у стандартні функції ініціалізації та виходу модуля (`module_init` та `module_exit`).

### 2.2. Інстанціювання клієнтських пристроїв

- `struct i2c_client *i2c_new_client_device(struct i2c_adapter *adap, struct i2c_board_info const *info)`  
  Створює, ініціалізує та реєструє новий об'єкт `struct i2c_client` на вказаному адаптері.
- `void i2c_unregister_device(struct i2c_client *client)`  
  Видаляє раніше створений клієнтський пристрій із системи.
- `struct i2c_client *devm_i2c_new_dummy_device(struct device *dev, struct i2c_adapter *adap, u16 address)`  
  Створює фіктивний (dummy) клієнтський пристрій для мікросхем, що займають декілька послідовних I²C-адрес (наприклад, багатосторінкові EEPROM), із автоматичним керуванням життєвим циклом через підсистему `devres`.

---

## 3. Функції виконання транзакцій

### 3.1. Сирий обмін I²C

- `int i2c_transfer(struct i2c_adapter *adap, struct i2c_msg *msgs, int num)`  
  Виконує атомарну послідовність із `num` транзакцій `msgs` без звільнення шини між ними (через Repeated START). Повертає кількість успішно переданих повідомлень або від'ємний код помилки.
- `int i2c_master_send(const struct i2c_client *client, const char *buf, int count)`  
  Виконує просту операцію запису `count` байтів із буфера `buf` на адресу `client->addr`.
- `int i2c_master_recv(const struct i2c_client *client, char *buf, int count)`  
  Виконує просту операцію читання `count` байтів у буфер `buf` з адреси `client->addr`.

### 3.2. Допоміжні функції SMBus

Ядро автоматично транслює ці виклики або у нативний `smbus_xfer`, або в послідовності `i2c_msg` через `master_xfer`:

| Функція | Опис операції | Переданий блок / Довжина |
| :--- | :--- | :--- |
| `i2c_smbus_read_byte(client)` | Читання одного байта без передачі номера регістра | Receive Byte (1 байт) |
| `i2c_smbus_write_byte(client, val)` | Запис одного байта без передачі номера регістра | Send Byte (1 байт) |
| `i2c_smbus_read_byte_data(client, cmd)` | Зчитування одного байта з вказаного регістра `cmd` | Read Byte Data (1 байт) |
| `i2c_smbus_write_byte_data(client, cmd, val)` | Запис байта `val` у вказаний регістр `cmd` | Write Byte Data (1 байт) |
| `i2c_smbus_read_word_data(client, cmd)` | Зчитування 16-бітного слова з регістра `cmd` | Read Word Data (2 байти, little-endian) |
| `i2c_smbus_write_word_data(client, cmd, val)` | Запис 16-бітного слова `val` у регістр `cmd` | Write Word Data (2 байти, little-endian) |
| `i2c_smbus_read_i2c_block_data(client, cmd, len, vals)` | Зчитування послідовності `len` байтів без лічильника | I2C Block Read (1..32 байти) |
| `i2c_smbus_write_i2c_block_data(client, cmd, len, vals)` | Запис послідовності `len` байтів без лічильника | I2C Block Write (1..32 байти) |
| `i2c_smbus_read_block_data(client, cmd, vals)` | Стандартне зчитування блоку SMBus із передачею Byte Count | SMBus Block Read (1..32 байти) |
| `i2c_smbus_write_block_data(client, cmd, len, vals)` | Стандартний запис блоку SMBus із передачею Byte Count | SMBus Block Write (1..32 байти) |

---

## 4. Прапорці функціональності та повідомлень

### 4.1. Прапорці структури `struct i2c_msg`

- `I2C_M_RD` (`0x0001`) — операція читання з шини (виставляє 1 у біті R/W кадру адреси).
- `I2C_M_TEN` (`0x0010`) — використання 10-бітної адресації пристрою.
- `I2C_M_RECV_LEN` (`0x0400`) — перший байт відповіді інтерпретується як довжина наступного блоку даних.
- `I2C_M_NO_RD_ACK` (`0x0800`) — ігнорувати позитивне підтвердження ACK від ведучого під час читання.
- `I2C_M_IGNORE_NAK` (`0x1000`) — продовжувати передачу наступних байтів навіть у разі отримання NACK від веденого.
- `I2C_M_REV_DIR_ADDR` (`0x2000`) — інвертувати значення біта напрямку R/W в адресному байті.
- `I2C_M_NOSTART` (`0x4000`) — не формувати повторний START між послідовними повідомленнями однакового напрямку.
- `I2C_M_STOP` (`0x8000`) — примусово сформувати фінальний STOP після завершення поточного повідомлення.

### 4.2. Прапорці можливостей шини (`I2C_FUNC_*`)

```c
#define I2C_FUNC_I2C                    0x00000001 /* Підтримка сирих i2c_msg */
#define I2C_FUNC_10BIT_ADDR             0x00000002 /* 10-бітна адресація */
#define I2C_FUNC_PROTOCOL_MANGLING      0x00000004 /* Підтримка прапорців модифікації протоколу */
#define I2C_FUNC_SMBUS_PEC              0x00000008 /* Апаратна генерація та перевірка PEC CRC-8 */
#define I2C_FUNC_NOSTART                0x00000010 /* Підтримка прапорця I2C_M_NOSTART */
#define I2C_FUNC_SLAVE                  0x00000020 /* Підтримка режиму веденого пристрою */
#define I2C_FUNC_SMBUS_QUICK            0x00010000 /* Quick Command (0 байтів даних) */
#define I2C_FUNC_SMBUS_READ_BYTE        0x00020000 /* Receive Byte */
#define I2C_FUNC_SMBUS_WRITE_BYTE       0x00040000 /* Send Byte */
#define I2C_FUNC_SMBUS_READ_BYTE_DATA   0x00080000 /* Read Byte Data */
#define I2C_FUNC_SMBUS_WRITE_BYTE_DATA  0x00100000 /* Write Byte Data */
#define I2C_FUNC_SMBUS_READ_WORD_DATA   0x00200000 /* Read Word Data */
#define I2C_FUNC_SMBUS_WRITE_WORD_DATA  0x00400000 /* Write Word Data */
#define I2C_FUNC_SMBUS_PROC_CALL        0x00800000 /* Process Call */
#define I2C_FUNC_SMBUS_READ_BLOCK_DATA  0x01000000 /* Block Read з лічильником */
#define I2C_FUNC_SMBUS_WRITE_BLOCK_DATA 0x02000000 /* Block Write з лічильником */
#define I2C_FUNC_SMBUS_READ_I2C_BLOCK   0x04000000 /* I2C Block Read */
#define I2C_FUNC_SMBUS_WRITE_I2C_BLOCK  0x08000000 /* I2C Block Write */

#define I2C_FUNC_SMBUS_EMUL             (I2C_FUNC_SMBUS_QUICK | \
					 I2C_FUNC_SMBUS_BYTE | \
					 I2C_FUNC_SMBUS_BYTE_DATA | \
					 I2C_FUNC_SMBUS_WORD_DATA | \
					 I2C_FUNC_SMBUS_PROC_CALL | \
					 I2C_FUNC_SMBUS_WRITE_BLOCK_DATA | \
					 I2C_FUNC_SMBUS_I2C_BLOCK | \
					 I2C_FUNC_SMBUS_PEC)
```

---

## 5. Системні виклики `ioctl` простору користувача (`/dev/i2c-N`)

Символьні вузли `/dev/i2c-N`, які створюються драйвером `i2c-dev.ko`, підтримують такі команди системного виклику `ioctl`:

### 5.1. Конфігурація адресації та параметрів сесії

- `ioctl(fd, I2C_SLAVE, unsigned long addr)`  
  Прив'язує файловий дескриптор до вказаної 7-бітної або 10-бітної адреси пристрою. Якщо адреса вже обслуговується зареєстрованим драйвером ядра, виклик завершується помилкою `-EBUSY`.
- `ioctl(fd, I2C_SLAVE_FORCE, unsigned long addr)`  
  Примусово встановлює адресу пристрою, ігноруючи блокування ядра (призначено для налагоджувальних утиліт).
- `ioctl(fd, I2C_TENBIT, unsigned long enable)`  
  Вмикає (`enable != 0`) або вимикає режим 10-бітної адресації для поточного файлового дескриптора.
- `ioctl(fd, I2C_PEC, unsigned long enable)`  
  Вмикає або вимикає автоматичне додавання контрольного байта PEC до всіх операцій SMBus.
- `ioctl(fd, I2C_FUNCS, unsigned long *funcs)`  
  Копіює в простір користувача 32-бітну маску можливостей шинного адаптера (`I2C_FUNC_*`).
- `ioctl(fd, I2C_RETRIES, unsigned long count)`  
  Задає кількість повторних спроб надсилання пакета при отриманні NACK від пристрою.
- `ioctl(fd, I2C_TIMEOUT, unsigned long timeout_jiffies)`  
  Встановлює таймаут очікування відповіді шини у системних джифісах.

### 5.2. Виконання транзакцій

#### `I2C_RDWR` — складена транзакція масиву повідомлень

```c
struct i2c_rdwr_ioctl_data {
	struct i2c_msg *msgs;
	__u32 nmsgs;
};
```

Команда `ioctl(fd, I2C_RDWR, struct i2c_rdwr_ioctl_data *data)` передає масив повідомлень `msgs` на адаптер без проміжного звільнення шини. Застосовується для читання даних із внутрішніх регістрів сенсорів: перше повідомлення здійснює запис номера регістра, а друге виконує читання з прапорцем `I2C_M_RD`.

#### `I2C_SMBUS` — пряме виконання команд протоколу SMBus

```c
struct i2c_smbus_ioctl_data {
	__u8 read_write;
	__u8 command;
	__u32 size;
	union i2c_smbus_data *data;
};
```

Команда `ioctl(fd, I2C_SMBUS, struct i2c_smbus_ioctl_data *data)` викликає обробник `i2c_smbus_xfer()` у ядрі. Поле `size` визначає протокол обміну (`I2C_SMBUS_BYTE_DATA`, `I2C_SMBUS_WORD_DATA`, `I2C_SMBUS_BLOCK_DATA`, `I2C_SMBUS_I2C_BLOCK_DATA`), а поле `read_write` містить прапорець напрямку `I2C_SMBUS_READ` або `I2C_SMBUS_WRITE`.

---

## 6. Коди помилок операцій шини

- `-ENXIO` — адресований пристрій не відповів підтвердженням ACK на передачу свого адресного байта (пристрій відсутній або знеструмлений).
- `-EIO` — пристрій виставив NACK посеред передачі потоку даних або на лінії виявлено збій парності PEC.
- `-ETIMEDOUT` — час очікування операції вичерпано або лінія SCL залишалася в низькому стані довше встановленого таймауту контролера.
- `-EOPNOTSUPP` — запитана операція (наприклад, довільний `master_xfer`) не підтримується апаратним адаптером шини.
- `-EBUSY` — ресурс або адреса шини зайняті іншим потоком керування чи штатним драйвером ядра.
- `-EAGAIN` — втрачено арбітраж на шині з кількома майстрами під час спроби захоплення лінії.
