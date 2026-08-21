# ⚙️ Взаємодія з I²C/SMBus пристроями через /dev/i2c-N у просторі користувача

Під час розробки вбудованих застосунків, системних служб телеметрії, засобів виробничого калібрування чи діагностичних утиліт інженерам часто потрібно взаємодіяти з периферійними мікросхемами — датчиками температури й тиску, годинниками RTC, розширювачами портів GPIO та мікросхемами пам'яті EEPROM — безпосередньо з простору користувача. Створення повноцінного драйвера ядра не завжди є доцільним, якщо пристрій використовується лише однією спеціалізованою програмою або перебуває на стадії прототипування.

Ядро Linux надає стандартний механізм прямого доступу до шини через модуль `i2c-dev.ko`, який створює в каталозі `/dev/` символьні вузли виду `/dev/i2c-N` для кожного зареєстрованого в системі шинного адаптера. У цьому практичному проєкті ми розберемо повний життєвий цикл роботи з цифровим сенсором середовища Bosch BMP280 через символьний інтерфейс, вивчимо внутрішню механіку викликів `ioctl`, розглянемо зчитування масивів даних за допомогою атомарних транзакцій та напишемо повноцінні програми на C та сучасному ідіоматичному C++.

## 1. Архітектурна модель та вибір між інтерфейсами `read/write` та `I2C_RDWR`

При відкритті файлового дескриптора `/dev/i2c-N` ядро створює контекст сесії `struct i2c_client` у пам'яті драйвера `i2c-dev`. Для подальшого обміну даними простір користувача може використовувати два принципово різних підходи:

### 1.1. Базовий інтерфейс `read()` / `write()` із прив'язкою адреси `I2C_SLAVE`

Програма встановлює цільову 7-бітну адресу веденого пристрою за допомогою виклику `ioctl(fd, I2C_SLAVE, addr)`. Після цього стандартні системні виклики VFS функціонують так:
- `write(fd, buf, len)` — формує кадр START, передає адресний байт із бітом `W = 0`, послідовно передає `len` байтів із буфера та завершує транзакцію кадром STOP.
- `read(fd, buf, len)` — формує кадр START, передає адресний байт із бітом `R = 1`, зчитує `len` байтів у буфер і формує фінальний кадр STOP.

Головний недолік цієї схеми полягає у відсутності атомарності між записом адреси регістра та зчитуванням його вмісту. Якщо програма спочатку записує `write()` номер регістра `0xD0`, а потім викликає `read()` для отримання значення, між цими двома викликами шина повністю звільняється генерацією кадру STOP. У багатозадачній системі або на шині з кількома майстрами інший процес може перехопити шину між `write` та `read`, змінити вказівник внутрішнього регістра сенсора або адреситися до іншого чипа. Крім того, деякі пристрої апаратно скидають внутрішній покажчик регістрів на нуль при отриманні сигналу STOP, що робить роздільні виклики непрацездатними.

### 1.2. Атомарний інтерфейс `ioctl(fd, I2C_RDWR, &rdwr_data)`

Команда `I2C_RDWR` приймає масив дескрипторів `struct i2c_msg`. Під час обробки цього виклику драйвер ядра `i2c-dev` копіює масив повідомлень із пам'яті користувача в ядро через `memdup_user()`, блокує м'ютекс шинного адаптера `adap->bus_lock` і викликає метод `adap->algo->master_xfer()`.

Шинний контролер формує одне неподільне комплексне повідомлення: надсилає номер регістра на запис, а замість завершального кадру STOP генерує повторний старт (Repeated START, `Sr`) і одразу перемикає лінію на читання. Лінія залишається безперервно захопленою процесом, що унеможливлює стан гонитви.

## 2. Реалізація опитування сенсора BMP280

У прикладі нижче ми виконуємо послідовність дій:
1. Відкриваємо дескриптор шини `/dev/i2c-1` та перевіряємо прапорці можливостей адаптера через `ioctl(fd, I2C_FUNCS, &funcs)`.
2. Зчитуємо 8-бітний регістр ідентифікації чипа `0xD0` (для BMP280 очікується значення `0x58`).
3. Записуємо байт конфігурації у регістр керування живленням та режимами вимірювання `0xF4` (вмикаємо режим Normal Mode з оверсемплінгом температури x2 та тиску x16).
4. Зчитуємо суцільний блок із 6 регістрів даних вимірювань `0xF7..0xFC` за одну атомарну операцію `I2C_RDWR`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

