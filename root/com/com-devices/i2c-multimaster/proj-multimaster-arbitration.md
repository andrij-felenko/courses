# ⚙️ Обробка втрати арбітражу I2C у багатомайстровій системі

У системах із кількома ведучими мікроконтролерами керування шиною I2C перестає бути детермінованою послідовністю викликів «старт — запис — стоп». Щойно два контролери одночасно намагаються розпочати передачу, апаратний блок одного з них неминуче виявить розбіжність виведеного й зчитаного бітів і зафіксує втрату арбітражу (*Arbitration Lost*, у регістрах зазвичай позначається прапорцем `ARLO` або `AL`).

Якщо драйвер спроєктовано без урахування багатомайстрової специфіки, втрата арбітражу часто призводить до фатальних наслідків: контролер зависає в очікуванні прапорця завершення передачі байта, втрачає запит іншого ведучого, який звертався саме до нього, або миттєво робить повторну спробу й знову врізається в чужу транзакцію. Розберімо, як побудувати надійний, енергоефективний драйвер на базі автомата станів із підтримкою подвійної ролі (ведучий/ведений), обробки переривань та псевдовипадкового експоненційного відступу (*exponential backoff*).

### Анатомія апаратного прапорця ARLO

Сучасні апаратні контролери I2C (наприклад, периферійні блоки мікроконтролерів сімейств STM32, NXP LPC, Texas Instruments MSPM0 або ESP32) виконують контроль арбітражу на рівні кремнієвої логіки безпосередньо в тракті передавача. Під час активної генерації тактового сигналу SCL блок порівняння зчитує логічний рівень на виході вхідного тригера Шмітта лінії SDA в мить, коли лінія SCL перетинає поріг логічної одиниці `VIH`.

Коли контролер намагається відпустити лінію SDA у логічну одиницю (високий імпеданс, підтяжка `Rp`), але виявляє логічний нуль від іншого вузла, кремнієва логіка миттєво виконує чотири апаратні дії:
1. **Негайне відключення вихідного каскаду:** Вимикає вихідний польовий транзистор лінії SDA, залишаючи лінію у вільному стані, щоб не спотворити поточний біт переможця.
2. **Вимкнення внутрішнього тактового генератора:** Припиняє декремент внутрішнього таймера SCL і переходить у пасивний режим спостереження за зовнішнім тактом.
3. **Встановлення статусного біта:** Виставляє біт втрати арбітражу (`ARLO = 1`) у регістрі стану (`I2C_SR1` у класичній периферії або `I2C_ISR` у новіших генераціях STM32).
4. **Генерація переривання помилки:** Якщо в регістрі керування дозволено переривання помилок (`ERRIE = 1`), ядро процесора отримує запит на вектор обробника переривань (ISR).

```
   Регістр статусу I2C (наприклад, STM32 I2C_ISR):
   ┌──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┐
   │ ALERT│ TIMOUT│ PECERR│ OVR  │ ARLO │ NACKF│ BERR │  ... │
   └──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┘
                                  ▲
                                  │ Втрата арбітражу (ARLO = 1)
```

Головна архітектурна пастка полягає в тому, що після виставлення `ARLO` контролер не повинен просто скидати шину й повертатися в стан спокою. Оскільки переможець арбітражу продовжує передавати адресний байт, переможений вузол зобов'язаний негайно перемкнутися в режим веденого (*Slave Receiver*) і перевірити, чи не адресовано поточний пакет його власному інтерфейсу.

### Відмінності регістрових моделей: STM32 v1 проти v2/v3

При написанні низькорівневого коду важливо враховувати генерацію периферійного модуля I2C:
- **Застаріла периферія I2C v1 (STM32F1, F2, F4):** Очищення прапорця `ARLO` вимагає специфічної послідовності: програмного зчитування регістра `I2C_SR1` з наступним записом нуля в біт `ARLO` (або записом регістра `I2C_SR1 = 0`). Пропуск зчитування призводить до того, що прапорець не скидається, викликаючи нескінченний шторм переривань.
- **Сучасна периферія I2C v2/v3 (STM32F7, G0, G4, L4, H7, U5):** Архітектура суттєво спрощена та вдосконалена. Прапорець `ARLO` у регістрі `I2C_ISR` є прапорцем лише для читання, а його апаратне очищення виконується прямим записом логічної одиниці в біт `ARLOCF` окремого регістра очищення переривань `I2C_ICR`. Крім того, блок підтримує автоматичну апаратну фільтрацію цифрових та аналогових завад безпосередньо перед детектором арбітражу через біти `ANFOFF` та `DNF[3:0]` у регістрі `I2C_CR1`.

