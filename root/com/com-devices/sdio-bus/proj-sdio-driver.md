# ⚙️ Емуляція та реалізація клієнтського драйвера SDIO: від ініціалізації до асинхронного потоку

Розробка та налагодження низькорівневого програмного забезпечення для бездротових модулів SDIO (Wi-Fi, Bluetooth, стільникові модеми LTE/5G) у вбудованих системах стикається з низкою специфічних апаратних бар'єрів. Високі тактові частоти шини (50 МГц у режимі High Speed та до 208 МГц у режимі UHS-I SDR104), малі габарити розпаяних мікросхем BGA/QFN та відсутність доступу до контрольних точок роблять використання фізичних логічних аналізаторів трудомістким процесом. Крім того, на ранніх етапах проектування системної плати фізичний модуль ще відсутній, що вимагає створення надійного програмного стенда для відпрацювання протокольного стека.

Створення програмного емулятора SDIO-периферії та повнофункціонального клієнтського драйвера дозволяє ізольовано відтворити повний життєвий цикл обміну даними: від первинного опитування робочих умов (`CMD5`) та ініціалізації системних регістрів CCCR/FBR до високошвидкісного блокового вичитування мережевих пакетів через команду `CMD53` та диспетчеризації асинхронних внутрішньосмугових переривань на лінії DAT1.

---

## 1. Архітектура та послідовність взаємодії компонентів

Програмний комплекс моделювання розділено на два функціональні шари: шар емуляції апаратного пристрою (SDIO Target Device Simulator) та шар клієнтського хост-драйвера (SDIO Host Driver Layer).

```
                      +──────────────────────────────────────────+
                      |         Клієнтський хост-драйвер         |
                      |          (SDIO Host Controller)          |
                      +────────────────────┬─────────────────────+
                                           │
       1. Ініціалізація шини (CMD52)       │ 4. Асинхронний запит IRQ (DAT1 = 0)
       2. Налаштування FBR BlkSize (CMD52) │ 5. Читання INT_PENDING (CMD52)
       3. Пакетне читання FIFO (CMD53)     │ 6. Очищення стану та квітування
                                           ▼
                      +──────────────────────────────────────────+
                      |       Емулятор апаратного модуля         |
                      |        (SDIO Target Peripheral)          |
                      |  - Простір CIA: CCCR (0x00..0x13)        |
                      |  - Простір FBR: Функція 1 (0x100..0x111) |
                      |  - Апаратний FIFO черги пакетів RX       |
                      |  - Стан віртуальної лінії DAT1 / IRQ     |
                      +──────────────────────────────────────────+
```

### Фази життєвого циклу взаємодії

1. **Фаза скидання та ідентифікації:** драйвер хоста надсилає команду `CMD52` за адресою `0x00` простору Function 0 для зчитування версії специфікації SDIO. Пристрій повертає значення `0x32` (SDIO 3.00, формат CCCR 2.00). На цьому етапі хост перевіряє сумісність форматів та підтверджує готовність внутрішніх регістрів.
2. **Фаза активації логічної функції:** драйвер записує біт `IOE1` (`0x02`) у регістр `IO_ENABLE` (CCCR `0x02`), переводячи радіочастотний тракт Функції 1 у робочий стан. Після цього драйвер входить у цикл опитування регістру `IO_READY` (CCCR `0x03`), доки апаратна частина не виставить біт готовності `IOR1`. Це запобігає спробам читання чи запису в неініціалізовану пам'ять модуля.
3. **Фаза конфігурації блокового режиму:** драйвер програмує робочий розмір сектора у регістрах FBR Функції 1 (`0x110` — молодший байт, `0x111` — старший байт), записуючи значення 512 байтів (`0x0200`). Це значення використовується апаратним DMA-контролером для розбиття мережевих кадрів на пакети фіксованої довжини без залишку.
4. **Фаза налаштування переривань:** записом у регістр `INT_ENABLE` (CCCR `0x04`) активуються маска переривань для Функції 1 та глобальний прапорець дозволу `IENM`. З цього моменту будь-яка подія всередині модуля Wi-Fi викликає апаратне стягування лінії DAT1 до рівня землі під час пауз між передачами даних.
5. **Фаза генерації та обслуговування подій:** при надходженні бездротового кадру (наприклад, Beacon або Data-пакета стандарту IEEE 802.11) емулятор пристрою заповнює внутрішній кільцевий буфер FIFO, виставляє біт `0x02` у регістрі `INT_PENDING` (CCCR `0x05`) та опускає віртуальну сигнальну лінію DAT1 у низький логічний рівень (`0`).
6. **Фаза вичитування даних:** переривання активує потік обробника хоста. Хост захоплює м'ютекс шини (`claim_host`), зчитує статус очікуючих запитів через `CMD52`, ініціює блокову транзакцію `CMD53` у режимі фіксованої адреси (`OpCode=0`) для вичитування корисного навантаження з порту FIFO `0x00050` і після спустошення буфера звільняє лінію переривання.

