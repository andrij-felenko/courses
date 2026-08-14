# 📋 Інтерфейс програмування ядра Linux для шини I3C

Підсистема I3C у ядрі Linux надає двосторонній програмний інтерфейс. З одного боку, це внутрішнє C API ядра для розробників драйверів хост-контролерів та периферійних пристроїв (заголовки `include/linux/i3c/master.h` та `include/linux/i3c/device.h`). З іншого боку, це користувацький інтерфейс символьних пристроїв (`/dev/i3c-X`), що дозволяє утилітам простору користувача виконувати транзакції з шиною через механізм системних викликів `ioctl`.

## 1. Внутрішньоядерні структури та таблиці зворотних викликів

Центральним елементом управління майстер-контролером є структура `struct i3c_master_controller_ops`. Вона визначає точки входу, які драйвер апаратного контролера зобов'язаний реалізувати для делегування транзакцій від `i3c-core` до фізичного IP-ядра.

### 1.1. Детальний опис операцій `struct i3c_master_controller_ops`

| Функція зворотного виклику | Сигнатура та параметри | Опис механізму та виконання |
| :--- | :--- | :--- |
| `bus_init` | `int (*bus_init)(struct i3c_master_controller *master)` | Викликається під час реєстрації контролера. Контролер подає живлення на фізичний каскад PHY, налаштовує тактову частоту SCL та виділяє внутрішні кільцеві буфери DMA. Повертає `0` при успіху або від'ємний код помилки (`-ENODEV`, `-ETIMEDOUT`). |
| `bus_cleanup` | `void (*bus_cleanup)(struct i3c_master_controller *master)` | Викликається при вивантаженні модуля контролера. Зупиняє генератор тактування, деактивує переривання та звільняє виділені буфери. |
| `do_daa` | `int (*do_daa)(struct i3c_master_controller *master)` | Запускає процедуру Dynamic Address Assignment (ENTDAA). Якщо контролер виконує DAA апаратно, функція повертає кількість виявлених пристроїв. Якщо DAA виконується програмно-апаратно, вона надсилає широкомовну CCC команду та обробляє відповіді PID. |
| `send_ccc_cmd` | `int (*send_ccc_cmd)(struct i3c_master_controller *master, struct i3c_ccc_cmd *cmd)` | Відправляє загальну команду CCC. Структура `cmd` містить ID команди, біт типу (Broadcast/Direct), масив адресатів та корисне навантаження (Payload). |
| `priv_xfers` | `int (*priv_xfers)(struct i3c_dev_desc *dev, struct i3c_priv_xfer *xfers, int nxfers)` | Синхронно передає серію приватних пакетів читання/запису напряму до I3C-пристрою з призначеною динамічною адресою. повертає кількість успішно виконаних пакетів. |
| `i2c_xfers` | `int (*i2c_xfers)(struct i2c_dev_desc *dev, const struct i2c_msg *xfers, int nxfers)` | Транзитна функція сумісності. Приймає класичні повідомлення `struct i2c_msg` від старого I2C-драйвера і транслює їх у кадрову послідовність на I3C-майстрі. |
| `request_ibi` | `int (*request_ibi)(struct i3c_dev_desc *dev, const struct i3c_ibi_setup *req)` | Конфігурує апаратні слоти IBI у контролері для пристрою, виділяє пам'ять під корисне навантаження MDB та реєструє кільцеві буфери. |
| `enable_ibi` | `int (*enable_ibi)(struct i3c_dev_desc *dev)` | Активує маску переривань IBI на контролері та надсилає пристрою команду CCC `ENEC` (Enable Events Command). |
| `disable_ibi` | `int (*disable_ibi)(struct i3c_dev_desc *dev)` | Надсилає команду CCC `DISEC` (Disable Events Command) та вимикає обробку IBI для даного пристрою на рівні контролера. |

### 1.2. Структури даних передачі транзакцій та загальних команд CCC

Для виконання приватних транзакцій драйвери периферійних пристроїв використовують структуру `struct i3c_priv_xfer`:

```c
struct i3c_priv_xfer {
	u16 len;
	bool rnw;
	union {
		void *in;
		const void *out;
	} data;
	u8 err;
};
```

Поле `rnw` (Read-not-Write) визначає напрямок передачі: якщо `rnw == false`, транзакція є записом, і дані беруться з буфера `data.out`; якщо `rnw == true`, виконується читання у буфер `data.in`. Поле `err` повертає апаратний статус виконання транзакції (наприклад, `0` для успіху, або коди помилок колізії/NACK).

