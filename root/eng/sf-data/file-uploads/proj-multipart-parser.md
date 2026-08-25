# ⚙️ Потоковий розбір multipart/form-data на скінченному автоматі

Задача розбору потоку `multipart/form-data` (RFC 7578) виникає в кожному серверному рушії, що приймає файли від браузерів. Традиційний підхід вебфреймворків — зчитати весь HTTP-запит у буфер пам'яті, знайти всі входження роздільника `--boundary` і зберегти файли на диск — стає прямою дорогою до аварійного вичерпання пам'яті (англ. *Out-Of-Memory*, OOM) та відмови в обслуговуванні (DoS). Якщо 100 клієнтів одночасно вантажать відеофайли по 500 МБ, серверу потрібно виділити 50 ГБ оперативної пам'яті лише на утримання вхідних TCP-буферів.

Архітектурне вирішення полягає у створенні потокового парсера (англ. *streaming parser*) на базі детермінованого скінченного автомата (англ. *Deterministic Finite Automaton*, DFA). Такий парсер працює з фіксованим буфером фіксованого розміру (наприклад, 64 КБ), обробляє байти на льоту в міру їх надходження із мережевого сокета, миттєво віддає розібрані блоки у цільовий файл чи хмарний потік і споживає константний обсяг пам'яті `O(1)` незалежно від гігабайтного розміру вхідного файлу.

## Чому наївні алгоритми пошуку підрядка не працюють у потоці

У класичних задачах пошуку підрядка (як-от алгоритми Боєра — Мура чи Кнута — Морріса — Пратта) передбачається, що весь текст уже завантажено в пам'ять як неперервний масив байтів. У мережевому потоці це припущення хибне: дані надходять фрагментами через системний виклик `read()` або подію `epoll`.

Розглянемо ситуацію, коли довжина рядка роздільника становить 32 байти. Сервер виділив буфер розміром 64 КБ. Якщо перші 20 байтів роздільника надійшли на позиції `65516..65535` поточного блоку, а решта 12 байтів надійдуть лише в наступному TCP-пакеті, звичайний виклик `memmem()` або `strstr()` на поточному буфері зазнає невдачі.

Наївний розробник міг би спробувати склеювати буфери (англ. *buffer concatenation*), копіюючи залишок кінця першого блоку на початок другого. Проте це вимагає додаткових операцій копіювання пам'яті (`memcpy`), збільшує накладні витрати на вирівнювання і створює ризик неконтрольованого зростання пам'яті при повільних атаках (коли клієнт шле по одному байту за секунду).

Скінченний автомат усуває копіювання: він зберігає лише індекс збігу `match_idx` у структурі стану. Поки байти збігаються із символами очікуваної межі, автомат лише інкрементально просуває індекс. Якщо на черговому байті виникає розбіжність, автомат знає, скільки саме байтів було помилково прийнято за межу, і миттєво відкатує їх у потік виводу даних файлу.

## Стан автомата та протокольна граматика

Формат `multipart/form-data` складається з послідовності частин, розділених рядком-межею. Повний життєвий цикл автомата охоплює такі стани:

```
[Початок запиту]
       │
       ▼
 ┌──────────────┐
 │ PREAMBLE     │ ── (пропуск сміття до першої межі)
 └──────────────┘
       │
       ▼  знайдено "\r\n--" + boundary
 ┌──────────────┐
 │ PART_HEADERS │ ── (побайтовий розбір Content-Disposition та Content-Type)
 └──────────────┘
       │
       ▼  знайдено "\r\n\r\n" (завершення заголовків частини)
 ┌──────────────┐
 │ PART_DATA    │ ── (потокове викачування тіла файлу через callback)
 └──────────────┘
       │
       ├─────────────────────────────────────────┐
       ▼  знайдено "\r\n--" + boundary           ▼  знайдено "\r\n--" + boundary + "--"
 ┌──────────────┐                          ┌──────────────┐
 │ NEXT_PART    │                          │ END_STREAM   │ (фінал парсингу)
 └──────────────┘                          └──────────────┘
```

Покроковий механізм переходів між станами працює за такими правилами:

1. **`MP_STATE_START` / `MP_STATE_START_BOUNDARY`:** Парсер перебуває у пошуку початкової межі, яка відкриває першу частину форми. Будь-які байти преамбули до першої межі (якщо вони присутні за специфікацією MIME) ігноруються.
2. **`MP_STATE_HEADERS_ALMOST_DONE`:** Після виявлення межі парсер очікує переведення рядка `\r\n`, після чого переходить до читання заголовків окремої частини.
3. **`MP_STATE_HEADER_FIELD`:** Зчитування назви заголовка (наприклад, `Content-Disposition` або `Content-Type`). Зустріч символу двокрапки `:` переводить автомат у стан читання значення. Якщо на першій позиції рядка зустрічається символ `\r\n`, це сигналізує про порожній рядок — заголовки частини завершилися, починається тіло файлу.
4. **`MP_STATE_HEADER_VALUE`:** Накопичення значення заголовка до символу `\r\n`. Після завершення рядка викликається функція зворотного виклику `on_header`, яка передає ім'я та значення заголовка без виділення додаткової динамічної пам'яті.
5. **`MP_STATE_PART_DATA`:** Основний робочий стан. Усі байти потоку напряму передаються у функцію зворотного виклику `on_part_data` (яка одразу скидає їх у дескриптор цільового файлу або сокет S3). Щойно зустрічається символ повернення каретки `\r`, автомат призупиняє скидання даних і переходить у стан перевірки межі.
6. **`MP_STATE_BOUNDARY_MATCH`:** Автомат побайтово звіряє наступні байти з очікуваним рядком `\n--` + `boundary`. Якщо рядок збігся повністю, частина вважається завершеною (викликається `on_part_end`). Якщо ж на будь-якому кроці виявлено невідповідність (наприклад, у двійковому файлі просто зустрівся байт `\r\n` після якого йдуть інші байти), автомат повертає помилково затримані байти у потік виводу частини та повертається до стану `MP_STATE_PART_DATA`.

## Реалізація потокового парсера

Розглянемо реалізацію потокового парсера, який приймає фрагменти вхідного потоку байтів довільної довжини, інкрементально шукає межу за допомогою автомата станів і викликає функції зворотного виклику (англ. *callbacks*) при знаходженні заголовків, нових блоків даних частини та кінця частини.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

typedef enum {
    MP_STATE_START,
    MP_STATE_START_BOUNDARY,
    MP_STATE_HEADER_FIELD,
    MP_STATE_HEADER_VALUE,
    MP_STATE_HEADERS_ALMOST_DONE,
    MP_STATE_PART_DATA,
    MP_STATE_BOUNDARY_MATCH,
    MP_STATE_END
} mp_state_t;

typedef struct {
    void (*on_part_begin)(void *user_data);
    void (*on_header)(const char *name, size_t nlen, const char *val, size_t vlen, void *user_data);
    void (*on_part_data)(const unsigned char *data, size_t len, void *user_data);
    void (*on_part_end)(void *user_data);
} mp_callbacks_t;

typedef struct {
    mp_state_t state;
    char boundary[128];
    size_t boundary_len;
    size_t match_idx;
    char header_name[256];
    size_t header_name_len;
    char header_val[1024];
    size_t header_val_len;
    mp_callbacks_t cb;
    void *user_data;
} mp_parser_t;

void mp_parser_init(mp_parser_t *p, const char *boundary, mp_callbacks_t cb, void *user_data) {
    memset(p, 0, sizeof(*p));
    p->state = MP_STATE_START;
    p->boundary[0] = '-';
    p->boundary[1] = '-';
    strncpy(p->boundary + 2, boundary, sizeof(p->boundary) - 3);
    p->boundary_len = strlen(p->boundary);
    p->cb = cb;
    p->user_data = user_data;
}