---

## 2. Алгоритмічний розрахунок продуктивності та накладних витрат

Головною відмінністю між командами прямого доступу `CMD52` та розширеного пакетного доступу `CMD53` є ефективність використання смуги пропускання шини при передачі масивів даних.

### Розрахунок часу передачі пакета Ethernet MTU (1500 байтів)

Розглянемо передачу стандартного мережевого кадру розміром `N = 1500 байтів` при тактовій частоті шини `f_clk = 50 МГц` (період такту `T_clk = 20 нс`) у 4-бітному режимі шини (передача 4 бітів, тобто 0.5 байта за один такт `CLK`).

#### Варіант А: Передача через побайтові команди CMD52

Кожен байт вимагає повної 48-бітної команди на лінії CMD, затримки відповіді `Ncr ≈ 4 такти`, 48-бітної відповіді R5 та інтервалу перепочинку `Nrc ≈ 2 такти`.

```
Час_CMD52(1 байт)
= (48 + 4 + 48 + 2) · T_clk
= 102 такти · 20 нс
= 2040 нс = 2.04 мкс

Сумарний_час_CMD52(1500 байтів)
= 1500 · 2.04 мкс
= 3060 мкс ≈ 3.06 мс

Ефективна_швидкість_CMD52
= 1500 байтів / 0.00306 с
≈ 0.49 МБ/с (3.92 Мбіт/с)
```

Утилізація 4-бітної шини даних DAT[0..3] становить рівно `0%`, оскільки лінії даних взагалі не використовуються, а командна лінія CMD перевантажена 1500 окремими транзакціями.

#### Варіант Б: Передача через пакетну команду CMD53 у блоковому режимі (Block Mode = 512 байтів)

Кадр розміром 1500 байтів упаковується у 3 блоки по 512 байтів (разом 1536 байтів з урахуванням 36 байтів службового заповнення). Передача виконується за **одну** команду `CMD53`.

Транзакція на лінії CMD:
- Кадр команди CMD53: `48 тактів`.
- Затримка відповіді Ncr: `4 такти`.
- Відповідь R5: `48 тактів`.

Транзакція на лініях даних DAT[0..3] для 3 блоків:
- Для кожного блока (512 байтів):
  - Стартовий біт: `1 такт`.
  - Передача 512 байтів у 4-бітному режимі (по 2 нібли на байт): `512 · 2 = 1024 такти`.
  - Контрольна сума CRC16 (16 бітів на лінію, по 1 біту за такт): `16 тактів`.
  - Стоповий біт: `1 такт`.
  - Токен відповіді та пауза між блоками: `6 тактів`.
  - Разом на один блок: `1 + 1024 + 16 + 1 + 6 = 1048 тактів`.
- Разом для 3 блоків: `3 · 1048 = 3144 такти`.

```
Сумарний_час_CMD53
= (48 + 4 + 48) + 3144 тактів
= 3244 такти · 20 нс
= 64.88 мкс

Ефективна_швидкість_CMD53
= 1500 байтів / 0.00006488 с
≈ 23.12 МБ/с (184.96 Мбіт/с)
```

Застосування блокового режиму `CMD53` скорочує час зайнятості шини у `47.1 раза` (з 3.06 мс до 64.88 мкс) і піднімає реальну пропускну здатність каналу майже до теоретичної межі 50-мегагерцової шини (25 МБ/с).

---

## 3. Реалізація моделі та драйвера на C та C++

Нижче наведено самодостатню реалізацію протокольної моделі. Усі алгоритми обчислення контрольних сум, обробки кадрових структур та синхронізації реалізовано мовою C за стандартом C99 та мовою C++ за стандартом C++20 із застосуванням сучасних ідіом проектування (RAII-обгортки захоплення шини, шаблони безпечної роботи з пам'яттю `std::span`, контейнери `std::array` та обробка помилок через `std::expected`).

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CCCR_SDIO_REV       0x00
#define CCCR_IO_ENABLE      0x02
#define CCCR_IO_READY       0x03
#define CCCR_INT_ENABLE     0x04
#define CCCR_INT_PENDING    0x05
#define CCCR_BUS_IF_CTRL    0x07

#define FBR_FUNC1_BASE      0x100
#define FBR_BLK_SIZE_L      (FBR_FUNC1_BASE + 0x10)
#define FBR_BLK_SIZE_H      (FBR_FUNC1_BASE + 0x11)

#define FUNC1_RX_FIFO_REG   0x00050
#define FUNC1_STATUS_REG    0x00054

/* ── 1. Емулятор апаратної частини SDIO-пристрою ─────────────────────────── */
typedef struct {
    uint8_t cccr[0x100];
    uint8_t func1_regs[0x20000];
    uint8_t rx_fifo[4096];
    size_t  rx_fifo_head;
    size_t  rx_fifo_tail;
    bool    dat1_irq_asserted;
} sdio_device_sim_t;

/* Обчислення контрольної суми CRC7 для кадру команд */
static uint8_t calc_crc7(const uint8_t *data, size_t len) {
    uint8_t crc = 0;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int b = 0; b < 8; ++b) {
            if (crc & 0x80)
                crc = (uint8_t)((crc << 1) ^ 0x12); /* Поліном x^7 + x^3 + 1 */
            else
                crc <<= 1;
        }
    }
    return (uint8_t)(crc >> 1);
}

