# ⚙️ Практикум: інженерне порівняння девборди та власної плати

Коли макет на оціночній платі (ESP32 DevKit або STM32 Nucleo) перестає стабільно працювати при підвищенні тактової частоти чи відмовляється засинати на батареї, інженер мусить локалізувати джерело проблеми інструментально, а не здогадками. Для цього проводять порівняльний аудит за трьома критичними осями: форма фронтів і дзвін на швидкій шині SPI, амплітуда просідання живильної шини при радіоімпульсі та реальний витік струму в режимі глибокого сну.

Нижче наведено практичну методику лабораторних вимірювань, аналіз фізичних причин спотворень та тестову прошивку, що генерує каліброване навантаження для оцінки цілісності шини даних і перевірки чистоти споживання.

---

## 1. Порівняльний стенд та методика вимірювань

Щоб виміряти реальний вплив паразитної індуктивності та ємності макетних з'єднань («соплів» DuPont), збирають дві ідентичні за електричною схемою конфігурації:

1. **Конфігурація А (Макетна):** Мікроконтролерний модуль на макетній платі безпайкового типу, з'єднаний із давачем та зовнішньою флеш-пам'яттю шлейфом із дротів DuPont завдовжки 15 см. Живлення подається через вбудований на девборду лінійний стабілізатор (LDO) від порту USB.
2. **Конфігурація Б (Цільова PCB):** Двошарова друкована плата, де той самий чип встановлено на суцільний мідний шар землі (GND), сигнальні доріжки SPI мають розраховану ширину під хвильовий опір `50 Ом`, а блокувальні керамічні конденсатори на 100 нФ та 10 мкФ розпаяні безпосередньо біля виводів живлення (відстань < 2 мм).

### Інструментальне вимірювання дзвону на лінії тактування SPI (SCK)

Для коректного зняття осцилограми на частоті `16 МГц` стандартний 15-сантиметровий дріт заземлення щупа осцилографа («крокодил») створює власну паразитну індуктивність близько `100–150 нГн`. Разом із вхідною ємністю щупа (близько `10–15 пФ`) цей дріт утворює паразитний коливальний контур, який сам генерує фальшивий дзвін на екрані приладу.

Щоб усунути похибку самого вимірювального інструменту, штатний затискач заземлення знімають і використовують коротку коаксіальну пружину заземлення (*ground spring*), притискаючи її безпосередньо до земляного кільця щупа та найближчого виводу GND на платі. Це знижує індуктивність вимірювальної петлі з `150 нГн` до `< 2 нГн`.

```
Параметри вимірюваного тракту SPI (SCK = 16 МГц, C_load = 25 пФ, t_rise = 2.5 нс):

Параметр                      Макетка (DuPont 15 см)     Власна PCB (мікрополосок)
───────────────────────────────────────────────────────────────────────────────────
Паразитна індуктивність L     ≈ 180 нГн                  ≈ 0.8 нГн
Викид напруги (Overshoot)     4.85 В (+1.55 В до VDD)    3.38 В (+0.08 В)
Просідання (Undershoot)       -0.72 В (під GND)          -0.05 В
Час заспокоєння дзвону        18.5 нс                    1.2 нс
Пакетні помилки (PER @ 10^6)  1.4 · 10⁻² (1.4% збоїв)    < 10⁻⁸ (0 помилок)
```

На макетці викид напруги перевищує номінальну напругу живлення `3.3 В` майже на 50%, що викликає спрацьовування внутрішніх захисних діодів чипа приймача і призводить до паразитного пробою або виникнення ефекту защіпання (*latch-up*). Від'ємний викид `-0.72 В` зміщує підкладку кристала у прямому напрямку, відкриваючи паразитичні транзистори всередині кремнієвої структури. На власній платі швидкий фронт лишається строго в межах дозволених логічних рівнів CMOS.

---

## 2. Пульсації шини живлення під час радіопередачі (ESP32 Wi-Fi TX Burst)

Під час активації радіочастотного тракту струм споживання мікроконтролера стрибає з базових `30 мА` до пікових `380–450 мА` за час менше `1 мкс`.

