# ⚙️ Низькорівневий драйвер радіомодуля (SPI + IRQ + T/R Switch)

Розробка апаратного драйвера радіомодуля є критичним етапом побудови надійної бездротової системи. Програмне забезпечення повинно гарантувати точну послідовність подачі команд конфігурації, надійне читання та запис регістрів ВЧ-трансивера через шину SPI, керування апаратними пінами фронтенду (T/R Switch), а також високоефективну обробку апаратних переривань від лінії IRQ без блокування основного циклу мікроконтролера.

Драйвер радіомодуля будується за принципом двошарової апаратної архітектури:
1. **Низькорівневий шар адаптації (HAL — Hardware Abstraction Layer)**: забезпечує виклики атомарних операцій вибору пристрою на шині SPI (лінія Chip Select / CS), передачу й прийом байтів, виставлення логічних рівнів на пінах керування фронтендом та апаратні затримки.
2. **Високорівневий шар драйвера радіомодуля**: реалізує кінцевий автомат станів (Sleep, Standby, TX, RX), обчислює адреси регістрів, здійснює упаковку пакунків у FIFO-буфер трансивера та скидає прапорці переривань.

### Схемотехніка та протокол SPI ВЧ-трансиверів

Переважна більшість ВЧ-трансиверів (таких як Semtech SX126x/SX127x, Texas Instruments CC1101 чи Nordic nRF24L01) використовують 8-бітовий або 16-бітовий формат команд SPI.

При передачі адреси регістра найвищий біт байта адреси (MSB, біт 7) слугує прапорцем напрямку операції:
- Якщо `Bit 7 = 1` — це операція **запису** в регістр (`REG | 0x80`).
- Якщо `Bit 7 = 0` — це операція **читання** з регістра (`REG & 0x7F`).

При масивному обміні з буфером FIFO шина SPI переводиться у режим пакетного читання/запису (Burst mode), де після подачі адреси регістра FIFO лінія CS утримується в низькому стані, а мікроконтролер послідовно тактує необхідну кількість байтів пакунка.

Важливою практичною деталлю є перемикання підсилювача потужності (PA) та малошумного підсилювача (LNA) у фронтенд-модулі (FEM). Перед викликом команди передачі `MODE_TX` драйвер повинен апаратно переключити лінію T/R Switch у стан передачі (виставити високий рівень на піні `PA_EN`). Інакше вихідний ВЧ-сигнал трансивера не дійде до антени або пошкодить вхідний LNA.

### Автомат станів і часові затримки

Радіомодуль функціонує як кінцевий автомат із чотирма основними станами:
- **Sleep (Сон)**: споживання струму мінімальне (наноампери). Всі внутрішні блоки, синтезатор PLL та кварцовий генератор вимкнені. Вхід у цей режим виконується після завершення сеансу зв'язку.
- **Standby (Очікування)**: кварцовий генератор (XTAL/TCXO) працює, але підсилювачі та модем вимкнені. Споживання становить 1–3 мА. Це проміжний стан для зміни конфігураційних регістрів та завантаження FIFO.
- **TX (Передача)**: ввімкнено синтезатор PLL, модем та підсилювач потужності PA. Споживання досягає 100–500 мА.
- **RX (Прийом)**: ввімкнено синтезатор PLL, модем та малошумний підсилювач LNA. Трансивер постійно сканує ефір.

При переході зі стану Sleep у Standby драйвер повинен забезпечити апаратну затримку в 2–5 мілісекунд, необхідну для стабілізації генератора TCXO та захоплення частоти петельним фільтром PLL.

### Двомовна реалізація драйвера

Нижче наведено повну реалізацію низькорівневого драйвера радіомодуля у двох ідіоматичних варіантах:
- **Процедурний варіант на мові C**: ідеально підходить для мікроконтролерів із обмеженими ресурсами пам'яті (AVR, STM32 HAL, bare-metal C), використовує чіткі типи `uint8_t` та функціональний підхід.
- **Об'єктно-орієнтований варіант на C++20**: втілює сучасні стандарти розробки надійного ПЗ (RAII для автоматичного переведення в Sleep при знищенні об'єкта, концептуальні інтерфейси шини, безпечну роботу з пам'яттю через `std::span` та обробку помилок без винятків через `std::expected`).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Адреси регістрів та маски RF-трансивера */
#define RF_REG_OP_MODE        0x01
#define RF_REG_FIFO           0x00
#define RF_REG_IRQ_FLAGS      0x12
#define RF_REG_PAYLOAD_LEN    0x22

#define RF_MODE_SLEEP         0x00
#define RF_MODE_STANDBY       0x01
#define RF_MODE_TX            0x03
#define RF_MODE_RX            0x05

