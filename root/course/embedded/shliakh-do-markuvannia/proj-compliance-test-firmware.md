# ⚙️ Тестова прошивка для сертифікаційних випробувань: керування радіотрактом і навантаженням

<preknowlist>
- [Радіосертифікація](root:sys-notary/regulatory-radio-certification) — норми FCC Part 15C та RED щодо займаної смуги, позасмугових випромінювань і потужності передавача.
- [EMC-сертифікація](root:sys-notary/emc-certification) — вимірювання максимальної емісії у гіршому режимі роботи пристрою.
</preknowlist>

Коли готовий пристрій потрапляє до акредитованої випробувальної лабораторії зі стандартною робочою прошивкою, вимірювання зазвичай зупиняються на першій хвилині. Серійна прошивка енергоефективного пристрою більшу частину часу проводить у глибокому сні, прокидається на кілька мілісекунд, відправляє короткий зашифрований пакет із перемиканням частот (*frequency hopping*) і знову засинає. Інженер лабораторії не може виміряти ні пікову потужність передавача, ні стабільність тримання частоти, ні форму спектральної маски, оскільки вимірювальний приймач зі швидкістю розгортки в кілька сотень мілісекунд просто пропускає короткі поодинокі імпульси.

Для проходження сертифікаційних випробувань за стандартами FCC (США) та RED/ETSI (ЄС) розробник зобов'язаний надати спеціальну **сертифікаційну тестову прошивку** (англ. *Compliance Test Firmware* або *Direct Test Mode / DTM*). Ця прошивка дозволяє оператору лабораторії через простий інтерфейс (UART або кнопки) перемикати радіотракт і цифрову периферію у фіксовані безперервні режими.

---

## П'ять обов'язкових режимів сертифікаційного тесту

Стандарти радіовипробувань вимагають вимірювання параметрів на трьох фіксованих частотах діапазону: найнижчій (Bottom), середній (Middle) і найвищій (Top). Для діапазону 2.4 ГГц ISM це зазвичай канали 2402 МГц, 2440 МГц та 2480 МГц.

Тестова прошивка повинна підтримувати п'ять базових станів:

1. **Несуча без модуляції (Continuous Wave, CW):** радіопередавач випромінює чисту немодульовану синусоїду на заданій частоті з максимальною вихідною потужністю. Цей режим використовують для перевірки точності калібрування опорного кварцового генератора, вимірювання фазового шуму та абсолютної потужності випромінювання. Лабораторія підключає спектроаналізатор у режимі нульового огляду (*Zero Span*) або з вузькою смугою пропускання (RBW = 100 кГц) і фіксує відхилення центральної частоти, яке за стандартом не повинно перевищувати ±20 ppm (частин на мільйон).
2. **Модульована передача з коефіцієнтом заповнення 100% (Modulated TX 100% Duty Cycle):** передавач безперервно генерує пакети стандартного протоколу (наприклад, псевдовипадкову послідовність PRBS9 для BLE або Wi-Fi OFDM-кадри) без пауз між ними. Режим слугує для вимірювання займаної смуги частот (Occupied Bandwidth, OBW), спектральної щільності потужності (PSD) та позасмугових гармонік на межах діапазону (*Band Edge Compliance*). Якщо коефіцієнт заповнення менший за 98–100%, лабораторія змушена застосовувати математичні коефіцієнти корекції шпаруватості, що збільшує похибку вимірювань і затягує випробування.
3. **Режим стрибків частоти (Frequency Hopping):** якщо пристрій використовує FHSS (Bluetooth Classic або власні протоколи 868/915 МГц), лабораторія перевіряє рівномірність розподілу енергії по всій виділеній смузі та час утримання каналу (*dwell time*). Регуляції FCC Part 15.247 вимагають, щоб передавач використовував щонайменше 15 або 50 каналів (залежно від ширини каналу), а середній час перебування на одній частоті не перевищував 0.4 секунди протягом періоду спостереження.
4. **Безперервний прийом (Continuous RX):** приймач постійно увімкнений на фіксованій частоті. У цьому режимі вимірюють паразитне випромінювання гетеродина (Local Oscillator Leakage) та стійкість до блокування сильним сусіднім сигналом (*Receiver Blocking / Selectivity*). За нормами ETSI EN 300 328, чутливість приймача не повинна деградувати більше ніж на допустимий рівень помилок пакетів (PER ≤ 10%) при подачі завади рівнем −30 дБм на сусідніх частотах.
5. **Максимальне навантаження цифрової системи (Digital Stress Mode):** для загального тесту на електромагнітну сумісність (EMC) усі вузли плати переводяться в режим граничного енергоспоживання: мікроконтролер обчислює циклічні тести на максимальній частоті ядра, опитуються всі шини I2C/SPI, перемикаються ШІМ-виходи та блимають світлодіоди. Це створює найгірший сценарій цифрового шуму, гарантуючи, що за будь-яких умов експлуатації пристрій не перевищить ліміти емісії.