size_t mp_parser_execute(mp_parser_t *p, const unsigned char *buf, size_t len) {
    size_t i = 0;
    size_t mark = 0;

    for (i = 0; i < len; ++i) {
        unsigned char c = buf[i];

        switch (p->state) {
        case MP_STATE_START:
        case MP_STATE_START_BOUNDARY:
            if (c == (unsigned char)p->boundary[p->match_idx]) {
                p->match_idx++;
                if (p->match_idx == p->boundary_len) {
                    p->match_idx = 0;
                    p->state = MP_STATE_HEADERS_ALMOST_DONE;
                    if (p->cb.on_part_begin) p->cb.on_part_begin(p->user_data);
                }
            } else {
                p->match_idx = 0;
            }
            break;

        case MP_STATE_HEADERS_ALMOST_DONE:
            if (c == '\n') {
                p->state = MP_STATE_HEADER_FIELD;
                p->header_name_len = 0;
                p->header_val_len = 0;
            }
            break;

        case MP_STATE_HEADER_FIELD:
            if (c == '\r') {
                /* Порожній рядок перед тілом даних */
            } else if (c == '\n') {
                p->state = MP_STATE_PART_DATA;
                mark = i + 1;
            } else if (c == ':') {
                p->state = MP_STATE_HEADER_VALUE;
            } else if (p->header_name_len + 1 < sizeof(p->header_name)) {
                p->header_name[p->header_name_len++] = (char)c;
            }
            break;

        case MP_STATE_HEADER_VALUE:
            if (c == '\r') {
                /* Очікування LF */
            } else if (c == '\n') {
                if (p->cb.on_header) {
                    p->cb.on_header(p->header_name, p->header_name_len,
                                    p->header_val, p->header_val_len, p->user_data);
                }
                p->header_name_len = 0;
                p->header_val_len = 0;
                p->state = MP_STATE_HEADER_FIELD;
            } else if (c != ' ' || p->header_val_len > 0) {
                if (p->header_val_len + 1 < sizeof(p->header_val)) {
                    p->header_val[p->header_val_len++] = (char)c;
                }
            }
            break;

        case MP_STATE_PART_DATA:
            if (c == '\r') {
                if (i > mark && p->cb.on_part_data) {
                    p->cb.on_part_data(buf + mark, i - mark, p->user_data);
                }
                p->state = MP_STATE_BOUNDARY_MATCH;
                p->match_idx = 0;
            }
            break;

        case MP_STATE_BOUNDARY_MATCH:
            if (p->match_idx == 0 && c == '\n') {
                p->match_idx = 1;
            } else if (p->match_idx >= 1 && (p->match_idx - 1) < p->boundary_len &&
                       c == (unsigned char)p->boundary[p->match_idx - 1]) {
                p->match_idx++;
                if ((p->match_idx - 1) == p->boundary_len) {
                    if (p->cb.on_part_end) p->cb.on_part_end(p->user_data);
                    p->state = MP_STATE_HEADERS_ALMOST_DONE;
                    p->match_idx = 0;
                }
            } else {
                /* Несправжня межа: скидаємо накопичені байти назад у тіло частини */
                if (p->cb.on_part_data) {
                    p->cb.on_part_data((const unsigned char *)"\r", 1, p->user_data);
                    if (p->match_idx > 1) {
                        p->cb.on_part_data((const unsigned char *)"\n", 1, p->user_data);
                        p->cb.on_part_data((const unsigned char *)p->boundary, p->match_idx - 2, p->user_data);
                    }
                }
                p->state = MP_STATE_PART_DATA;
                mark = i;
                i--; /* повторна обробка поточного байта */
            }
            break;

        case MP_STATE_END:
            return i;
        }
    }

    if (p->state == MP_STATE_PART_DATA && i > mark) {
        if (p->cb.on_part_data) {
            p->cb.on_part_data(buf + mark, i - mark, p->user_data);
        }
    }

    return len;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <span>
#include <functional>
#include <vector>
#include <cstdint>

enum class MultipartState {
    Start,
    StartBoundary,
    HeaderField,
    HeaderValue,
    HeadersAlmostDone,
    PartData,
    BoundaryMatch,
    End
};

struct MultipartCallbacks {
    std::function<void()> on_part_begin;
    std::function<void(std::string_view name, std::string_view value)> on_header;
    std::function<void(std::span<const uint8_t> chunk)> on_part_data;
    std::function<void()> on_part_end;
};

class StreamingMultipartParser {
public:
    explicit StreamingMultipartParser(std::string_view boundary, MultipartCallbacks callbacks)
        : callbacks_(std::move(callbacks)),
          boundary_("--" + std::string(boundary)),
          state_(MultipartState::Start),
          match_index_(0) {}

    void execute(std::span<const uint8_t> buffer) {
        size_t mark = 0;

        for (size_t i = 0; i < buffer.size(); ++i) {
            const uint8_t byte = buffer[i];

            switch (state_) {
            case MultipartState::Start:
            case MultipartState::StartBoundary:
                if (byte == static_cast<uint8_t>(boundary_[match_index_])) {
                    if (++match_index_ == boundary_.size()) {
                        match_index_ = 0;
                        state_ = MultipartState::HeadersAlmostDone;
                        if (callbacks_.on_part_begin) callbacks_.on_part_begin();
                    }
                } else {
                    match_index_ = 0;
                }
                break;

            case MultipartState::HeadersAlmostDone:
                if (byte == '\n') {
                    state_ = MultipartState::HeaderField;
                    header_name_.clear();
                    header_value_.clear();
                }
                break;

            case MultipartState::HeaderField:
                if (byte == '\r') {
                    // Очікуємо переведення рядка
                } else if (byte == '\n') {
                    state_ = MultipartState::PartData;
                    mark = i + 1;
                } else if (byte == ':') {
                    state_ = MultipartState::HeaderValue;
                } else {
                    header_name_.push_back(static_cast<char>(byte));
                }
                break;

            case MultipartState::HeaderValue:
                if (byte == '\r') {
                    // Очікуємо переведення рядка
                } else if (byte == '\n') {
                    if (callbacks_.on_header) {
                        callbacks_.on_header(header_name_, header_value_);
                    }
                    header_name_.clear();
                    header_value_.clear();
                    state_ = MultipartState::HeaderField;
                } else if (byte != ' ' || !header_value_.empty()) {
                    header_value_.push_back(static_cast<char>(byte));
                }
                break;

            case MultipartState::PartData:
                if (byte == '\r') {
                    if (i > mark && callbacks_.on_part_data) {
                        callbacks_.on_part_data(buffer.subspan(mark, i - mark));
                    }
                    state_ = MultipartState::BoundaryMatch;
                    match_index_ = 0;
                }
                break;

            case MultipartState::BoundaryMatch:
                if (match_index_ == 0 && byte == '\n') {
                    match_index_ = 1;
                } else if (match_index_ >= 1 && (match_index_ - 1) < boundary_.size() &&
                           byte == static_cast<uint8_t>(boundary_[match_index_ - 1])) {
                    match_index_++;
                    if ((match_index_ - 1) == boundary_.size()) {
                        if (callbacks_.on_part_end) callbacks_.on_part_end();
                        state_ = MultipartState::HeadersAlmostDone;
                        match_index_ = 0;
                    }
                } else {
                    // Відкат помилкового збігу межі у двійковому вмісті
                    if (callbacks_.on_part_data) {
                        const uint8_t cr = '\r';
                        callbacks_.on_part_data(std::span<const uint8_t>(&cr, 1));
                        if (match_index_ > 1) {
                            const uint8_t lf = '\n';
                            callbacks_.on_part_data(std::span<const uint8_t>(&lf, 1));
                            auto bspan = std::span<const uint8_t>(
                                reinterpret_cast<const uint8_t*>(boundary_.data()), match_index_ - 2);
                            callbacks_.on_part_data(bspan);
                        }
                    }
                    state_ = MultipartState::PartData;
                    mark = i;
                    i--; // Повторно обробляємо поточний байт
                }
                break;

            case MultipartState::End:
                return;
            }
        }

        if (state_ == MultipartState::PartData && buffer.size() > mark) {
            if (callbacks_.on_part_data) {
                callbacks_.on_part_data(buffer.subspan(mark, buffer.size() - mark));
            }
        }
    }

private:
    MultipartCallbacks callbacks_;
    std::string boundary_;
    MultipartState state_;
    size_t match_index_;
    std::string header_name_;
    std::string header_value_;
};
```
```ts
import { Readable, Writable, Transform } from 'node:stream';
import { pipeline } from 'node:stream/promises';
import * as fs from 'node:fs';

export interface MultipartPartHeader {
  name: string;
  filename?: string;
  contentType?: string;
}

export class StreamingMultipartWriter extends Writable {
  private boundary: Buffer;
  private currentPartFile?: fs.WriteStream;
  private isCollectingHeader = false;
  private headerBuffer = '';

  constructor(boundaryStr: string, private outputDir: string) {
    super();
    this.boundary = Buffer.from(`--${boundaryStr}`);
  }

  override _write(chunk: Buffer, _encoding: BufferEncoding, callback: (error?: Error | null) => void): void {
    // Потоковий запис безпосередньо у дескриптор цільового файлу
    // Backpressure підтримується вбудованою чергою Node.js Stream
    if (this.currentPartFile && !this.currentPartFile.write(chunk)) {
      this.currentPartFile.once('drain', callback);
    } else {
      callback();
    }
  }

  override _final(callback: (error?: Error | null) => void): void {
    if (this.currentPartFile) {
      this.currentPartFile.end(callback);
    } else {
      callback();
    }
  }
}
```
:::

## Покроковий розбір проходження байтів крізь буфер

Щоби зрозуміти, як саме забезпечується константне споживання пам'яті, простежимо рух байтів крізь парсер на конкретному прикладі.

Припустімо, клієнт надсилає файл із рядком-роздільником `BOUNDARY123`. Вхідний потік надходить двома послідовними фрагментами (чанками) по 16 байтів:

```
Чанк 1: [ 'H', 'e', 'l', 'l', 'o', ' ', 'W', 'o', 'r', 'l', 'd', '\r', '\n', '-', '-', 'B' ]
Чанк 2: [ 'O', 'U', 'N', 'D', 'A', 'R', 'Y', '1', '2', '3', '\r', '\n', 'P', 'a', 'r', 't' ]
```

Простежимо стан автомата на кожному кроці:

1. **Обробка Чанка 1:**
   - Байти з індексами `0..10` (`Hello World`): Автомат перебуває у стані `MP_STATE_PART_DATA`. Кожен байт ідентифікується як корисне навантаження файлу.
   - Байт `11` (`\r`): Автомат фіксує маркер початку можливої межі. Він викликає `on_part_data` для зрізу `buf[0..11]` (передаючи байти `Hello World`) і перемикає стан у `MP_STATE_BOUNDARY_MATCH` із `match_idx = 0`.
   - Байт `12` (`\n`): Збігається з першим очікуваним символом розриву рядка межі. `match_idx` стає `1`.
   - Байти `13..15` (`--B`): Збігаються з першими трьома байтами рядка `--BOUNDARY123`. `match_idx` зростає до `4`.
   - **Кінець Чанка 1:** Робочий буфер вичерпано. Зверніть увагу: жоден байт із послідовності `\r\n--B` не було скинуто в цільовий файл! Вони зберігаються у внутрішньому стані перевірки. Пам'ять звільнено, дескриптор сокета готовий приймати наступний пакет.

2. **Обробка Чанка 2:**
   - Байти `0..8` (`OUNDARY123`): Автомат продовжує порівняння з місця `match_idx = 4`. Усі символи послідовно збігаються до повного розміру межі.
   - Повний збіг досягнуто: автомат викликає `on_part_end()`, сповіщаючи сховище, що поточний файл повністю прийнято.
   - Стан перемикається у `MP_STATE_HEADERS_ALMOST_DONE`, а `match_idx` скидається в `0`.
   - Байти `9..15` (`\r\nPart`): Автомат починає парсинг заголовків наступної частини форми.

## Розрахунок бюджету оперативної пам'яті під високим навантаженням

Щоби переконатися в масштабованості потокового підходу, порахуємо бюджет пам'яті для високонавантаженого сервера, який обслуговує `10 000` одночасних активних з'єднань завантаження файлів по 1 ГБ кожне.

### Модель 1: Наївна повна буферизація в пам'яті
Якщо сервер намагається накопичити тіло кожного файлу в пам'яті до завершення завантаження:

```
Пам'ять на з'єднання = 1 ГБ
Сумарна пам'ять = 10 000 з'єднань · 1 ГБ = 10 ТБ оперативної пам'яті
```
Жоден типовий вебсервер не має 10 ТБ оперативної пам'яті. Результат: миттєве спрацьовування механізму ядра Linux OOM Killer, завершення процесу сервера та падіння системи.

### Модель 2: Потоковий парсер із контролем зворотного тиску
При потоковій обробці витрати пам'яті на одне з'єднання складаються з фіксованих структур:

```
Буфер прийому сокета TCP (SO_RCVBUF)      : 64 КБ
Буфер сесії TLS/SSL (OpenSSL SSL_read)   : 16 КБ
Внутрішній буфер чанка парсера DFA       : 64 КБ
Структура стану парсера (mp_parser_t)     : ~2 КБ
Буфер вихідного потоку запису (диск/S3)  : 128 КБ
-------------------------------------------------
Разом на одне активне з'єднання          : ~274 КБ

Сумарна пам'ять на 10 000 з'єднань = 10 000 · 274 КБ ≈ 2.67 ГБ
```

Сервер вільно обробляє 10 000 одночасних гігабайтних завантажень, споживаючи менше ніж 3 ГБ оперативної пам'яті. Усі ресурси витрачаються лише на поточне обслуговування активного мережевого вікна, а не на пасивне очікування завершення передачі гігабайтів.

## Одночасне обчислення криптографічного хешу на льоту

Важливою практичною перевагою архітектури зворотних викликів є можливість обчислення контрольної суми (SHA-256) без повторного читання файлу з диска.

У традиційній буферизованій схемі сервер спершу записує 5 ГБ на диск, а потім знову відкриває дескриптор, вичитує всі 5 ГБ крізь процесор для розрахунку хешу SHA-256 і зберігає результат. Це подвоює навантаження на дисковий контролер і кеш процесора.

У потоковому парсері контекст хешування ініціалізується під час спрацьовування `on_part_begin()`, і кожен блок байтів передається у криптографічний рушій паралельно із записом:

:::tabs
```c
/* Ініціалізація SHA-256 у колбеку початку частини */
SHA256_Init(&user_ctx->sha256_ctx);

/* У колбеку on_part_data байти одночасно летять у сокет/диск та в хеш-функцію */
void on_part_data_handler(const unsigned char *data, size_t len, void *user_data) {
    upload_context_t *ctx = (upload_context_t *)user_data;
    write(ctx->out_fd, data, len);              /* запис на диск */
    SHA256_Update(&ctx->sha256_ctx, data, len); /* оновлення хешу в L1-кеші */
}

/* У колбеку on_part_end фіналізується результат */
SHA256_Final(ctx->final_sha256_digest, &ctx->sha256_ctx);
```
```cpp
#include <openssl/evp.h>
#include <memory>
#include <span>
#include <vector>
#include <cstdint>

class StreamingHasher {
public:
    StreamingHasher() : ctx_(EVP_MD_CTX_new(), &EVP_MD_CTX_free) {
        EVP_DigestInit_ex(ctx_.get(), EVP_sha256(), nullptr);
    }

    void update(std::span<const uint8_t> chunk) {
        EVP_DigestUpdate(ctx_.get(), chunk.data(), chunk.size());
    }

    std::vector<uint8_t> finalize() {
        std::vector<uint8_t> digest(EVP_MD_size(EVP_sha256()));
        unsigned int len = 0;
        EVP_DigestFinal_ex(ctx_.get(), digest.data(), &len);
        return digest;
    }

private:
    std::unique_ptr<EVP_MD_CTX, decltype(&EVP_MD_CTX_free)> ctx_;
};
```
:::

Байти файлу потрапляють у криптографічний блок безпосередньо з кешу L1 процесора в момент першого проходження крізь парсер, зменшуючи час постобробки до нуля.

## Керування пулом структур стану парсера

Щоби запобігти фрагментації пам'яті при обробці тисяч коротких та довгих запитів, сервери не викликають системний алокатор `malloc()` / `free()` на кожному HTTP-запиті.

Замість цього застосовується пул об'єктів (англ. *object pool* / *slab allocator*). Фіксований масив структур `mp_parser_t` виділяється один раз під час запуску робочого процесу. Коли сокет підключається, вільна структура дістається зі стека вільних дескрипторів за час `O(1)`. Після завершення читання виклик `mp_parser_init()` скидає лічильники та індекси, і структура повертається назад у пул без звернення до ядра ОС.

## Керування тиском зворотного потоку (Backpressure)

Якщо вхідний мережевий канал клієнта працює на швидкості 1 Гбіт/с, а сервер записує файл на повільний диск або транслює його у віддалене хмарне сховище зі швидкістю 50 МБ/с, виникає невідповідність швидкостей виробника та споживача даних.

Якщо парсер безконтрольно читатиме дані із сокета, несинхронізовані байти накопичуватимуться у черзі вихідного буфера в оперативній пам'яті сервера. Для файлу розміром 2 ГБ це призведе до поступового виділення всіх 2 ГБ RAM, нівелюючи всю перевагу потокового парсингу.

Механізм *backpressure* (зворотного тиску) реалізується через поріг високої води (англ. *high-watermark*) та поріг низької води (англ. *low-watermark*):

1. Коли розмір нескинутого буфера запису досягає порогу високої води (наприклад, 256 КБ), сервер викликає примусову зупинку читання з мережевого сокета (зняття прапорця `EPOLLIN` у Linux або виклик `stream.pause()` у подієво-орієнтованих середовищах).
2. Операційна система сервера перестає вичитувати пакети з буфера ядра TCP.
3. Буфер прийому TCP (англ. *TCP Receive Window*, `rcv_wnd`) заповнюється, і стек TCP автоматично надсилає клієнту сегмент із нульовим розміром вікна (англ. *TCP ZeroWindow*).
4. Клієнтська операційна система апаратно призупиняє передачу пакетів у фізичний кабель.
5. Щойно цільовий диск вичитує накопичені дані нижче порогу низької води (наприклад, 64 КБ), сервер відновлює прапорець `EPOLLIN`, TCP-стек надсилає оновлення вікна (англ. *Window Update*), і потік байтів відновлюється.

Завдяки цьому ланцюжку зворотного зв'язку максимальний обсяг пам'яті на одне активне з'єднання суворо обмежений розміром буфера високої води (256 КБ) незалежно від швидкості клієнта чи тривалості завантаження.

## Асинхронна інтеграція з неблоківними сокетами (epoll / kqueue)

У реальних виробничих вебсерверах (як-от NGINX або Envoy) потоковий парсер інтегрується безпосередньо в неблоківний цикл подій:

```
[Подія сокета: EPOLLIN]
         │
         ▼
  Виклик read(fd, buf, sizeof(buf))
         │
         ├─► повернув -1 (errno == EAGAIN) ──► вихід із циклу, чекаємо наступної події
         ├─► повернув 0 (EOF) ──────────────► обрив зв'язку, очищення ресурсів
         │
         ▼
  mp_parser_execute(&parser, buf, bytes_read)
         │
         ▼
  Колбек on_part_data скидає байти у вихідний канал
         │
         ├─► вихідний канал заповнений (EAGAIN) ──► вимикаємо EPOLLIN на сокеті клієнта
         │                                          вмикаємо EPOLLOUT на сокеті диску
         └─► вихідний канал вільний ──────────────► продовжуємо читання
```

Якщо клієнт починає навмисно надсилати по 1 байту кожні 10 секунд (атака повільного завантаження, Slow POST), сервер не блокує окремий системний потік ОС. Таймер бездіяльності (англ. *idle socket timeout*) автоматично закриває з'єднання, якщо з моменту останнього байта минуло понад 30 секунд.

## Техніка Zero-Copy через Linux splice()

У високонавантажених C/C++ серверах під Linux копіювання байтів із буфера сокета в простір користувача (англ. *user space*) і назад у дескриптор диска створює помітне навантаження на підсистему пам'яті процесора.

Для досягнення максимальної пропускної здатності застосовують системний виклик `splice()`. Архітектура виглядає так:

1. Парсер простору користувача зчитує лише заголовки частини (перші кілька сотень байтів).
2. Щойно виявлено перехід у `MP_STATE_PART_DATA`, сервер створює неіменований системний канал ядра (англ. *pipe*).
3. Основне тіло файлу перекачується безпосередньо між сокетом клієнта та файловим дескриптором цільового диска в просторі ядра (англ. *kernel space*) без жодного переходу контексту:

:::tabs
```c
/* Перекачування без копіювання в пам'ять процесу користувача */
ssize_t bytes_spliced = splice(client_socket_fd, NULL, pipe_fd[1], NULL,
                               chunk_len, SPLICE_F_MOVE | SPLICE_F_NONBLOCK);
splice(pipe_fd[0], NULL, destination_file_fd, NULL,
       bytes_spliced, SPLICE_F_MOVE | SPLICE_F_NONBLOCK);
```
```cpp
#include <fcntl.h>
#include <unistd.h>
#include <system_error>
#include <cstdint>

class KernelSpliceBridge {
public:
    KernelSpliceBridge() {
        if (::pipe2(pipe_fd_, O_NONBLOCK) == -1) {
            throw std::system_error(errno, std::generic_category(), "pipe2 failed");
        }
    }

    ~KernelSpliceBridge() {
        if (pipe_fd_[0] != -1) ::close(pipe_fd_[0]);
        if (pipe_fd_[1] != -1) ::close(pipe_fd_[1]);
    }

    ssize_t transfer(int source_fd, int dest_fd, size_t max_bytes) {
        ssize_t in = ::splice(source_fd, nullptr, pipe_fd_[1], nullptr,
                              max_bytes, SPLICE_F_MOVE | SPLICE_F_NONBLOCK);
        if (in <= 0) return in;

        return ::splice(pipe_fd_[0], nullptr, dest_fd, nullptr,
                        static_cast<size_t>(in), SPLICE_F_MOVE | SPLICE_F_NONBLOCK);
    }

private:
    int pipe_fd_[2] = {-1, -1};
};
```
:::

4. Ядро переставляє покажчики на фізичні сторінки оперативної пам'яті (англ. *page remapping*), усуваючи навантаження на шину оперативної пам'яті процесора.

## Парсинг кодованих параметрів (RFC 5987 / RFC 2231)

Заголовок `Content-Disposition` часто містить імена файлів із національними абетками (наприклад, кирилицею чи ієрогліфами). Сучасні браузери надсилають їх у розширеному форматі RFC 5987:

```http
Content-Disposition: form-data; name="document"; filename="zvity.pdf"; filename*=UTF-8''%D0%B7%D0%B2%D1%96%D1%82%D0%B8.pdf
```

Потоковий парсер розбирає ці параметри за таким алгоритмом:

1. **Пріоритет розширеного параметра `filename*`.** Якщо присутні обидва параметри (`filename` та `filename*`), парсер зобов'язаний віддати перевагу `filename*`, оскільки він містить точну вказівку кодування та мови.
2. **Розділення трійки полів.** Значення параметра `filename*` розбивається двома одинарними лапками `'` на три компоненти: кодування (`UTF-8`), мовний тег (може бути порожнім) та відсотково-кодований рядок (`%D0%B7%D0%B2%D1%96%D1%82%D0%B8.pdf`).
3. **Потокове розкодування відсоткових послідовностей.** Парсер перетворює кожні три символи `%XX` на один відповідний байт на льоту, перевіряючи валідність отриманої UTF-8 послідовності. Якщо байти утворюють некоректний UTF-8 символ, парсер відкочується до безпечного ASCII-параметра `filename`.

## Обробка помилок диска та очищення тимчасових ресурсів

Якщо під час потокового запису файлу розміром кілька гігабайтів на серверному диску закінчується вільне місце (помилка ядра `ENOSPC`), система повинна коректно відреагувати:

* **Миттєве переривання сокета.** Парсер не повинен продовжувати зчитувати залишок мегабайтів від клієнта. Сокет закривається або клієнту надсилається відповідь `507 Insufficient Storage`.
* **Атомарне видалення часткового файлу (Unlink).** Сервер негайно викликає системний виклик `unlink()` на дескрипторі тимчасового файлу. Якщо цього не зробити, незавершені завантаження поступово заб'ють дисковий простір «файлами-зомбі», які не прив'язані до жодного запису в базі даних.
* **Таймаути незавершених сесій.** Фоновий процес періодично перевіряє каталог тимчасових файлів і видаляє будь-які файли, час останньої модифікації яких перевищує 1 годину.

## Порівняльний аналіз парсерів в екосистемах

| Екосистема / Бібліотека | Архітектурна модель | Споживання RAM | Обробка Backpressure |
| :--- | :--- | :--- | :--- |
| **Node.js (`busboy`)** | Скінченний автомат на базі подій | Константне (`O(1)`, ~32 КБ) | Нативна через потоки `stream.Readable.pause()` |
| **Node.js (`multer` memory)** | Буферизація всього масиву | Пропорційне (`O(N)`, розмір файлу) | Відсутня (небезпечно для файлів >10 МБ) |
| **Go (`mime/multipart`)** | Буферизований потік `io.Reader` | Фіксований буфер (`32 МБ` за дефолтом) | Підтримується через блокування горутини читача |
| **Rust (`actix-multipart`)** | Асинхронний акторний потік (`Stream`) | Константне (`O(1)`, чанки по 64 КБ) | Повний контроль через систему опитування `Poll` |
| **C/C++ (DFA Parser)** | Побайтовий автомат без динамічної RAM | Абсолютний мінімум (<4 КБ на стан) | Через селектори `epoll` / зняття `EPOLLIN` |

## Пастки реалізації та захист від атак

1. **Фальшивий збіг межі всередині двійкових файлів (False Positive Boundary).**
   Двійковий файл (наприклад, скомпільований бінарник чи заархівований ZIP) може містити випадкову послідовність байтів, яка збігається з першими 10–15 символами рядка `boundary`. Якщо парсер наївно відкидає ці байти і переходить у стан закриття частини, файл буде непоправно пошкоджено. Автомат зобов'язаний реалізувати механізм відкату (англ. *rollback*): якщо повна межа не підтвердилася, всі накопичені символи повертаються назад у потік виводу частини.

2. **Захист від атак вичерпання пам'яті через заголовки (Slowloris Header Exhaustion).**
   Зловмисник може надіслати запит із нескінченно довгим рядком заголовка (наприклад, `Content-Disposition: form-data; name="xxxx..."` довжиною 100 МБ) без переведення рядка `\r\n`. Потоковий парсер зобов'язаний обмежувати максимальний розмір буфера заголовків (зазвичай 4–8 КБ) і негайно обривати TCP-з'єднання з кодом помилки `431 Request Header Fields Too Large` при перевищенні ліміту.

3. **Колізія випадкового роздільника.**
   Імовірність того, що випадково згенерований 70-символьний рядок межі (наприклад, `----WebKitFormBoundary7MA4YWxkTrZu0gW`) повністю збіжиться із двійковими даними всередині файлу, становить приблизно `1 / (64^70) ≈ 10^(-126)`, що практично неможливо у спостережуваному всесвіті. Проте для гарантованої стійкості протокол дозволяє передавати префікс подвійного дефісу та суворий контроль структури `\r\n`.