На макетній платі високий контактний опір пружинних гнізд (`50–150 мОм` на кожне з'єднання) та значна індуктивність тонких з'єднувальних дротів викликають комбіноване динамічне та омічне падіння напруги живлення:

```
ΔV_droop
= I_peak · R_contact + L_wire · (di / dt)       [сума омічного та індуктивного спаду напруги]
= 0.45 · 0.2 + 200·10⁻⁹ · (0.45 / 10⁻⁶)         [підстановка: I = 450 мА, R = 0.2 Ом, L = 200 нГн, dt = 1 мкс]
= 0.09 + 0.09                                  [омічна (90 мВ) та індуктивна (90 мВ) складові]
= 0.18 В                                       [сумарне просідання напруги на з'єднувачах]
```

Якщо врахувати повільний відгук типового дешевого LDO (наприклад, AMS1117 зі спадом напруги при різкому навантаженні) та відсутність кераміки низького ESR безпосередньо біля виводів живлення модуля, сумарне просідання напруги на лінії VDD мікроконтролера сягає `450–600 мВ`. 

Коли напруга живлення падає нижче апаратного порогу схеми виявлення просідання (Brown-out Reset, зазвичай налаштованого на `2.7 В` або `2.8 В`), процесорне ядро миттєво скидається в апаратний ресет. Зовні це виглядає як нескінченна петля перезавантажень (*bootloop*), що повторюється рівно в момент виклику функції `esp_wifi_start()` або `WiFi.begin()`.

На власній друкованій платі танталовий конденсатор низького ESR ємністю `47 мкФ` (або полімерний алюмінієвий конденсатор) у парі з трьома керамічними конденсаторами `10 мкФ X7R` та широкими суцільними мідними полігонами живлення утримують динамічне просідання шини на рівні `< 35 мВ`, що повністю виключає помилкові спрацьовування захисту BOR.

---

## 3. Аудит паразитних витоків струму в режимі Deep Sleep

Типова оціночна плата (NodeMCU, ESP32 WROOM DevKit, Arduino Nano) рекламується як платформа для енергоощадних пристроїв, оскільки сам мікроконтролер має паспортне споживання в глибокому сні на рівні `5–15 мкА`. Проте пряме підключення мікроамперметра до входу живлення девборди часто показує струм `12–25 мА` навіть тоді, коли код успішно перевів чип у сон.

Головні паразитичні шляхи витоку енергії на девбордах включають:

1. **Лінійний стабілізатор живлення (LDO):** Встановлені на більшості масових плат стабілізатори AMS1117 або ME6211 мають власний струм спокою холостого ходу (*quiescent current*, `I_q`) від `5 мА` до `11 мА`. Навіть якщо ядро процесора споживає рівно нуль, цей стабілізатор безперервно спалює міліампери лише на власне функціонування.
2. **Світлодіод індикації живлення (Power LED):** Звичайний індикаторний діод червоного або синього кольору, підключений до шини 3.3 В через баластний резистор `1 кОм`, безперервно споживає струм:
   ```
   I_led
   = (V_rail - V_forward) / R_ballast   [закон Ома для світлодіодного кола]
   = (3.3 - 1.9) / 1000                 [підстановка: V_rail = 3.3 В, V_f = 1.9 В, R = 1000 Ом]
   = 1.4·10⁻³ А                         [струм споживання світлодіода: 1.4 мА]
   ```
   Один цей світлодіод споживає у 140 разів більше струму, ніж весь сплячий мікроконтролер.
3. **USB-UART перетворювач (CP2102, CH340G, FT232R):** Мікросхема мосту живиться від спільної шини. Коли USB-кабель відключено, внутрішні вузли мосту залишаються під напругою від батареї й тягнуть від `3 мА` до `15 мА`. Більше того, лінії TX/RX мосту з'єднані з виводами МК. Якщо вивід мікроконтролера в режимі сну залишається у стані логічної одиниці, струм витікає через верхній захисний діод входу UART-мосту, викликаючи ефект паразитного живлення (*phantom powering*).

---

## 4. Прошивка для верифікації шини та аудиту споживання

Для автоматизованої перевірки якості апаратного тракту використовують тестовий стенд. Прошивка виконує дві взаємопов'язані задачі:

1. **Стрес-тест SPI з підрахунком CRC32:** генерує циклічний потік псевдовипадкових пакетів на максимальній тактовій частоті апаратного SPI (`20 МГц`), записує їх у ведений пристрій і зчитує назад, реєструючи бітові та пакетні помилки (*Packet Error Rate*).
2. **Керований перехід у Deep Sleep:** перед засинанням прошивка коректно конфігурує всі задіяні виводи GPIO у стан високого імпедансу (Hi-Z) без внутрішніх підтяжок, вимикає тактування периферійних блоків і переводить контролер у режим глибокого сну.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "esp_system.h"
#include "esp_sleep.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_rom_crc.h"

#define PIN_NUM_MISO  19
#define PIN_NUM_MOSI  23
#define PIN_NUM_CLK   18
#define PIN_NUM_CS    5

#define TEST_PACKET_SIZE  256
#define TEST_ITERATIONS   10000

typedef struct {
    uint32_t total_packets;
    uint32_t crc_errors;
    uint32_t timeout_errors;
} BusAuditStats;

static const char *TAG = "BUS_AUDIT";
static spi_device_handle_t spi_handle;

static void init_spi_test_bus(int clock_speed_hz) {
    spi_bus_config_t buscfg = {
        .miso_io_num = PIN_NUM_MISO,
        .mosi_io_num = PIN_NUM_MOSI,
        .sclk_io_num = PIN_NUM_CLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = TEST_PACKET_SIZE + 8
    };

    spi_device_interface_config_t devcfg = {
        .clock_speed_hz = clock_speed_hz,
        .mode = 0,
        .spics_io_num = PIN_NUM_CS,
        .queue_size = 1,
        .flags = SPI_DEVICE_NO_DUMMY
    };

    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO));
    ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &devcfg, &spi_handle));
}