---

## Прямий тестовий режим (Direct Test Mode) проти ASCII-консолі

У бездротових технологіях Bluetooth і Wi-Fi існує два підходи до організації тестового керування:

* **Стандартизований протокол Direct Test Mode (DTM):** специфікація Bluetooth SIG визначає строго формалізований 2-байтовий двійковий протокол поверх UART зі швидкістю 115200 або 9600 бод. Перший байт задає команду (`CMD_RESET`, `CMD_RECEIVER_TEST`, `CMD_TRANSMITTER_TEST`, `CMD_TEST_END`), а другий — номер частотного каналу, довжину пакета (до 255 байтів) та тип корисного навантаження (PRBS9, чергування одиниць і нулів `10101010` або `11110000`). Перевага DTM полягає в тому, що автоматизовані радіочастотні тестові стенди лабораторій (наприклад, Rohde & Schwarz CMW500 або Anritsu MT8852B) самостійно підключаються до UART-порту пристрою і керують вимірами за лічені секунди без участі людини.
* **Текстова ASCII-консоль розробника:** застосовується для пропрієтарних радіомодулів (LoRa, Sub-GHz, Zigbee, Wi-Fi ESP32). Оператор лабораторії вводить зрозумілі рядкові команди у терміналі, отримуючи текстове підтвердження статусу.

Нижче наведено реалізацію універсального тестового диспетчера мовами C та C++, який поєднує керування радіотрактом і стрес-навантаженням цифрової периферії:

:::tabs
```c
/* test_firmware.c — Диспетчер сертифікаційних режимів для вбудованої системи */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    TEST_MODE_IDLE = 0,
    TEST_MODE_CW_TX,
    TEST_MODE_MODULATED_TX,
    TEST_MODE_RX,
    TEST_MODE_DIGITAL_STRESS
} test_mode_t;

typedef struct {
    test_mode_t mode;
    uint8_t channel;      /* Номер каналу (наприклад, 0..39 для BLE) */
    int8_t power_dbm;     /* Цільова потужність у дБм */
    bool is_active;
} rf_test_state_t;

static rf_test_state_t g_state = {TEST_MODE_IDLE, 0, 0, false};

/* Апаратні абстракції керування трансивером */
extern void radio_set_channel(uint8_t ch);
extern void radio_set_power(int8_t dbm);
extern void radio_start_cw(void);
extern void radio_start_modulated_stream(void);
extern void radio_start_rx(void);
extern void radio_stop(void);
extern void digital_peripherals_stress_start(void);
extern void digital_peripherals_stress_stop(void);
extern void uart_send_string(const char *msg);

void test_firmware_stop_all(void) {
    radio_stop();
    digital_peripherals_stress_stop();
    g_state.is_active = false;
    g_state.mode = TEST_MODE_IDLE;
    uart_send_string("STATUS: IDLE\r\n");
}

void test_firmware_process_command(const char *cmd) {
    if (strncmp(cmd, "STOP", 4) == 0) {
        test_firmware_stop_all();
    } else if (strncmp(cmd, "TX_CW", 5) == 0) {
        /* Формат команди: TX_CW <ch> <pwr_dbm> */
        test_firmware_stop_all();
        g_state.channel = 19; /* За замовчуванням середній канал */
        g_state.power_dbm = 4;
        radio_set_channel(g_state.channel);
        radio_set_power(g_state.power_dbm);
        radio_start_cw();
        g_state.mode = TEST_MODE_CW_TX;
        g_state.is_active = true;
        uart_send_string("STATUS: CW_TX_RUNNING\r\n");
    } else if (strncmp(cmd, "TX_MOD", 6) == 0) {
        test_firmware_stop_all();
        g_state.channel = 19;
        g_state.power_dbm = 4;
        radio_set_channel(g_state.channel);
        radio_set_power(g_state.power_dbm);
        radio_start_modulated_stream();
        g_state.mode = TEST_MODE_MODULATED_TX;
        g_state.is_active = true;
        uart_send_string("STATUS: MODULATED_TX_RUNNING\r\n");
    } else if (strncmp(cmd, "RX_CONT", 7) == 0) {
        test_firmware_stop_all();
        g_state.channel = 19;
        radio_set_channel(g_state.channel);
        radio_start_rx();
        g_state.mode = TEST_MODE_RX;
        g_state.is_active = true;
        uart_send_string("STATUS: RX_RUNNING\r\n");
    } else if (strncmp(cmd, "STRESS", 6) == 0) {
        test_firmware_stop_all();
        digital_peripherals_stress_start();
        g_state.mode = TEST_MODE_DIGITAL_STRESS;
        g_state.is_active = true;
        uart_send_string("STATUS: STRESS_RUNNING\r\n");
    } else {
        uart_send_string("ERROR: UNKNOWN_CMD\r\n");
    }
}
```
```cpp
// test_firmware.hpp / test_firmware.cpp — Об'єктний диспетчер тестових режимів
#include <cstdint>
#include <string_view>
#include <span>

enum class TestMode : uint8_t {
    Idle,
    CarrierWaveTx,
    ModulatedTx,
    ContinuousRx,
    DigitalStress
};

struct RadioConfig {
    uint8_t channel{19};
    int8_t power_dbm{4};
};

class ComplianceEngine {
public:
    ComplianceEngine() = default;

    void process_command(std::string_view cmd) {
        if (cmd.starts_with("STOP")) {
            stop_all();
            send_response("STATUS: IDLE\r\n");
        } else if (cmd.starts_with("TX_CW")) {
            stop_all();
            apply_radio_config();
            start_carrier_wave();
            current_mode_ = TestMode::CarrierWaveTx;
            send_response("STATUS: CW_TX_RUNNING\r\n");
        } else if (cmd.starts_with("TX_MOD")) {
            stop_all();
            apply_radio_config();
            start_modulated_stream();
            current_mode_ = TestMode::ModulatedTx;
            send_response("STATUS: MODULATED_TX_RUNNING\r\n");
        } else if (cmd.starts_with("RX_CONT")) {
            stop_all();
            apply_radio_config();
            start_receiver();
            current_mode_ = TestMode::ContinuousRx;
            send_response("STATUS: RX_RUNNING\r\n");
        } else if (cmd.starts_with("STRESS")) {
            stop_all();
            start_digital_stress();
            current_mode_ = TestMode::DigitalStress;
            send_response("STATUS: STRESS_RUNNING\r\n");
        } else {
            send_response("ERROR: UNKNOWN_CMD\r\n");
        }
    }

    void stop_all() noexcept {
        stop_radio_hardware();
        stop_digital_stress_hardware();
        current_mode_ = TestMode::Idle;
    }

    [[nodiscard]] TestMode current_mode() const noexcept { return current_mode_; }

private:
    TestMode current_mode_{TestMode::Idle};
    RadioConfig config_{};

    void apply_radio_config() noexcept;
    void start_carrier_wave() noexcept;
    void start_modulated_stream() noexcept;
    void start_receiver() noexcept;
    void stop_radio_hardware() noexcept;
    void start_digital_stress() noexcept;
    void stop_digital_stress_hardware() noexcept;
    void send_response(std::string_view msg) noexcept;
};
```
:::

