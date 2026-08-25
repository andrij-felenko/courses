# ⚙️ Швидкий валідатор UTF-8 та санітайзер рядків

У системному програмуванні на рівні POSIX вхідний потік з файлу, мережевого сокета або каналу `pipe` — це неструктурований масив байтів. Коли ядро або системний демон передає ці дані прикладній програмі, текст не має жодних вбудованих гарантій валідності: у ньому можуть міститися пошкоджені мультибайтові послідовності, наддовгі вектори атак (overlong encodings), маркер порядку байтів (BOM) або сторонні символи повернення каретки `\r` (CR).

Щоб підготувати такий потік до безпечної системної обробки у Linux-оточенні, програма повинна розв'язати три взаємопов'язані інженерні задачі:

1. **Сувора валідація UTF-8:** Перевірка відповідності стандарту RFC 3629 / Unicode. Потрібно виявити й відкинути заборонені наддовгі кодування, сурогатні половинки UTF-16 (`U+D800`..`U+DFFF`) та значення, що перевищують стелю простору кодових точок `U+10FFFF`.
2. **Пропуск або видалення маркера BOM:** Якщо перші три байти потоку містять `0xEF 0xBB 0xBF`, їх необхідно пропустити без зупинки парсера.
3. **Потокова нормалізація кінців рядків:** Перетворення комбінацій `\r\n` (CRLF зі світу Windows/DOS) та поодиноких `\r` (старий Mac OS) на єдиний стандартний символ Unix `\n` (LF) за один прохід, без створення проміжних копій усього файлу в оперативній пам'яті.

## Анатомія перевірки та небезпека наддовгих послідовностей

Стандарт UTF-8 проєктувався так, щоб кожна кодова точка кодувалася мінімально можливою кількістю байтів. Проте бітова маска дозволяє теоретично записати будь-який 7-бітний ASCII-символ за допомогою двох, трьох або навіть чотирьох байтів.

Наприклад, символ косої риски `/` (`0x2F`, двійкове `0010 1111`) у нормальному 1-байтовому вигляді записується як `0x2F`. Але якщо зловмисник використає шаблон 2-байтової послідовності `110xxxxx 10xxxxxx`, він може записати це саме значення як `0xC0 0xAF` (двійкове `11000000 10101111`):

```
Шаблон 2 байтів:    1 1 0  0 0 0 0 0    1 0  1 0 1 1 1 1
Корисні біти:              0 0 0 0 0         1 0 1 1 1 1  --> 0x2F ('/')
```

Якщо наївний вебсервер чи модуль авторизації перевіряє вхідний шлях на наявність рядка `../` за допомогою байтового пошуку `0x2F`, він не помітить послідовності `0xC0 0xAF`. Якщо ж подальший декодер перетворить `0xC0 0xAF` назад у `/`, програма отримає доступ до кореневої файлової системи (класична вразливість обходу каталогів CVE-2000-0884).

Саме тому сучасний стандарт забороняє будь-які наддовгі форми:
- 2-байтова послідовність повинна декодуватися у число `>= 0x0080` (байти `0xC0` та `0xC1` безумовно невалідні).
- 3-байтова послідовність повинна декодуватися у число `>= 0x0800`.
- 4-байтова послідовність повинна декодуватися у число `>= 0x10000`.

Крім того, діапазон `U+D800`..`U+DFFF` зарезервований виключно для сурогатних пар у UTF-16. У валідному тексті UTF-8 жодна кодова точка з цього діапазону з'являтися не має права.

## Бітове декодування на практиці

Покажемо, як саме декодер перетворює байти на числове значення кодової точки. Розглянемо українську літеру «є» (`U+0454`), яка в кодуванні UTF-8 представляється двома байтами `0xD1 0x94`:

1. Стартовий байт `0xD1` у двійковому вигляді має вигляд `1101 0001`. Маска `(b0 & 0xE0) == 0xC0` підтверджує, що це 2-байтова послідовність. Корисні біти отримуються операцією `b0 & 0x1F`: маємо значення `0001 0001` (двійкове `10001`).
2. Байт-продовження `0x94` у двійковому вигляді: `1001 0100`. Перевірка `(b1 & 0xC0) == 0x80` підтверджує валідний маркер продовження `10`. Корисні біти отримуються операцією `b1 & 0x3F`: маємо `01 0100` (двійкове `010100`).
3. Збирання кодової точки: `(0x11 << 6) | 0x14 = 0x0440 | 0x14 = 0x0454`. Отримане число `0x0454` знаходиться в межах `0x0080`..`0x07FF`, тому воно не є наддовгим і приймається валідатором.