#define RF_SPI_WRITE_MASK     0x80

/* Зовнішній апаратний інтерфейс (HAL) */
extern void hal_spi_select(bool enable);
extern uint8_t hal_spi_transfer_byte(uint8_t data);
extern void hal_gpio_set_tx_mode(bool tx_on);
extern void hal_delay_ms(uint32_t ms);

typedef enum {
    RF_OK = 0,
    RF_ERR_TIMEOUT,
    RF_ERR_PARAM
} rf_status_t;

/* Запис значення в регістр модуля */
rf_status_t rf_module_write_reg(uint8_t reg, uint8_t val) {
    hal_spi_select(true);
    hal_spi_transfer_byte(reg | RF_SPI_WRITE_MASK);
    hal_spi_transfer_byte(val);
    hal_spi_select(false);
    return RF_OK;
}

/* Читання значення з регістра модуля */
uint8_t rf_module_read_reg(uint8_t reg) {
    hal_spi_select(true);
    hal_spi_transfer_byte(reg & ~RF_SPI_WRITE_MASK);
    uint8_t val = hal_spi_transfer_byte(0x00);
    hal_spi_select(false);
    return val;
}

/* Зміна режиму роботи радіомодуля та керування T/R перемикачем */
rf_status_t rf_module_set_mode(uint8_t mode) {
    if (mode == RF_MODE_TX) {
        hal_gpio_set_tx_mode(true);  /* Перемикаємо FEM на TX (PA_EN = 1) */
    } else {
        hal_gpio_set_tx_mode(false); /* Перемикаємо FEM на RX/Standby */
    }
    return rf_module_write_reg(RF_REG_OP_MODE, mode);
}

/* Ініціалізація радіомодуля */
rf_status_t rf_module_init(void) {
    hal_spi_select(false);
    hal_gpio_set_tx_mode(false);
    
    rf_module_set_mode(RF_MODE_STANDBY);
    hal_delay_ms(5);
    
    /* Перевірка зв'язку з трансивером */
    uint8_t mode = rf_module_read_reg(RF_REG_OP_MODE);
    if ((mode & 0x07) != RF_MODE_STANDBY) {
        return RF_ERR_TIMEOUT;
    }
    return RF_OK;
}

/* Передача пакунка даних через FIFO */
rf_status_t rf_module_send_packet(const uint8_t *data, size_t len) {
    if (!data || len == 0 || len > 255) {
        return RF_ERR_PARAM;
    }

    rf_module_set_mode(RF_MODE_STANDBY);
    rf_module_write_reg(RF_REG_PAYLOAD_LEN, (uint8_t)len);

    /* Запис даних у FIFO буфер */
    hal_spi_select(true);
    hal_spi_transfer_byte(RF_REG_FIFO | RF_SPI_WRITE_MASK);
    for (size_t i = 0; i < len; i++) {
        hal_spi_transfer_byte(data[i]);
    }
    hal_spi_select(false);

    /* Запуск передачі в ефір */
    rf_module_set_mode(RF_MODE_TX);
    return RF_OK;
}

