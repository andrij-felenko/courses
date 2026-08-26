# ⚙️ Автономний фазинг-харнес для перевірки бінарного кадрувальника

Цей практичний проєкт демонструє створення повноцінного автономного фазинг-харнеса (Fuzz Harness) для перевірки надійності та безпеки бінарного кадрувальника протоколу зв'язку. Використання рушія LLVM LibFuzzer у поєднанні з інструментацією AddressSanitizer (ASan) та UndefinedBehaviorSanitizer (UBSan) дозволяє виявити критичні вразливості пам'яті (переповнення буферів на стеку та купі, розіменування нульових покажчиків, використання звільненої пам'яті, невирівняний доступ) та логічні зависання ще на етапі розробки на хост-комп'ютері, без потреби у фізичному підключенні мікроконтролера.

## Принцип роботи LibFuzzer та інтерфейс тестової точки входу

На відміну від сліпих генераторів випадкового шуму (Blackbox Fuzzers), LibFuzzer є еволюційним фазером із контролем покриття коду (Coverage-guided Graybox Fuzzer). Під час компіляції вихідного коду компілятор Clang вбудовує в кожну точку розгалуження програми (блоки `if`, `switch`, цикли) спеціальні лічильники відвідувань (`SanitizerCoverage`). 

Фазер виконує мільйони ітерацій у пам'яті одного процесу, викликаючи обов'язкову стандартизовану точку входу з інтерфейсом:

:::tabs
```c
/* Обов'язковий C-інтерфейс точки входу для LibFuzzer */
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size);
```
```cpp
/* C++ інтерфейс точки входу з C-зв'язуванням */
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size);
```
:::

Процес еволюційного тестування складається з таких фаз:
1. **Вибір предка з корпусу**: Фазер обирає один із раніше збережених тестових векторів (`Seed Input`), який показав цікаве покриття нових гілок коду.
2. **Мутація**: До вхідного масиву застосовуються випадкові операції: інверсія окремих бітів (`Bitflip`), заміна байтів на граничні цілі числа (`0`, `0xFF`, `0x7FFF`), вставка випадкових блоків або обрізання довжини.
3. **Виконання в пам'яті**: Мутований масив передається у функцію `LLVMFuzzerTestOneInput`. Завдяки роботі в межах одного адресного простору швидкість сягає від 50 000 до 300 000 викликів на секунду на одне ядро процесора.
4. **Оцінка покриття**: Якщо мутація змусила парсер піти новою гілкою виконання (наприклад, потрапити в рідкісний обробник помилки кадру або пройти специфічну перевірку заголовка), цей вектор додається в активний корпус як новий предок.
5. **Фіксація аварії**: Якщо стається вихід за межі масиву або спрацьовує перевірка санітайзера, процес аварійно завершується, а вхідний пакет, що викликав збій, зберігається на диск у файл `crash-<hash>`.

## Механізм роботи AddressSanitizer: тіньова пам'ять і червоні зони

Щоб зрозуміти, чому фазинг під AddressSanitizer знаходить помилки, непомітні для звичайного тестування, розглянемо архітектуру захисту пам'яті:

- **Тіньова пам'ять (Shadow Memory)**: ASan відображає кожні 8 байтів віртуальної пам'яті процесу в 1 байт спеціальної тіньової пам'яті. Значення цього байта кодує стан відповідних 8 байтів: `0x00` означає, що всі 8 байтів доступні для читання й запису, а від `0x01` до `0x07` — що доступні лише перші `k` байтів.
- **Червоні зони (Redzones)**: Навколо кожного виділеного буфера на стеку або в купі компілятор автоматично вставляє отруєні байти (*poisoned redzones*) розміром від 16 до 32 байтів.
- **Миттєва діагностика**: Кожне читання чи запис компілюється з префіксною перевіркою тіньового байта:
  ```
  ShadowAddr = (AppAddr >> 3) + 0x7fff8000;
  if (*ShadowAddr != 0) ReportAndCrash();
  ```
Якщо зловмисний пакет змушує вказівник читання зсунутися на 1 байт далі виділеного масиву `payload`, ASan фіксує спробу читання отруєної червоної зони і миттєво генерує аварійний дамп, унеможливлюючи пропуск помилки.

## Повна реалізація потокового кадрувальника та фазинг-харнеса

Розгляньмо практичну реалізацію бінарного кадрувальника, який обробляє безперервний потік байтів, знаходить маркер кадру `0xAA`, перевіряє довжину, витягує корисне навантаження та верифікує 16-бітну контрольну суму CRC-16/CCITT.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include <stdlib.h>

#define FRAME_MAGIC_BYTE 0xAA
#define MAX_PAYLOAD_SIZE 64
#define HEADER_SIZE      3 /* Magic(1B) + MsgType(1B) + PayloadLen(1B) */
#define CRC_SIZE         2

typedef struct {
    uint8_t msg_type;
    uint8_t payload_len;
    uint8_t payload[MAX_PAYLOAD_SIZE];
    uint16_t crc16;
} DecodedFrame_t;

/* Обчислення контрольної суми CRC-16/CCITT-FALSE (поліном 0x1021) */
static uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

/* 
 * Функція розбору сирого потоку байтів.
 * Шукає маркер 0xAA, перевіряє межі буфера та валідує контрольну суму.
 * Повертає true, якщо знайдено та успішно декодовано валідний кадр.
 */
bool parse_raw_stream(const uint8_t *data, size_t size, DecodedFrame_t *out_frame) {
    if (data == NULL || size < (HEADER_SIZE + CRC_SIZE) || out_frame == NULL) {
        return false;
    }

    size_t cursor = 0;
    while (cursor < size) {
        /* 1. Пошук маркера початку кадру */
        if (data[cursor] != FRAME_MAGIC_BYTE) {
            cursor++;
            continue;
        }

        /* 2. Перевірка, чи доступний повний заголовок */
        if (cursor + HEADER_SIZE > size) {
            break;
        }

        uint8_t msg_type = data[cursor + 1];
        uint8_t payload_len = data[cursor + 2];

        /* 3. Захист від некоректного розміру корисного навантаження */
        if (payload_len > MAX_PAYLOAD_SIZE) {
            cursor++;
            continue;
        }

        size_t total_frame_len = HEADER_SIZE + (size_t)payload_len + CRC_SIZE;
        if (cursor + total_frame_len > size) {
            /* Кадр неповний — очікуємо надходження решти байтів */
            break;
        }

        /* 4. Вилучення та перевірка контрольної суми CRC-16 */
        size_t crc_offset = cursor + HEADER_SIZE + payload_len;
        uint16_t expected_crc = (uint16_t)data[crc_offset] |
                                ((uint16_t)data[crc_offset + 1] << 8);

        uint16_t calculated_crc = crc16_ccitt(&data[cursor + 1], (size_t)HEADER_SIZE - 1 + payload_len);

        if (calculated_crc == expected_crc) {
            out_frame->msg_type = msg_type;
            out_frame->payload_len = payload_len;
            if (payload_len > 0) {
                memcpy(out_frame->payload, &data[cursor + HEADER_SIZE], payload_len);
            }
            out_frame->crc16 = expected_crc;
            return true;
        }

        /* CRC не зійшлася — продовжуємо пошук наступного маркера 0xAA */
        cursor++;
    }

    return false;
}

/* Обов'язкова точка входу для LLVM LibFuzzer */
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    DecodedFrame_t frame;
    memset(&frame, 0, sizeof(frame));
    
    /* Передаємо згенеровані мутатором байти у тестовану функцію розбору */
    parse_raw_stream(data, size, &frame);
    
    return 0; /* 0 сигналізує фазеру про успішну обробку входу */
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <optional>
#include <array>

namespace protocol_fuzzer {

constexpr uint8_t FRAME_MAGIC_BYTE = 0xAA;
constexpr size_t MAX_PAYLOAD_SIZE = 64;
constexpr size_t HEADER_SIZE = 3;
constexpr size_t CRC_SIZE = 2;

struct DecodedFrame {
    uint8_t msg_type{0};
    uint8_t payload_len{0};
    std::array<uint8_t, MAX_PAYLOAD_SIZE> payload{};
    uint16_t crc16{0};
};

[[nodiscard]] constexpr uint16_t crc16_ccitt(std::span<const uint8_t> data) noexcept {
    uint16_t crc = 0xFFFF;
    for (const uint8_t byte : data) {
        crc ^= static_cast<uint16_t>(byte) << 8;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

[[nodiscard]] std::optional<DecodedFrame> parse_raw_stream(std::span<const uint8_t> stream) noexcept {
    if (stream.size() < (HEADER_SIZE + CRC_SIZE)) {
        return std::nullopt;
    }

    size_t cursor = 0;
    while (cursor < stream.size()) {
        if (stream[cursor] != FRAME_MAGIC_BYTE) {
            ++cursor;
            continue;
        }

        if (cursor + HEADER_SIZE > stream.size()) {
            break;
        }

        const uint8_t msg_type = stream[cursor + 1];
        const uint8_t payload_len = stream[cursor + 2];

        if (payload_len > MAX_PAYLOAD_SIZE) {
            ++cursor;
            continue;
        }

        const size_t total_frame_len = HEADER_SIZE + payload_len + CRC_SIZE;
        if (cursor + total_frame_len > stream.size()) {
            break;
        }

        const size_t crc_offset = cursor + HEADER_SIZE + payload_len;
        const uint16_t expected_crc = static_cast<uint16_t>(stream[crc_offset]) |
                                      (static_cast<uint16_t>(stream[crc_offset + 1]) << 8);

        const auto crc_data_span = stream.subspan(cursor + 1, (HEADER_SIZE - 1) + payload_len);
        const uint16_t calculated_crc = crc16_ccitt(crc_data_span);

        if (calculated_crc == expected_crc) {
            DecodedFrame frame{};
            frame.msg_type = msg_type;
            frame.payload_len = payload_len;
            if (payload_len > 0) {
                std::memcpy(frame.payload.data(), &stream[cursor + HEADER_SIZE], payload_len);
            }
            frame.crc16 = expected_crc;
            return frame;
        }

        ++cursor;
    }

    return std::nullopt;
}

} // namespace protocol_fuzzer

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    const std::span<const uint8_t> input_stream(data, size);
    auto result = protocol_fuzzer::parse_raw_stream(input_stream);
    (void)result;
    return 0;
}
```
:::

## Словник протоколу та кастомні мутації з підтримкою CRC

Якщо вхідний парсер захищено контрольною сумою CRC-16, випадкові мутації не зможуть проникнути глибше перевірки суми: ймовірність випадково вгадати правильний 16-бітний CRC для зміненого тіла становить лише приблизно 0.0015% (один шанс із 65 536). Фазер витрачатиме процесорний час на генерацію невалідних сум, які негайно відкидаються на початку функції, не заходячи у внутрішню логіку обробки корисних даних.

Для вирішення цієї проблеми застосовують два взаємодоповнюючі інструменти:

### 1. Словник токенів протоколу (`protocol.dict`)
Файл словника містить ключові послідовності байтів, які компілятор LibFuzzer використовує як атомарні блоки під час підстановки:

```ini
# protocol.dict - словник констант протоколу для LibFuzzer
magic_start="\xAA"
msg_heartbeat="\x01"
msg_telemetry="\x02"
msg_config_set="\x03"
msg_reboot="\xFF"
len_empty="\x00"
len_single="\x01"
len_max="\x40"
```

### 2. Кастомний мутатор кадру (`LLVMFuzzerCustomMutator`)
Функція кастомного мутатора дозволяє розробнику втрутитися в процес спотворення байтів. Вона викликає стандартний генератор мутацій LibFuzzer, але після модифікації корисного навантаження автоматично перераховує та записує валідний CRC у хвіст пакета. Завдяки цьому 100% згенерованих пакетів проходять перевірку контрольної суми, спрямовуючи фазер безпосередньо на стрес-тестування логіки розбору полів.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

/* Прототип внутрішнього генератора мутацій LibFuzzer */
size_t LLVMFuzzerMutate(uint8_t *data, size_t size, size_t max_size);

/* Кастомний мутатор зі збереженням коректності заголовка та CRC */
size_t LLVMFuzzerCustomMutator(uint8_t *data, size_t size, size_t max_size, unsigned int seed) {
    /* 1. Застосовуємо стандартні мутації LibFuzzer */
    size_t mutated_size = LLVMFuzzerMutate(data, size, max_size);
    if (mutated_size < (HEADER_SIZE + CRC_SIZE)) {
        return mutated_size;
    }

    /* 2. Якщо знайдено маркер кадру, коригуємо заголовок та перераховуємо CRC */
    if (data[0] == FRAME_MAGIC_BYTE) {
        uint8_t payload_len = data[2];
        if (payload_len <= MAX_PAYLOAD_SIZE && (HEADER_SIZE + (size_t)payload_len + CRC_SIZE) <= mutated_size) {
            uint16_t crc = crc16_ccitt(&data[1], (HEADER_SIZE - 1) + payload_len);
            size_t crc_pos = HEADER_SIZE + payload_len;
            data[crc_pos] = (uint8_t)(crc & 0xFF);
            data[crc_pos + 1] = (uint8_t)((crc >> 8) & 0xFF);
        }
    }

    return mutated_size;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>

extern "C" size_t LLVMFuzzerMutate(uint8_t *data, size_t size, size_t max_size);

extern "C" size_t LLVMFuzzerCustomMutator(uint8_t *data, size_t size, size_t max_size, unsigned int seed) {
    size_t mutated_size = LLVMFuzzerMutate(data, size, max_size);
    if (mutated_size < (protocol_fuzzer::HEADER_SIZE + protocol_fuzzer::CRC_SIZE)) {
        return mutated_size;
    }

    if (data[0] == protocol_fuzzer::FRAME_MAGIC_BYTE) {
        const uint8_t payload_len = data[2];
        if (payload_len <= protocol_fuzzer::MAX_PAYLOAD_SIZE && 
            (protocol_fuzzer::HEADER_SIZE + payload_len + protocol_fuzzer::CRC_SIZE) <= mutated_size) {
            
            const auto span = std::span<const uint8_t>(&data[1], (protocol_fuzzer::HEADER_SIZE - 1) + payload_len);
            const uint16_t crc = protocol_fuzzer::crc16_ccitt(span);
            
            const size_t crc_pos = protocol_fuzzer::HEADER_SIZE + payload_len;
            data[crc_pos] = static_cast<uint8_t>(crc & 0xFF);
            data[crc_pos + 1] = static_cast<uint8_t>((crc >> 8) & 0xFF);
        }
    }

    return mutated_size;
}
```
:::

## Керування корпусом та мінімізація тестових наборів

Під час тривалого фазингу (наприклад, нічного запуску в фоновому режимі) фазер генерує десятки тисяч нових файлів у директорії корпусу. З часом такий роздутий корпус починає сповільнювати процес тестування, оскільки багато входів покривають одні й ті самі базові блоки коду, відрізняючись лише незначними байтами.

Для оптимізації застосовують процедуру мінімізації корпусу (*Corpus Minimization*):

```bash
# Створення порожньої директорії для очищеного корпусу
mkdir -p corpus_minimized

# Запуск злиття: LibFuzzer відбирає найменшу підмножину файлів, яка дає 100% покриття
./protocol_fuzzer -merge=1 corpus_minimized/ corpus/

# Заміна роздутого корпусу на мінімізований
rm -rf corpus
mv corpus_minimized corpus
```

Зменшення корпусу зі 100 000 до 300 унікальних еталонних пакетів прискорює швидкість пошуку нових шляхів у 5–10 разів і дозволяє зберігати компактний набір тестів безпосередньо в репозиторії вихідного коду для регресійного тестування.

## Збірка з санітайзерами та аналіз звіту AddressSanitizer

Для компіляції тестового стенду використовується компілятор Clang з набором прапорців санітайзерів пам'яті:

```bash
# 1. Компіляція з інструментацією LibFuzzer, ASan та UBSan
clang++ -O2 -g -fsanitize=fuzzer,address,undefined \
    -Wall -Wextra -std=c++20 \
    fuzz_harness.cpp -o protocol_fuzzer

# 2. Підготовка початкового корпусу валідних пакетів
mkdir -p corpus artifacts
python3 -c "
import struct
# Створюємо валідний пакет Heartbeat (0xAA, msg_type=0x01, len=2, payload='OK', crc16)
payload = b'OK'
# CRC для b'\x01\x02OK' = 0x7849
frame = struct.pack('<BBB2sH', 0xAA, 0x01, len(payload), payload, 0x7849)
open('corpus/seed_valid_heartbeat.raw', 'wb').write(frame)
"

# 3. Запуск фазингу на 4 паралельних потоках
./protocol_fuzzer corpus/ \
    -dict=protocol.dict \
    -artifact_prefix=artifacts/ \
    -max_len=256 \
    -rss_limit_mb=512 \
    -jobs=4 \
    -workers=4
```

### Розбір звіту AddressSanitizer та відтворення збою

Якщо у парсері присутній дефект (наприклад, помилкове копіювання `memcpy` за некоректним зміщенням або читання неініціалізованої пам'яті), LibFuzzer негайно зупиняє виконання та виводить детальний звіт:

```
=================================================================
==28491==ERROR: AddressSanitizer: global-buffer-overflow on address 0x55d2b380a064
READ of size 2 at 0x55d2b380a064 thread T0
    #0 0x55d2b37c4120 in parse_raw_stream fuzz_harness.cpp:52
    #1 0x55d2b37c4490 in LLVMFuzzerTestOneInput fuzz_harness.cpp:78
    #2 0x55d2b36f1831 in fuzzer::Fuzzer::ExecuteCallback(unsigned char const*, unsigned long)
    #3 0x55d2b36f0db5 in fuzzer::Fuzzer::RunOne(unsigned char const*, unsigned long, bool, fuzzer::InputInfo*, bool*)
artifact_prefix='./artifacts/'; Test unit written to ./artifacts/crash-b49d71a8e8e7c102
```

Для покрокового налагодження знайденої проблеми розробнику достатньо запустити скомпільований бінарник у налагоджувачі GDB, передавши шлях до збереженого файлу збою:

```bash
gdb --args ./protocol_fuzzer artifacts/crash-b49d71a8e8e7c102
(gdb) run
(gdb) bt
(gdb) print cursor
(gdb) print payload_len
```

Кожен знайдений збій перетворюється на звичайний модульний тест (`Regression Test`), який додається до тестового набору в CI/CD, що назавжди гарантує неможливість повторної появи виправленої помилки.