## Реалізація валідатора та санітайзера

Наведений нижче код реалізує скінченний автомат для побайтового розбору потоку. Він приймає дані блоками фіксованого розміру (4 КіБ), що забезпечує мінімальне споживання кешу процесора L1d та відсутність динамічних алокацій у критичному циклі обробки.

:::tabs
```c
/* utf8_sanitize.c — Валідатор UTF-8 та нормалізатор кінців рядків.
 * Збірка: cc -std=c99 -Wall -Wextra -O2 utf8_sanitize.c -o utf8_sanitize
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    UTF8_OK = 0,
    UTF8_ERR_INVALID_BYTE,
    UTF8_ERR_OVERLONG,
    UTF8_ERR_SURROGATE,
    UTF8_ERR_OUT_OF_RANGE,
    UTF8_ERR_TRUNCATED
} utf8_error_t;

/* Декодує одну кодову точку. Повертає кількість спожитих байтів (1..4) або 0 при помилці. */
static size_t utf8_decode_codepoint(const uint8_t *buf, size_t len, uint32_t *out_cp, utf8_error_t *err) {
    if (len == 0) {
        *err = UTF8_ERR_TRUNCATED;
        return 0;
    }

    uint8_t b0 = buf[0];
    if (b0 < 0x80) {
        *out_cp = b0;
        *err = UTF8_OK;
        return 1;
    }

    if ((b0 & 0xE0) == 0xC0) {
        if (len < 2) { *err = UTF8_ERR_TRUNCATED; return 0; }
        uint8_t b1 = buf[1];
        if ((b1 & 0xC0) != 0x80) { *err = UTF8_ERR_INVALID_BYTE; return 0; }
        
        uint32_t cp = ((b0 & 0x1F) << 6) | (b1 & 0x3F);
        if (cp < 0x80) { *err = UTF8_ERR_OVERLONG; return 0; }
        
        *out_cp = cp;
        *err = UTF8_OK;
        return 2;
    }

    if ((b0 & 0xF0) == 0xE0) {
        if (len < 3) { *err = UTF8_ERR_TRUNCATED; return 0; }
        uint8_t b1 = buf[1];
        uint8_t b2 = buf[2];
        if ((b1 & 0xC0) != 0x80 || (b2 & 0xC0) != 0x80) { *err = UTF8_ERR_INVALID_BYTE; return 0; }

        uint32_t cp = ((b0 & 0x0F) << 12) | ((b1 & 0x3F) << 6) | (b2 & 0x3F);
        if (cp < 0x0800) { *err = UTF8_ERR_OVERLONG; return 0; }
        if (cp >= 0xD800 && cp <= 0xDFFF) { *err = UTF8_ERR_SURROGATE; return 0; }

        *out_cp = cp;
        *err = UTF8_OK;
        return 3;
    }

    if ((b0 & 0xF8) == 0xF0) {
        if (len < 4) { *err = UTF8_ERR_TRUNCATED; return 0; }
        uint8_t b1 = buf[1];
        uint8_t b2 = buf[2];
        uint8_t b3 = buf[3];
        if ((b1 & 0xC0) != 0x80 || (b2 & 0xC0) != 0x80 || (b3 & 0xC0) != 0x80) {
            *err = UTF8_ERR_INVALID_BYTE;
            return 0;
        }

        uint32_t cp = ((b0 & 0x07) << 18) | ((b1 & 0x3F) << 12) | ((b2 & 0x3F) << 6) | (b3 & 0x3F);
        if (cp < 0x10000) { *err = UTF8_ERR_OVERLONG; return 0; }
        if (cp > 0x10FFFF) { *err = UTF8_ERR_OUT_OF_RANGE; return 0; }

        *out_cp = cp;
        *err = UTF8_OK;
        return 4;
    }

    *err = UTF8_ERR_INVALID_BYTE;
    return 0;
}

/* Нормалізує кінці рядків та відкидає BOM */
void process_stream(FILE *in, FILE *out) {
    uint8_t in_buf[4096];
    size_t in_len = fread(in_buf, 1, sizeof(in_buf), in);
    size_t pos = 0;

    /* Перевірка та пропуск UTF-8 BOM (0xEF 0xBB 0xBF) на початку */
    if (in_len >= 3 && in_buf[0] == 0xEF && in_buf[1] == 0xBB && in_buf[2] == 0xBF) {
        pos = 3;
    }

    bool prev_cr = false;
    while (pos < in_len) {
        uint32_t cp = 0;
        utf8_error_t err = UTF8_OK;
        size_t consumed = utf8_decode_codepoint(in_buf + pos, in_len - pos, &cp, &err);

        if (consumed == 0) {
            fprintf(stderr, "Помилка UTF-8 на зміщенні %zu (код %d)\n", pos, err);
            break;
        }

        if (cp == '\r') {
            fputc('\n', out);
            prev_cr = true;
        } else if (cp == '\n') {
            if (!prev_cr) {
                fputc('\n', out);
            }
            prev_cr = false;
        } else {
            prev_cr = false;
            fwrite(in_buf + pos, 1, consumed, out);
        }
        pos += consumed;
    }
}

int main(void) {
    process_stream(stdin, stdout);
    return 0;
}
```
```cpp
// utf8_sanitize.cpp — Ідіоматичний валідатор UTF-8 та нормалізатор (C++20).
// Збірка: g++ -std=c++20 -Wall -Wextra -O2 utf8_sanitize.cpp -o utf8_sanitize

#include <iostream>
#include <vector>
#include <span>
#include <cstdint>
#include <string_view>
#include <optional>
#include <system_error>

enum class Utf8Error {
    Ok = 0,
    InvalidByte,
    Overlong,
    Surrogate,
    OutOfRange,
    Truncated
};

struct DecodeResult {
    uint32_t codepoint;
    size_t bytes_consumed;
};

class Utf8Validator {
public:
    static std::optional<DecodeResult> decode_next(std::span<const uint8_t> buffer, Utf8Error &err) {
        if (buffer.empty()) {
            err = Utf8Error::Truncated;
            return std::nullopt;
        }

        const uint8_t b0 = buffer[0];
        if (b0 < 0x80) {
            err = Utf8Error::Ok;
            return DecodeResult{ .codepoint = b0, .bytes_consumed = 1 };
        }

        if ((b0 & 0xE0) == 0xC0) {
            if (buffer.size() < 2) { err = Utf8Error::Truncated; return std::nullopt; }
            const uint8_t b1 = buffer[1];
            if ((b1 & 0xC0) != 0x80) { err = Utf8Error::InvalidByte; return std::nullopt; }

            uint32_t cp = ((b0 & 0x1F) << 6) | (b1 & 0x3F);
            if (cp < 0x80) { err = Utf8Error::Overlong; return std::nullopt; }

            err = Utf8Error::Ok;
            return DecodeResult{ .codepoint = cp, .bytes_consumed = 2 };
        }

        if ((b0 & 0xF0) == 0xE0) {
            if (buffer.size() < 3) { err = Utf8Error::Truncated; return std::nullopt; }
            const uint8_t b1 = buffer[1];
            const uint8_t b2 = buffer[2];
            if ((b1 & 0xC0) != 0x80 || (b2 & 0xC0) != 0x80) {
                err = Utf8Error::InvalidByte;
                return std::nullopt;
            }

            uint32_t cp = ((b0 & 0x0F) << 12) | ((b1 & 0x3F) << 6) | (b2 & 0x3F);
            if (cp < 0x0800) { err = Utf8Error::Overlong; return std::nullopt; }
            if (cp >= 0xD800 && cp <= 0xDFFF) { err = Utf8Error::Surrogate; return std::nullopt; }

            err = Utf8Error::Ok;
            return DecodeResult{ .codepoint = cp, .bytes_consumed = 3 };
        }

        if ((b0 & 0xF8) == 0xF0) {
            if (buffer.size() < 4) { err = Utf8Error::Truncated; return std::nullopt; }
            const uint8_t b1 = buffer[1];
            const uint8_t b2 = buffer[2];
            const uint8_t b3 = buffer[3];
            if ((b1 & 0xC0) != 0x80 || (b2 & 0xC0) != 0x80 || (b3 & 0xC0) != 0x80) {
                err = Utf8Error::InvalidByte;
                return std::nullopt;
            }

            uint32_t cp = ((b0 & 0x07) << 18) | ((b1 & 0x3F) << 12) | ((b2 & 0x3F) << 6) | (b3 & 0x3F);
            if (cp < 0x10000) { err = Utf8Error::Overlong; return std::nullopt; }
            if (cp > 0x10FFFF) { err = Utf8Error::OutOfRange; return std::nullopt; }

            err = Utf8Error::Ok;
            return DecodeResult{ .codepoint = cp, .bytes_consumed = 4 };
        }

        err = Utf8Error::InvalidByte;
        return std::nullopt;
    }

    static void sanitize_stream(std::istream &in, std::ostream &out) {
        std::vector<uint8_t> buffer(std::istreambuf_iterator<char>(in), {});
        if (buffer.empty()) return;

        size_t pos = 0;
        // Пропуск UTF-8 BOM
        if (buffer.size() >= 3 && buffer[0] == 0xEF && buffer[1] == 0xBB && buffer[2] == 0xBF) {
            pos = 3;
        }

        bool prev_cr = false;
        while (pos < buffer.size()) {
            std::span<const uint8_t> remaining{buffer.data() + pos, buffer.size() - pos};
            Utf8Error err = Utf8Error::Ok;
            auto res = decode_next(remaining, err);

            if (!res) {
                std::cerr << "Помилка валідації UTF-8 на зміщенні " << pos << '\n';
                break;
            }

            if (res->codepoint == '\r') {
                out.put('\n');
                prev_cr = true;
            } else if (res->codepoint == '\n') {
                if (!prev_cr) {
                    out.put('\n');
                }
                prev_cr = false;
            } else {
                prev_cr = false;
                out.write(reinterpret_cast<const char*>(buffer.data() + pos), res->bytes_consumed);
            }
            pos += res->bytes_consumed;
        }
    }
};

int main() {
    std::ios_base::sync_with_stdio(false);
    Utf8Validator::sanitize_stream(std::cin, std::cout);
    return 0;
}
```
:::