#define I2C_DEV_PATH     "/dev/i2c-1"
#define BMP280_ADDR      0x76
#define BMP280_REG_ID    0xD0
#define BMP280_REG_CTRL  0xF4
#define BMP280_REG_DATA  0xF7
#define BMP280_EXPECT_ID 0x58

/* Читання Chip ID через виклик I2C_RDWR з Repeated START */
static int bmp280_read_id(int fd, uint8_t *chip_id)
{
	uint8_t reg = BMP280_REG_ID;
	struct i2c_msg msgs[2];
	struct i2c_rdwr_ioctl_data rdwr;

	/* Повідомлення 1: Запис адреси цільового регістра */
	msgs[0].addr  = BMP280_ADDR;
	msgs[0].flags = 0;
	msgs[0].len   = 1;
	msgs[0].buf   = &reg;

	/* Повідомлення 2: Зчитування 1 байта значення */
	msgs[1].addr  = BMP280_ADDR;
	msgs[1].flags = I2C_M_RD;
	msgs[1].len   = 1;
	msgs[1].buf   = chip_id;

	rdwr.msgs  = msgs;
	rdwr.nmsgs = 2;

	if (ioctl(fd, I2C_RDWR, &rdwr) < 0)
		return -errno;

	return 0;
}

/* Запис 1 байта конфігурації у регістр пристрою */
static int bmp280_write_reg(int fd, uint8_t reg, uint8_t val)
{
	uint8_t buf[2] = { reg, val };
	struct i2c_msg msg;
	struct i2c_rdwr_ioctl_data rdwr;

	msg.addr  = BMP280_ADDR;
	msg.flags = 0;
	msg.len   = 2;
	msg.buf   = buf;

	rdwr.msgs  = &msg;
	rdwr.nmsgs = 1;

	if (ioctl(fd, I2C_RDWR, &rdwr) < 0)
		return -errno;

	return 0;
}

/* Зчитування блоку вимірювань (6 байтів: тиск + температура) */
static int bmp280_read_measurements(int fd, uint8_t raw_data[6])
{
	uint8_t reg = BMP280_REG_DATA;
	struct i2c_msg msgs[2];
	struct i2c_rdwr_ioctl_data rdwr;

	msgs[0].addr  = BMP280_ADDR;
	msgs[0].flags = 0;
	msgs[0].len   = 1;
	msgs[0].buf   = &reg;

	msgs[1].addr  = BMP280_ADDR;
	msgs[1].flags = I2C_M_RD;
	msgs[1].len   = 6;
	msgs[1].buf   = raw_data;

	rdwr.msgs  = msgs;
	rdwr.nmsgs = 2;

	if (ioctl(fd, I2C_RDWR, &rdwr) < 0)
		return -errno;

	return 0;
}

