# ⚙️ Розробка аналізатора затримок та захисту від ретрансляції NFC на C/C++

Практична оцінка стійкості безконтактних зчитувачів проти атак ретрансляції вимагає вимірювання затримок обміну кадрами ISO/IEC 14443-4 APDU з мікросекундною точністю. Якщо виміряний час відповіді тега перевищує заданий поріг `MAX_ALLOWED_RTT_US`, зчитувач повинен перервати транзакцію та заблокувати сесію.

Нижче наведено практичну реалізацію програмного модуля аналізатора трафіку та контролера таймінгу для NFC-зчитувачів на базі низькорівневої бібліотеки `libnfc`.

---

### 1. Схемотехніка зв'язку та архітектура таймінгу

При обміні кадрами через контролер NFC (наприклад, NXP PN532 або STMicroelectronics ST25R3916) таймер вимірювання затримки розпочинає відлік у момент відправки останнього біта кадру запиту `Tx` та зупиняється в момент розпізнавання старт-біта кадру відповіді `Rx`.

```
Зчитувач (Host)  ──[libnfc transceive]──> NFC Controller (PN532) ──[H-поле]──> Тег
       │                                        │
  start_time (t₁)                        Апаратний таймер
       │                                        │
  end_time   (t₂) ◄──[інтеррупт IRQ]────────────┴── відповідь кадру Rx
```

Двома ключовими вимогами до програмної реалізації є:
1. **Використання монотонного годинника (`CLOCK_MONOTONIC`):** Звичайний системний час `CLOCK_REALTIME` піддається коригуванню демоном NTP або стрибкам літнього часу, що створює хибні сплески затримок. Монотонний таймер гарантує відсутність зворотного ходу часу.
2. **Пряма обробка без буферизації:** Виклики напівдуплексного трансферу кадру `nfc_initiator_transceive_bytes` мають виконуватися з мінімальним накладним часом стеку ОС.

#### Низькорівневий режим `InCommunicateThru` контролера PN532

Бібліотека `libnfc` обгортає низькорівневу команду контролера PN532 `InCommunicateThru` (код `0x42`). У цьому режимі контролер не вносить власної програмної затримки на інтерпретацію вищих протоколів, а передає сирий потік байтів безпосередньо у фізичний модуль модуляції 13.56 МГц.

Обчислення апаратної затримки контролера `t_pn532` здійснюється за формулою:

```
t_pn532 = t_tx_frame + t_rx_frame + t_analog_delay
```

де `t_tx_frame` — час передачі кадрів по шині UART/SPI між хостом і PN532 на швидкості 115200 бод (близько 86 мкс на кожен байт). Тому для забезпечення високої точності таймінгу рекомендується підключати NFC-контролер через високошвидкісну шину SPI (до 5 Мбіт/с) або I2C.

---

### 2. Практична реалізація: вимірювання затримки APDU та верифікація часу