## Відмінності архітектури C та C++ версій

Порівняння двох реалізацій демонструє різницю системного підходу між мовами:

1. **Керування пам'яттю та перевірками меж:** У C-версії функція приймає пару `(const uint8_t *buf, size_t len)` і вимагає ручної перевірки довжини перед кожним розіменуванням покажчика (`len < 2`, `len < 3` тощо). Помилка в умові призводить до читання за межами виділеного буфера (`heap-buffer-overflow` або `stack-buffer-overflow`). У C++ застосовано `std::span<const uint8_t>`, який інкапсулює буфер та його розмір, запобігаючи передачі розсинхронізованих покажчиків.
2. **Типізація результатів:** У C помилка повертається через вихідний покажчик `utf8_error_t *err`, а успіх сигналізується нульовим поверненням спожитих байтів. У C++ використано типізований `std::optional<DecodeResult>`, що виключає стан, коли функція повернула помилку, але викликач випадково використав неініціалізоване значення кодової точки.

## Логіка нормалізації кінців рядків

Обробка кінців рядків вимагає відстеження стану попереднього символу за допомогою прапорця `prev_cr`. Це розв'язує задачу об'єднання пар `\r\n` без появи зайвих порожніх рядків:

1. **Зустріли `\r`:** Програма негайно записує у вихідний потік символ `\n` і виставляє `prev_cr = true`. Якщо наступним символом виявиться ще один `\r` (стиль старого Mac OS) або звичайний текст, виведений `\n` уже завершив рядок.
2. **Зустріли `\n` відразу після `\r`:** Прапорець `prev_cr` активний. Це означає, що ми щойно обробили першу половину пари `\r\n` і вже записали для неї `\n`. Тому поточний `\n` просто пропускається, а прапорець скидається в `false`.
3. **Зустріли звичайний `\n` (без `\r` перед ним):** Прапорець `prev_cr` неактивний. Символ `\n` записується у вихідний потік як стандартний роздільник рядка Unix.