static BusAuditStats run_spi_integrity_test(void) {
    BusAuditStats stats = {0};
    uint8_t tx_buf[TEST_PACKET_SIZE];
    uint8_t rx_buf[TEST_PACKET_SIZE];

    for (uint32_t i = 0; i < TEST_ITERATIONS; i++) {
        for (size_t b = 0; b < TEST_PACKET_SIZE - 4; b++) {
            tx_buf[b] = (uint8_t)(i + b);
        }

        uint32_t crc = esp_rom_crc32_le(0, tx_buf, TEST_PACKET_SIZE - 4);
        memcpy(&tx_buf[TEST_PACKET_SIZE - 4], &crc, sizeof(crc));
        memset(rx_buf, 0, sizeof(rx_buf));

        spi_transaction_t t;
        memset(&t, 0, sizeof(t));
        t.length = TEST_PACKET_SIZE * 8;
        t.tx_buffer = tx_buf;
        t.rx_buffer = rx_buf;

        esp_err_t ret = spi_device_transmit(spi_handle, &t);
        stats.total_packets++;

        if (ret != ESP_OK) {
            stats.timeout_errors++;
            continue;
        }

        uint32_t rx_crc = esp_rom_crc32_le(0, rx_buf, TEST_PACKET_SIZE - 4);
        uint32_t expected_crc;
        memcpy(&expected_crc, &rx_buf[TEST_PACKET_SIZE - 4], sizeof(expected_crc));

        if (rx_crc != expected_crc || memcmp(tx_buf, rx_buf, TEST_PACKET_SIZE - 4) != 0) {
            stats.crc_errors++;
        }
    }

    return stats;
}

static void prepare_and_enter_deep_sleep(uint64_t sleep_duration_us) {
    spi_bus_remove_device(spi_handle);
    spi_bus_free(SPI2_HOST);

    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << PIN_NUM_MISO) | (1ULL << PIN_NUM_MOSI) |
                        (1ULL << PIN_NUM_CLK)  | (1ULL << PIN_NUM_CS),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    ESP_LOGI(TAG, "Всі піни ізольовано в Hi-Z. Перехід у Deep Sleep на %llu с", sleep_duration_us / 1000000ULL);
    esp_sleep_enable_timer_wakeup(sleep_duration_us);
    esp_deep_sleep_start();
}

void app_main(void) {
    ESP_LOGI(TAG, "--- Старт тесту цілісності шини SPI (20 МГц) ---");
    init_spi_test_bus(20000000);

    BusAuditStats stats = run_spi_integrity_test();
    ESP_LOGI(TAG, "Всього пакетів: %lu | Помилок CRC: %lu | Таймаутів: %lu",
             stats.total_packets, stats.crc_errors, stats.timeout_errors);

    prepare_and_enter_deep_sleep(30 * 1000000ULL);
}
```
```cpp
#include <cstdint>
#include <array>
#include <string_view>
#include <span>
#include <expected>
#include "esp_system.h"
#include "esp_sleep.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_rom_crc.h"

namespace HardwareAudit {

constexpr gpio_num_t PinMiso = GPIO_NUM_19;
constexpr gpio_num_t PinMosi = GPIO_NUM_23;
constexpr gpio_num_t PinClk  = GPIO_NUM_18;
constexpr gpio_num_t PinCs   = GPIO_NUM_5;

constexpr size_t PacketSize = 256;
constexpr uint32_t TestIterations = 10000;
constexpr std::string_view LogTag = "BUS_AUDIT_CPP";

struct BusStats {
    uint32_t totalPackets{0};
    uint32_t crcErrors{0};
    uint32_t timeoutErrors{0};
};

class SpiBusManager {
public:
    explicit SpiBusManager(int clockHz) {
        spi_bus_config_t buscfg{};
        buscfg.miso_io_num = PinMiso;
        buscfg.mosi_io_num = PinMosi;
        buscfg.sclk_io_num = PinClk;
        buscfg.quadwp_io_num = -1;
        buscfg.quadhd_io_num = -1;
        buscfg.max_transfer_sz = PacketSize + 8;

        spi_device_interface_config_t devcfg{};
        devcfg.clock_speed_hz = clockHz;
        devcfg.mode = 0;
        devcfg.spics_io_num = PinCs;
        devcfg.queue_size = 1;
        devcfg.flags = SPI_DEVICE_NO_DUMMY;

        ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO));
        ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &devcfg, &handle_));
    }

    ~SpiBusManager() {
        if (handle_) {
            spi_bus_remove_device(handle_);
            spi_bus_free(SPI2_HOST);
        }
    }

    SpiBusManager(const SpiBusManager&) = delete;
    SpiBusManager& operator=(const SpiBusManager&) = delete;

    [[nodiscard]] esp_err_t transfer(std::span<const uint8_t> tx, std::span<uint8_t> rx) noexcept {
        spi_transaction_t t{};
        t.length = tx.size() * 8;
        t.tx_buffer = tx.data();
        t.rx_buffer = rx.data();
        return spi_device_transmit(handle_, &t);
    }

