# ⚙️ Потоковий розбір NDJSON: обробка великих потоків зі сталим споживанням пам'яті

Коли сервер журналізує події, агрегує метрики або приймає телеметрію з тисяч пристроїв, сукупний обсяг даних швидко сягає десятків гігабайтів. Спроба завантажити такий масив у пам'ять як єдиний документ JSON (`[ { ... }, { ... } ]`) невідворотно спричиняє аварійне завершення процесу через вичерпання пам'яті (*Out of Memory*, OOM): об'єктне дерево парсера у моделі DOM (*Document Object Model*) займає у 4–8 разів більше оперативної пам'яті, ніж сам вихідний текстовий файл. Формат **NDJSON** (*Newline Delimited JSON*, також відомий як *JSON Lines*) розв'язує цю проблему, розбиваючи нескінченний потік на окремі незалежні документи JSON, розділені символом нового рядка `\n` (`0x0A`). Щоб обробити довільно великий потік даних зі сталим обсягом пам'яті `O(1)`, потрібен потоковий аналізатор із ковзним буфером, здатний коректно збирати записи, розірвані межами блоків читання з мережі або диска.

### Задача: потік необмеженої довжини у фіксованому буфері

Вхідні дані надходять шматками фіксованого розміру (наприклад, по 4096 байтів із системного виклику `read()` над сокетом чи файловим дескриптором). Окремий запис JSON майже ніколи не вирівняний за розміром блоку операційної системи: він може починатися всередині одного блока й закінчуватися посередині наступного.

Потоковий обробник мусить задовольняти чотири суворі вимоги:
1. **Сталий обсяг пам'яті (Memory Ceiling):** Використовувати заздалегідь виділений буфер фіксованого розміру, запобігаючи неконтрольованій динамічній алокації під час тривалого виконання.
2. **Коректне склеювання розірваних рядків:** Накопичувати незавершений хвіст попереднього блока та приєднувати до нього початок наступного.
3. **Підтримка різних закінчень рядків:** Знаходити як Unix-роздільник `\n` (`0x0A`), так і мережевий або Windows-роздільник CRLF `\r\n` (`0x0D 0x0A`), відсікаючи службові байти без пошкодження тіла JSON.
4. **Обробка без зайвого копіювання (Zero-Copy View):** Передавати виділені рядки в обробник як діапазони пам'яті (`const char*` з довжиною або `std::string_view`), уникаючи створення тимчасових об'єктів рядків у купі (*heap allocation*).

### Механіка ковзного буфера та обробка меж

Аналізатор підтримує масив байтів фіксованої місткості `MAX_LINE_LEN` та лічильник `unread_bytes`. Робота розбивається на цикл трьох кроків:
1. **Прийом нової порції (Feed):** Нові байти записуються в масив, починаючи зі зміщення `unread_bytes`. Загальний обсяг даних стає рівним `unread_bytes + chunk_len`. Якщо цей розмір перевищує місткість буфера, фіксується помилка переповнення — окремий рядок перевищив допустиму довжину запису.
2. **Лінійне сканування роздільників:** Вказівник переглядає накопичені байти в пошуках `0x0A`. Щойно знайдено переведення рядка, обчислюється довжина поточного запису від точки `processed_offset`. Якщо безпосередньо перед `\n` стоїть символ `\r` (`0x0D`), довжина зменшується на 1. Отриманий зріз пам'яті негайно передається у функцію зворотного виклику. Після виклику `processed_offset` встановлюється на байт, наступний за `\n`.
3. **Компактифікація залишку (Shift / Slide):** Після завершення перегляду блока перевіряється кількість необроблених байтів у хвості: `remaining = unread_bytes - processed_offset`. Якщо `remaining > 0`, цей неповний фрагмент наступного запису зсувається на початок буфера викликом `memmove()`, а `unread_bytes` встановлюється рівним `remaining`.

Така схема гарантує, що час обробки кожного байта залишається амортизовано сталим `O(1)`, а обсяг пам'яті процесу обмежений точно заданою верхньою межею незалежно від того, скільки терабайтів проходить крізь потік.

### Робочий код: реалізація мовами C та C++