### Фази виникнення арбітражу в різних точках транзакції

Арбітраж може бути програний не лише на етапі надсилання 7-бітної адреси. Розглянемо чотири типові сценарії, де апаратний блок фіксує подію `ARLO`:

1. **Колізія на адресному байті (Address Phase):** Найпоширеніший випадок. Обидва ведучі одночасно видали `START` і почали передачу адрес. Ведучий, що надсилає вищу за числовим значенням адресу, поступається на першому біті, де в нього одиниця, а у суперника нуль.
2. **Колізія на біті напрямку R/W:** Обидва ведучі звертаються до одного й того самого веденого пристрою (наприклад, сенсора тиску з адресою `0x76`), але перший ведучий хоче записати дані (`W = 0`), а другий — прочитати (`R = 1`). На восьмому такті SCL другий ведучий виставляє `1`, бачить `0` першого ведучого і програє арбітраж. Перший ведучий продовжує запис без перешкод.
3. **Колізія на байтах даних (Data Phase):** Два ведучі одночасно звернулися до одного давача в режимі запису. Їхні адреси збіглися, давач відповів спільним `ACK`, і обидва ведучі почали передавати байти даних. Арбітраж триватиме до першого біта даних, у якому значення розійдуться.
4. **Колізія під час повторного старту (Repeated START vs STOP):** Перший ведучий намагається сформувати умову `Repeated START` (притягує SDA до нуля при високому SCL), а другий ведучий вирішив завершити свою транзакцію умовою `STOP` (відпускає SDA в одиницю при високому SCL). Перший ведучий формує нуль і виграє, а другий фіксує помилку на лінії й аварійно скасовує вихід на шину.

### Арбітраж при 10-бітній адресації та в протоколах SMBus / PMBus

У системах, що використовують розширену 10-бітну адресацію I2C або промислові протоколи керування живленням PMBus, арбітраж має додаткові особливості:

1. **Дводіапазонний арбітраж 10-бітних адрес:** Передача 10-бітної адреси веденого складається з двох байтів. Перший байт містить зарезервований префікс `1111 0XX0b` (де `XX` — два старші біти адреси), а другий байт містить вісім молодших бітів. Якщо два ведучі одночасно звертаються до різних 10-бітних пристроїв із однаковими старшими бітами, арбітраж успішно переходить на другий адресний байт і розв'язується саме там, без порушення стану ведених мікросхем.
2. **Протокол сповіщення хоста SMBus (Host Notify Protocol):** У стандарті SMBus ведений пристрій (наприклад, розумна батарея Smart Battery) може сам тимчасово виступати в ролі ведучого, щоб повідомити хост-контролер про критичну подію через надсилання пакета на зарезервовану адресу `0x08` (*SMBus Host Address*). Якщо два пристрої одночасно намагаються надіслати сповіщення хосту, побітовий арбітраж I2C природним чином надає пріоритет вузлу з меншою власною адресою, повністю запобігаючи втраті аварійних телеметричних повідомлень.

### Подвійна роль: Master Transmitter та Slave Target

У надійних багатомайстрових мережах кожен ведучий мікроконтролер одночасно конфігурується зі своєю унікальною 7-бітною адресою веденого (*Own Address*, що записується в регістри `I2C_OAR1` або `I2C_OAR2`). Розглянемо життєвий цикл автомата станів під час колізії:

```
[Початок транзакції: MASTER TX] ──► [Виявлено колізію: ARLO=1]
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    ▼                                                   ▼
         [Чужа адреса в кадрі]                                [Власна адреса в кадрі!]
                    │                                                   │
         [Очікування звільнення]                              [Видача ACK на 9-му такті]
                    │                                                   │
         [Запуск таймера Backoff]                             [Прийом байтів як SLAVE RX]
                    │                                                   │
         [Повтор вихідного запиту]                            [Виклик обробника даних]
```

Якщо інший ведучий надіслав адресу нашого вузла, апаратний блок упізнає збіг власної адреси (`ADDR = 1`), формує підтвердження `ACK` на дев'ятому такті SCL і переводить автомат станів у прийом корисного навантаження. Пропуск цього переходу призведе до того, що відправник отримає `NACK` і вважатиме пристрій несправним.

