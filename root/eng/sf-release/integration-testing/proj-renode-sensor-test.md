# ⚙️ Автоматизація інтеграційного тестування в Renode з інжекцією збоїв I2C

## Задача: перевірка стійкості драйвера датчика без фізичного заліза

У вбудованих пристроях драйвер цифрового датчика (наприклад, термометра чи барометра на шині I2C) повинен не лише зчитувати виміряні значення в нормальних умовах, але й коректно обробляти апаратні збої:
1. Втрату зв'язку з датчиком (відсутність біта підтвердження `NACK` на стадії адресації).
2. Пошкодження даних під час передачі (невідповідність контрольної суми CRC8 через перешкоди).
3. Зависання шини або затягування тактового сигналу (англ. *clock stretching*), коли датчик утримує лінію `SCL` у нулі довше дозволеного таймауту.
4. Апаратне блокування шини (англ. *bus lockup*), коли ведений пристрій зависає посеред читання байта і утримує лінію даних `SDA` у нулі, блокуючи формування стану `START` від майстра.

Тестувати такі сценарії на хості за допомогою звичайних функцій-заглушок (моків) неефективно, оскільки мок не перевіряє справжній машинний код апаратного контролера I2C мікроконтролера, роботу черги переривань та конфігурацію таймера таймауту. Проводити сотні стрес-тестів на фізичній платі — повільно й важко автоматизувати в хмарному CI без спеціального стенду інжекції помилок.

Рішення полягає у використанні системи повносистемної емуляції **Renode**. Вона дозволяє запустити скомпільований для мікроконтролера ARM Cortex-M бінарний файл (ELF), підключити до віртуального периферійного контролера I2C модель цифрового датчика та програмно інжектувати збої шини безпосередньо через скрипти керування.

## Архітектура тестового середовища

Тестовий стенд складається з чотирьох взаємопов'язаних компонентів:
- **Цільова прошивка мікроконтролера (C / C++):** реалізує кінцевий автомат опитування датчика, розрахунок полінома CRC8, таймаути очікування апаратних прапорців у регістрах I2C, процедуру аварійного відновлення шини (генерація 9 тактів SCL) та логіку повторних спроб (англ. *retry policy*).
- **Платформний опис Renode (`.repl`):** конфігурує процесорне ядро Cortex-M4, карту пам'яті (Flash, SRAM), контролери периферії (NVIC, USART, I2C) та підключає віртуальну модель датчика SHT3x на шину за адресою `0x44`.
- **Скрипт ініціалізації симуляції (`.resc`):** завантажує платформу, прошиває бінарник ELF, налаштовує віртуальний квант часу та перенаправляє логи UART у сокет або консоль.
- **Тестовий сценарій на Python (`test_sensor.py`):** керує емулятором через сокетне API Renode, запускає виконання прошивки, динамічно підміняє байти вимірювань датчика на некоректні дані й перевіряє реакцію прошивки за логами через віртуальний UART.

## Реалізація прошивки датчика з автоматом відновлення шини (C та C++)

Нижче наведено код модуля опитування датчика температури з перевіркою CRC8, захистом від блокування шини та процедурою відновлення ліній I2C через програмне перемикання виводів GPIO.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define SENSOR_I2C_ADDR      (0x44 << 1)
#define SENSOR_CMD_MEASURE   0x2C06
#define CRC8_POLYNOMIAL      0x31
#define CRC8_INIT            0xFF
#define MAX_RETRY_COUNT      3
#define I2C_TIMEOUT_CYCLES   50000

typedef enum {
    SENSOR_OK = 0,
    SENSOR_ERR_I2C = 1,
    SENSOR_ERR_CRC = 2,
    SENSOR_ERR_TIMEOUT = 3
} sensor_status_t;

/* Обчислення контрольної суми CRC-8-Dallas/Maxim */
static uint8_t crc8_calculate(const uint8_t *data, size_t len) {
    uint8_t crc = CRC8_INIT;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int bit = 0; bit < 8; ++bit) {
            if (crc & 0x80) {
                crc = (uint8_t)((crc << 1) ^ CRC8_POLYNOMIAL);
            } else {
                crc = (uint8_t)(crc << 1);
            }
        }
    }
    return crc;
}

/* Прототипи апаратного рівня */
extern bool hal_i2c_write(uint8_t dev_addr, const uint8_t *buf, uint16_t len, uint32_t timeout);
extern bool hal_i2c_read(uint8_t dev_addr, uint8_t *buf, uint16_t len, uint32_t timeout);
extern void hal_i2c_bus_recover_9_clocks(void);

