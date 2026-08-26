# ⚙️ Практикум: автономний драйвер крипточипа захищеного сховища

Робота з апаратним чипом безпеки вимагає суворого дотримання часових діаграм і бінарного формату пакетів, де будь-яка помилка в розрахунку контрольної суми або тривалості імпульсу пробудження блокує зв'язок на фізичному рівні. Цей практикум надає повний, незалежний від платформи драйвер криптографічного чипа ATECC608A/B мовами C та C++, реалізуючи повний життєвий цикл операції: пробудження шини, генерацію команди підпису ECDSA P-256 над зовнішнім дайджестом, перевірку відповідей та коректне переведення в режим глибокого сну.

### Структура протоколу та кадрування ATECC608

Чип ATECC608 взаємодіє з мікроконтролером через шину I2C (типова 7-бітна адреса пристрою за замовчуванням `0x60` або `0x58`, що на шині відповідає байту запису `0xC0` та байту читання `0xC1`).

Оскільки чип більшу частину часу проводить у глибокому сні з вимкненим тактовим генератором (споживаючи струм менше 150 нА), будь-якій транзакції має передувати фізичний імпульс пробудження (англ. *Wake token*). Для цього хост примусово утримує лінію SDA на низькому логічному рівні впродовж щонайменше 60 мікросекунд (параметр `t_WLO`), після чого відпускає її і чекає щонайменше 1.5 мілісекунди (`t_WHI`), доки стабілізується внутрішній RC-генератор чипа. Після цього ATECC608 надсилає 4-байтове слово готовності `0x04 0x11 0x33 0x43` (де `0x11` означає успішне пробудження). Якщо мікроконтролер не надсилає жодних команд усередині інтервалу сторожового таймера (Watchdog Timeout, зазвичай 1.7 секунди), чип автоматично вимикає генератор і повертається в режим сну.

Кожен командний пакет, що надсилається в чип, має фіксовану бінарну структуру:

```
[ Байт 0 ]  Word Address (0x03 — запис команди)
[ Байт 1 ]  Count (Загальна довжина пакета, включно з цим байтом і двома байтами CRC)
[ Байт 2 ]  Opcode (Код операції, наприклад 0x41 для Sign)
[ Байт 3 ]  Param1 (Режим виконання команди)
[ Байт 4 ]  Param2_LSB (Молодший байт аргументу, наприклад номер слота)
[ Байт 5 ]  Param2_MSB (Старший байт аргументу)
[ Байт 6..N-3 ] Data (Опційні корисні дані, наприклад 32 байти хешу)
[ Байт N-2 ] CRC16_LSB (Молодший байт контрольної суми CRC16-CCITT)
[ Байт N-1 ] CRC16_MSB (Старший байт контрольної суми CRC16-CCITT)
```

Контрольна сума розраховується від байта `Count` до останнього байта даних `Data`. Поліном — стандартизований `0x8005` (зворотний бітовий порядок для CCITT-16), початкове значення акумулятора — `0x0000`. Якщо розрахована чипом сума не збігається з переданою хостом, ATECC608 відхиляє команду й записує у вихідний буфер однобайтовий код помилки `0x01` (Bad CRC).

### Життєвий цикл команди підпису (Sign Command)

Команда `Sign` (`Opcode = 0x41`) є наріжним каменем асиметричної автентифікації пристрою. Вона інструктує апаратне ядро еліптичної кривої згенерувати цифровий підпис за алгоритмом ECDSA на кривій secp256r1 (NIST P-256).

Параметр `Param1` визначає джерело даних для підпису:
- Значення `0x80` (External Digest) означає, що 32-байтний хеш повідомлення (наприклад, дайджест SHA-256 від TLS handshake або MQTT повідомлення) передається безпосередньо в полі даних пакета.
- Значення `0x00` (Internal Digest) вказує чипу підписати внутрішній результат виконання команди `GenDig` або `Nonce`, що зберігається у тимчасовому буфері TempKey.

Параметр `Param2` вказує цільовий номер слота (від 0 до 15), у якому замкнено приватний ключ. Чип вичитує 256-бітний приватний ключ із внутрішнього масиву EEPROM через зашифровану внутрішню шину, завантажує його в математичний співпроцесор і запускає обчислення точки кривої `(R, S)`. По завершенню чип формує 67-байтову відповідь, де першим байтом є довжина `0x43` (67 у десятковій системі), наступні 32 байти містять вектор `R`, наступні 32 байти — вектор `S`, а останні 2 байти — контрольну суму CRC16 відповіді. Приватний ключ при цьому жодного разу не потрапляє ні в регістри інтерфейсу I2C, ні на зовнішні виводи чипа.