Нижче наведено робочу реалізацію потокового конвеєра NDJSON. Вкладка C демонструє пряме керування пам'яттю з функціями зворотного виклику за покажчиком; вкладка C++ реалізує типобезпечний клас-обгортку за принципами RAII, використовуючи `std::string_view` та шаблони для функціональних об'єктів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define CHUNK_SIZE 4096
#define MAX_LINE_LEN 65536

typedef struct {
    char buffer[MAX_LINE_LEN];
    size_t unread_bytes;
} ndjson_stream_t;

typedef void (*record_callback_t)(const char *json_line, size_t length, void *user_data);

void ndjson_stream_init(ndjson_stream_t *stream) {
    stream->unread_bytes = 0;
}

/* Обробляє порційний блок даних із джерела */
bool ndjson_stream_feed(ndjson_stream_t *stream, const char *chunk, size_t chunk_len,
                        record_callback_t on_record, void *user_data) {
    if (stream->unread_bytes + chunk_len > MAX_LINE_LEN) {
        /* Переповнення: окремий запис перевищив максимальний ліміт пам'яті */
        return false;
    }

    /* Додаємо нові байти в кінець накопиченого залишку */
    memcpy(stream->buffer + stream->unread_bytes, chunk, chunk_len);
    stream->unread_bytes += chunk_len;

    size_t processed_offset = 0;

    for (size_t i = 0; i < stream->unread_bytes; ++i) {
        if (stream->buffer[i] == '\n') {
            size_t line_len = i - processed_offset;

            /* Відкидаємо можливий '\r' перед '\n' */
            if (line_len > 0 && stream->buffer[processed_offset + line_len - 1] == '\r') {
                line_len--;
            }

            /* Ігноруємо порожні рядки між записами */
            if (line_len > 0) {
                on_record(stream->buffer + processed_offset, line_len, user_data);
            }

            processed_offset = i + 1;
        }
    }

    /* Зсуваємо незавершений залишок на початок буфера */
    if (processed_offset > 0) {
        size_t remaining = stream->unread_bytes - processed_offset;
        if (remaining > 0) {
            memmove(stream->buffer, stream->buffer + processed_offset, remaining);
        }
        stream->unread_bytes = remaining;
    }

    return true;
}

/* Обробка кінця потоку для перевірки залишкового запису */
void ndjson_stream_flush(ndjson_stream_t *stream, record_callback_t on_record, void *user_data) {
    if (stream->unread_bytes > 0) {
        size_t len = stream->unread_bytes;
        if (stream->buffer[len - 1] == '\r') {
            len--;
        }
        if (len > 0) {
            on_record(stream->buffer, len, user_data);
        }
        stream->unread_bytes = 0;
    }
}

static void print_record(const char *json_line, size_t length, void *user_data) {
    int *count = (int *)user_data;
    (*count)++;
    printf("[%d] Отримано запис (%zu байтів): %.*s\n", *count, length, (int)length, json_line);
}

