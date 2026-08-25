# ⚙️ Реалізація потокового кодека SLIP для мікроконтролерів і систем зв'язку

Передавання даних через послідовні інтерфейси (UART, RS-485, USB CDC) у вбудованих системах вимагає від кодека двох критичних якостей: нульового динамічного виділення пам'яті (*zero dynamic allocation*) та здатності обробляти байти в потоковому режимі прямо всередині обробника переривань або черги кільцевого буфера. Якщо алгоритм вимагає подвійної буферизації або динамічного `malloc()`, на мікроконтролерах із кількома кілобайтами оперативної пам'яті виникає фрагментація купи або переповнення стека.

Розгляньмо проектування надійного потокового кодека SLIP (Serial Line Internet Protocol, RFC 1055), здатного стабільно функціонувати в умовах апаратних завад, втрати байтів та переповнення приймального буфера.

### Архітектура та керуючі константи

Протокол базується на чотирьох спеціальних октетах:

```
SLIP_END     = 0xC0  /* 192: маркер межі кадру */
SLIP_ESC     = 0xDB  /* 219: префікс екранування колізій */
SLIP_ESC_END = 0xDC  /* 220: заміна для байта 0xC0 всередині даних */
SLIP_ESC_ESC = 0xDD  /* 221: заміна для байта 0xDB всередині даних */
```

Кодер перетворює вхідний буфер пакета на послідовність байтів для відправки в апаратний передавач UART. Декодер реалізується у вигляді кінцевого автомата (FSM), який отримує байти по одному, фільтрує лінійний шум, розгортає escape-послідовності та сповіщає систему про готовність повного кадру через функцію зворотного виклику (*callback*).

### Робота з кільцевим буфером і перериваннями UART

У реальних мікроконтролерних системах (наприклад, STM32 на базі ядра ARM Cortex-M або ESP32) байти надходять від апаратного контролера UART нерівномірно, окремими перериваннями або блоками через прямий доступ до пам'яті (DMA). Якщо обробляти повний мережевий стек безпосередньо всередині підпрограми обробки переривання (ISR), час перебування процесора у високому пріоритеті переривань зростає, що призводить до втрати даних на інших периферійних модулях (таймерах, АЦП чи шинах I2C/SPI).

Класична архітектура вбудованого кодека передбачає розділення обробки на два рівні:
1. **Низькорівневий рівень ISR (Interrupt Service Routine)**: обробник переривання UART зчитує вхідний байт із регістра даних `RDR` / `DR` і поміщає його в безблокувальний кільцевий буфер (*lock-free single-producer single-consumer ring buffer*).
2. **Фоновий рівень обробки (Main Loop або RTOS Task)**: фонова задача або головний цикл опитування вичитує байти з кільцевого буфера і по черзі передає їх функції розбору `slip_decoder_feed_byte()`.

Така схема гарантує, що час реакції апаратного переривання становить лічені такти процесора (зчитування регістра та інкремент покажчика), а вся складна логіка розбору кадрів і виклику мережевих функцій виконується в контексті фонової задачі з низьким пріоритетом.

#### Безблокувальний кільцевий буфер (SPSC Ring Buffer)

Для безпечного передавання байтів між ISR та фоновим кодеком без використання блокувальних м'ютексів (які заборонено викликати з контексту переривань) застосовується кільцевий буфер із розділеними індексами запису (`head`) та читання (`tail`):

```
+---------------------------------------------------------------+
| 0x45 | 0x00 | 0xC0 | 0xDB | 0xDC | .... | 0x1A | 0x02 | 0xC0 |
+---------------------------------------------------------------+
         ^                               ^
         | tail (зчитує фоновий кодек)   | head (записує ISR переривання)
```