Для формування та передачі команд CCC використовується структура `struct i3c_ccc_cmd`:

```c
struct i3c_ccc_cmd {
	u8 rnw;
	u8 id;
	struct {
		u16 len;
		void *data;
	} payload;
	struct i3c_ccc_target_payload *targets;
	int ndests;
	int err;
};
```

Поле `id` визначає семантику команди (наприклад, `I3C_CCC_ENTDAA` = `0x07`, `I3C_CCC_ENEC` = `0x00`, `I3C_CCC_RSTDAA` = `0x06`). Поле `ndests` вказує кількість цільових пристроїв для адресних (Direct) команд, а масив `targets` описує окремі буфери для кожного периферійного вузла.

Для конфігурування внутрішньосмугових переривань використовується структура `struct i3c_ibi_setup`:

```c
struct i3c_ibi_setup {
	unsigned int max_payload_len;
	unsigned int num_slots;
	void (*handler)(struct i3c_device *dev, const struct i3c_ibi_payload *payload);
};
```

Поле `max_payload_len` задає максимальний розмір байтів корисного навантаження Mandatory Data Byte (MDB), яке периферійний пристрій може передати разом із перериванням. Поле `num_slots` визначає глибину кільцевого буфера вказівників на виділені слоти у ядрі, що запобігає втраті переривань при високій частоті їх виникнення.

### 1.3. Коди помилок та обробка крайніх випадків у ядрі

Під час виконання транзакцій функції ядра `i3c_device_do_priv_xfers()` та `i3c_master_send_ccc_cmd()` можуть повертати такі коди помилок:

- `-EAGAIN`: Програш арбітражу на відкритому стоці під час передачі CCC або транзакції. Драйвер повинен повторити спробу передачі після паузи.
- `-ENXIO`: Пристрій з вказаною динамічною адресою не відповів на сигнатуру адресації (отримано NACK). Можливо, пристрій знеструмлений або скинув динамічну адресу.
- `-ETIMEDOUT`: Таймаут виконання апаратного кадру на контролері. Вказує на зависання лінії SCL (Clock Stretching Timeout) або несправність фізичного каскаду PHY.
- `-EBUSY`: Контролер шини знаходиться у стані виконання процедури DAA або обробки вищого за пріоритетом переривання Hot-Join.

## 2. Інтерфейс користувацького простору (`/dev/i3c-X` та `ioctl`)

Для взаємодії з шиною I3C з простору користувача ядро Linux надає символьні пристрої `/dev/i3c-X`. Застосунки можуть відкривати ці файли пристроїв та виконувати виклики `ioctl` для надсилання пакетів даних.

Під час виконання виклику `open("/dev/i3c-0", O_RDWR)` підсистема VFS звертається до зареєстрованих точок входу `struct file_operations i3c_dev_fops`. Символьний пристрій автоматично виділяє динамічний старший номер (Major Number) через `alloc_chrdev_region()` і реєструє клас пристроїв `i3c_class` у sysfs.

Запити `ioctl` спираються на масив структур `struct i3c_ioc_priv_xfer`, який відображає приватні транзакції у користувацьку пам'ять. Драйвер символьного пристрою перевіряє права доступу (`CAP_SYS_RAWIO`), копіює масив дескрипторів із простору користувача у пам'ять ядра через `copy_from_user()`, виділяє тимчасові буфери DMA та передає виконання функції `i3c_device_do_priv_xfers()`.

Нижче наведено практичний приклад програми користувацького простору для взаємодії з I3C пристроєм. Для дотримання вимог канону щодо мов розробки приклад реалізовано двома вкладками: мовою C та ідіоматичною мовою C++20 із застосуванням концепції RAII для управління файловими ресурсами.