void sdio_device_init(sdio_device_sim_t *dev) {
    memset(dev, 0, sizeof(*dev));
    dev->cccr[CCCR_SDIO_REV] = 0x32; /* SDIO 3.00, CCCR 2.00 */
    dev->cccr[CCCR_BUS_IF_CTRL] = 0x00; /* 1-бітний режим за замовчуванням */
}

/* Обробка команди прямого доступу CMD52 (1 байт) */
int sdio_device_cmd52(sdio_device_sim_t *dev, bool write, uint8_t func,
                      uint32_t addr, uint8_t val, uint8_t *resp_val) {
    if (func == 0) {
        if (addr >= sizeof(dev->cccr)) return -1;
        if (write) {
            if (addr == CCCR_IO_ENABLE) {
                dev->cccr[CCCR_IO_ENABLE] = val;
                dev->cccr[CCCR_IO_READY] |= (uint8_t)(val & 0xFE); /* Апаратна готовність */
            } else if (addr == CCCR_INT_ENABLE) {
                dev->cccr[CCCR_INT_ENABLE] = val;
            } else if (addr == CCCR_BUS_IF_CTRL) {
                dev->cccr[CCCR_BUS_IF_CTRL] = val;
            }
        }
        if (resp_val) *resp_val = dev->cccr[addr];
        return 0;
    } else if (func == 1) {
        if (addr >= sizeof(dev->func1_regs)) return -1;
        if (write) dev->func1_regs[addr] = val;
        if (resp_val) *resp_val = dev->func1_regs[addr];
        return 0;
    }
    return -1;
}

/* Обробка команди розширеного доступу CMD53 (пакети) */
int sdio_device_cmd53(sdio_device_sim_t *dev, bool write, uint8_t func,
                      bool block_mode, bool inc_addr, uint32_t addr,
                      uint8_t *buf, size_t len) {
    if (func != 1) return -1;

    if (!write) { /* Читання з пристрою в пам'ять хоста */
        if (!inc_addr && addr == FUNC1_RX_FIFO_REG) {
            /* Потоковий вивід із порту FIFO без зміни адреси */
            for (size_t i = 0; i < len; ++i) {
                if (dev->rx_fifo_tail != dev->rx_fifo_head) {
                    buf[i] = dev->rx_fifo[dev->rx_fifo_tail++];
                    if (dev->rx_fifo_tail >= sizeof(dev->rx_fifo)) dev->rx_fifo_tail = 0;
                } else {
                    buf[i] = 0x00; /* Заповнення нулями при спустошенні */
                }
            }
            /* Якщо черга порожня — скидаємо переривання на лінії DAT1 */
            if (dev->rx_fifo_tail == dev->rx_fifo_head) {
                dev->dat1_irq_asserted = false;
                dev->cccr[CCCR_INT_PENDING] &= (uint8_t)~0x02;
            }
            return 0;
        } else if (inc_addr) {
            /* Читання масиву пам'яті з автоінкрементом адреси */
            if (addr + len > sizeof(dev->func1_regs)) return -1;
            memcpy(buf, &dev->func1_regs[addr], len);
            return 0;
        }
    }
    return -1;
}

/* Додавання вхідного бездротового кадру в чергу FIFO */
void sdio_device_inject_packet(sdio_device_sim_t *dev, const uint8_t *pkt, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        dev->rx_fifo[dev->rx_fifo_head++] = pkt[i];
        if (dev->rx_fifo_head >= sizeof(dev->rx_fifo)) dev->rx_fifo_head = 0;
    }
    if (dev->cccr[CCCR_INT_ENABLE] & 0x02) {
        dev->cccr[CCCR_INT_PENDING] |= 0x02;
        dev->dat1_irq_asserted = true; /* Стягуємо лінію DAT1 до GND */
    }
}

/* ── 2. Драйвер хост-контролера та клієнтський модуль ─────────────────────── */
typedef struct {
    sdio_device_sim_t *target;
    bool host_locked;
    uint16_t func1_block_size;
} sdio_host_driver_t;

void sdio_claim_host(sdio_host_driver_t *drv) {
    drv->host_locked = true;
}

void sdio_release_host(sdio_host_driver_t *drv) {
    drv->host_locked = false;
}