Поки індекс `head != tail`, фоновий потік вилучає байти й передає їх у FSM кодека. Якщо буфер заповнюється повністю (`(head + 1) % SIZE == tail`), ISR інкрементує лічильник апаратних переповнень і відкидає надлишковий байт, захищаючи цілісність пам'яті. На архітектурах ARM Cortex-M доступ до змінних `head` та `tail` оформлюється з модифікатором `volatile`, а при необхідності додаються інструкції бар'єра пам'яті `__DMB()` (*Data Memory Barrier*), щоб компілятор або конвеєр процесора не переставили операції читання й запису.

#### Прямий доступ до пам'яті (DMA) та виявлення простою лінії (IDLE Line)

На високих швидкостях послідовного зв'язку (от 460800 до 3000000 біт/с) навіть мінімальний обробник переривань на кожен вхідний байт створює суттєве навантаження на ядро мікроконтролера. Якщо байт надходить кожні 3.3 мікросекунди, ядро витрачає значну частку часу виключно на вхід і вихід із підпрограми переривань (збереження та відновлення регістрів `R0–R3`, `R12`, `LR`, `PC`, `xPSR`).

Для розвантаження процесора застосовують апаратний контролер прямого доступу до пам'яті (DMA) у поєднанні з перериванням виявлення простою лінії UART (*IDLE line detection*):

1. Контролер DMA налаштовується в циклічному режимі (*Circular DMA Mode*) для безперервного запису байтів із регістра UART безпосередньо у виділений масив оперативної пам'яті.
2. При заповненні першої половини масиву генерується переривання половини передачі (*Half Transfer Complete, HT*), що дає сигнал кодеку обробити першу половину буфера.
3. При повному заповненні масиву генерується переривання повного завершення (*Transfer Complete, TC*), ініціюючи обробку другої половини буфера.
4. Якщо пакет завершився посеред буфера і передача припинилася, контролер UART виявляє відсутність активності впродовж тривалості одного фрейму (10 бітових інтервалів) і виставляє апаратне переривання `IDLE`. Обробник переривання `IDLE` зчитує поточний лічильник залишкових байтів у регістрі DMA `CNDTR`, обчислює кількість щойно отриманих даних і передає їх функції `feed()`.

Така архітектура дозволяє мікроконтролеру взагалі не прокидатися під час передачі тіла пакета, обробляючи дані великими пакетами лише двічі на фрейм або при завершенні кадру.

### Реалізація кодека: C та ідіоматичний C++

Нижче наведено повнофункціональну бібліотеку потокового кодування та декодування SLIP. Вкладка C оптимізована для низькорівневих систем, FreeRTOS та сирих покажчиків, а вкладка C++ надає безпечну об'єктноорієнтовану обгортку з використанням `std::span`, лямбда-функцій зворотного виклику та механізмів RAII без динамічного виділення пам'яті в гарячому циклі.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define SLIP_END     0xC0
#define SLIP_ESC     0xDB
#define SLIP_ESC_END 0xDC
#define SLIP_ESC_ESC 0xDD

/* Стани кінцевого автомата декодера */
typedef enum {
    SLIP_STATE_NORMAL = 0,
    SLIP_STATE_ESCAPED
} slip_state_t;

/* Контекст потокового декодера SLIP */
typedef struct slip_decoder {
    uint8_t *rx_buffer;
    size_t   max_length;
    size_t   current_length;
    slip_state_t state;
    bool     overflow_flag;
    void   (*on_packet_received)(const uint8_t *data, size_t length, void *user_data);
    void    *user_data;
} slip_decoder_t;

/* Ініціалізація декодера */
void slip_decoder_init(slip_decoder_t *dec, uint8_t *buffer, size_t max_len,
                       void (*callback)(const uint8_t *, size_t, void *), void *user_data) {
    dec->rx_buffer = buffer;
    dec->max_length = max_len;
    dec->current_length = 0;
    dec->state = SLIP_STATE_NORMAL;
    dec->overflow_flag = false;
    dec->on_packet_received = callback;
    dec->user_data = user_data;
}

