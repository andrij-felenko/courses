# ⚙️ Драйвер 3-провідного арбітражу пакетів (PTA) співіснування

Проєкт реалізує кінцевий автомат (FSM) та низькорівневий драйвер 3-провідного апаратного інтерфейсу арбітражу пакетів (Packet Traffic Arbitration — PTA, стандартизованого в IEEE 802.15.2). Драйвер керує виводами `COEX_REQ`, `COEX_PRI` та `COEX_GNT` у реальному часі з мікросекундною точністю, забезпечуючи пріоритетний доступ до радіоефіру та антени для Bluetooth Low Energy або IEEE 802.15.4 під час активності потужного передавача Wi-Fi на одній платі.

---

## 1. Архітектура апаратного інтерфейсу та часові контракти

3-провідна схема арбітражу базується на трьох дискретних цифрових лініях зв'язку між вторинним радіоконтролером (BLE/Zigbee клієнт) та головним арбітром (Wi-Fi SoC):

1. **`COEX_REQ` (Вихід клієнта -> Вхід арбітра):** Запит на захоплення ефіру або антени. Виставляється за час випередження `t_req` (типово від 20 до 50 мкс) до фактичного увімкнення передавача або приймача радіокадру. Цей часовий інтервал необхідний арбітру Wi-Fi, щоб завершити передачу поточного OFDM-символу або відкласти відправку наступного кадру в черзі MAC.
2. **`COEX_PRI` (Вихід клієнта -> Вхід арбітра):** Рівень пріоритету транзакції. Логічна одиниця сигналізує про критичну подію, втрата якої призведе до розриву радіолінка (подія з'єднання BLE Connection Event, прийом маяка синхронізації, відправка службового підтвердження ACK). Логічний нуль встановлюється для фонових задач (неперіодичне сканування ефіру, некритична телеметрія).
3. **`COEX_GNT` (Вхід клієнта <- Вихід арбітра):** Сигнал дозволу (Grant) від арбітра Wi-Fi. Високий рівень дозволяє клієнту перемкнути високочастотний RF-перемикач на свій тракт і розпочати радіотранзакцію. Якщо арбітр скидає лінію `COEX_GNT` у нуль під час активної транзакції (Preemption), клієнт зобов'язаний негайно зупинити передачу (TX Abort) протягом не більше ніж 5 мкс, щоб уникнути пошкодження вихідних каскадів.

---

## 2. Кінцевий автомат клієнта PTA

Драйвер клієнта функціонує як детермінований скінченний автомат з п'ятьма базовими станами:

```
  +-------------------------------------------------------------+
  |                                                             |
  v                                                             |
[ IDLE ] --(request)--> [ REQUESTING ] --(GNT=1)--> [ GRANTED ]-+
   ^                           |                        |
   |                        (timeout)               (GNT=0 / abort)
   |                           v                        v
   +-------------------- [ DENIED ]                 [ ABORTED ]--+
                                                        |        |
                                                        +--------+
```

- **`IDLE`:** Лінії `COEX_REQ` та `COEX_PRI` скинуті в нуль. Радіотракт клієнта вимкнено або перебуває в режимі глибокого сну.
- **`REQUESTING`:** Встановлено рівень `COEX_PRI` та піднято `COEX_REQ`. Драйвер очікує підняття лінії `COEX_GNT` з таймаутом `t_timeout` (зазвичай 100 мкс).
- **`GRANTED`:** Дозвіл отримано. Клієнт вмикає синтезатор частоти, активує PA/LNA та здійснює прийом або передачу пакетів.
- **`DENIED`:** Арбітр не надав дозвіл протягом встановленого таймауту або відхилив запит через передачу критичного Wi-Fi кадру (наприклад, Beacon). Клієнт скидає `COEX_REQ` і переносить подію на наступний інтервал.
- **`ABORTED`:** Під час передачі арбітр зняв сигнал `COEX_GNT`. Обробник апаратного переривання негайно записує команду `TX_ABORT` у регістр радіомодуля, знімає запит і переводить систему в безпечний стан.

---

## 3. Реалізація драйвера PTA

:::tabs
@tab C
```c
#include <stdint.h>
#include <stdbool.h>

/* Апаратні часові константи інтерфейсу PTA */
#define PTA_REQ_LEAD_TIME_US   30
#define PTA_GRANT_TIMEOUT_US   100

typedef enum {
    PTA_PRIORITY_LOW = 0,
    PTA_PRIORITY_HIGH = 1
} pta_priority_t;

typedef enum {
    PTA_STATE_IDLE = 0,
    PTA_STATE_REQUESTING,
    PTA_STATE_GRANTED,
    PTA_STATE_DENIED,
    PTA_STATE_ABORTED
} pta_state_t;

typedef struct {
    uint8_t pin_req;
    uint8_t pin_pri;
    uint8_t pin_gnt;
    pta_state_t state;
    pta_priority_t current_priority;
} pta_driver_t;

/* Низькорівневі виклики апаратного рівня (HAL) */
extern void hal_gpio_write(uint8_t pin, bool level);
extern bool hal_gpio_read(uint8_t pin);
extern void hal_delay_us(uint32_t us);
extern void hal_radio_abort_tx(void);

void pta_init(pta_driver_t *drv, uint8_t req, uint8_t pri, uint8_t gnt) {
    drv->pin_req = req;
    drv->pin_pri = pri;
    drv->pin_gnt = gnt;
    drv->state = PTA_STATE_IDLE;
    drv->current_priority = PTA_PRIORITY_LOW;

    hal_gpio_write(drv->pin_req, false);
    hal_gpio_write(drv->pin_pri, false);
}

bool pta_request_access(pta_driver_t *drv, pta_priority_t pri, uint32_t timeout_us) {
    drv->current_priority = pri;
    drv->state = PTA_STATE_REQUESTING;

    /* 1. Виставляємо пріоритет перед підняттям запиту */
    hal_gpio_write(drv->pin_pri, (pri == PTA_PRIORITY_HIGH));
    hal_gpio_write(drv->pin_req, true);

    /* 2. Забезпечуємо мінімальний час попередження для Wi-Fi арбітра */
    hal_delay_us(PTA_REQ_LEAD_TIME_US);

    /* 3. Опитування лінії підтвердження COEX_GNT */
    uint32_t elapsed = 0;
    while (elapsed < timeout_us) {
        if (hal_gpio_read(drv->pin_gnt)) {
            drv->state = PTA_STATE_GRANTED;
            return true;
        }
        hal_delay_us(5);
        elapsed += 5;
    }

    /* Доступ відхилено або таймаут — знімаємо запит */
    hal_gpio_write(drv->pin_req, false);
    hal_gpio_write(drv->pin_pri, false);
    drv->state = PTA_STATE_DENIED;
    return false;
}

void pta_release_access(pta_driver_t *drv) {
    hal_gpio_write(drv->pin_req, false);
    hal_gpio_write(drv->pin_pri, false);
    drv->state = PTA_STATE_IDLE;
}

/* Обробник апаратного переривання на спадний фронт лінії COEX_GNT */
void pta_grant_lost_isr(pta_driver_t *drv) {
    if (drv->state == PTA_STATE_GRANTED) {
        /* Екстрена зупинка радіотракту при відкликанні дозволу арбітром */
        hal_radio_abort_tx();
        hal_gpio_write(drv->pin_req, false);
        hal_gpio_write(drv->pin_pri, false);
        drv->state = PTA_STATE_ABORTED;
    }
}
```
@tab C++
```cpp
#include <cstdint>
#include <chrono>
#include <optional>
#include <expected>

namespace coex {

using namespace std::chrono_literals;

enum class Priority : uint8_t {
    Low = 0,
    High = 1
};

enum class State : uint8_t {
    Idle = 0,
    Requesting,
    Granted,
    Denied,
    Aborted
};

enum class Error : uint8_t {
    Timeout,
    Preempted,
    HardwareFault
};

class HalInterface {
public:
    virtual ~HalInterface() = default;
    virtual void set_gpio(uint8_t pin, bool level) = 0;
    virtual bool read_gpio(uint8_t pin) = 0;
    virtual void delay(std::chrono::microseconds us) = 0;
    virtual void abort_radio_tx() = 0;
};

class PtaArbiter {
public:
    static constexpr auto ReqLeadTime = 30us;

    PtaArbiter(HalInterface& hal, uint8_t req_pin, uint8_t pri_pin, uint8_t gnt_pin)
        : hal_{hal}, req_pin_{req_pin}, pri_pin_{pri_pin}, gnt_pin_{gnt_pin}, state_{State::Idle} {
        hal_.set_gpio(req_pin_, false);
        hal_.set_gpio(pri_pin_, false);
    }

    ~PtaArbiter() {
        release();
    }

    PtaArbiter(const PtaArbiter&) = delete;
    PtaArbiter& operator=(const PtaArbiter&) = delete;

    std::expected<void, Error> request(Priority pri, std::chrono::microseconds timeout = 100us) {
        state_ = State::Requesting;
        hal_.set_gpio(pri_pin_, pri == Priority::High);
        hal_.set_gpio(req_pin_, true);

        hal_.delay(ReqLeadTime);

        auto elapsed = 0us;
        const auto step = 5us;

        while (elapsed < timeout) {
            if (hal_.read_gpio(gnt_pin_)) {
                state_ = State::Granted;
                return {};
            }
            hal_.delay(step);
            elapsed += step;
        }

        release();
        state_ = State::Denied;
        return std::unexpected(Error::Timeout);
    }

    void release() noexcept {
        hal_.set_gpio(req_pin_, false);
        hal_.set_gpio(pri_pin_, false);
        state_ = State::Idle;
    }

    void on_grant_revoked_isr() noexcept {
        if (state_ == State::Granted) {
            hal_.abort_radio_tx();
            hal_.set_gpio(req_pin_, false);
            hal_.set_gpio(pri_pin_, false);
            state_ = State::Aborted;
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }

private:
    HalInterface& hal_;
    uint8_t req_pin_;
    uint8_t pri_pin_;
    uint8_t gnt_pin_;
    State state_;
};

/* RAII-обгортка для автоматичного звільнення радіоефіру */
class [[nodiscard]] ScopedPtaTransaction {
public:
    ScopedPtaTransaction(PtaArbiter& arbiter, Priority pri)
        : arbiter_{arbiter}, acquired_{false} {
        if (auto res = arbiter_.request(pri); res.has_value()) {
            acquired_ = true;
        }
    }

    ~ScopedPtaTransaction() {
        if (acquired_) {
            arbiter_.release();
        }
    }

    [[nodiscard]] bool is_granted() const noexcept { return acquired_; }

private:
    PtaArbiter& arbiter_;
    bool acquired_;
};

} // namespace coex
```
:::

---

## 4. Інтеграція з операційними системами реального часу (RTOS)

У складних прошивках на базі FreeRTOS або Zephyr OS виклик арбітражу не може блокувати ядро процесора в активному циклі `delay_us()`. Для цього застосовують апаратні таймери та черги подій:

1. **Апаратний таймер передпідйому:** Замість програмної затримки `hal_delay_us(30)` мікроконтролер налаштовує апаратний таймер (наприклад, Timer Compare Event) за 30 мкс до наступу запланованої події Bluetooth Link Layer. Таймер піднімає вивід `COEX_REQ` через систему взаємодії периферії (PPI/DPPI в nRF52/nRF53 або DMA Event в STM32) повністю без участі ядра процесора.
2. **Асинхронний обробник Grant:** Лінія `COEX_GNT` заводиться на вивід зовнішнього переривання (EXTI). Якщо сигнал дозволу вже присутній у момент старту слота передачі, радіомодуль запускається апаратно за подією готовності.
3. **Синхронізація з планувальником RTOS:** При відмові в доступі (`DENIED`) стек Bluetooth не блокує інші задачі ОС, а повертає керування планувальнику і призначає таймер повторної спроби (Backoff Timer) відповідно до поточного інтервалу з'єднання (`connInterval`).

---

## 5. Схемотехнічні вимоги та підтягувальні резистори

Під час перехідних процесів — увімкнення живлення, скидання мікроконтролера (Hardware Reset) або оновлення прошивки по повітрю (OTA) — цифрові виводи GPIO перебувають у високоімпедансному стані (Hi-Z). Щоб запобігти неконтрольованій поведінці арбітражу, на платі обов'язково встановлюють зовнішні резистори:

- **Лінія `COEX_REQ`:** Підтяжка до землі (Pull-Down, 10–47 кОм). Гарантує, що під час перезавантаження клієнта Wi-Fi арбітр не бачитиме хибного запиту на захоплення ефіру.
- **Лінія `COEX_PRI`:** Підтяжка до землі (Pull-Down, 10–47 кОм). За замовчуванням встановлює низький пріоритет.
- **Лінія `COEX_GNT`:** Підтяжка до землі (Pull-Down, 10–47 кОм) або до напруги живлення відповідно до логіки за замовчуванням головного арбітра.

---

## 6. Діагностика та налагодження арбітражу за допомогою логічного аналізатора

Під час первинного запуску плати з PTA обов'язково виконують захоплення сигналів логічним аналізатором із частотою дискретизації не менше 50 МГц. На осцилограмі перевіряють три ключові інваріанти:

- **Інваріант випередження:** Інтервал між наростаючим фронтом `COEX_REQ` та початком генерації RF-потужності передавача на виводі антени мусить складати не менше 20 мкс. Якщо радіо вмикається раніше, передавач Wi-Fi не встигає зреагувати і виникає апаратна колізія.
- **Інваріант скидання:** Лінія `COEX_REQ` має спадати в логічний нуль не пізніше ніж через 5 мкс після закінчення останнього біта CRC пакета, інакше Wi-Fi модуль буде необґрунтовано простоювати, знижуючи загальну пропускну здатність TCP/IP.
- **Відсутність «голок» (Glitch Immunity):** Цифрові лінії PTA не повинні мати паразитних імпульсів тривалістю менше 100 нс, які можуть бути спричинені наведеннями від сусідніх шин QSPI або силовими струмами драйверів двигунів.