int sdio_init_func1(sdio_host_driver_t *drv) {
    sdio_claim_host(drv);

    uint8_t rev = 0;
    sdio_device_cmd52(drv->target, false, 0, CCCR_SDIO_REV, 0, &rev);
    printf("[Host C] SDIO Spec Rev: 0x%02X\n", rev);

    /* 1. Активація живлення логіки Функції 1 */
    sdio_device_cmd52(drv->target, true, 0, CCCR_IO_ENABLE, 0x02, NULL);

    /* 2. Опитування прапорця готовності IO_READY */
    uint8_t ready = 0;
    for (int retry = 0; retry < 5; ++retry) {
        sdio_device_cmd52(drv->target, false, 0, CCCR_IO_READY, 0, &ready);
        if (ready & 0x02) break;
    }
    if (!(ready & 0x02)) {
        sdio_release_host(drv);
        return -1;
    }

    /* 3. Встановлення розміру блока 512 байтів */
    drv->func1_block_size = 512;
    sdio_device_cmd52(drv->target, true, 0, FBR_BLK_SIZE_L, 0x00, NULL);
    sdio_device_cmd52(drv->target, true, 0, FBR_BLK_SIZE_H, 0x02, NULL);

    /* 4. Дозвіл переривань для Функції 1 та Master Enable */
    sdio_device_cmd52(drv->target, true, 0, CCCR_INT_ENABLE, 0x03, NULL);

    printf("[Host C] Функція 1 готова, BlockSize=%u байтів, IRQ увімкнено\n",
           drv->func1_block_size);

    sdio_release_host(drv);
    return 0;
}

void sdio_poll_irq_and_service(sdio_host_driver_t *drv) {
    if (!drv->target->dat1_irq_asserted) return;

    sdio_claim_host(drv);
    uint8_t pending = 0;
    sdio_device_cmd52(drv->target, false, 0, CCCR_INT_PENDING, 0, &pending);

    if (pending & 0x02) {
        uint8_t packet_buffer[512];
        /* Зчитування 512-байтового блока через CMD53 Fixed Address */
        sdio_device_cmd53(drv->target, false, 1, true, false,
                          FUNC1_RX_FIFO_REG, packet_buffer, sizeof(packet_buffer));

        printf("[Host C IRQ] Зчитано мережевий кадр: \"%s\" (довжина %zu байтів)\n",
               (char*)packet_buffer, strlen((char*)packet_buffer));
    }
    sdio_release_host(drv);
}