int main(void)
{
	int fd;
	unsigned long funcs;
	uint8_t chip_id = 0;
	uint8_t raw_data[6];

	fd = open(I2C_DEV_PATH, O_RDWR);
	if (fd < 0) {
		fprintf(stderr, "Помилка відкриття %s: %s\n", I2C_DEV_PATH, strerror(errno));
		return EXIT_FAILURE;
	}

	/* Перевірка підтримки атомарних транзакцій адаптером */
	if (ioctl(fd, I2C_FUNCS, &funcs) < 0) {
		fprintf(stderr, "Не вдалося отримати можливості адаптера: %s\n", strerror(errno));
		close(fd);
		return EXIT_FAILURE;
	}

	if (!(funcs & I2C_FUNC_I2C)) {
		fprintf(stderr, "Шинний адаптер не підтримує сирі I2C транзакції I2C_RDWR\n");
		close(fd);
		return EXIT_FAILURE;
	}

	/* Перевірка зв'язку з чипом */
	if (bmp280_read_id(fd, &chip_id) < 0) {
		fprintf(stderr, "Помилка зв'язку з BMP280 на адресі 0x%02X: %s\n",
			BMP280_ADDR, strerror(errno));
		close(fd);
		return EXIT_FAILURE;
	}

	printf("Знайдено чип з ID: 0x%02X (очікувався: 0x%02X)\n", chip_id, BMP280_EXPECT_ID);

	/* Налаштування: Normal Mode, оверсемплінг температури x2, тиску x16 */
	if (bmp280_write_reg(fd, BMP280_REG_CTRL, 0x57) < 0) {
		fprintf(stderr, "Помилка конфігурації сенсора: %s\n", strerror(errno));
		close(fd);
		return EXIT_FAILURE;
	}

	usleep(50000); /* Очікування завершення першого циклу вимірювання */

	if (bmp280_read_measurements(fd, raw_data) < 0) {
		fprintf(stderr, "Помилка зчитування результатів вимірювання: %s\n", strerror(errno));
		close(fd);
		return EXIT_FAILURE;
	}

	/* Декодування сирих 20-бітних відліків */
	int32_t raw_press = ((int32_t)raw_data[0] << 12) | ((int32_t)raw_data[1] << 4) | ((int32_t)raw_data[2] >> 4);
	int32_t raw_temp  = ((int32_t)raw_data[3] << 12) | ((int32_t)raw_data[4] << 4) | ((int32_t)raw_data[5] >> 4);

	printf("Сирі відліки: Температура = %d, Тиск = %d\n", raw_temp, raw_press);

	close(fd);
	return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

/* RAII-обгортка дескриптора I2C-адаптера */
class I2cBus {
public:
	explicit I2cBus(const std::string& dev_node) {
		fd_ = ::open(dev_node.c_str(), O_RDWR);
		if (fd_ < 0) {
			throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити I2C вузол");
		}

		unsigned long funcs = 0;
		if (::ioctl(fd_, I2C_FUNCS, &funcs) < 0) {
			::close(fd_);
			throw std::system_error(errno, std::generic_category(), "Помилка запиту I2C_FUNCS");
		}

		if (!(funcs & I2C_FUNC_I2C)) {
			::close(fd_);
			throw std::runtime_error("Адаптер не підтримує сирі I2C-транзакції");
		}
	}

	~I2cBus() noexcept {
		if (fd_ >= 0) {
			::close(fd_);
		}
	}

	I2cBus(const I2cBus&) = delete;
	I2cBus& operator=(const I2cBus&) = delete;
	I2cBus(I2cBus&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
	I2cBus& operator=(I2cBus&& other) noexcept {
		if (this != &other) {
			if (fd_ >= 0) ::close(fd_);
			fd_ = other.fd_;
			other.fd_ = -1;
		}
		return *this;
	}

	/* Атомарне читання регістрів через Repeated START */
	void read_registers(uint16_t addr, uint8_t reg, std::span<uint8_t> out_buf) const {
		uint8_t target_reg = reg;
		struct i2c_msg msgs[2];
		struct i2c_rdwr_ioctl_data rdwr;

		msgs[0].addr  = addr;
		msgs[0].flags = 0;
		msgs[0].len   = 1;
		msgs[0].buf   = &target_reg;

		msgs[1].addr  = addr;
		msgs[1].flags = I2C_M_RD;
		msgs[1].len   = static_cast<__u16>(out_buf.size());
		msgs[1].buf   = out_buf.data();

		rdwr.msgs  = msgs;
		rdwr.nmsgs = 2;

		if (::ioctl(fd_, I2C_RDWR, &rdwr) < 0) {
			throw std::system_error(errno, std::generic_category(), "Помилка I2C_RDWR читання");
		}
	}

	/* Запис байта в регістр */
	void write_register(uint16_t addr, uint8_t reg, uint8_t val) const {
		uint8_t buf[2] = { reg, val };
		struct i2c_msg msg;
		struct i2c_rdwr_ioctl_data rdwr;

		msg.addr  = addr;
		msg.flags = 0;
		msg.len   = 2;
		msg.buf   = buf;

		rdwr.msgs  = &msg;
		rdwr.nmsgs = 1;

		if (::ioctl(fd_, I2C_RDWR, &rdwr) < 0) {
			throw std::system_error(errno, std::generic_category(), "Помилка I2C_RDWR запису");
		}
	}

private:
	int fd_{-1};
};

int main() {
	constexpr const char* dev_path = "/dev/i2c-1";
	constexpr uint16_t bmp280_addr = 0x76;
	constexpr uint8_t reg_id       = 0xD0;
	constexpr uint8_t reg_ctrl     = 0xF4;
	constexpr uint8_t reg_data     = 0xF7;

	try {
		I2cBus bus(dev_path);

		uint8_t chip_id = 0;
		bus.read_registers(bmp280_addr, reg_id, std::span(&chip_id, 1));
		std::cout << "Зчитано Chip ID: 0x" << std::hex << static_cast<int>(chip_id) << std::dec << "\n";

		/* Normal Mode, передискретизація температури x2, тиску x16 */
		bus.write_register(bmp280_addr, reg_ctrl, 0x57);

		::usleep(50000);

		std::vector<uint8_t> raw_data(6);
		bus.read_registers(bmp280_addr, reg_data, std::span(raw_data));

		int32_t raw_press = (raw_data[0] << 12) | (raw_data[1] << 4) | (raw_data[2] >> 4);
		int32_t raw_temp  = (raw_data[3] << 12) | (raw_data[4] << 4) | (raw_data[5] >> 4);

		std::cout << "Сирі показники сенсора: Температура = " << raw_temp
		          << ", Тиск = " << raw_press << "\n";

	} catch (const std::exception& ex) {
		std::cerr << "Критична помилка: " << ex.what() << "\n";
		return EXIT_FAILURE;
	}

	return EXIT_SUCCESS;
}
```
:::

## 3. Налагодження та аналіз через трасування ядра

Для діагностики проблем на шині простір користувача може використовувати вбудовані точки трасування ядра (ftrace tracepoints). Підсистема I²C надає події для відстеження кожного переданого повідомлення:

```bash
# Увімкнення трасування I2C повідомлень
echo 1 > /sys/kernel/debug/tracing/events/i2c/enable

# Запуск нашої тестової програми
./bmp280_reader

# Перегляд результатів трасування
cat /sys/kernel/debug/tracing/trace
```

У лозі трасування з'являться чіткі записи з таймстемпами, адресами та байтами даних:
```text
i2c_write: i2c-1 #0 a=076 f=0000 l=1 [d0]
i2c_read:  i2c-1 #1 a=076 f=0001 l=1 [58]
i2c_result: i2c-1 n=2 ret=2
```

Це дозволяє точно побачити, чи дійшов адресний байт до шини і які саме байти повернув апаратний контролер.

## 4. Типові пастки та крайові випадки

1. **Ілюзія успіху виклику `ioctl(I2C_SLAVE)`:** Системний виклик `ioctl(fd, I2C_SLAVE, addr)` є суто локальною операцією ядра: він зберігає адресу в дескрипторі файлу і не надсилає жодних сигналів на фізичну шину. Якщо мікросхема відсутня або знеструмлена, `I2C_SLAVE` все одно поверне `0` (успіх), а справжня помилка `-ENXIO` (No such device or address) виникне лише під час першої спроби передачі даних.
2. **Конфлікт блокування адреси драйвером ядра (`-EBUSY`):** Якщо для пристрою в системі вже завантажено штатний драйвер ядра (наприклад, модуль `bmp280.ko` із підсистеми `iio`), ядро блокує виклик `ioctl(I2C_SLAVE, addr)` і повертає помилку `-EBUSY`. Для експериментів існує виклик `I2C_SLAVE_FORCE`, однак його використання у виробничих сервісах заборонено, оскільки одночасний доступ ядра та користувацького простору руйнує внутрішній стан мікросхеми.
3. **Плутанина між `I2C_SMBUS_BLOCK_DATA` та `I2C_SMBUS_I2C_BLOCK_DATA`:** Стандартний блоковий протокол SMBus вимагає, щоб ведений пристрій передавав першим байтом довжину блоку (Byte Count). Більшість класичних сенсорів I²C не підтримують лічильник і передають лише потік корисних байтів. Спроба застосувати стандартну команду блокового читання SMBus призведе до зсуву даних і помилки обробки.
4. **Нестача прав доступу до вузлів `/dev/i2c-N`:** За замовчуванням файли пристроїв `/dev/i2c-N` належать користувачеві `root` та групі `i2c`. Для запуску прикладних програм від імені звичайного користувача необхідно додати його до відповідної групи (`usermod -aG i2c $USER`) або налаштувати правила `udev` у файлі `/etc/udev/rules.d/99-i2c.rules`.