:::tabs
```c
/* c_nfc_relay_verifier.c - C implementation of NFC RTT Timing Verifier */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <nfc/nfc.h>

#define MAX_ALLOWED_RTT_US 15000L  /* Гранична затримка: 15 мс (15 000 мкс) */
#define BUFFER_SIZE 264

typedef struct {
    uint8_t data[BUFFER_SIZE];
    size_t length;
    int64_t rtt_microseconds;
} nfc_apdu_response_t;

/* Отримання поточного монотонного часу в мікросекундах */
static int64_t get_monotonic_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ((int64_t)ts.tv_sec * 1000000L) + (ts.tv_nsec / 1000L);
}

/* Надсилання APDU-команди з точним вимірюванням RTT */
bool nfc_send_apdu_with_timing(nfc_device *pnd, 
                               const uint8_t *apdu_tx, 
                               size_t tx_len, 
                               nfc_apdu_response_t *resp) {
    if (!pnd || !apdu_tx || !resp || tx_len == 0) {
        return false;
    }

    int64_t start_time = get_monotonic_time_us();

    /* Виклик трансферу кадрів libnfc */
    int res = nfc_initiator_transceive_bytes(pnd, apdu_tx, tx_len, 
                                             resp->data, BUFFER_SIZE, -1);
    int64_t end_time = get_monotonic_time_us();

    if (res < 0) {
        fprintf(stderr, "Помилка передачі APDU кадру: %d\n", res);
        return false;
    }

    resp->length = (size_t)res;
    resp->rtt_microseconds = end_time - start_time;
    return true;
}

int main(void) {
    nfc_context *context = NULL;
    nfc_device *pnd = NULL;

    nfc_init(&context);
    if (!context) {
        fprintf(stderr, "Не вдалося ініціалізувати libnfc context\n");
        return EXIT_FAILURE;
    }

    pnd = nfc_open(context, NULL);
    if (!pnd) {
        fprintf(stderr, "Не вдалося відкрити NFC-зчитувач\n");
        nfc_exit(context);
        return EXIT_FAILURE;
    }

    if (nfc_initiator_init(pnd) < 0) {
        nfc_perror(pnd, "nfc_initiator_init");
        nfc_close(pnd);
        nfc_exit(context);
        return EXIT_FAILURE;
    }

    /* Команда ISO 7816-4 SELECT AID */
    const uint8_t select_aid[] = {
        0x00, 0xA4, 0x04, 0x00, 0x07,
        0xA0, 0x00, 0x00, 0x00, 0x04, 0x10, 0x10
    };

    nfc_apdu_response_t response;
    memset(&response, 0, sizeof(response));

    printf("Надсилання APDU та вимірювання затримки RTT...\n");
    if (nfc_send_apdu_with_timing(pnd, select_aid, sizeof(select_aid), &response)) {
        printf("Отримано %zx байтів. Виміряний RTT: %lld мкс\n", 
               response.length, (long long)response.rtt_microseconds);

        if (response.rtt_microseconds > MAX_ALLOWED_RTT_US) {
            printf("[УВАГА! АТАКА] Затримка %lld мкс перевищує поріг %ld мкс! "
                   "Сесію заблоковано (виявлено ретрансляцію).\n",
                   (long long)response.rtt_microseconds, MAX_ALLOWED_RTT_US);
        } else {
            printf("[OK] Затримка в межах норми. Тег знаходиться поруч.\n");
        }
    }

    nfc_close(pnd);
    nfc_exit(context);
    return EXIT_SUCCESS;
}
```
```cpp
// cpp_nfc_relay_verifier.cpp - C++17 RAII & Chrono NFC Timing Verifier
#include <iostream>
#include <vector>
#include <chrono>
#include <optional>
#include <span>
#include <memory>
#include <cstdint>
#include <nfc/nfc.h>

// RAII обгортка для libnfc context та device
class NfcReader {
public:
    NfcReader() {
        nfc_init(&context_);
        if (!context_) {
            throw std::runtime_error("Failed to initialize libnfc context");
        }
        device_ = nfc_open(context_, nullptr);
        if (!device_) {
            nfc_exit(context_);
            throw std::runtime_error("Failed to open NFC device");
        }
        if (nfc_initiator_init(device_) < 0) {
            nfc_close(device_);
            nfc_exit(context_);
            throw std::runtime_error("Failed to set NFC initiator mode");
        }
    }

    ~NfcReader() {
        if (device_) nfc_close(device_);
        if (context_) nfc_exit(context_);
    }

    // Заборона копіювання
    NfcReader(const NfcReader&) = delete;
    NfcReader& operator=(const NfcReader&) = delete;

    struct ApduResult {
        std::vector<uint8_t> payload;
        std::chrono::microseconds rtt;
    };

    std::optional<ApduResult> sendApdu(std::span<const uint8_t> apdu) {
        std::vector<uint8_t> rx_buf(264);
        
        auto start = std::chrono::steady_clock::now();
        int res = nfc_initiator_transceive_bytes(device_, apdu.data(), apdu.size(),
                                                 rx_buf.data(), rx_buf.size(), -1);
        auto end = std::chrono::steady_clock::now();

        if (res < 0) {
            return std::nullopt;
        }

        rx_buf.resize(static_cast:size_t>(res));
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        return ApduResult{ std::move(rx_buf), duration };
    }

private:
    nfc_context* context_{nullptr};
    nfc_device* device_{nullptr};
};

int main() {
    constexpr std::chrono::microseconds kMaxAllowedRtt{15000}; // 15 ms

    try {
        NfcReader reader;
        
        const std::vector<uint8_t> select_aid = {
            0x00, 0xA4, 0x04, 0x00, 0x07,
            0xA0, 0x00, 0x00, 0x00, 0x04, 0x10, 0x10
        };

        std::cout << "Надсилання APDU кадру через C++ RAII верифікатор...\n";
        auto result = reader.sendApdu(select_aid);

        if (result) {
            std::cout << "Відповідь: " << result->payload.size() << " байтів, "
                      << "RTT: " << result->rtt.count() << " мкс\n";

            if (result->rtt > kMaxAllowedRtt) {
                std::cout << "[УВАГА! АТАКА] Затримка перевищує поріг! "
                          << "Виявлено ретранслятор.\n";
            } else {
                std::cout << "[OK] Автентичний тег у Ближній Зоні.\n";
            }
        } else {
            std::cerr << "Помилка обміну кадрами NFC.\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Виняток NFC: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

---

### 3. Детальний аналіз реалізації та архітектури C vs C++

#### Особливості реалізації мовою C
1. **Пряме управління ресурсами:** У реалізації на C виклик `nfc_init` створює контекст драйвера, а `nfc_open` відкриває системний хендл пристрою (наприклад, `/dev/ttyUSB0` або USB-пристрій PN532). Кожна гілка обробки помилок вимагає явного виклику `nfc_close` та `nfc_exit`.
2. **Структура `timespec` та `CLOCK_MONOTONIC`:** Обчислення різниці секунд `tv_sec` та наносекунд `tv_nsec` виконується вручну з приведенням до 64-бітного цілого `int64_t`, що запобігає переповненню таймера при довготривалій роботі сервера.

#### Особливості реалізації мовою C++
1. **Автоматичне управління ресурсами (RAII):** Клас `NfcReader` забирає володіння контекстом `nfc_context*` та пристроєм `nfc_device*`. У разі виникнення винятку або виходу з області видимості деструктор гарантовано звільняє апаратні ресурси драйвера.
2. **Сучасні типи `std::span` та `std::chrono`:** Використання `std::span<const uint8_t>` дозволяє передавати масиви даних без копіювання пам'яті. Модуль `std::chrono::steady_clock` забезпечує типобезпечне обчислення затримок у мікросекундах `std::chrono::microseconds`.

---

### 4. Інженерні пастки та боротьба з джитером операційної системи

При практичному розгортанні аналізатора затримок у реальних пристроях (на базі Raspberry Pi або Embedded Linux) розробники стикаються з трьома основними апаратними й програмними проблемами:

1. **Джитер планировщика ОС (Context Switch Jitter):** Операційні системи загального призначення (стандартне ядро Linux) можуть призупинити процес верифікатора в момент очікування переривання від NFC-контролера через квантування часу CPU. Це створює паразитичні затримки від `1 мс` до `5 мс`.
   - *Рішення:* Процес верифікатора повинен перевозитися в режим реального часу за допомогою виклику `sched_setscheduler` з политикою `SCHED_FIFO` або `SCHED_RR` та пріоритетом `99`.
2. **Обробка розширення часу очікування WTX (Frame Waiting Extension):** За стандартом ISO/IEC 14443-4, якщо тег виконує складні криптографічні обчислення (наприклад, асиметричний підпис RSA-4096), він повертає контрольний кадр `S-Block WTX` із коефіцієнтом `WTXM`. 
   - *Вразливість ретранслятора:* Зловмисник може навмисно надсилати зчитувачу кадри `WTX`, щоб штучно розширити часове вікно очікування від відповіді тега.
   - *Рішення:* Алгоритм захисту повинен жорстко обмежувати сумарний лічильник `WTX` (не більше 1–2 запитів за сесію) та враховувати час `WTX` у загальному часовому бюджеті сесії.
3. **Флуктувальна швидкість Baud Rate:** При роботі на базах 212–848 кбіт/с час передачі самого кадру зменшується у 2–8 разів, що вимагає перерахунку порогу `MAX_ALLOWED_RTT_US` залежно від обраної швидкості під час процедури PPS.

---

### 5. Оптимізація ядра реального часу (RT-PREEMPT) та прямий DMA

Для усунення затримок операційної системи в промислових зчитувачах застосовують спеціально пропатчене ядро Linux із плагіном **RT-PREEMPT**. 

У такому середовищі обробник переривань від ноги IRQ NFC-контролера виконується в контексті потоку реального часу з найвищим пріоритетом `PRICLN_RT`, що знижує випадковий джитер обробки кадрів до рівня не більше `5–10 мікросекунд`.

Крім того, передача блоків даних через шину SPI оптимізується за допомогою прямого доступу до пам'яті (DMA), минаючи проміжні буфери ядра. Це дозволяє здійснювати фіксацію часових міток передачі безпосередньо у моменти спрацьовування апаратних тригерів DMA, забезпечуючи високу відтворюваність часових профілів.