:::tabs
```c
/* i3c_user_app.c - Приклад користувацької програми на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/types.h>

/* Структура приватного переказу для ioctl у користувацькому просторі */
struct i3c_ioc_priv_xfer {
	__u16 len;
	__u8 rnw;
	__u8 pad;
	__u64 data;
};

#define I3C_IOC_MAGIC 'I'
#define I3C_IOC_PRIV_XFER(n) _IOC(_IOC_WRITE, I3C_IOC_MAGIC, 0x01, (n) * sizeof(struct i3c_ioc_priv_xfer))

int main(void)
{
	int fd = open("/dev/i3c-0", O_RDWR);
	if (fd < 0) {
		perror("Не вдалося відкрити /dev/i3c-0");
		return 1;
	}

	uint8_t reg_addr = 0x0A;
	uint8_t read_buf[4] = {0};

	struct i3c_ioc_priv_xfer xfers[2] = {
		{
			.len = 1,
			.rnw = 0, /* Запис адреси регістра */
			.data = (uintptr_t)&reg_addr,
		},
		{
			.len = sizeof(read_buf),
			.rnw = 1, /* Читання даних */
			.data = (uintptr_t)read_buf,
		}
	};

	if (ioctl(fd, I3C_IOC_PRIV_XFER(2), xfers) < 0) {
		perror("Помилка виконання ioctl I3C_IOC_PRIV_XFER");
		close(fd);
		return 2;
	}

	printf("Прочитано значення: 0x%02X 0x%02X 0x%02X 0x%02X\n",
	       read_buf[0], read_buf[1], read_buf[2], read_buf[3]);

	close(fd);
	return 0;
}
```
```cpp
// i3c_user_app.cpp - Приклад користувацької програми на ідіоматичному C++20
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/types.h>

struct i3c_ioc_priv_xfer {
	uint16_t len;
	uint8_t rnw;
	uint8_t pad;
	uint64_t data;
};

#define I3C_IOC_MAGIC 'I'
#define I3C_IOC_PRIV_XFER(n) _IOC(_IOC_WRITE, I3C_IOC_MAGIC, 0x01, (n) * sizeof(struct i3c_ioc_priv_xfer))

// RAII обгортка для файлового дескриптора Linux
class ScopedFd {
public:
	explicit ScopedFd(const char* path, int flags) 
		: fd_(::open(path, flags)) {}

	~ScopedFd() {
		if (fd_ >= 0) ::close(fd_);
	}

	[[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
	[[nodiscard]] int get() const noexcept { return fd_; }

	ScopedFd(const ScopedFd&) = delete;
	ScopedFd& operator=(const ScopedFd&) = delete;

private:
	int fd_{-1};
};

int main()
{
	ScopedFd dev("/dev/i3c-0", O_RDWR);
	if (!dev.valid()) {
		std::cerr << "Помилка відкриття символьного пристрою I3C\n";
		return 1;
	}

	uint8_t reg_addr = 0x0A;
	std::array<uint8_t, 4> read_buf{};

	std::array<i3c_ioc_priv_xfer, 2> xfers{{
		{
			.len = 1,
			.rnw = 0,
			.pad = 0,
			.data = reinterpret_cast<uint64_t>(&reg_addr)
		},
		{
			.len = static_cast<uint16_t>(read_buf.size()),
			.rnw = 1,
			.pad = 0,
			.data = reinterpret_cast<uint64_t>(read_buf.data())
		}
	}};

	if (::ioctl(dev.get(), I3C_IOC_PRIV_XFER(xfers.size()), xfers.data()) < 0) {
		std::cerr << "Помилка ioctl виконання транзакції I3C\n";
		return 2;
	}

	std::cout << "Прочитано байтів: ";
	for (auto byte : read_buf) {
		std::cout << "0x" << std::hex << static_cast<int>(byte) << " ";
	}
	std::cout << "\n";

	return 0;
}
```
:::

## 3. Синхронізація та блокування у ядрі

Виконання транзакцій на шині I3C вимагає суворого дотримання послідовності станів, щоб уникнути колізій між звичайними приватними пакетами, загальними командами CCC та асинхронними перериваннями IBI.

Підсистема ядра `i3c-core` реалізує двоуровневу схему блокувань:

1. **`bus->lock` (М'ютекс шини):** Захищає списки виявлених пристроїв `bus->devs`, таблицю виділених динамічних адрес `bus->addrslots` та гарантує атомарність виконання серії приватних транзакцій `i3c_device_do_priv_xfers()`. Будь-яка спроба виконання DAA або надсилання CCC команди захоплює цей м'ютекс у монопольному режимі.
2. **Спінлоки прийому IBI (`ibi_lock`):** Оскільки апаратне переривання IBI виникає в атомарному контексті (Top-Half IRQ handler контролера), обробка слота IBI виконується під захистом спінлока. Обробник витягує байт MDB із FIFO контролера, копіює його у передвиділений слот `struct i3c_ibi_slot` і передає роботу у робочу чергу ядра, звільняючи спінлок протягом декількох мікросекунд.