int main(void) {
    sdio_device_sim_t dev;
    sdio_device_init(&dev);

    sdio_host_driver_t host = { .target = &dev, .host_locked = false };
    if (sdio_init_func1(&host) != 0) {
        printf("Помилка ініціалізації SDIO\n");
        return 1;
    }

    /* Симуляція надходження кадру Wi-Fi */
    const char *test_frame = "IEEE 802.11 Beacon: SSID=Lab_Network, Ch=6, RSSI=-42dBm";
    sdio_device_inject_packet(&dev, (const uint8_t*)test_frame, strlen(test_frame) + 1);

    /* Обробка запиту переривання */
    sdio_poll_irq_and_service(&host);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <expected>
#include <string_view>
#include <cstdint>
#include <cstring>

namespace sdio {

enum class Error {
    InvalidFunction,
    OutOfRange,
    DeviceNotReady,
    CrcMismatch,
    Timeout,
    BusBusy
};

constexpr uint32_t CCCR_SDIO_REV    = 0x00;
constexpr uint32_t CCCR_IO_ENABLE   = 0x02;
constexpr uint32_t CCCR_IO_READY    = 0x03;
constexpr uint32_t CCCR_INT_ENABLE  = 0x04;
constexpr uint32_t CCCR_INT_PENDING = 0x05;
constexpr uint32_t CCCR_BUS_IF_CTRL = 0x07;

constexpr uint32_t FBR_BLK_SIZE_L   = 0x110;
constexpr uint32_t FBR_BLK_SIZE_H   = 0x111;

constexpr uint32_t FUNC1_RX_FIFO    = 0x00050;

/* ── 1. Емулятор апаратної частини SDIO-периферії ─────────────────────────── */
class SdioDeviceSim {
public:
    SdioDeviceSim() {
        cccr_.fill(0);
        func1_regs_.fill(0);
        rx_fifo_.fill(0);
        cccr_[CCCR_SDIO_REV] = 0x32; /* SDIO 3.00, CCCR 2.00 */
    }

    std::expected<uint8_t, Error> cmd52(bool write, uint8_t func, uint32_t addr, uint8_t val) {
        if (func == 0) {
            if (addr >= cccr_.size()) return std::unexpected(Error::OutOfRange);
            if (write) {
                if (addr == CCCR_IO_ENABLE) {
                    cccr_[CCCR_IO_ENABLE] = val;
                    cccr_[CCCR_IO_READY] |= static_cast<uint8_t>(val & 0xFE);
                } else if (addr == CCCR_INT_ENABLE || addr == CCCR_BUS_IF_CTRL) {
                    cccr_[addr] = val;
                }
            }
            return cccr_[addr];
        } else if (func == 1) {
            if (addr >= func1_regs_.size()) return std::unexpected(Error::OutOfRange);
            if (write) func1_regs_[addr] = val;
            return func1_regs_[addr];
        }
        return std::unexpected(Error::InvalidFunction);
    }

    std::expected<void, Error> cmd53_read(uint8_t func, bool inc_addr, uint32_t addr, std::span<uint8_t> dst) {
        if (func != 1) return std::unexpected(Error::InvalidFunction);

        if (!inc_addr && addr == FUNC1_RX_FIFO) {
            for (auto &byte : dst) {
                if (fifo_tail_ != fifo_head_) {
                    byte = rx_fifo_[fifo_tail_++];
                    if (fifo_tail_ >= rx_fifo_.size()) fifo_tail_ = 0;
                } else {
                    byte = 0x00;
                }
            }
            if (fifo_tail_ == fifo_head_) {
                dat1_irq_ = false;
                cccr_[CCCR_INT_PENDING] &= static_cast<uint8_t>(~0x02);
            }
            return {};
        } else if (inc_addr) {
            if (addr + dst.size() > func1_regs_.size()) return std::unexpected(Error::OutOfRange);
            std::memcpy(dst.data(), &func1_regs_[addr], dst.size());
            return {};
        }
        return std::unexpected(Error::OutOfRange);
    }

    void inject_packet(std::span<const uint8_t> pkt) {
        for (uint8_t b : pkt) {
            rx_fifo_[fifo_head_++] = b;
            if (fifo_head_ >= rx_fifo_.size()) fifo_head_ = 0;
        }
        if (cccr_[CCCR_INT_ENABLE] & 0x02) {
            cccr_[CCCR_INT_PENDING] |= 0x02;
            dat1_irq_ = true;
        }
    }

    [[nodiscard]] bool is_dat1_irq_active() const noexcept { return dat1_irq_; }

private:
    std::array<uint8_t, 256>    cccr_{};
    std::array<uint8_t, 131072> func1_regs_{};
    std::array<uint8_t, 4096>   rx_fifo_{};
    size_t fifo_head_{0};
    size_t fifo_tail_{0};
    bool   dat1_irq_{false};
};

/* ── 2. RAII-обгортка захисту та блокування шини хоста ─────────────────────── */
class SdioHostDriver;

class SdioHostGuard {
public:
    explicit SdioHostGuard(SdioHostDriver &drv);
    ~SdioHostGuard();
    SdioHostGuard(const SdioHostGuard &) = delete;
    SdioHostGuard &operator=(const SdioHostGuard &) = delete;

private:
    SdioHostDriver &drv_;
};

/* ── 3. Клієнтський драйвер хоста на C++ ─────────────────────────────────── */
class SdioHostDriver {
public:
    explicit SdioHostDriver(SdioDeviceSim &dev) : target_(dev) {}

    void lock()   noexcept { locked_ = true; }
    void unlock() noexcept { locked_ = false; }
    [[nodiscard]] bool is_locked() const noexcept { return locked_; }

    std::expected<void, Error> init_device() {
        SdioHostGuard guard(*this);

        auto rev = target_.cmd52(false, 0, CCCR_SDIO_REV, 0);
        if (!rev) return std::unexpected(rev.error());
        std::cout << "[Host C++] SDIO Ревізія: 0x" << std::hex << static_cast<int>(*rev) << std::dec << "\n";

        /* Активація Функції 1 */
        auto en_res = target_.cmd52(true, 0, CCCR_IO_ENABLE, 0x02);
        if (!en_res) return std::unexpected(en_res.error());

        /* Очікування готовності IO_READY */
        bool ready = false;
        for (int i = 0; i < 5; ++i) {
            auto r = target_.cmd52(false, 0, CCCR_IO_READY, 0);
            if (r && (*r & 0x02)) {
                ready = true;
                break;
            }
        }
        if (!ready) return std::unexpected(Error::DeviceNotReady);

        /* Налаштування розміру блока 512 байтів */
        block_size_ = 512;
        target_.cmd52(true, 0, FBR_BLK_SIZE_L, 0x00);
        target_.cmd52(true, 0, FBR_BLK_SIZE_H, 0x02);

        /* Увімкнення переривань */
        target_.cmd52(true, 0, CCCR_INT_ENABLE, 0x03);

        std::cout << "[Host C++] Пристрій налаштовано: Функція 1 готова, BlockSize="
                  << block_size_ << " байтів\n";
        return {};
    }

    void handle_irq() {
        if (!target_.is_dat1_irq_active()) return;

        SdioHostGuard guard(*this);
        auto pending = target_.cmd52(false, 0, CCCR_INT_PENDING, 0);
        if (pending && (*pending & 0x02)) {
            std::array<uint8_t, 512> rx_buf{};
            auto res = target_.cmd53_read(1, false, FUNC1_RX_FIFO, rx_buf);
            if (res) {
                std::string_view sv(reinterpret_cast<char*>(rx_buf.data()));
                std::cout << "[Host C++ IRQ] Отримано пакет через CMD53: \""
                          << sv << "\" (розмір " << sv.size() << " байтів)\n";
            }
        }
    }

private:
    SdioDeviceSim &target_;
    bool          locked_{false};
    uint16_t      block_size_{0};
};

inline SdioHostGuard::SdioHostGuard(SdioHostDriver &drv) : drv_(drv) { drv_.lock(); }
inline SdioHostGuard::~SdioHostGuard() { drv_.unlock(); }

} // namespace sdio

int main() {
    sdio::SdioDeviceSim dev;
    sdio::SdioHostDriver host(dev);

    if (auto res = host.init_device(); !res) {
        std::cerr << "Помилка ініціалізації SDIO\n";
        return 1;
    }

    std::string_view payload = "IEEE 802.11ac Frame: Rate=433Mbps, SNR=32dB, Encryption=WPA3-SAE";
    dev.inject_packet(std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(payload.data()), payload.size() + 1));

    host.handle_irq();
    return 0;
}
```
:::

---

## 4. Апаратна інтеграція: мікроконтролери ESP32 як SDIO Slave

На практиці концепція емульованого модуля SDIO повністю відповідає апаратній структурі реальних мікроконтролерів. Зокрема, у сімействах мікроконтролерів ESP32, ESP32-S3 та ESP32-C3 від компанії Espressif реалізовано повноцінний апаратний периферійний блок **SDIO Slave Controller**, що дозволяє використовувати мікроконтролер як недорогий бездротовий співпроцесор.

### Карта апаратних регістрів та лічильників черги

Апаратний блок SDIO Slave у ESP32 автоматично підтримує специфікацію SDIO 2.00 / 3.00 і надає системі наступні керуючі структури:

1. **Регістр довжини пакета в черзі (`SLCHOST_PKT_LEN`):** коли прошивка ESP32 формує вихідний мережевий кадр (наприклад, пакет від сканера Wi-Fi), вона завантажує його в оперативну пам'ять, формує зв'язаний список дескрипторів DMA та записує кількість готових байтів у регістр `SLCHOST_PKT_LEN`. Апаратна логіка ESP32 автоматично стягує лінію DAT1 до низького рівня.
2. **Вікно доступу до дескрипторів DMA (`SLCHOST_SLCDMA_FIFO`):** адреса порту `0x00050` у просторі Функції 1 відображається безпосередньо на внутрішній апаратний арбітр шини AHB. Коли зовнішній Linux-хост надсилає команду `CMD53 Read` за цією фіксованою адресою, вбудований контролер DMA автоматично вичитує дані з RAM без участі центрального ядра CPU ESP32.
3. **Регістри переривання хоста (`SLCHOST_INT_RAW` та `SLCHOST_INT_CLR`):** дозволяють основному хосту надсилати повідомлення та синхронізувати транзакції з мікроконтролером через команду запису `CMD52`.

```
                  ┌────────────────────────────────────────┐
                  |      Linux Host (Raspberry Pi 4)       |
                  |     drivers/net/wireless/esp32_sdio    |
                  └───────────────────┬────────────────────┘
                                      │  Шина SDIO (CLK, CMD, DAT[0..3])
                                      ▼
                  ┌────────────────────────────────────────┐
                  |          ESP32 SDIO Slave              |
                  |  ┌──────────────────────────────────┐  |
                  |  │ Апаратний блок SDIO (AHB Bridge) │  |
                  |  └────────────────┬─────────────────┘  |
                  |                   │ Внутрішній DMA     |
                  |  ┌────────────────▼─────────────────┐  |
                  |  │ SRAM Буфери мережевих кадрів     │  |
                  |  └──────────────────────────────────┘  |
                  └────────────────────────────────────────┘