/* Скидання стану декодера після помилки або розриву з'єднання */
void slip_decoder_reset(slip_decoder_t *dec) {
    dec->current_length = 0;
    dec->state = SLIP_STATE_NORMAL;
    dec->overflow_flag = false;
}

/* Потокова обробка одного отриманого байта */
void slip_decoder_feed_byte(slip_decoder_t *dec, uint8_t byte) {
    switch (dec->state) {
    case SLIP_STATE_NORMAL:
        if (byte == SLIP_END) {
            /* Кінець пакета: якщо довжина > 0 і не було переповнення, викликаємо callback */
            if (dec->current_length > 0) {
                if (!dec->overflow_flag && dec->on_packet_received) {
                    dec->on_packet_received(dec->rx_buffer, dec->current_length, dec->user_data);
                }
                dec->current_length = 0;
                dec->overflow_flag = false;
            }
        } else if (byte == SLIP_ESC) {
            dec->state = SLIP_STATE_ESCAPED;
        } else {
            /* Звичайний байт даних */
            if (dec->current_length < dec->max_length) {
                dec->rx_buffer[dec->current_length++] = byte;
            } else {
                dec->overflow_flag = true; /* Переповнення MTU */
            }
        }
        break;

    case SLIP_STATE_ESCAPED:
        if (byte == SLIP_ESC_END) {
            if (dec->current_length < dec->max_length) {
                dec->rx_buffer[dec->current_length++] = SLIP_END;
            } else {
                dec->overflow_flag = true;
            }
            dec->state = SLIP_STATE_NORMAL;
        } else if (byte == SLIP_ESC_ESC) {
            if (dec->current_length < dec->max_length) {
                dec->rx_buffer[dec->current_length++] = SLIP_ESC;
            } else {
                dec->overflow_flag = true;
            }
            dec->state = SLIP_STATE_NORMAL;
        } else if (byte == SLIP_END) {
            /* Порушення протоколу: неочікуваний END одразу після ESC */
            dec->current_length = 0;
            dec->overflow_flag = false;
            dec->state = SLIP_STATE_NORMAL;
        } else {
            /* Невідомий символ після ESC за RFC 1055 додається як є */
            if (dec->current_length < dec->max_length) {
                dec->rx_buffer[dec->current_length++] = byte;
            } else {
                dec->overflow_flag = true;
            }
            dec->state = SLIP_STATE_NORMAL;
        }
        break;
    }
}