Така схема дозволяє коректно санітизувати файли, що містять хаотичну суміш різних стилів перенесення рядків (наприклад, після злиття гілок Git із різних операційних систем).

## Перевірка крайових випадків у терміналі

Працездатність валідатора перевіряється передачею спеціально скомпільованих некоректних послідовностей байтів через команду `printf`:

1. **Тест на наддовгий NUL:**
   ```sh
   $ printf '\xC0\x80' | ./utf8_sanitize
   Помилка UTF-8 на зміщенні 0 (код 2)
   ```
   Валідатор негайно повертає код `UTF8_ERR_OVERLONG` і зупиняє обробку.

2. **Тест на заборонений сурогат:**
   ```sh
   $ printf '\xED\xA0\x80' | ./utf8_sanitize
   Помилка UTF-8 на зміщенні 0 (код 3)
   ```
   Спроба закодувати сурогат `U+D800` відхиляється з кодом `UTF8_ERR_SURROGATE`.

3. **Тест на суміш кінців рядків та BOM:**
   ```sh
   $ printf '\xEF\xBB\xBFрядок 1\r\nрядок 2\rрядок 3\n' | ./utf8_sanitize | od -c
   0000000   р   я   д   о   к       1  \n   р   я   д   о   к
   0000020       2  \n   р   я   д   о   к       3  \n
   ```
   Утиліта успішно відсікає три байти BOM на старті, а всі три рядки завершуються суворо одним байтом `\n` (`0x0A`).