---

## Інженерні пастки під час лабораторних випробувань

При написанні та використанні сертифікаційної прошивки інженери найчастіше стикаються з трьома критичними проблемами:

* **Спрацьовування апаратного сторожового таймера (Watchdog):** У режимі безперервної передачі CW процесор може зависнути у щільному порожньому циклі очікування або бути зупиненим апаратним радіоблоком. Якщо сторожовий таймер не скидати регулярно в головному циклі або не вимкнути його для тесту, плата раптово перезавантажуватиметься кожні 2–8 секунд, зриваючи вимірювання лабораторії. У сертифікаційній прошивці сторожовий таймер або повністю деактивують на рівні ініціалізації апаратних регістрів, або прив'язують його періодичне скидання до апаратного таймера низького пріоритету, який не залежить від стану радіотракту.
* **Теплове тротління вихідного каскаду:** У реальному житті радіопередавач працює зі шпаруватістю менш як 1%. При переході в режим 100% безперервної передачі кристал трансивера починає виділяти постійне тепло, його температура підіймається до +70...+85 °C, а коефіцієнт підсилення вихідного підсилювача потужності (PA) падає на 1.5–3 дБ через зміну рухливості носіїв заряду в напівпровіднику. Лабораторія зафіксує занижену вихідну потужність, якщо вимірювання почнуться через хвилину після прогріву, або навпаки — завищену нестабільність частоти через температурний дрейф кварцового резонатора. Тестова прошивка повинна забезпечувати стабільний тепловий баланс або дозволяти проводити короткі серії імпульсів фіксованої довжини для коректного вимірювання пікової потужності.
* **Шум тестового інтерфейсу UART:** Якщо прошивка постійно друкує налагоджувальні логи під час тесту випромінювання, фронти сигналу UART (особливо на довгих незаекранованих проводах до комп'ютера оператора) створюють додаткові гармоніки в діапазоні 30–300 МГц. Тестовий інтерфейс повинен відповідати лише коротким рядком на команди керування й повністю переводити лінії TX/RX у стан спокою (високий логічний рівень без активності) під час самого випромінювання.