/* Обробник переривання IRQ (викликуваний з ISR хост-MCU) */
void rf_module_handle_irq(void) {
    uint8_t flags = rf_module_read_reg(RF_REG_IRQ_FLAGS);
    if (flags & 0x08) { /* TX Done */
        rf_module_write_reg(RF_REG_IRQ_FLAGS, 0x08); /* Скидання прапорця */
        rf_module_set_mode(RF_MODE_STANDBY);
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

enum class RfMode : uint8_t {
    Sleep   = 0x00,
    Standby = 0x01,
    Tx      = 0x03,
    Rx      = 0x05
};

enum class RfError {
    HardwareTimeout,
    InvalidParameter,
    SpiFailure
};

/* Абстрактний апаратний шинний інтерфейс */
class ISpiBus {
public:
    virtual ~ISpiBus() = default;
    virtual void select(bool enable) noexcept = 0;
    virtual uint8_t transfer(uint8_t byte) noexcept = 0;
};

/* Клас керування ВЧ-фронтендом (T/R Switch & PA Enable) */
class IRfFrontend {
public:
    virtual ~IRfFrontend() = default;
    virtual void setTxEnabled(bool enable) noexcept = 0;
};

class RfModule {
public:
    explicit RfModule(ISpiBus& spi, IRfFrontend& frontend) noexcept
        : spi_(spi), frontend_(frontend) {}

    ~RfModule() {
        (void)setMode(RfMode::Sleep);
    }

    [[nodiscard]] std::expected<void, RfError> init() noexcept {
        spi_.select(false);
        frontend_.setTxEnabled(false);

        auto res = setMode(RfMode::Standby);
        if (!res) return res;

        uint8_t mode = readReg(RegOpMode);
        if ((mode & 0x07) != static_cast<uint8_t>(RfMode::Standby)) {
            return std::unexpected(RfError::HardwareTimeout);
        }
        return {};
    }

    [[nodiscard]] std::expected<void, RfError> setMode(RfMode mode) noexcept {
        frontend_.setTxEnabled(mode == RfMode::Tx);
        writeReg(RegOpMode, static_cast<uint8_t>(mode));
        return {};
    }

    [[nodiscard]] std::expected<void, RfError> sendPacket(std::span<const uint8_t> payload) noexcept {
        if (payload.empty() || payload.size() > 255) {
            return std::unexpected(RfError::InvalidParameter);
        }

        auto res = setMode(RfMode::Standby);
        if (!res) return res;

        writeReg(RegPayloadLen, static_cast<uint8_t>(payload.size()));

        spi_.select(true);
        spi_.transfer(RegFifo | SpiWriteMask);
        for (uint8_t byte : payload) {
            spi_.transfer(byte);
        }
        spi_.select(false);

        return setMode(RfMode::Tx);
    }

    void handleInterrupt() noexcept {
        uint8_t flags = readReg(RegIrqFlags);
        if (flags & TxDoneMask) {
            writeReg(RegIrqFlags, TxDoneMask);
            (void)setMode(RfMode::Standby);
        }
    }

private:
    static constexpr uint8_t RegOpMode     = 0x01;
    static constexpr uint8_t RegFifo       = 0x00;
    static constexpr uint8_t RegIrqFlags   = 0x12;
    static constexpr uint8_t RegPayloadLen = 0x22;
    static constexpr uint8_t SpiWriteMask  = 0x80;
    static constexpr uint8_t TxDoneMask    = 0x08;

    ISpiBus& spi_;
    IRfFrontend& frontend_;

    void writeReg(uint8_t reg, uint8_t val) noexcept {
        spi_.select(true);
        spi_.transfer(reg | SpiWriteMask);
        spi_.transfer(val);
        spi_.select(false);
    }

    [[nodiscard]] uint8_t readReg(uint8_t reg) noexcept {
        spi_.select(true);
        spi_.transfer(reg & ~SpiWriteMask);
        uint8_t val = spi_.transfer(0x00);
        spi_.select(false);
        return val;
    }
};
```
:::

### Пояснення архітектурних рішень та захист від збоїв

1. **Ізоляція апаратних залежностей через інверсію залежностей (DIP)**:
   У C++ версії клас `RfModule` не містить прямих викликів конкретних регістрів мікроконтролера STM32 чи ESP32. Замість цього він приймає посилання на абстрактні інтерфейси `ISpiBus` та `IRfFrontend`. Це дозволяє використовувати один і той самий код драйвера радіомодуля на будь-якій апаратній платформі або проганяти юніт-тести на персональному комп'ютері за допомогою компонентів-заглушок (Mock objects).

2. **Захист від невалідних покажчиків та переповнення буфера**:
   У той час як C-версія покладається на перевірку покажчика `if (!data)` та ручний контроль довжини, C++ реалізація приймає `std::span<const uint8_t>`. Це повністю виключає можливість передачі "дикого" покажчика та передає довжину буфера як невід'ємну частину об'єкта.

3. **Гарантоване скидання прапорців переривань**:
   ВЧ-трансивери мають важливу особливість: прапорці переривань у регістрі `RegIrqFlags` не скидаються автоматично при прочитанні. Для їх зняття драйвер повинен повторно записати одиницю в той самий біт регістра (`writeReg(RegIrqFlags, TxDoneMask)`). Якщо цього не зробити, лінія IRQ залишиться в активному стані, і мікроконтролер замкнеться у нескінченному циклі виклику обробника переривань ISR.

4. **Безпечна робота з живленням у деструкторі**:
   Деструктор `~RfModule()` автоматично переводить трансивер у режим найглибшого сну `RfMode::Sleep`. Це гарантує, що при виході об'єкта з області видимості радіомодуль не залишиться у режимі прийому чи передачі зі підвищеним споживанням струму.

5. **Особливості обробки переривань у реальному часі**:
   Обробник переривання `handleInterrupt()` призначений для швидкого виклику всередині переривання (ISR) або у фоновому циклі (Event Loop). Утилізація прапорця `TxDoneMask` повертає радіомодуль у безпечний стан `Standby`, запобігаючи неконтрольованій роботі підсилювача потужності після випромінювання останнього байта пакунка.