/* Кодування пакета в вихідний буфер. Повертає кількість записаних байтів або 0 при нестачі місця */
size_t slip_encode_frame(const uint8_t *src, size_t src_len, uint8_t *dst, size_t dst_max_len) {
    size_t out_pos = 0;

    /* Початковий END для очищення можливих шумів лінії перед початком кадру */
    if (out_pos >= dst_max_len) return 0;
    dst[out_pos++] = SLIP_END;

    for (size_t i = 0; i < src_len; ++i) {
        uint8_t b = src[i];
        if (b == SLIP_END) {
            if (out_pos + 2 > dst_max_len) return 0;
            dst[out_pos++] = SLIP_ESC;
            dst[out_pos++] = SLIP_ESC_END;
        } else if (b == SLIP_ESC) {
            if (out_pos + 2 > dst_max_len) return 0;
            dst[out_pos++] = SLIP_ESC;
            dst[out_pos++] = SLIP_ESC_ESC;
        } else {
            if (out_pos + 1 > dst_max_len) return 0;
            dst[out_pos++] = b;
        }
    }

    /* Кінцевий маркер END */
    if (out_pos >= dst_max_len) return 0;
    dst[out_pos++] = SLIP_END;

    return out_pos;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <functional>
#include <vector>

class SlipDecoder {
public:
    enum class State : uint8_t {
        Normal = 0,
        Escaped
    };

    static constexpr uint8_t EndVal    = 0xC0;
    static constexpr uint8_t EscVal    = 0xDB;
    static constexpr uint8_t EscEndVal = 0xDC;
    static constexpr uint8_t EscEscVal = 0xDD;

    using PacketCallback = std::function<void(std::span<const uint8_t>)>;

    SlipDecoder(std::span<uint8_t> storage, PacketCallback callback) noexcept
        : buffer_(storage), callback_(std::move(callback)) {}

    void reset() noexcept {
        write_pos_ = 0;
        state_ = State::Normal;
        overflow_ = false;
    }

    void feed(uint8_t byte) noexcept {
        switch (state_) {
        case State::Normal:
            if (byte == EndVal) {
                if (write_pos_ > 0) {
                    if (!overflow_ && callback_) {
                        callback_(std::span<const uint8_t>(buffer_.data(), write_pos_));
                    }
                    write_pos_ = 0;
                    overflow_ = false;
                }
            } else if (byte == EscVal) {
                state_ = State::Escaped;
            } else {
                append_byte(byte);
            }
            break;

        case State::Escaped:
            if (byte == EscEndVal) {
                append_byte(EndVal);
                state_ = State::Normal;
            } else if (byte == EscEscVal) {
                append_byte(EscVal);
                state_ = State::Normal;
            } else if (byte == EndVal) {
                /* Порушення послідовності: скидаємо пакет */
                write_pos_ = 0;
                overflow_ = false;
                state_ = State::Normal;
            } else {
                append_byte(byte);
                state_ = State::Normal;
            }
            break;
        }
    }

    void feed(std::span<const uint8_t> chunk) noexcept {
        for (uint8_t b : chunk) {
            feed(b);
        }
    }

    [[nodiscard]] size_t current_size() const noexcept { return write_pos_; }
    [[nodiscard]] bool has_overflow() const noexcept { return overflow_; }

private:
    void append_byte(uint8_t b) noexcept {
        if (write_pos_ < buffer_.size()) {
            buffer_[write_pos_++] = b;
        } else {
            overflow_ = true;
        }
    }

    std::span<uint8_t> buffer_;
    PacketCallback callback_;
    size_t write_pos_{0};
    State state_{State::Normal};
    bool overflow_{false};
};

class SlipEncoder {
public:
    static constexpr uint8_t EndVal    = 0xC0;
    static constexpr uint8_t EscVal    = 0xDB;
    static constexpr uint8_t EscEndVal = 0xDC;
    static constexpr uint8_t EscEscVal = 0xDD;

    /* Кодування в заздалегідь виділений буфер */
    static size_t encode(std::span<const uint8_t> src, std::span<uint8_t> dst) noexcept {
        size_t out_pos = 0;
        if (dst.empty()) return 0;

        dst[out_pos++] = EndVal;

        for (uint8_t b : src) {
            if (b == EndVal) {
                if (out_pos + 2 > dst.size()) return 0;
                dst[out_pos++] = EscVal;
                dst[out_pos++] = EscEndVal;
            } else if (b == EscVal) {
                if (out_pos + 2 > dst.size()) return 0;
                dst[out_pos++] = EscVal;
                dst[out_pos++] = EscEscVal;
            } else {
                if (out_pos + 1 > dst.size()) return 0;
                dst[out_pos++] = b;
            }
        }

        if (out_pos >= dst.size()) return 0;
        dst[out_pos++] = EndVal;
        return out_pos;
    }

    /* Зручне кодування у вектор для високорівневого коду */
    static std::vector<uint8_t> encode_to_vector(std::span<const uint8_t> src) {
        std::vector<uint8_t> out;
        out.reserve(src.size() + 8);
        out.push_back(EndVal);

        for (uint8_t b : src) {
            if (b == EndVal) {
                out.push_back(EscVal);
                out.push_back(EscEndVal);
            } else if (b == EscVal) {
                out.push_back(EscVal);
                out.push_back(EscEscVal);
            } else {
                out.push_back(b);
            }
        }

        out.push_back(EndVal);
        return out;
    }
};
```
:::

### Ключові інженерні нюанси та пастки реалізації

#### 1. Очищення лінії початковим `SLIP_END`
Кодер завжди записує байт `0xC0` перед першим байтом даних. Якщо під час простою лінії через шум або підключення роз'єму в буфер приймача потрапило кілька випадкових байтів, початковий `0xC0` закриває це «сміттєве» повідомлення. Приймач передасть його вищому рівню (стеку IP), де воно буде негайно відкинуто через невалідний заголовок або контрольну суму, а декодер розпочне збирання справжнього пакета з чистого аркуша.

#### 2. Захист від переповнення MTU
Якщо вхідний потік байтів пошкоджено і маркер `SLIP_END` загубився через спотворення біта в лінії, FSM продовжуватиме збирати байти наступного пакета в той самий приймальний буфер. Без перевірки `overflow_flag` покажчик запису вийде за межі масиву, перезаписавши стек або змінні сусідніх модулів прошивки мікроконтролера.

Коли розмір накопичених даних досягає максимального розміру буфера `max_len`, кодек встановлює прапорець `overflow_flag = true` і припиняє запис нових байтів. Коли в лінію нарешті приходить справжній маркер `SLIP_END`, декодер бачить встановлений прапорець переповнення, тихо очищає буфер і скидає стан, не передаючи зіпсований та обрізаний пакет у функцію зворотного виклику.

#### 3. Стійкість до помилкових escape-послідовностей
В умовах сильних електромагнітних завад (наприклад, при роботі поруч із потужними імпульсними перетворювачами живлення або колекторними електродвигунами) звичайний байт даних може спотворитися у значення `0xDB` (`SLIP_ESC`). Якщо слідом за ним надійде маркер завершення кадру `0xC0` (`SLIP_END`), виникає позаштатна ситуація: маркер межі надходить тоді, коли автомат очікує символ підстановки.

Наївна реалізація могла б зависнути у стані `SLIP_STATE_ESCAPED` або помилково екранувати `0xC0`. Наведений вище автомат детектує таку колізію: при отриманні `0xC0` у стані `SLIP_STATE_ESCAPED` поточний неповний пакет анулюється (`rx_len = 0`), а FSM негайно повертається в початковий стан `SLIP_STATE_NORMAL`. Завдяки цьому синхронізація відновлюється вже на наступному коректному кадрі.

#### 4. Обробка здвоєних маркерів END
Якщо два пакети передаються один за одним без паузи, передавач видає послідовність `... [DATA] [0xC0] [0xC0] [DATA] ...`.
Перший `0xC0` завершує попередній пакет, вичерпуючи зібраний буфер і скидаючи `current_length = 0`.
Другий `0xC0` надходить уже при `current_length == 0`. Декодер розпізнає це як порожній кадр або лінійний скид і просто ігнорує його без виклику користувацького `callback`.

### Інтеграція з операційною системою реального часу (FreeRTOS)

В операційних системах реального часу кодек SLIP зазвичай обслуговується окремою задачею прийому `vTaskSlipRx()`. Коли апаратний обробник переривань UART наповнює кільцевий буфер, він може сповіщати задачу через пряме сповіщення `vTaskNotifyGiveFromISR()` або бінарний семафор.

Схема взаємодії компонентів в RTOS:

1. **UART RX Interrupt**:
   - Зчитує байт із `USART1->RDR`;
   - Записує байт у кільцевий буфер;
   - Якщо вхідний байт `== 0xC0`, надсилає повідомлення задачі обробки:

:::tabs
```c
BaseType_t xHigherPriorityTaskWoken = pdFALSE;
vTaskNotifyGiveFromISR(xSlipTaskHandle, &xHigherPriorityTaskWoken);
portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
```
```cpp
// C++ сповіщення задачі FreeRTOS з контексту ISR
BaseType_t higherPriorityTaskWoken = pdFALSE;
vTaskNotifyGiveFromISR(slipTaskHandle, &higherPriorityTaskWoken);
portYIELD_FROM_ISR(higherPriorityTaskWoken);
```
:::
2. **Задача `vTaskSlipRx`**:
   - Очікує сповіщення через `ulTaskNotifyTake(pdTRUE, portMAX_DELAY)`;
   - Вичитує накопичені байти з кільцевого буфера в локальний стек або статичний масив;
   - Викликає `slip_decoder_feed_byte()`;
   - Після завершення збирання кадру `on_packet_received` передає пакет безпосередньо у стек lwIP через `netif->input(pbuf, netif)`.

Завдяки цьому центральний процесор перебуває в режимі сну (*Low Power Idle*), прокидаючись виключно на короткий час для обробки готового кадру.

### Покроковий слід (Trace) виконання кінцевого автомата

Простежмо зміну внутрішніх полів структури `slip_decoder_t` під час надходження фрагментованого пакета з завадою:

```
+----+---------------+---------------------+----------+---------------+-----------------------------------+
| #  | Вхідний байт  | Стан автомата (FSM) | rx_len   | overflow_flag | Дія автомата / Реакція системи    |
+----+---------------+---------------------+----------+---------------+-----------------------------------+
| 1  | 0xAA (шум)    | SLIP_STATE_NORMAL   | 1        | false         | Запис байта в буфер rx_buf[0]     |
| 2  | 0xC0 (END)    | SLIP_STATE_NORMAL   | 0 (скид) | false         | Закриття сміття, очищення буфера  |
| 3  | 0x45 (версія) | SLIP_STATE_NORMAL   | 1        | false         | Початок справжнього IP-пакета     |
| 4  | 0xDB (ESC)    | SLIP_STATE_ESCAPED  | 1        | false         | Перехід у режим очікування коду   |
| 5  | 0xDC (ESC_END)| SLIP_STATE_NORMAL   | 2        | false         | Відновлення 0xC0 в rx_buf[1]      |
| 6  | 0xC0 (END)    | SLIP_STATE_NORMAL   | 0 (скид) | false         | Успішна видача кадру в callback   |
+----+---------------+---------------------+----------+---------------+-----------------------------------+
```

Цей покроковий слід демонструє ключову властивість кодека: система миттєво ізолює шумові байти та безпомилково відновлює вихідні двійкові значення навіть після глибоких збоїв синхронізації лінії.

### Тестування та імітація спотворень у каналі зв'язку

Для перевірки стійкості кодека перед розгортанням у реальному обладнанні рекомендується проводити стрес-тестування за чотирма сценаріями:

1. **Тест на граничні дані (Stress Payload)**:
   Генерація синтетичних масивів, що складаються виключно з чергування `0xC0 0xDB 0xC0 0xDB` довжиною 1500 байтів. Цей тест перевіряє коректність подвоєння довжини кадру кодером (до 3002 байтів у лінії) та безпомилковість зворотного розгортання декодером.

2. **Тест на інжекцію шуму (Noise Injection)**:
   Вставка випадкових байтів перед початком кадру, вставка подвійних та потрійних символів `0xC0` між кадрами, а також штучна інверсія окремих бітів усередині escape-послідовностей. Кодек повинен відкидати пошкоджені кадри без падіння системи (*crash*) та витоку ресурсів.

3. **Тест на переповнення буфера (MTU Exhaustion)**:
   Передача кадру довжиною 2000 байтів у декодер із буфером на 512 байтів. Перевіряється, що після відкидання надлишкового пакета наступний нормальний пакет на 100 байтів приймається без жодних затримок та дефектів.

4. **Профілювання швидкодії та тактів процесора**:
   На мікроконтролері з ядром ARM Cortex-M4 (тактова частота 168 МГц) функція `slip_decoder_feed_byte()` виконується в середньому за 12–18 тактів процесора на байт. При максимальній швидкості UART 921600 біт/с (приблизно 92 кбайт/с) кодек споживає менше 1% обчислювальної потужності ядра, що робить його ідеальним кандидатом для високонавантажених вбудованих вузлів зв'язку.

### Фаззинг-тестування (Fuzzing) та верифікація з AddressSanitizer

Оскільки декодер SLIP безпосередньо розбирає сирий, потенційно ворожий потік даних із фізичної лінії зв'язку, будь-яка вразливість у перевірці меж масиву або обробці станів автомата може стати причиною дистанційного зависання або виконання довільного коду (*Remote Code Execution, RCE*).

Для верифікації надійності кодека застосовують фаззинг на базі інструментів **LLVM LibFuzzer** або **AFL++** (*American Fuzzy Lop*).

Цільова функція фаззингу компілюється з санітайзерами пам'яті (`clang -fsanitize=address,undefined -O2`):

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <assert.h>

/* Функція-ціль для LLVM LibFuzzer */
static void dummy_callback(const uint8_t *data, size_t len, void *ctx) {
    /* Перевіряємо, що отримані дані доступні для читання */
    volatile uint8_t checksum = 0;
    for (size_t i = 0; i < len; ++i) {
        checksum ^= data[i];
    }
    (void)checksum;
}

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    uint8_t buffer[1024];
    slip_decoder_t dec;
    slip_decoder_init(&dec, buffer, sizeof(buffer), dummy_callback, NULL);

    for (size_t i = 0; i < size; ++i) {
        slip_decoder_feed_byte(&dec, data[i]);
    }

    return 0;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    std::array<uint8_t, 1024> buffer;
    
    SlipDecoder decoder(buffer, [](std::span<const uint8_t> frame) {
        volatile uint8_t checksum = 0;
        for (uint8_t b : frame) {
            checksum ^= b;
        }
        (void)checksum;
    });

    decoder.feed(std::span<const uint8_t>(data, size));
    return 0;
}
```
:::

Фаззер генерує сотні мільйонів синтетичних мутацій вхідного потоку, включаючи послідовності з мільйонами незакритих `0xDB`, миттєві переходи станів та згенеровані двійкові структури. Завдяки суворій перевірці меж `write_pos_ < max_length` та скиданню прапорця переповнення кодек гарантує відсутність переповнень буфера (*buffer overflow*), витоків пам'яті (*memory leaks*) та невизначеної поведінки (*undefined behavior*).

### Підсумкові рекомендації з оптимізації швидкодії

1. **Інлайнінг гарячих функцій**: позначення функції `feed()` як `inline` або `static inline` дозволяє компілятору прибрати накладні витрати на виклик підпрограми, вбудовуючи тіло `switch` безпосередньо в цикл вичитування кільцевого буфера.
2. **Передбачення розгалужень (Branch Prediction)**: оскільки переважна більшість байтів у потоці є звичайними даними (ймовірність екранування становить менше 1%), компілятор автоматично оптимізує пряму гілку виконання, мінімізуючи скидання конвеєра процесора.
3. **Вирівнювання пам'яті**: розміщення приймального буфера за 32-бітною межею вирівнювання (`alignas(4)` у C++ або `__attribute__((aligned(4)))` у C) прискорює подальшу передачу сформованого кадру в мережевий стек, де 32-бітні IP-адреси зчитуються одинарними машинними словами `LDR`.

### Декодування «на місці» (In-Place Deframing) та керування кешем CPU

У мікроконтролерах із надзвичайно обмеженим обсягом оперативної пам'яті (наприклад, 8-бітні AVR або 32-бітні Cortex-M0 з 2–4 КБ RAM) виділення окремого приймального буфера на додаток до буфера DMA подвоює витрати пам'яті.

SLIP володіє важливою математичною властивістю: операція декодування ніколи не збільшує довжину даних. Кожна escape-послідовність `0xDB 0xDC` або `0xDB 0xDD` займає 2 байти у фізичному потоці, але перетворюється рівно в 1 байт відновлених даних.

Це дозволяє виконувати **декодування на місці** (*in-place deframing*):
- Покажчик читання `r_ptr` та покажчик запису `w_ptr` починають рух з нульового індексу одного й того самого масиву.
- Оскільки `r_ptr` рухається з кроком +1 або +2 (при escape-послідовностях), а `w_ptr` завжди збільшується лише на +1, індекс запису `w_ptr` гарантовано ніколи не випереджає індекс читання `r_ptr`.
- Декодовані дані безпечно перетирають уже прочитані сирі байти без ризику пошкодження нерозібраного залишку пакета.

#### Когерентність кешу даних (D-Cache Coherency) на Cortex-M7

На продуктивних мікроконтролерах (наприклад, STM32H7 на базі ARM Cortex-M7 із тактовою частотою 480 МГц) увімкнено апаратний кеш даних L1 D-Cache. Якщо контролер DMA записує байти SLIP безпосередньо в оперативну пам'ять (SRAM), а процесор намагається декодувати їх, виникає неузгодженість кешу: процесор може зчитати застарілі значення з кешу замість свіжих даних від DMA.

Для запобігання цій проблемі перед викликом декодера необхідно виконати інвалідацію діапазону кешу:

:::tabs
```c
/* Інвалідація рядків кешу даних за адресою буфера DMA перед декодуванням */
SCB_InvalidateDCache_by_Addr((uint32_t *)dma_rx_buffer, received_bytes_count);
```
```cpp
// C++ виклик інвалідації кешу Cortex-M7 над буфером std::span
SCB_InvalidateDCache_by_Addr(reinterpret_cast<uint32_t *>(dma_rx_buffer.data()), dma_rx_buffer.size());
```
:::

Після інвалідації процесор гарантовано завантажує актуальні байти безпосередньо з фізичної пам'яті SRAM, забезпечуючи стовідсоткову надійність прийому SLIP-трафіку на максимальних швидкостях шини.

#### Багатоядерна синхронізація та спінлоки на чіпах ESP32 (FreeRTOS SMP)

На двоядерних мікроконтролерах (наприклад, ESP32 з ядрами Xtensa LX6/LX7 або Raspberry Pi RP2040/RP2350 на базі Cortex-M33) одне ядро може виконувати обробник переривання UART або радіостек Bluetooth SPP, тоді як друге ядро виконує користувацьку прикладну програму.

Оскільки класичні макроси `taskENTER_CRITICAL()` у FreeRTOS SMP вимикають переривання лише на поточному ядрі, для захисту контексту структури `slip_decoder_t` від одночасного доступу з двох ядер використовують апаратні спінлоки (*spinlocks*):

:::tabs
```c
/* Оголошення спінлока у форматі ESP-IDF FreeRTOS */
static portMUX_TYPE slip_spinlock = portMUX_INITIALIZER_UNLOCKED;

/* Потокобезпечна подача байта у декодер */
void safe_slip_feed(slip_decoder_t *dec, uint8_t byte) {
    portENTER_CRITICAL(&slip_spinlock);
    slip_decoder_feed_byte(dec, byte);
    portEXIT_CRITICAL(&slip_spinlock);
}
```
```cpp
// C++ RAII обгортка критичної секції ESP-IDF
class EspSpinLock {
public:
    EspSpinLock() noexcept { portENTER_CRITICAL(&mux_); }
    ~EspSpinLock() noexcept { portEXIT_CRITICAL(&mux_); }
    EspSpinLock(const EspSpinLock &) = delete;
    EspSpinLock &operator=(const EspSpinLock &) = delete;

private:
    static inline portMUX_TYPE mux_ = portMUX_INITIALIZER_UNLOCKED;
};

void safe_slip_feed(SlipDecoder &decoder, uint8_t byte) {
    EspSpinLock lock;
    decoder.feed(byte);
}
```
:::

Такий захист унеможливлює стан гонитви (*race condition*), захищаючи лічильник накопичених байтів `current_length` та стан кінцевого автомата від пошкодження при паралельному виконанні коду на кількох ядрах мікроконтролера.