```

Така апаратна архітектура повністю розвантажує обчислювальні ресурси обох пристроїв: процесор Linux-хоста ініціює DMA-транзакцію, а мікроконтролер ESP32 апаратно передає пакети на максимальній швидкості шини 50 МГц (25 МБ/с), що є достатнім для забезпечення стабільного трафіку Wi-Fi на рівні 150 Мбіт/с.

---

## 5. Діагностика та трасування стека SDIO в Linux (Ftrace & Tracepoints)

Під час налагодження реальних драйверів бездротових модулів (наприклад, драйвера Broadcom `brcmfmac` або Marvell `mwifiex`) найпотужнішим інструментом діагностики є вбудована система трасування ядра Linux (Ftrace / Tracepoints).

### Активація подій трасування підсистеми MMC/SDIO

Підсистема ядра `drivers/mmc/core/` містить статичні точки трасування, що реєструють початок та завершення кожної команди `CMD52` та `CMD53`. Для активації трасування у просторі `debugfs` виконуються наступні системні команди:

```bash
# Монтування віртуальної файлової системи debugfs (якщо не змонтована)
mount -t debugfs nodev /sys/kernel/debug

# Увімкнення трасування запитів та відповідей шини MMC/SDIO
echo 1 > /sys/kernel/debug/tracing/events/mmc/mmc_request_start/enable
echo 1 > /sys/kernel/debug/tracing/events/mmc/mmc_request_done/enable