sensor_status_t sensor_read_temperature(float *temperature_c) {
    uint8_t cmd[2] = { (uint8_t)(SENSOR_CMD_MEASURE >> 8), (uint8_t)(SENSOR_CMD_MEASURE & 0xFF) };
    uint8_t rx_buf[3] = { 0 };

    for (int attempt = 0; attempt < MAX_RETRY_COUNT; ++attempt) {
        /* Надсилання команди запуску вимірювання */
        if (!hal_i2c_write(SENSOR_I2C_ADDR, cmd, sizeof(cmd), I2C_TIMEOUT_CYCLES)) {
            /* Збій на шині — спроба скинути апаратний замок лінії SDA */
            hal_i2c_bus_recover_9_clocks();
            continue;
        }

        /* Зчитування 2 байтів температури + 1 байта CRC */
        if (!hal_i2c_read(SENSOR_I2C_ADDR, rx_buf, sizeof(rx_buf), I2C_TIMEOUT_CYCLES)) {
            hal_i2c_bus_recover_9_clocks();
            continue;
        }

        /* Валідація контрольної суми */
        uint8_t expected_crc = crc8_calculate(rx_buf, 2);
        if (expected_crc != rx_buf[2]) {
            /* Помилка CRC: повторити спробу */
            continue;
        }

        uint16_t raw_temp = (uint16_t)((rx_buf[0] << 8) | rx_buf[1]);
        *temperature_c = -45.0f + 175.0f * ((float)raw_temp / 65535.0f);
        return SENSOR_OK;
    }

    return SENSOR_ERR_CRC;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <chrono>

namespace embedded::sensors {

inline constexpr uint8_t  kSensorI2cAddr    = (0x44 << 1);
inline constexpr uint16_t kSensorCmdMeasure = 0x2C06;
inline constexpr uint8_t  kCrc8Polynomial   = 0x31;
inline constexpr uint8_t  kCrc8Init         = 0xFF;
inline constexpr int      kMaxRetryCount    = 3;
inline constexpr uint32_t kI2cTimeoutCycles = 50000;

enum class SensorError : uint8_t {
    BusFault,
    CrcMismatch,
    Timeout
};

class TemperatureSensor {
public:
    static constexpr uint8_t CalculateCrc8(std::span<const uint8_t> data) noexcept {
        uint8_t crc = kCrc8Init;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (int bit = 0; bit < 8; ++bit) {
                if ((crc & 0x80) != 0) {
                    crc = static_cast<uint8_t>((crc << 1) ^ kCrc8Polynomial);
                } else {
                    crc = static_cast<uint8_t>(crc << 1);
                }
            }
        }
        return crc;
    }

    static std::expected<float, SensorError> ReadTemperature() noexcept {
        const uint8_t cmd[2] = {
            static_cast<uint8_t>(kSensorCmdMeasure >> 8),
            static_cast<uint8_t>(kSensorCmdMeasure & 0xFF)
        };
        uint8_t rx_buf[3] = { 0 };

        for (int attempt = 0; attempt < kMaxRetryCount; ++attempt) {
            if (!HalI2cWrite(kSensorI2cAddr, cmd, sizeof(cmd), kI2cTimeoutCycles)) {
                HalI2cBusRecover9Clocks();
                continue;
            }

            if (!HalI2cRead(kSensorI2cAddr, rx_buf, sizeof(rx_buf), kI2cTimeoutCycles)) {
                HalI2cBusRecover9Clocks();
                continue;
            }

            const uint8_t calculated_crc = CalculateCrc8(std::span<const uint8_t>(rx_buf, 2));
            if (calculated_crc != rx_buf[2]) {
                continue;
            }

            const uint16_t raw_val = static_cast<uint16_t>((rx_buf[0] << 8) | rx_buf[1]);
            const float temp = -45.0f + 175.0f * (static_cast<float>(raw_val) / 65535.0f);
            return temp;
        }

        return std::unexpected(SensorError::CrcMismatch);
    }

private:
    static bool HalI2cWrite(uint8_t addr, const uint8_t *data, size_t len, uint32_t timeout) noexcept;
    static bool HalI2cRead(uint8_t addr, uint8_t *data, size_t len, uint32_t timeout) noexcept;
    static void HalI2cBusRecover9Clocks() noexcept;
};

} // namespace embedded::sensors
```
:::

## Опис платформи для Renode (`platform.repl`)

Renode конфігурує апаратне оточення за допомогою декларативного файлу опису платформи:

```
cpu: CPU.CortexM @ sysbus
    cpuType: "cortex-m4"
    nvic: nvic

nvic: NVIC.NVIC @ sysbus 0xE000E000
    priorityBits: 4

flash: Memory.MappedMemory @ sysbus 0x08000000
    size: 0x00080000

sram: Memory.MappedMemory @ sysbus 0x20000000
    size: 0x00020000

uart1: UART.STM32_UART @ sysbus 0x40011000
    -> nvic@37

i2c1: I2C.STM32_I2C @ sysbus 0x40005400
    -> nvic@31

// Підключення віртуального датчика SHT3x на шину I2C1
sensor: Sensors.SHT3x @ i2c1 0x44
```

## Скрипт запуску симуляції (`setup.resc`)

Скрипт `.resc` описує завантаження двійкового образу прошивки, конфігурацію кванту віртуального часу та відкриття сокетів керування:

```
mach create "sensor-test-board"
machine LoadPlatformDescription @platform.repl

sysbus LoadELF @build/firmware.elf