Якщо ж передана адреса належить іншому веденому (наприклад, сторонньому сенсору), наш драйвер повинен:
1. Очистити прапорець `ARLO` (записом одиниці у відповідний біт очищення, наприклад `I2C_ICR_ARLOCF`).
2. Залишатися в режимі пасивного слухача до виявлення умови `STOP` на шині (`STOPF = 1`).
3. Розрахувати псевдовипадкову затримку (*Backoff delay*) і повторно поставити транзакцію в чергу відправлення.

### Взаємодія з контролером прямого доступу до пам'яті (DMA)

При використанні DMA для передачі блоків даних виникає додаткова небезпека. Якщо передавач I2C працює через канал DMA, апаратний контролер продовжуватиме спустошувати буфер пам'яті та генерувати запити до DMA навіть після того, як лінія зв'язку буде втрачена через `ARLO`, якщо драйвер негайно не зупинить потік.

Правильний алгоритм обробки переривання `ARLO` при роботі з DMA включає такі кроки:
1. Примусове вимкнення запитів DMA з боку периферійного модуля I2C (скидання біта `TXDMAEN` у регістрі `I2C_CR1`).
2. Блокування відповідного каналу DMA (`DMA_Channel->CCR &= ~DMA_CCR_EN`).
3. Зчитування кількості непереданих байтів з лічильника `DMA_CNDTR` для коректного відновлення покажчика буфера при повторній спробі.
4. Очищення прапорців переривань DMA.

### Архітектура інтеграції з операційними системами реального часу (RTOS)

У багатозадачних середовищах (FreeRTOS, Zephyr, RT-Thread) завдання прикладного рівня не повинні самостійно взаємодіяти з регістрами I2C. Керування транзакціями організовується через виділений сервісний потік або чергу завдань:

1. **Черга транзакцій (Transaction Queue):** Прикладні задачі формують дескриптор `i2c_transaction_t` і надсилають його в чергу через `xQueueSend()`.
2. **М'ютекс шини (Bus Mutex):** Захищає контекст драйвера від одночасного виклику з різних потоків. Задача захоплює м'ютекс перед стартом транзакції.
3. **Семафор очікування (Completion Semaphore):** Після запуску апаратної передачі викликаюча задача блокується на бінарному семафорі `xSemaphoreTake(sem, timeout)`.
4. **Обробка в ISR:** Подія успішного завершення (`STOPF`) або фатальної помилки розблоковує задачу через `xSemaphoreGiveFromISR()`. У разі виявлення `ARLO` обробник переривання не будить задачу негайно, а запускає неблокувальний програмний таймер відступу (`xTimerStartFromISR()`), який перезапустить передачу після паузи.

Така структура гарантує, що прикладний потік залишається заблокованим у стані очікування, звільняючи процесор для виконання корисних обчислень під час пауз між спробами захоплення шини.

### Алгоритм псевдовипадкового відступу (Exponential Backoff)

Пряма спроба повторити транзакцію негайно після появи сигналу `STOP` створює високий ризик повторної колізії, якщо обидва ведучі намагаються синхронно виконати циклічні операції (наприклад, щосекундне опитування сенсора за системним таймером).

Для розподілу запитів у часі застосовується усічений двійковий експоненційний відступ:

```
T_backoff = T_base × (2^k − 1) × R

де:
T_base — базовий квант часу (час передачі одного байта: ~100 мкс на 100 кГц);
k — кількість послідовних невдалих спроб (обмежується k_max = 5);
R — випадкове псевдовипадкове число з рівномірним розподілом у діапазоні [0.0 ... 1.0].
```

Такий підхід гарантує, що при повторних зіткненнях діапазон випадкових затримок експоненційно розширюється, мінімізуючи ймовірність синхронного входу на вільну шину.

### Обробка арбітражу на рівні підсистеми Linux I2C