### Автономна реалізація драйвера

Нижче наведено модульний драйвер, відокремлений від конкретного апаратного рівня (HAL). Він приймає три функції зворотного виклику для I2C: запис буфера, читання буфера та затримку в мілісекундах.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ATECC_I2C_ADDR           0x60
#define ATECC_CMD_WORD_ADDR      0x03
#define ATECC_SLEEP_WORD_ADDR    0x01
#define ATECC_OP_SIGN            0x41
#define ATECC_SIGN_MODE_EXTERNAL 0x80
#define ATECC_EXEC_TIME_SIGN_MS  115

typedef struct {
    bool (*i2c_write)(uint8_t addr, const uint8_t *data, uint16_t len);
    bool (*i2c_read)(uint8_t addr, uint8_t *data, uint16_t len);
    void (*wake_pulse)(void);
    void (*delay_ms)(uint32_t ms);
} atecc_hal_t;

typedef enum {
    ATECC_OK = 0,
    ATECC_ERR_HAL,
    ATECC_ERR_CRC,
    ATECC_ERR_STATUS,
    ATECC_ERR_TIMEOUT
} atecc_status_t;

static uint16_t atecc_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0x0000;
    for (size_t i = 0; i < length; i++) {
        for (uint8_t shift = 0x01; shift > 0x00; shift <<= 1) {
            uint8_t data_bit = (data[i] & shift) ? 1 : 0;
            uint8_t crc_bit = (crc >> 15) & 0x01;
            crc <<= 1;
            if (data_bit ^ crc_bit) {
                crc ^= 0x8005;
            }
        }
    }
    return crc;
}

atecc_status_t atecc_wake(const atecc_hal_t *hal) {
    hal->wake_pulse();
    hal->delay_ms(2); // Очікування готовності (t_WHI)

    uint8_t resp[4] = {0};
    if (!hal->i2c_read(ATECC_I2C_ADDR, resp, 4)) {
        return ATECC_ERR_HAL;
    }
    if (resp[0] != 0x04 || resp[1] != 0x11) {
        return ATECC_ERR_STATUS;
    }
    return ATECC_OK;
}

void atecc_sleep(const atecc_hal_t *hal) {
    uint8_t sleep_cmd = ATECC_SLEEP_WORD_ADDR;
    hal->i2c_write(ATECC_I2C_ADDR, &sleep_cmd, 1);
}

atecc_status_t atecc_sign_digest(const atecc_hal_t *hal, uint8_t slot_id,
                                const uint8_t digest[32], uint8_t signature[64]) {
    uint8_t tx_buf[40]; // 1(WordAddr) + 1(Count) + 1(Op) + 1(P1) + 2(P2) + 32(Data) + 2(CRC)
    uint8_t count = 39;

    tx_buf[0] = ATECC_CMD_WORD_ADDR;
    tx_buf[1] = count;
    tx_buf[2] = ATECC_OP_SIGN;
    tx_buf[3] = ATECC_SIGN_MODE_EXTERNAL;
    tx_buf[4] = (uint8_t)(slot_id & 0x0F);
    tx_buf[5] = 0x00;
    memcpy(&tx_buf[6], digest, 32);

    uint16_t crc = atecc_crc16(&tx_buf[1], count - 2);
    tx_buf[38] = (uint8_t)(crc & 0xFF);
    tx_buf[39] = (uint8_t)((crc >> 8) & 0xFF);

    if (!hal->i2c_write(ATECC_I2C_ADDR, tx_buf, 40)) {
        return ATECC_ERR_HAL;
    }

    hal->delay_ms(ATECC_EXEC_TIME_SIGN_MS);

    // Відповідь: 1 байт Count (67) + 64 байти (R, S) + 2 байти CRC
    uint8_t rx_buf[67];
    if (!hal->i2c_read(ATECC_I2C_ADDR, rx_buf, sizeof(rx_buf))) {
        return ATECC_ERR_HAL;
    }

    if (rx_buf[0] != 67) {
        return ATECC_ERR_STATUS;
    }

    uint16_t expected_crc = (uint16_t)(rx_buf[65] | (rx_buf[66] << 8));
    uint16_t calc_crc = atecc_crc16(rx_buf, 65);
    if (expected_crc != calc_crc) {
        return ATECC_ERR_CRC;
    }

    memcpy(signature, &rx_buf[1], 64);
    return ATECC_OK;
}
```
```cpp
#include <array>
#include <cstdint>
#include <expected>
#include <functional>
#include <span>