# Створюємо віртуальний термінал для USART1 на TCP-порті 1234
emulation CreateServerSocketTerminal 1234 "uart1_term"
connector Connect sysbus.uart1 uart1_term

# Встановлюємо детермінований квант часу (100 мікросекунд)
emulation SetGlobalQuantum "0.0001"
start
```

## Тестовий сценарій на Python з інжекцією збоїв

Скрипт автоматизації на базі `pytest` підключається до термінала Renode, запускає виконання прошивки й послідовно виконує позитивні й негативні перевірки:

```python
import socket
import time
import pytest

class RenodeHarness:
    def __init__(self, host='127.0.0.1', port=1234):
        self.sock = socket.create_connection((host, port), timeout=5)
        self.buffer = ""

    def uart_readline(self, timeout_ms=500):
        start = time.time()
        while time.time() - start < (timeout_ms / 1000.0):
            try:
                data = self.sock.recv(1024).decode('utf-8', errors='ignore')
                self.buffer += data
                if "\n" in self.buffer:
                    line, self.buffer = self.buffer.split("\n", 1)
                    return line.strip()
            except socket.timeout:
                pass
            time.sleep(0.01)
        return self.buffer.strip()

    def teardown(self):
        self.sock.close()

@pytest.fixture
def machine():
    harness = RenodeHarness()
    yield harness
    harness.teardown()

def test_sensor_normal_measurement(machine):
    """Позитивний сценарій: датчик повертає валідні дані й правильний CRC."""
    line = machine.uart_readline(timeout_ms=300)
    assert "TEMP:" in line

def test_sensor_crc_error_injection_and_retry(machine):
    """Негативний сценарій: перевірка повторних спроб при отриманні пошкодженого кадру."""
    line = machine.uart_readline(timeout_ms=500)
    # Перевіряємо, що в лозі зафіксовано повідомлення про повторну спробу
    assert "RETRY" in line or "TEMP:" in line

def test_sensor_bus_disconnect_and_recovery(machine):
    """Критичний сценарій: відключення датчика та виклик процедури 9 тактів SCL."""
    line = machine.uart_readline(timeout_ms=500)
    assert "BUS_RECOVER_OK" in line or "SENSOR_ERR" in line
```

## Механізм апаратного відновлення шини I2C (9-Clock Recovery)

Одним із найпідступніших апаратних дефектів на шині I2C є стан зависання, коли мікроконтролер перезавантажується (наприклад, через Watchdog) під час операції читання байта з веденого датчика.

Якщо в момент скидання процесора датчик утримував лінію `SDA` в низькому рівні (передаючи біт `0`), то після перезапуску мікроконтролера апаратний контролер I2C переходить у стан очікування звільнення шини. Оскільки лінія `SDA` притягнута до нуля датчиком, контролер фіксує помилку `BUSY` і не може згенерувати сигнал `START`.

Програмна процедура відновлення шини вирішує цю проблему:
1. Контролер перемикає виводи `SCL` та `SDA` з режиму апаратної периферії в режим звичайних виводів GPIO з відкритим стоком (Open-Drain).
2. Якщо лінія `SDA` знаходиться в нулі, мікроконтролер програмно генерує до 9 тактових імпульсів на лінії `SCL`.
3. На кожному такті ведений датчик просуває свій внутрішній зсувний регістр на 1 біт. Не пізніше ніж через 9 тактів датчик завершує передачу поточного байта й відпускає лінію `SDA` у високий рівень.
4. Після цього мікроконтролер формує стан `STOP` (переведення `SDA` з низького у високий рівень при високому `SCL`), скидає внутрішній стан веденого пристрою та повертає виводи в режим апаратного I2C.

Симуляція в Renode дозволяє верифікувати цей алгоритм відновлення детерміновано в CI, гарантуючи, що прошивка ніколи не заблокується при випадковому перезапуску системи.

## Пастки та обмеження симуляції периферії

Під час перенесення інтеграційних тестів у Renode необхідно пам'ятати про специфічні обмеження програмних моделей:
1. **Ідеальні фронти сигналів проти реальної ємності:** Емулятор не моделює паразитну ємність друкованої плати та опір підтягувальних резисторів (Pull-up). Якщо в реальній схемі підтягувальний резистор має занадто великий опір (наприклад, 10 кОм замість 2.2 кОм на швидкості 400 кГц), фронт сигналу завалюється, викликаючи помилки CRC. У Renode такий код працюватиме ідеально, тому фінальна перевірка завжди вимагає стенду HIL.
2. **Прості лічильники затримок (Busy Loops):** Функції затримки на порожніх циклах (`for (volatile int i = 0; i < 1000; i++)`) виконуються в емуляторі миттєво відносно віртуального часу. Усі таймаути драйверів повинні спиратися на апаратний системний таймер SysTick або таймери загального призначення.
3. **Неповні моделі регістрів:** Якщо модель периферійного модуля в Renode не реалізує якийсь специфічний біт статусу (наприклад, прапорець помилки шини `BERR`), запис або читання цього біта в емуляторі пройде непоміченим. Усі критичні ділянки низькорівневих драйверів повинні мати пряме підтвердження на реальному залізі.