У вбудованих системах на базі Linux (наприклад, одноплатні комп'ютери Raspberry Pi, BeagleBone або модулі на NXP i.MX) керування багатомайстровою шиною реалізовано всередині драйвера адаптера ядра (`drivers/i2c/busses/`).

Коли апаратний контролер SOC фіксує втрату арбітражу під час виконання системного виклику `ioctl(fd, I2C_RDWR, ...)`:
1. Драйвер адаптера перехоплює апаратне переривання `ARLO`, скидає внутрішні черги FIFO та повертає код помилки `-EAGAIN` (*Resource temporarily unavailable*) або `-EBUSY` в ядро.
2. Підсистема ядра `i2c-core` автоматично виконує задану кількість спроб повтору (параметр `adapter->retries`, за замовчуванням 3) з невеликим мікросекундним інтервалом.
3. Якщо після всіх спроб шину захопити не вдалося, системний виклик у просторі користувача завершується з поверненням `-1`, а змінна `errno` встановлюється у значення `EAGAIN`.

Приклад коректної обробки колізій у просторі користувача Linux з використанням механізму повторів:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

/* Обробка втрати арбітражу I2C у Linux (C) */
int linux_i2c_transfer_with_retry(int fd, struct i2c_msg *msgs, int num_msgs, int max_retries) {
    struct i2c_rdwr_ioctl_data packets = {
        .msgs = msgs,
        .nmsgs = num_msgs
    };

    for (int attempt = 0; attempt < max_retries; ++attempt) {
        if (ioctl(fd, I2C_RDWR, &packets) >= 0) {
            return 0; /* Успішна передача */
        }

        if (errno == EAGAIN || errno == EBUSY) {
            /* Втрата арбітражу: робимо випадковий мікросекундний відступ */
            uint32_t delay_us = 100 + (uint32_t)(rand() % 500);
            usleep(delay_us);
        } else {
            /* Фатальна апаратна помилка (наприклад, NACK) */
            return -1;
        }
    }
    errno = ETIMEDOUT;
    return -1;
}
```
```cpp
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>
#include <chrono>
#include <thread>
#include <random>
#include <expected>
#include <span>
#include <cerrno>

/* Обробка втрати арбітражу I2C у Linux (C++) */
class LinuxI2cBus {
public:
    explicit LinuxI2cBus(int fd) : fd_{fd}, rng_{std::random_device{}()} {}

    [[nodiscard]] std::expected<void, int> transfer(std::span<i2c_msg> messages, int maxRetries = 5) {
        i2c_rdwr_ioctl_data packets{
            .msgs = messages.data(),
            .nmsgs = static_cast<__u32>(messages.size())
        };

        std::uniform_int_distribution<int> jitterDist(100, 600);

        for (int attempt = 0; attempt < maxRetries; ++attempt) {
            if (::ioctl(fd_, I2C_RDWR, &packets) >= 0) {
                return {};
            }

            if (errno == EAGAIN || errno == EBUSY) {
                /* Втрата арбітражу: неблокувальна пауза з джиттером */
                std::this_thread::sleep_for(std::chrono::microseconds(jitterDist(rng_)));
            } else {
                return std::unexpected(errno);
            }
        }
        return std::unexpected(ETIMEDOUT);
    }

private:
    int fd_{-1};
    std::mt19937 rng_;
};
```
:::

### Повна реалізація драйвера Multi-Master

Нижче наведено промисловий модульний драйвер керування шиною I2C для багатомайстрових систем. Код демонструє повну обробку переривань подій та помилок, перемикання ролей між ведучим і веденим, керування чергою повідомлень та генерацію псевдовипадкового відступу.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#define I2C_MAX_BUFFER_SIZE      32
#define I2C_MAX_RETRIES          5
#define I2C_BASE_BACKOFF_US      100

typedef enum {
    I2C_STATE_IDLE = 0,
    I2C_STATE_MASTER_TX,
    I2C_STATE_MASTER_RX,
    I2C_STATE_SLAVE_TX,
    I2C_STATE_SLAVE_RX,
    I2C_STATE_ARBITRATION_LOST,
    I2C_STATE_ERROR
} i2c_bus_state_t;

typedef enum {
    I2C_STATUS_OK = 0,
    I2C_STATUS_BUSY,
    I2C_STATUS_ARBITRATION_LOST,
    I2C_STATUS_NACK,
    I2C_STATUS_TIMEOUT,
    I2C_STATUS_OVERFLOW
} i2c_status_t;

/* Дескриптор повідомлення I2C */
typedef struct {
    uint8_t target_address;
    uint8_t buffer[I2C_MAX_BUFFER_SIZE];
    size_t  length;
    size_t  transferred;
    bool    is_read;
    uint8_t retry_count;
} i2c_transaction_t;

/* Структура контексту драйвера багатомайстрового I2C */
typedef struct {
    volatile i2c_bus_state_t state;
    uint8_t                  own_address;
    i2c_transaction_t        active_msg;
    
    /* Буфер веденого для прийому запитів від інших ведучих */
    uint8_t                  slave_rx_buf[I2C_MAX_BUFFER_SIZE];
    size_t                   slave_rx_len;
    
    /* Колбек обробки даних, отриманих у режимі веденого */
    void (*slave_rx_callback)(const uint8_t *data, size_t len);
    
    /* Лічильники статистики */
    uint32_t                 arlo_count;
    uint32_t                 tx_success_count;
    uint32_t                 rx_success_count;
} i2c_multimaster_driver_t;

static i2c_multimaster_driver_t g_i2c_drv;

/* Псевдоапаратні функції доступу до регістрів контролера */
extern void hw_i2c_generate_start(void);
extern void hw_i2c_generate_stop(void);
extern void hw_i2c_write_byte(uint8_t byte);
extern uint8_t hw_i2c_read_byte(void);
extern void hw_i2c_enable_ack(bool enable);
extern void hw_i2c_clear_arlo_flag(void);
extern void hw_i2c_disable_tx_interrupts(void);
extern void hw_i2c_enable_slave_listening(uint8_t own_addr);
extern void hw_delay_us(uint32_t us);

/* Генерація випадкового відступу за алгоритмом Exponential Backoff */
static uint32_t calculate_backoff_delay_us(uint8_t retry_count) {
    if (retry_count > I2C_MAX_RETRIES) {
        retry_count = I2C_MAX_RETRIES;
    }
    uint32_t max_slots = (1U << retry_count);
    uint32_t random_slot = (uint32_t)rand() % max_slots;
    return (random_slot + 1) * I2C_BASE_BACKOFF_US;
}

/* Ініціалізація драйвера з власною адресою веденого */
void i2c_multimaster_init(uint8_t own_address, void (*rx_cb)(const uint8_t *, size_t)) {
    g_i2c_drv.state = I2C_STATE_IDLE;
    g_i2c_drv.own_address = own_address;
    g_i2c_drv.slave_rx_callback = rx_cb;
    g_i2c_drv.arlo_count = 0;
    g_i2c_drv.tx_success_count = 0;
    g_i2c_drv.rx_success_count = 0;
    g_i2c_drv.active_msg.length = 0;
    
    hw_i2c_enable_slave_listening(own_address);
}

/* Спроба передачі пакета ведучим */
i2c_status_t i2c_multimaster_transmit(uint8_t target_addr, const uint8_t *data, size_t len) {
    if (len > I2C_MAX_BUFFER_SIZE || len == 0) {
        return I2C_STATUS_OVERFLOW;
    }
    if (g_i2c_drv.state != I2C_STATE_IDLE) {
        return I2C_STATUS_BUSY;
    }

    g_i2c_drv.active_msg.target_address = target_addr;
    g_i2c_drv.active_msg.length = len;
    g_i2c_drv.active_msg.transferred = 0;
    g_i2c_drv.active_msg.is_read = false;
    g_i2c_drv.active_msg.retry_count = 0;
    
    for (size_t i = 0; i < len; ++i) {
        g_i2c_drv.active_msg.buffer[i] = data[i];
    }

    g_i2c_drv.state = I2C_STATE_MASTER_TX;
    hw_i2c_generate_start();
    return I2C_STATUS_OK;
}

/* Обробник переривання подій I2C (Event ISR) */
void I2C_EV_IRQHandler(void) {
    switch (g_i2c_drv.state) {
        case I2C_STATE_MASTER_TX:
            /* Подія: START надіслано -> передаємо адресу з бітом W (0) */
            if (g_i2c_drv.active_msg.transferred == 0) {
                uint8_t addr_byte = (g_i2c_drv.active_msg.target_address << 1) | 0x00;
                hw_i2c_write_byte(addr_byte);
                g_i2c_drv.active_msg.transferred = 1;
            } else {
                size_t byte_idx = g_i2c_drv.active_msg.transferred - 1;
                if (byte_idx < g_i2c_drv.active_msg.length) {
                    hw_i2c_write_byte(g_i2c_drv.active_msg.buffer[byte_idx]);
                    g_i2c_drv.active_msg.transferred++;
                } else {
                    /* Усі байти передано -> формуємо STOP */
                    hw_i2c_generate_stop();
                    g_i2c_drv.state = I2C_STATE_IDLE;
                    g_i2c_drv.tx_success_count++;
                }
            }
            break;

        case I2C_STATE_SLAVE_RX:
            /* Подія: отримано байт у режимі веденого */
            if (g_i2c_drv.slave_rx_len < I2C_MAX_BUFFER_SIZE) {
                g_i2c_drv.slave_rx_buf[g_i2c_drv.slave_rx_len++] = hw_i2c_read_byte();
            }
            break;

        default:
            break;
    }
}

/* Обробник переривання виявлення власної адреси (Match ADDR ISR) */
void I2C_ADDR_Match_IRQHandler(void) {
    /* Інший ведучий звернувся до нас */
    g_i2c_drv.state = I2C_STATE_SLAVE_RX;
    g_i2c_drv.slave_rx_len = 0;
    hw_i2c_enable_ack(true);
}

/* Обробник завершення передачі чужого пакета (STOPF ISR) */
void I2C_STOPF_IRQHandler(void) {
    if (g_i2c_drv.state == I2C_STATE_SLAVE_RX) {
        if (g_i2c_drv.slave_rx_callback && g_i2c_drv.slave_rx_len > 0) {
            g_i2c_drv.slave_rx_callback(g_i2c_drv.slave_rx_buf, g_i2c_drv.slave_rx_len);
        }
        g_i2c_drv.rx_success_count++;
        g_i2c_drv.state = I2C_STATE_IDLE;
    }
}

/* Обробник переривання помилок та колізій (Error ISR) */
void I2C_ER_IRQHandler(void) {
    /* 1. Перевіряємо біт втрати арбітражу ARLO */
    g_i2c_drv.arlo_count++;
    hw_i2c_clear_arlo_flag();
    hw_i2c_disable_tx_interrupts();
    
    g_i2c_drv.state = I2C_STATE_ARBITRATION_LOST;
    
    /* 2. Залишаємо ведений режим увімкненим: перевіряємо, чи не викликають нас */
    hw_i2c_enable_slave_listening(g_i2c_drv.own_address);
    
    /* 3. Плануємо повторну спробу, якщо не вичерпано ліміт */
    if (g_i2c_drv.active_msg.retry_count < I2C_MAX_RETRIES) {
        g_i2c_drv.active_msg.retry_count++;
        uint32_t backoff_us = calculate_backoff_delay_us(g_i2c_drv.active_msg.retry_count);
        hw_delay_us(backoff_us);
        
        /* Скидаємо індекс переданих байтів для повного рестарту */
        g_i2c_drv.active_msg.transferred = 0;
        g_i2c_drv.state = I2C_STATE_MASTER_TX;
        hw_i2c_generate_start();
    } else {
        /* Ліміт повторів вичерпано -> перехід у спокій */
        g_i2c_drv.state = I2C_STATE_IDLE;
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <vector>
#include <functional>
#include <random>
#include <expected>

class MultiMasterI2C {
public:
    enum class Error : uint8_t {
        Busy,
        ArbitrationLost,
        Nack,
        Timeout,
        BufferOverflow,
        MaxRetriesExceeded
    };

    enum class State : uint8_t {
        Idle,
        MasterTx,
        MasterRx,
        SlaveTx,
        SlaveRx,
        ArbitrationLost
    };

    static constexpr size_t MaxBufferSize = 32;
    static constexpr uint8_t MaxRetries = 5;
    static constexpr uint32_t BaseBackoffUs = 100;

    using RxCallback = std::function<void(std::span<const uint8_t>)>;

    explicit MultiMasterI2C(uint8_t ownAddress, RxCallback rxCallback = nullptr)
        : ownAddress_{ownAddress},
          rxCallback_{std::move(rxCallback)},
          rng_{std::random_device{}()} {}

    [[nodiscard]] std::expected<void, Error> transmit(uint8_t targetAddress, std::span<const uint8_t> data) {
        if (data.size() > MaxBufferSize) {
            return std::unexpected(Error::BufferOverflow);
        }
        if (state_ != State::Idle) {
            return std::unexpected(Error::Busy);
        }

        activeTarget_ = targetAddress;
        txBuffer_.assign(data.begin(), data.end());
        transferredBytes_ = 0;
        retryCount_ = 0;

        state_ = State::MasterTx;
        hwGenerateStart();
        return {};
    }

    /* Апаратні обробники переривань контролера */
    void onEventInterrupt() noexcept {
        switch (state_) {
            case State::MasterTx:
                handleMasterTxStep();
                break;
            case State::SlaveRx:
                handleSlaveRxStep();
                break;
            default:
                break;
        }
    }

    void onAddressMatchInterrupt() noexcept {
        state_ = State::SlaveRx;
        slaveRxBuffer_.clear();
        hwEnableAck(true);
    }

    void onStopConditionInterrupt() noexcept {
        if (state_ == State::SlaveRx) {
            if (rxCallback_ && !slaveRxBuffer_.empty()) {
                rxCallback_(std::span<const uint8_t>{slaveRxBuffer_});
            }
            ++rxSuccessCount_;
            state_ = State::Idle;
        }
    }

    void onErrorInterrupt() noexcept {
        ++arbitrationLostCount_;
        hwClearArloFlag();
        hwDisableTxInterrupts();

        state_ = State::ArbitrationLost;
        hwEnableSlaveListening(ownAddress_);

        if (retryCount_ < MaxRetries) {
            ++retryCount_;
            uint32_t delayUs = calculateBackoffDelay(retryCount_);
            hwDelayUs(delayUs);

            transferredBytes_ = 0;
            state_ = State::MasterTx;
            hwGenerateStart();
        } else {
            state_ = State::Idle;
        }
    }

    [[nodiscard]] uint32_t getArbitrationLostCount() const noexcept { return arbitrationLostCount_; }
    [[nodiscard]] uint32_t getTxSuccessCount() const noexcept { return txSuccessCount_; }
    [[nodiscard]] uint32_t getRxSuccessCount() const noexcept { return rxSuccessCount_; }

private:
    uint8_t ownAddress_{0};
    RxCallback rxCallback_;
    State state_{State::Idle};

    uint8_t activeTarget_{0};
    std::vector<uint8_t> txBuffer_;
    size_t transferredBytes_{0};
    uint8_t retryCount_{0};

    std::vector<uint8_t> slaveRxBuffer_;
    std::mt19937 rng_;

    uint32_t arbitrationLostCount_{0};
    uint32_t txSuccessCount_{0};
    uint32_t rxSuccessCount_{0};

    void handleMasterTxStep() noexcept {
        if (transferredBytes_ == 0) {
            uint8_t addrByte = static_cast<uint8_t>((activeTarget_ << 1) | 0x00);
            hwWriteByte(addrByte);
            transferredBytes_ = 1;
        } else {
            size_t idx = transferredBytes_ - 1;
            if (idx < txBuffer_.size()) {
                hwWriteByte(txBuffer_[idx]);
                ++transferredBytes_;
            } else {
                hwGenerateStop();
                state_ = State::Idle;
                ++txSuccessCount_;
            }
        }
    }

    void handleSlaveRxStep() noexcept {
        if (slaveRxBuffer_.size() < MaxBufferSize) {
            slaveRxBuffer_.push_back(hwReadByte());
        }
    }

    [[nodiscard]] uint32_t calculateBackoffDelay(uint8_t retries) noexcept {
        uint32_t maxSlots = 1U << std::min<uint8_t>(retries, MaxRetries);
        std::uniform_int_distribution<uint32_t> dist(1, maxSlots);
        return dist(rng_) * BaseBackoffUs;
    }

    /* Апаратні виклики рівня драйвера */
    void hwGenerateStart() noexcept;
    void hwGenerateStop() noexcept;
    void hwWriteByte(uint8_t byte) noexcept;
    uint8_t hwReadByte() noexcept;
    void hwEnableAck(bool enable) noexcept;
    void hwClearArloFlag() noexcept;
    void hwDisableTxInterrupts() noexcept;
    void hwEnableSlaveListening(uint8_t addr) noexcept;
    void hwDelayUs(uint32_t us) noexcept;
};
```
:::

### Методика налагодження та стрес-тестування арбітражу

Налагодження колізій на шині I2C ускладнюється тим, що арбітраж у нормальних умовах відбувається надзвичайно швидко і не залишає явних слідів спотворення сигналів на осцилограмі. Для якісної верифікації прошивки застосовують такі інженерні підходи:

#### 1. Синхронізація логічного аналізатора за фронтом колізії
Більшість сучасних логічних аналізаторів (наприклад, Saleae Logic або протокольні декодери осцилографів) підтримують розширені умови тригера:
- Встановіть тригер на умову появи сигналу `START` за наявності попереднього високого рівня на лініях.
- Використовуйте апаратний вивід налагодження GPIO на кожному мікроконтролері. Налаштуйте мікроконтролер на підняття псевдопіна `DEBUG_ARLO_PIN` у високий стан безпосередньо у першому рядку обробника `I2C_ER_IRQHandler()`.
- Тригер за фронтом на виводі `DEBUG_ARLO_PIN` дозволить зафіксувати точний момент втрати арбітражу та зіставити його з бітами на лініях SDA/SCL.

#### 2. Штучне генерування колізій (Fault Injection Testbench)
Для перевірки стійкості драйвера до частих зіткнень налаштовують тестовий стенд із двома платами, де обидва мікроконтролери запускають асинхронні таймери з взаємно простими періодами (наприклад, 1003 мкс та 1007 мкс) і безперервно відправляють випадкові пакети даних різної довжини.

Під час такого тестування контролюють три ключові показники:
- **Коефіцієнт успішних доставок:** Відношення успішно переданих пакетів до кількості спроб має становити 100% за умови достатньої кількості повторів (`I2C_MAX_RETRIES ≥ 5`).
- **Відсутність дедлоків:** Жоден із контролерів не повинен зависнути в нескінченному очікуванні прапорців передавача або лінії SCL.
- **Цілісність даних у режимі веденого:** Усі пакети, надіслані одним ведучим на власну адресу другого, мають бути коректно прийняті без пропусків байтів.

#### 3. Аварійне відновлення завислої лінії (9 Clock Pulses)
Якщо один із ведучих перезавантажився посеред арбітражу (наприклад, спрацював сторожовий таймер Watchdog), ведений пристрій може залишитися у стані очікування такту, утримуючи лінію SDA на нулі. У такій ситуації шина залишається назавжди заблокованою для всіх інших ведучих.

Для автоматичного виходу з цього аварійного стану драйвер перед первинною ініціалізацією модуля I2C виконує процедуру відновлення:
- Налаштовує вивід SCL як стандартний вихід `GPIO Push-Pull`, а SDA — як вхід `GPIO Input`.
- Перевіряє рівень SDA: якщо `SDA == 0`, видає до 9 тактових імпульсів на SCL із частотою 50 кГц.
- На кожному спаді SCL перевіряє стан SDA. Щойно ведений звільняє лінію (`SDA == 1`), цикл імпульсів переривається.
- Формує програмну умову `STOP` (перепад SDA з 0 в 1 при SCL = 1), після чого перемикає піни у функціональний режим апаратної периферії I2C.

### Телеметрія та моніторинг якості шини

У надійних промислових системах драйвер I2C збирає статистику колізій, що дозволяє виявляти апаратну деградацію шини ще до виникнення критичних відмов:

```
                  Кількість подій ARLO
Коефіцієнт колізій = ─────────────────────────────
                  Загальна кількість транзакцій
```

- Якщо коефіцієнт колізій перевищує `15–20%`, це свідчить про занадто високу щільність трафіку або погано налаштовані кванти опитування сенсорів (необхідно оптимізувати таймери задач).
- Якщо `ARLO` виникає під час звертання до адреси, якої взагалі немає на шині, це прямий індикатор електричних завад, затягнутого фронту наростання `t_r` або недостатнього номіналу резисторів підтяжки `Rp`.

### Практичні висновки для розробника

1. **Завжди вмикайте власну адресу веденого:** Ведучий мікроконтролер у багатомайстровій шині зобов'язаний мати налаштовану адресу в регістрі `OAR1` і бути готовим прийняти пакет у режимі веденого після втрати арбітражу.
2. **Ніколи не скидайте периферію «в лоб»:** Спроба вимкнути й увімкнути блок I2C через скидання біта `PE` (*Peripheral Enable*) під час активного чужого кадру порушить синхронізацію шини та може заблокувати лінію SDA.
3. **Використовуйте неблокувальні таймери для Backoff:** Уникайте функцій `delay()` всередині контексту переривань. У промисловому ПЗ затримка відступу реалізується через таймери операційної системи реального часу (FreeRTOS / Zephyr), звільняючи процесор для виконання інших задач.