namespace security {

enum class AteccError : uint8_t {
    HalError,
    CrcMismatch,
    DeviceError,
    Timeout
};

using Signature = std::array<uint8_t, 64>;
using Digest = std::array<uint8_t, 32>;

struct I2cBus {
    std::function<bool(uint8_t, std::span<const uint8_t>)> write;
    std::function<bool(uint8_t, std::span<uint8_t>)> read;
    std::function<void()> wakePulse;
    std::function<void(uint32_t)> delayMs;
};

class SecureElementSession {
public:
    static constexpr uint8_t I2cAddress = 0x60;
    static constexpr uint8_t CmdWord = 0x03;
    static constexpr uint8_t SleepWord = 0x01;
    static constexpr uint8_t OpSign = 0x41;
    static constexpr uint8_t SignModeExternal = 0x80;

    explicit SecureElementSession(I2cBus bus) : bus_(std::move(bus)) {}

    ~SecureElementSession() noexcept {
        if (isAwake_) {
            const std::array<uint8_t, 1> sleepCmd{SleepWord};
            bus_.write(I2cAddress, sleepCmd);
        }
    }

    SecureElementSession(const SecureElementSession&) = delete;
    SecureElementSession& operator=(const SecureElementSession&) = delete;
    SecureElementSession(SecureElementSession&&) noexcept = default;
    SecureElementSession& operator=(SecureElementSession&&) noexcept = default;

    [[nodiscard]] std::expected<void, AteccError> wake() noexcept {
        bus_.wakePulse();
        bus_.delayMs(2);

        std::array<uint8_t, 4> resp{};
        if (!bus_.read(I2cAddress, resp)) {
            return std::unexpected(AteccError::HalError);
        }
        if (resp[0] != 0x04 || resp[1] != 0x11) {
            return std::unexpected(AteccError::DeviceError);
        }
        isAwake_ = true;
        return {};
    }

    [[nodiscard]] std::expected<Signature, AteccError> signDigest(
        uint8_t slotId, const Digest& digest) noexcept {
        
        if (!isAwake_) {
            if (auto res = wake(); !res) return std::unexpected(res.error());
        }

        std::array<uint8_t, 40> txBuf{};
        constexpr uint8_t count = 39;

        txBuf[0] = CmdWord;
        txBuf[1] = count;
        txBuf[2] = OpSign;
        txBuf[3] = SignModeExternal;
        txBuf[4] = static_cast<uint8_t>(slotId & 0x0F);
        txBuf[5] = 0x00;
        std::copy(digest.begin(), digest.end(), txBuf.begin() + 6);

        const uint16_t crc = calculateCrc(std::span<const uint8_t>(txBuf.data() + 1, count - 2));
        txBuf[38] = static_cast<uint8_t>(crc & 0xFF);
        txBuf[39] = static_cast<uint8_t>((crc >> 8) & 0xFF);

        if (!bus_.write(I2cAddress, txBuf)) {
            return std::unexpected(AteccError::HalError);
        }

        bus_.delayMs(115); // Очікування апаратного розрахунку точки кривої

        std::array<uint8_t, 67> rxBuf{};
        if (!bus_.read(I2cAddress, rxBuf)) {
            return std::unexpected(AteccError::HalError);
        }

        if (rxBuf[0] != 67) {
            return std::unexpected(AteccError::DeviceError);
        }

        const uint16_t expectedCrc = static_cast<uint16_t>(rxBuf[65] | (rxBuf[66] << 8));
        const uint16_t actualCrc = calculateCrc(std::span<const uint8_t>(rxBuf.data(), 65));
        if (expectedCrc != actualCrc) {
            return std::unexpected(AteccError::CrcMismatch);
        }

        Signature sig{};
        std::copy_n(rxBuf.begin() + 1, 64, sig.begin());
        return sig;
    }

private:
    I2cBus bus_;
    bool isAwake_{false};