int main(void) {
    ndjson_stream_t stream;
    ndjson_stream_init(&stream);
    int records_count = 0;

    /* Симуляція надходження частин повідомлення з сокета */
    const char *chunk1 = "{\"id\":101,\"event\":\"login\"}\n{\"id\":102,\"event\":\"tra";
    const char *chunk2 = "nsfer\",\"amount\":450}\r\n{\"id\":103,\"event\":\"logout\"}\n";

    ndjson_stream_feed(&stream, chunk1, strlen(chunk1), print_record, &records_count);
    ndjson_stream_feed(&stream, chunk2, strlen(chunk2), print_record, &records_count);
    ndjson_stream_flush(&stream, print_record, &records_count);

    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <vector>
#include <functional>
#include <span>
#include <optional>

class NdjsonStreamParser {
public:
    explicit NdjsonStreamParser(size_t max_buffer_size = 65536)
        : max_size_(max_buffer_size) {
        buffer_.reserve(max_buffer_size);
    }

    /* Приймає порцію байтів і викликає обробник для кожного знайденого рядка JSON */
    template <typename Callback>
    bool feed(std::span<const char> chunk, Callback&& on_record) {
        if (buffer_.size() + chunk.size() > max_size_) {
            return false; /* Захист від неконтрольованого росту буфера */
        }

        buffer_.insert(buffer_.end(), chunk.begin(), chunk.end());
        size_t processed_offset = 0;

        for (size_t i = 0; i < buffer_.size(); ++i) {
            if (buffer_[i] == '\n') {
                size_t line_len = i - processed_offset;

                if (line_len > 0 && buffer_[processed_offset + line_len - 1] == '\r') {
                    --line_len;
                }

                if (line_len > 0) {
                    std::string_view record(buffer_.data() + processed_offset, line_len);
                    on_record(record);
                }

                processed_offset = i + 1;
            }
        }

        if (processed_offset > 0) {
            buffer_.erase(buffer_.begin(), buffer_.begin() + processed_offset);
        }

        return true;
    }

    /* Скидання залишкового запису в разі відсутності кінцевого переведення рядка */
    template <typename Callback>
    void flush(Callback&& on_record) {
        if (!buffer_.empty()) {
            size_t len = buffer_.size();
            if (buffer_[len - 1] == '\r') {
                --len;
            }
            if (len > 0) {
                on_record(std::string_view(buffer_.data(), len));
            }
            buffer_.clear();
        }
    }

private:
    size_t max_size_;
    std::vector<char> buffer_;
};

int main() {
    NdjsonStreamParser parser;
    int counter = 0;

    auto handle_record = [&counter](std::string_view line) {
        ++counter;
        std::cout << "[" << counter << "] Отримано запис: " << line << "\n";
    };

    const std::string_view p1 = "{\"sensor\":\"temp\",\"v\":21.5}\n{\"sensor\":\"press\",\"v\":101";
    const std::string_view p2 = ".3}\r\n{\"sensor\":\"hum\",\"v\":55.0}\n";

    parser.feed(std::span<const char>(p1.data(), p1.size()), handle_record);
    parser.feed(std::span<const char>(p2.data(), p2.size()), handle_record);
    parser.flush(handle_record);

    return 0;
}
```
:::

### Пастки та інженерні крайові випадки

1. **Екрановані символи нового рядка всередині JSON-рядків:**
   Якщо рядкове значення JSON містить переведення рядка, валідний серіалізатор кодує його двома байтами: зворотним слешем `\` (ASCII `0x5C`) та символом `n` (ASCII `0x6E`). Це **не є** сирим байтом `0x0A`, тому лінійний сканер не розриває рядок помилково. Якщо ж у потік потрапляє сирий байт `0x0A` без екранування всередині лапок, це є грубим порушенням як стандарту RFC 8259 (де всі керуючі символи `0x00..0x1F` підлягають екрануванню), так і специфікації NDJSON. Потоковий аналізатор передає такий рядок у розбірнику JSON, де він коректно відхиляється як синтаксично невалідний.
2. **Розрив послідовності `\r\n` на межі двох чанків читання:**
   Найпідступніший крайовий випадок виникає, коли символ повернення каретки `\r` потрапляє на останній байт поточного читання, а символ переведення рядка `\n` опиняється першим байтом наступного. Схема зі зсувом залишку `memmove()` гарантує, що одиночний `\r` залишається у буфері й після додавання наступного чанка об'єднується з `\n`, успішно відсікаючись під час виділення рядка.
3. **Багатобайтові послідовності UTF-8 на межі блоків:**
   У кодуванні UTF-8 байт `0x0A` зустрічається виключно як символ нового рядка ASCII. У 2-, 3- та 4-байтових послідовностях Юнікоду всі символи продовження лежать у діапазоні `0x80..0xBF`. Оскільки ці діапазони не перетинаються, потоковий сканер рядків принципово не здатний сплутати продовження юнікодного гліфа з роздільником записів. Розірваний між двома блоками символ UTF-8 зберігається в ковзному буфері цілком до завершення всього рядка JSON.
4. **Захист від наддовгих записів та виснаження пам'яті:**
   Якщо клієнт надсилає потік без жодного символу `\n` (наприклад, у результаті програмного збою або зловмисної атаки), буфер досягає позначки `MAX_LINE_LEN`. Функція `feed()` повертає `false`, що дозволяє серверу негайно закрити з'єднання та повернути помилку HTTP 413 (*Payload Too Large*), не допускаючи виснаження пам'яті хоста.