private:
    spi_device_handle_t handle_{nullptr};
};

class DeepSleepManager {
public:
    static void isolatePinsAndSleep(uint64_t durationUs) noexcept {
        gpio_config_t io_conf{};
        io_conf.pin_bit_mask = (1ULL << PinMiso) | (1ULL << PinMosi) |
                               (1ULL << PinClk)  | (1ULL << PinCs);
        io_conf.mode = GPIO_MODE_INPUT;
        io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
        io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
        io_conf.intr_type = GPIO_INTR_DISABLE;
        gpio_config(&io_conf);

        ESP_LOGI(LogTag.data(), "Усі піни переведено в Hi-Z стан.");
        esp_sleep_enable_timer_wakeup(durationUs);
        esp_deep_sleep_start();
    }
};

BusStats runStressTest(SpiBusManager& bus) noexcept {
    BusStats stats{};
    std::array<uint8_t, PacketSize> txBuf{};
    std::array<uint8_t, PacketSize> rxBuf{};

    for (uint32_t i = 0; i < TestIterations; ++i) {
        for (size_t b = 0; b < PacketSize - 4; ++b) {
            txBuf[b] = static_cast<uint8_t>(i + b);
        }

        const uint32_t crc = esp_rom_crc32_le(0, txBuf.data(), PacketSize - 4);
        std::memcpy(&txBuf[PacketSize - 4], &crc, sizeof(crc));
        rxBuf.fill(0);

        stats.totalPackets++;
        const esp_err_t err = bus.transfer(txBuf, rxBuf);
        if (err != ESP_OK) {
            stats.timeoutErrors++;
            continue;
        }

        const uint32_t rxCrc = esp_rom_crc32_le(0, rxBuf.data(), PacketSize - 4);
        uint32_t expectedCrc = 0;
        std::memcpy(&expectedCrc, &rxBuf[PacketSize - 4], sizeof(expectedCrc));

        if (rxCrc != expectedCrc || txBuf != rxBuf) {
            stats.crcErrors++;
        }
    }
    return stats;
}

} // namespace HardwareAudit

extern "C" void app_main() {
    ESP_LOGI(HardwareAudit::LogTag.data(), "Запуск C++ тесту шини SPI");

    {
        HardwareAudit::SpiBusManager bus(20000000);
        auto stats = HardwareAudit::runStressTest(bus);
        ESP_LOGI(HardwareAudit::LogTag.data(), "Тест завершено. Всього: %lu, Помилок CRC: %lu",
                 stats.totalPackets, stats.crcErrors);
    } // Деструктор SpiBusManager автоматично звільняє ресурси шини SPI (RAII)

    HardwareAudit::DeepSleepManager::isolatePinsAndSleep(30 * 1000000ULL);
}
```
:::

---

## 5. Інтерпретація результатів тесту

1. **Якщо помилки CRC зникають при зниженні тактової частоти з 20 МГц до 2 МГц:** першопричиною є фізична лінія зв'язку (паразитна індуктивність дротів DuPont та завал фронтів через ємність макетки). На друкованій платі з контрольованим імпедансом ця сама лінія працюватиме на частотах до `50 МГц` із нульовим рівнем помилок.
2. **Якщо контролер зависає або скидається в момент передачі великого блоку чи старту Wi-Fi:** має місце просідання живильної шини (VDD Brown-out). Рішення для власної PCB — розрахунок локальної батареї керамічних конденсаторів та зниження внутрішнього опору силових доріжок за рахунок широких полігонів живлення.
3. **Якщо струм спокою після виклику `esp_deep_sleep_start()` перевищує 50 мкА:** це свідчить про наявність на девборді невимкненої службової периферії (LDO, USB-міст, резистори підтяжки). Перехід на власну друковану плату з вимикачем навантаження (*load switch*) та енергоощадним стабілізатором (наприклад, TPS7A02 з `I_q = 25 нА`) повертає споживання до паспортних `10–15 мкА`.