    static constexpr uint16_t calculateCrc(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0x0000;
        for (uint8_t byte : data) {
            for (uint8_t shift = 0x01; shift > 0x00; shift <<= 1) {
                uint8_t dataBit = (byte & shift) ? 1 : 0;
                uint8_t crcBit = (crc >> 15) & 0x01;
                crc <<= 1;
                if (dataBit ^ crcBit) {
                    crc ^= 0x8005;
                }
            }
        }
        return crc;
    }
};

} // namespace security
```
:::

### Типові інженерні пастки при інтеграції

1. **Ігнорування часової затримки виконання (Execution Time):**
   Криптографічний процесор чипа виконує скалярне множення точок на еліптичній кривій NIST P-256 апаратним автоматом. Для команди `Sign` час розрахунку складає від 50 до 115 мілісекунд залежно від напруги живлення та екземпляра кристала. Якщо хост надсилає I2C Read занадто рано, чип не підтверджує свою адресу на шині (виставляє NACK) або повертає код помилки `0x0F` (Execution Error). Надійний драйвер або витримує гарантовану максимальну паузу, або здійснює періодичний опит (англ. *polling*) шини.

2. **Блокування слотів та конфігураційна зона (Slot Locking):**
   Кожен з 16 слотів пам'яті EEPROM має власну бітову маску дозволів у зоні конфігурації `SlotConfig[N]`. Якщо біт `IsSecret` виставлено в `1`, а прапорець слота переведено в стан `Locked`, чип апаратно блокує команди прямого читання (`Read`). Спроба виконати команду читання повертає статус `0x03` (Parse Error / Access Violation). Приватний ключ може використовуватися виключно криптографічним двигуном.

3. **Колізії напруги на лініях I2C під час Wake:**
   Генерація імпульсу низького рівня на лінії SDA для пробудження чипа не повинна створювати хибних сигналів Start/Stop для інших пристроїв на тій самій шині I2C. Якщо на спільній шині присутні чутливі сенсори, лінію SDA крипточипа часто під'єднують через окремий GPIO або використовують однопровідний інтерфейс SWI (англ. *Single Wire Interface*) замість I2C.

### Фабричне програмування та блокування зон (Provisioning)

Фізична безпека чипа активується лише після фінального блокування зон пам'яті на виробничій лінії:
- **Зона конфігурації (Configuration Zone, 128 байтів):** визначає I2C-адресу, типи ключів для кожного слота (ECC P-256, AES-128 або SHA-256), права читання/запису та обмеження використання. Доки конфігурація не заблокована командою `Lock(Zone=0)`, чип вважається незахищеним і відхиляє операції підпису.
- **Зона даних (Data Zone, 16 слотів):** містить самі ключі. Після генерації або імпорту приватного ключа виконується команда `Lock(Zone=1)`. Після цього біти блокування в eFuse чипа безповоротно блокують будь-яку можливість перезапису або вилучення ключа.

### Інтеграція з TLS-стеками (mbedTLS / WolfSSL)

Для встановлення захищеного з'єднання TLS (наприклад, взаємна автентифікація mbedTLS з AWS IoT або Azure IoT Hub) приватний ключ клієнта не передається у програмний стек. Замість цього створюється обгортка операції підпису:
1. Бібліотека TLS виконує звичайний обмін відкритими сертифікатами і рахує хеш транзакції рукостискання (Handshake Digest).
2. Замість виклику програмного алгоритму `mbedtls_ecdsa_sign()` стек викликає функцію `atecc_sign_digest()`.
3. Отримані вектори `(R, S)` упаковуються у формат ASN.1 DER і надсилаються серверу як стандартний підпис сертифіката клієнта `CertificateVerify`.

### Енергетичний бюджет операції

У режимі очікування зі збереженням стану чип споживає струм менше 150 нА при напрузі 3.3 В. Під час активного розрахунку підпису споживання зростає до 14 мА впродовж ~80 мс. Повна енергія на один цифровий підпис становить:

`E = U · I · t = 3.3 В · 0.014 А · 0.080 с ≈ 3.7 мДж`

Такий енергетичний профіль дозволяє застосовувати Secure Element навіть в автономних датчиках із живленням від дискових літієвих батарейок CR2032, виконуючи тисячі криптографічних автентифікацій без суттєвого впливу на ресурс живлення.