# Очищення буфера та старт запису
echo > /sys/kernel/debug/tracing/trace
echo 1 > /sys/kernel/debug/tracing/tracing_on
```

### Аналіз реального логу трасування транзакцій

Після надходження мережевого пакета у файлі `/sys/kernel/debug/tracing/trace` з'являється детальна хронологія подій із точними мітками часу та параметрами аргументів:

```text
# tracer: nop
#
#           TASK-PID   CPU#    TIMESTAMP  FUNCTION
#              | |       |         |         |
     irq/42-mmc0-182   [001]  142.105420: mmc_request_start: mmc0: start CMD52 arg 0x0a000000 flags 0x00000195
     irq/42-mmc0-182   [001]  142.105428: mmc_request_done:  mmc0: end   CMD52 tag 0 status 0 resp 0x00000200
     irq/42-mmc0-182   [001]  142.105435: mmc_request_start: mmc0: start CMD53 arg 0x12000001 flags 0x000001b5 blksz 512 blocks 1
     irq/42-mmc0-182   [001]  142.105470: mmc_request_done:  mmc0: end   CMD53 tag 0 status 0 resp 0x00000000
```

- **Рядок 1:** потік обробки переривань `irq/42-mmc0` надсилає `CMD52` з аргументом `0x0A000000` (читання регістру `INT_PENDING` за адресою `0x05` у Функції 0).
- **Рядок 2:** через 8 мікросекунд контролер отримує відповідь `0x00000200` (біт 1 встановлено, що свідчить про наявність пакета у Функції 1).
- **Рядок 3:** драйвер негайно формує запит `CMD53` з аргументом `0x12000001` (читання 1 блока розміром 512 байтів із фіксованого регістра FIFO Функції 1).
- **Рядок 4:** транзакція DMA завершується за 35 мікросекунд із кодом статусу `0` (успіх), після чого пакет передається у мережевий стек `netif_rx()`.

---

## 6. Керування енергоспоживанням (Runtime PM та Suspend/Resume)

У мобільних телефонах та портативних автономних приладах бездротовий модуль є одним із найбільших споживачів струму (до 200–400 мА в активному режимі передачі). Специфікація SDIO надає апаратні та програмні механізми переведення модуля у стани глибокого сну зі збереженням здатності розбудити хост.

### Конфігурація прапорців збереження живлення в ядрі Linux

Під час переходу операційної системи Linux у стан сну (System Suspend to RAM) клієнтський драйвер бездротового модуля викликає функцію налаштування політики живлення:

```c
static int my_sdio_suspend(struct device *dev)
{
    struct sdio_func *func = dev_to_sdio_func(dev);
    mmc_pm_flag_t pm_flags = 0;

    /* Перевіряємо, чи підтримує хост збереження живлення слота */
    pm_flags = sdio_get_host_pm_caps(func);
    if (!(pm_flags & MMC_PM_KEEP_POWER))
        return -ENOTSUPP;

    /* Залишаємо живлення модуля та дозволяємо асинхронне пробудження по DAT1 */
    if (sdio_set_host_pm_flags(func, MMC_PM_KEEP_POWER | MMC_PM_WAKE_SDIO_IRQ))
        return -EBUSY;

    return 0;
}
```

Прапорець `MMC_PM_KEEP_POWER` вказує хост-контролеру не вимикати стабілізатор напруги LDO лінії 3.3 В / 1.8 В, що зберігає прошивку в оперативній пам'яті Wi-Fi модуля. Прапорець `MMC_PM_WAKE_SDIO_IRQ` переводить лінію DAT1 хост-контролера у режим асинхронного детектора фронту спаду при зупиненій тактовій частоті шини CLK. Коли модуль фіксує вхідний пакет Wake-on-WLAN, він стягує лінію DAT1 до землі, пробуджуючи центральний процесор платформи.

---

## 7. Схемотехніка та цілісність сигналів швидкісної шини SDIO

Під час фізичного проектування друкованих плат із розпаяними модулями SDIO висока тактова частота (50–208 МГц) вимагає суворого дотримання правил високочастотного трасування:

1. **Узгодження довжини провідників (Trace Length Matching):**
   Усі сигнальні лінії шини (CLK, CMD, DAT0, DAT1, DAT2, DAT3) повинні мати строго вирівняну електричну довжину на платі. Допустима розбіжність затримки поширення сигналу між тактовою лінією CLK та будь-якою з ліній даних DAT[0..3] не повинна перевищувати `Δt < 100 пс` (що відповідає різниці довжини трас на склотекстоліті FR4 менше ніж `±1.5 мм`). Порушення цього правила у швидкісних режимах SDR50/SDR104 призводить до фазового зсуву (Skew), порушення інтервалів встановлення (Setup Time) та утримання (Hold Time), що викликає постійні помилки CRC16 на лініях даних.

2. **Контрольований хвильовий опір:**
   Траси шини SDIO розводяться як мікросмужкові лінії з одиничним характеристичним імпедансом `Z₀ = 50 Ом` відносно суцільного опорного шару заземлення (GND plane). Безпосередньо біля виводів передавача процесора хоста встановлюють послідовні демпферні резистори номіналом `22–33 Ом` для гасіння паразитних відбиттів від кінців лінії.

3. **Зовнішні підтягуючі резистори (Pull-Up Resistors):**
   Лінії CMD та DAT[0..3] обов'язково підтягуються до шини живлення I/O (3.3 В або 1.8 В) резисторами номіналом `10–47 кОм`. Це запобігає переходу сигнальних ліній у нестійкий плаваючий стан під час тристабілізації виходів (наприклад, під час передачі естафети Turnaround Bits або у паузах між пакетами).

---

## 8. Інженерні пастки, стан гонитви та стійкість до збоїв

При переході від програмної симуляції до реальних апаратних платформ (контролери SDHCI на ARM/x86 SoC або блоки SDIO на STM32/ESP32) інженер стикається з низкою критичних аспектів синхронізації та обробки виняткових станів.

### Стан гонитви (Race Condition) між передачею пакетів та перериванням

У високошвидкісних бездротових адаптерах часто виникає ситуація, коли периферійний модуль отримує новий бездротовий кадр у той самий момент, коли хост передає вихідний пакет через команду `CMD53 Write`.

Оскільки під час активної передачі блоків даних по лініях DAT[0..3] лінія DAT1 не може використовуватися для сигналізації IRQ (якщо тільки в регістрі `CARD_CAPABILITY` не активовано розширений режим `E4MI`), модуль зберігає стан запиту переривання у внутрішньому тригері. Щойно хост передає стоповий біт і шина переходить у фазу спокою (Idle Phase), периферія негайно опускає лінію DAT1 у нуль.

Якщо драйвер хоста після завершення запису не перевіряє стан лінії DAT1, виникає затримка доставки вхідного пакета. Правильно спроектований драйвер використовує чергу обробки переривань із двофазною перевіркою: апаратний тригер за спадом рівня плюс обов'язкова програмна перевірка регістра `INT_PENDING` наприкінці кожної транзакції `CMD53`.

### Взаємне блокування при повторному захопленні шини (Deadlock)

У ядрі Linux диспетчеризація внутрішньосмугових переривань виконується виділеним потоком `sdio_irq_thread`. Цей потік перед викликом функції зворотного виклику клієнтського драйвера (`sdio_irq_handler_t`) **самостійно** захоплює м'ютекс контролера шини за допомогою виклику `mmc_claim_host()`.

Якщо драйвер всередині зареєстрованого обробника переривання повторно викличе `sdio_claim_host()`, потік ядра заблокує сам себе назавжди. Це спричинить повне зависання підсистеми зв'язку. Тому всі службові виклики всередині обробника переривань повинні виконувати прямі операції вводу-виводу (`sdio_readb`, `sdio_memcpy_fromio`) без зовнішніх викликів блокування.

### Вирівнювання адрес і розмірів буферів прямого доступу до пам'яті (DMA)

При використанні команди `CMD53` у блоковому режимі апаратні контролери SDHCI (Secure Digital Host Controller Interface) використовують дескрипторні таблиці прямого доступу до пам'яті ADMA2. Контролер ADMA2 вимагає, щоб базові адреси системних буферів пам'яті були вирівняні щонайменше за 4-байтовою (а у багатьох 64-бітних SoC — за 64-байтовою або 128-байтовою) межею рядка процесорного кешу (Cache Line Alignment).

Якщо мережевий стек передає структуру `sk_buff` з невідповідним зсувом заголовків, спроба прямого запуску DMA призведе до апаратного винятку або руйнування сусідніх областей пам'яті. У таких випадках драйвер ядра зобов'язаний або використати проміжний вирівняний буфер підкачування (Bounce Buffer), або передати непарний хвіст кадру окремою байтовою транзакцією `CMD53 Byte Mode`.

### Аварійне скидання завислого каналу передачі (IO_ABORT)

Якщо під час виконання тривалого блокового читання через `CMD53` відбувається апаратний збій периферійного пристрою або втрата сигналу тактування CLK, лінія DAT0 може залишитися заблокованою у стані `BUSY` (низький рівень). Для відновлення працездатності шини без повного вимикання живлення драйвер надсилає команду прямого доступу `CMD52` у регістр аварійного переривання `IO_ABORT` (CCCR `0x06`).

Запис номера завислої функції у біти `AS[2:0]` змушує апаратний автомат пристрою негайно скинути внутрішні вказівники FIFO, завершити генерацію циклічних кодів CRC16 і повернути лінії DAT[0..3] у стан високого імпедансу. Після цього хост-контролер може безпечно повторити транзакцію або перезапустити функцію.
