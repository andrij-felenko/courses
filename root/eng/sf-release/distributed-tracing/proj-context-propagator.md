# ⚙️ Практикум: парсер W3C Trace Context та ядро спан-контексту

У високонавантажених сервісах, API-шлюзах та вбудованих системах використання повнорозмірних SDK телеметрії іноді виявляється неприпустимо дорогим через надмірне виділення динамічної пам'яті (англ. *heap allocation*), фонові потоки експортерів та накладні витрати на рефлексію. Проте необхідність брати участь у наскрізному розподіленому трейсингу залишається: шлюз або мікросервіс зобов'язаний вилучати вхідний контекст із заголовків, генерувати новий ідентифікатор спана, зв'язувати його з батьківським і коректно передавати сформований контекст далі за мережевим ланцюгом.

Розглянемо створення власного високоефективного, потокобезпечного та повністю вільного від алокацій (англ. *zero-allocation*) рушія поширення контексту відповідно до міжнародного стандарту W3C Trace Context.

## Архітектурний контракт W3C Traceparent

Заголовок `traceparent` має фіксовану довжину 55 байтів (для поточної версії `00`) і складається з чотирьох полів, розділених дефісом:

```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
             │  │                                │                │
             │  │                                │                └─ 4. Прапорці (2 hex, 1 байт)
             │  │                                └─ 3. Parent/Span ID (16 hex, 8 байтів)
             │  └─ 2. Trace ID (32 hex, 16 байтів)
             └─ 1. Версія (2 hex, 1 байт)
```

Специфікація накладає суворі валідаційні обмеження:
1. **Версія (`version`):** рівно 2 шістнадцяткових символи. Поточна версія — `00`. Значення `ff` вважається неприпустимим назавжди. Якщо версія більша за `00`, парсер повинен успішно зчитати перші 55 символів за правилами версії `00`, ігноруючи будь-які додаткові поля після четвертого дефіса (принцип прямої сумісності).
2. **Trace ID:** рівно 32 шістнадцяткових символи (16 байтів). Значення, що складається виключно з нулів (`00000000000000000000000000000000`), є недійсним (англ. *all-zero invalid*) і повинно призводити до відхилення всього заголовка.
3. **Parent / Span ID:** рівно 16 шістнадцяткових символів (8 байтів). Повністю нульовий ідентифікатор (`0000000000000000`) також є недійсним.
4. **Прапорці трейсу (`trace-flags`):** 2 шістнадцяткових символи (8-бітова бітова маска). Найменший значущий біт (`0x01`) визначає стан `Recorded` (запит відібрано для запису). Решта 7 бітів зарезервовані для майбутніх версій стандарту і не повинні спотворюватися під час ретрансляції.

## Реалізація парсера та генератора контексту

Реалізуємо модулі вилучення (Extract), валідації, генерації нового дочірнього спана та впровадження (Inject) заголовка різними мовами програмування.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TRACEPARENT_LEN 55
#define TRACE_ID_BYTES 16
#define SPAN_ID_BYTES 8

#define FLAG_RECORDED 0x01

typedef struct {
    uint8_t version;
    uint8_t trace_id[TRACE_ID_BYTES];
    uint8_t span_id[SPAN_ID_BYTES];
    uint8_t flags;
} trace_context_t;

/* Таблиця для швидкого декодування hex символів у 4-бітне значення */
static const int8_t hex_table[256] = {
    ['0'] = 0, ['1'] = 1, ['2'] = 2, ['3'] = 3, ['4'] = 4,
    ['5'] = 5, ['6'] = 6, ['7'] = 7, ['8'] = 8, ['9'] = 9,
    ['a'] = 10, ['b'] = 11, ['c'] = 12, ['d'] = 13, ['e'] = 14, ['f'] = 15,
    ['A'] = 10, ['B'] = 11, ['C'] = 12, ['D'] = 13, ['E'] = 14, ['F'] = 15,
    [0 ... '0' - 1] = -1,
    ['9' + 1 ... 'A' - 1] = -1,
    ['F' + 1 ... 'a' - 1] = -1,
    ['f' + 1 ... 255] = -1
};

static bool decode_hex_bytes(const char *src, size_t hex_len, uint8_t *dst) {
    for (size_t i = 0; i < hex_len; i += 2) {
        int8_t hi = hex_table[(uint8_t)src[i]];
        int8_t lo = hex_table[(uint8_t)src[i + 1]];
        if (hi < 0 || lo < 0) {
            return false;
        }
        dst[i / 2] = (uint8_t)((hi << 4) | lo);
    }
    return true;
}

static bool is_all_zeros(const uint8_t *data, size_t len) {
    uint8_t acc = 0;
    for (size_t i = 0; i < len; ++i) {
        acc |= data[i];
    }
    return acc == 0;
}

bool parse_traceparent(const char *header_val, size_t len, trace_context_t *out_ctx) {
    if (!header_val || len < TRACEPARENT_LEN) {
        return false;
    }

    /* Перевірка дефісів-розділювачів */
    if (header_val[2] != '-' || header_val[35] != '-' || header_val[52] != '-') {
        return false;
    }

    /* 1. Декодування версії */
    int8_t v_hi = hex_table[(uint8_t)header_val[0]];
    int8_t v_lo = hex_table[(uint8_t)header_val[1]];
    if (v_hi < 0 || v_lo < 0) return false;
    uint8_t ver = (uint8_t)((v_hi << 4) | v_lo);

    if (ver == 0xFF) {
        return false; /* Версія ff заборонена стандартом */
    }

    /* Для версії 00 довжина повинна бути строго 55 символів */
    if (ver == 0x00 && len != TRACEPARENT_LEN) {
        return false;
    }

    /* 2. Декодування Trace ID (32 hex -> 16 байтів) */
    uint8_t trace_id[TRACE_ID_BYTES];
    if (!decode_hex_bytes(header_val + 3, 32, trace_id)) {
        return false;
    }
    if (is_all_zeros(trace_id, TRACE_ID_BYTES)) {
        return false;
    }

    /* 3. Декодування Parent/Span ID (16 hex -> 8 байтів) */
    uint8_t span_id[SPAN_ID_BYTES];
    if (!decode_hex_bytes(header_val + 36, 16, span_id)) {
        return false;
    }
    if (is_all_zeros(span_id, SPAN_ID_BYTES)) {
        return false;
    }

    /* 4. Декодування прапорців (2 hex -> 1 байт) */
    int8_t f_hi = hex_table[(uint8_t)header_val[53]];
    int8_t f_lo = hex_table[(uint8_t)header_val[54]];
    if (f_hi < 0 || f_lo < 0) return false;
    uint8_t flags = (uint8_t)((f_hi << 4) | f_lo);

    out_ctx->version = ver;
    memcpy(out_ctx->trace_id, trace_id, TRACE_ID_BYTES);
    memcpy(out_ctx->span_id, span_id, SPAN_ID_BYTES);
    out_ctx->flags = flags;
    return true;
}

bool format_traceparent(const trace_context_t *ctx, char *out_buf, size_t buf_size) {
    if (!ctx || !out_buf || buf_size < (TRACEPARENT_LEN + 1)) {
        return false;
    }

    static const char hex_digits[] = "0123456789abcdef";
    char *p = out_buf;

    /* Версія */
    *p++ = hex_digits[(ctx->version >> 4) & 0x0F];
    *p++ = hex_digits[ctx->version & 0x0F];
    *p++ = '-';

    /* Trace ID */
    for (size_t i = 0; i < TRACE_ID_BYTES; ++i) {
        *p++ = hex_digits[(ctx->trace_id[i] >> 4) & 0x0F];
        *p++ = hex_digits[ctx->trace_id[i] & 0x0F];
    }
    *p++ = '-';

    /* Span ID */
    for (size_t i = 0; i < SPAN_ID_BYTES; ++i) {
        *p++ = hex_digits[(ctx->span_id[i] >> 4) & 0x0F];
        *p++ = hex_digits[ctx->span_id[i] & 0x0F];
    }
    *p++ = '-';

    /* Flags */
    *p++ = hex_digits[(ctx->flags >> 4) & 0x0F];
    *p++ = hex_digits[ctx->flags & 0x0F];
    *p = '\0';

    return true;
}
```
```cpp
#include <array>
#include <string_view>
#include <optional>
#include <expected>
#include <cstdint>
#include <chrono>
#include <random>
#include <format>
#include <iostream>
#include <span>

enum class TraceError {
    InvalidLength,
    InvalidDelimiter,
    InvalidVersion,
    InvalidHexCharacter,
    AllZerosNotAllowed
};

struct TraceContext {
    uint8_t version{0x00};
    std::array<uint8_t, 16> trace_id{};
    std::array<uint8_t, 8> span_id{};
    uint8_t flags{0x00};

    [[nodiscard]] bool is_sampled() const noexcept {
        return (flags & 0x01) != 0;
    }
};

class W3CPropagator {
    static constexpr std::string_view HEX_DIGITS = "0123456789abcdef";

    static constexpr int8_t parse_nibble(char c) noexcept {
        if (c >= '0' && c <= '9') return static_cast<int8_t>(c - '0');
        if (c >= 'a' && c <= 'f') return static_cast<int8_t>(c - 'a' + 10);
        if (c >= 'A' && c <= 'F') return static_cast<int8_t>(c - 'A' + 10);
        return -1;
    }

    template <size_t N>
    static bool decode_hex_span(std::string_view sv, std::array<uint8_t, N>& out) noexcept {
        uint8_t non_zero_acc = 0;
        for (size_t i = 0; i < N; ++i) {
            int8_t hi = parse_nibble(sv[i * 2]);
            int8_t lo = parse_nibble(sv[i * 2 + 1]);
            if (hi < 0 || lo < 0) return false;
            out[i] = static_cast<uint8_t>((hi << 4) | lo);
            non_zero_acc |= out[i];
        }
        return non_zero_acc != 0; /* Перевірка на заборонений zero-only ID */
    }

public:
    static std::expected<TraceContext, TraceError> extract(std::string_view header) noexcept {
        if (header.size() < 55) {
            return std::unexpected(TraceError::InvalidLength);
        }

        if (header[2] != '-' || header[35] != '-' || header[52] != '-') {
            return std::unexpected(TraceError::InvalidDelimiter);
        }

        int8_t v_hi = parse_nibble(header[0]);
        int8_t v_lo = parse_nibble(header[1]);
        if (v_hi < 0 || v_lo < 0) return std::unexpected(TraceError::InvalidHexCharacter);
        
        uint8_t ver = static_cast<uint8_t>((v_hi << 4) | v_lo);
        if (ver == 0xFF) return std::unexpected(TraceError::InvalidVersion);
        if (ver == 0x00 && header.size() != 55) return std::unexpected(TraceError::InvalidLength);

        TraceContext ctx;
        ctx.version = ver;

        if (!decode_hex_span(header.substr(3, 32), ctx.trace_id)) {
            return std::unexpected(TraceError::AllZerosNotAllowed);
        }

        if (!decode_hex_span(header.substr(36, 16), ctx.span_id)) {
            return std::unexpected(TraceError::AllZerosNotAllowed);
        }

        int8_t f_hi = parse_nibble(header[53]);
        int8_t f_lo = parse_nibble(header[54]);
        if (f_hi < 0 || f_lo < 0) return std::unexpected(TraceError::InvalidHexCharacter);
        ctx.flags = static_cast<uint8_t>((f_hi << 4) | f_lo);

        return ctx;
    }

    static void inject(const TraceContext& ctx, std::span<char, 55> out_buffer) noexcept {
        auto* p = out_buffer.data();
        *p++ = HEX_DIGITS[(ctx.version >> 4) & 0x0F];
        *p++ = HEX_DIGITS[ctx.version & 0x0F];
        *p++ = '-';

        for (uint8_t b : ctx.trace_id) {
            *p++ = HEX_DIGITS[(b >> 4) & 0x0F];
            *p++ = HEX_DIGITS[b & 0x0F];
        }
        *p++ = '-';

        for (uint8_t b : ctx.span_id) {
            *p++ = HEX_DIGITS[(b >> 4) & 0x0F];
            *p++ = HEX_DIGITS[b & 0x0F];
        }
        *p++ = '-';

        *p++ = HEX_DIGITS[(ctx.flags >> 4) & 0x0F];
        *p++ = HEX_DIGITS[ctx.flags & 0x0F];
    }
};

/* RAII-обгортка для відстеження тривалості спана */
class ScopedSpan {
    std::string_view operation_name_;
    TraceContext context_;
    std::chrono::steady_clock::time_point start_time_;

public:
    ScopedSpan(std::string_view name, TraceContext parent_ctx)
        : operation_name_(name), context_(parent_ctx), start_time_(std::chrono::steady_clock::now()) {
        /* Генерація нового SpanID для поточної операції */
        static thread_local std::mt19937_64 rng{std::random_device{}()};
        uint64_t new_id = rng();
        for (size_t i = 0; i < 8; ++i) {
            context_.span_id[i] = static_cast<uint8_t>(new_id >> (i * 8));
        }
    }

    ~ScopedSpan() {
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
            std::chrono::steady_clock::now() - start_time_
        ).count();
        std::cout << std::format("[SPAN END] op='{}' duration={}us sampled={}\n",
                                 operation_name_, duration, context_.is_sampled());
    }

    [[nodiscard]] const TraceContext& context() const noexcept { return context_; }
};
```
```go
package tracing

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"errors"
	"fmt"
	"net/http"
	"strings"
)

type contextKey struct{}

var traceContextKey = contextKey{}

type TraceContext struct {
	Version [1]byte
	TraceID [16]byte
	SpanID  [8]byte
	Flags   byte
}

func (tc TraceContext) IsSampled() bool {
	return (tc.Flags & 0x01) != 0
}

func ExtractTraceparent(header string) (TraceContext, error) {
	if len(header) < 55 {
		return TraceContext{}, errors.New("traceparent header too short")
	}
	parts := strings.Split(header, "-")
	if len(parts) < 4 || len(parts[0]) != 2 || len(parts[1]) != 32 || len(parts[2]) != 16 || len(parts[3]) != 2 {
		return TraceContext{}, errors.New("malformed traceparent format")
	}

	var ctx TraceContext
	if _, err := hex.Decode(ctx.Version[:], []byte(parts[0])); err != nil || ctx.Version[0] == 0xFF {
		return TraceContext{}, errors.New("invalid version")
	}
	if ctx.Version[0] == 0x00 && len(header) != 55 {
		return TraceContext{}, errors.New("invalid length for version 00")
	}

	if _, err := hex.Decode(ctx.TraceID[:], []byte(parts[1])); err != nil || ctx.TraceID == [16]byte{} {
		return TraceContext{}, errors.New("invalid trace ID")
	}
	if _, err := hex.Decode(ctx.SpanID[:], []byte(parts[2])); err != nil || ctx.SpanID == [8]byte{} {
		return TraceContext{}, errors.New("invalid span ID")
	}

	var flags [1]byte
	if _, err := hex.Decode(flags[:], []byte(parts[3])); err != nil {
		return TraceContext{}, errors.New("invalid flags")
	}
	ctx.Flags = flags[0]

	return ctx, nil
}

func (tc TraceContext) String() string {
	return fmt.Sprintf("%02x-%032x-%016x-%02x", tc.Version[0], tc.TraceID, tc.SpanID, tc.Flags)
}

func GenerateSpanID() [8]byte {
	var id [8]byte
	rand.Read(id[:])
	return id
}

// HTTP Middleware для автоматичного поширення контексту
func TracingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		incomingHeader := r.Header.Get("traceparent")
		traceCtx, err := ExtractTraceparent(incomingHeader)
		if err != nil {
			// Якщо заголовок відсутній або пошкоджений, генеруємо новий кореневий трейс
			traceCtx = TraceContext{Version: [1]byte{0x00}, Flags: 0x01}
			rand.Read(traceCtx.TraceID[:])
		}

		// Створюємо дочірній спан для поточної операції
		traceCtx.SpanID = GenerateSpanID()
		ctx := context.WithValue(r.Context(), traceContextKey, traceCtx)

		w.Header().Set("traceparent", traceCtx.String())
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
```
```ts
import { AsyncLocalStorage } from 'node:async_hooks';
import * as crypto from 'node:crypto';

export interface TraceContext {
  version: string;
  traceId: string;
  spanId: string;
  flags: string;
}

export const traceStorage = new AsyncLocalStorage<TraceContext>();

export function extractTraceparent(header: string | null): TraceContext | null {
  if (!header || header.length < 55) return null;
  const parts = header.split('-');
  if (parts.length < 4) return null;

  const [version, traceId, spanId, flags] = parts;
  if (version === 'ff' || (version === '00' && header.length !== 55)) return null;
  if (!/^[0-9a-fA-F]{32}$/.test(traceId) || /^0{32}$/.test(traceId)) return null;
  if (!/^[0-9a-fA-F]{16}$/.test(spanId) || /^0{16}$/.test(spanId)) return null;
  if (!/^[0-9a-fA-F]{2}$/.test(flags)) return null;

  return {
    version,
    traceId: traceId.toLowerCase(),
    spanId: spanId.toLowerCase(),
    flags: flags.toLowerCase()
  };
}

export function formatTraceparent(ctx: TraceContext): string {
  return `${ctx.version}-${ctx.traceId}-${ctx.spanId}-${ctx.flags}`;
}

export function generateSpanId(): string {
  return crypto.randomBytes(8).toString('hex');
}

export function generateTraceId(): string {
  return crypto.randomBytes(16).toString('hex');
}

// Обгортка для вихідних HTTP-запитів із впровадженням контексту
export async function tracedFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const currentCtx = traceStorage.getStore();
  const headers = new Headers(options.headers);

  if (currentCtx) {
    const childSpanId = generateSpanId();
    const childContext: TraceContext = { ...currentCtx, spanId: childSpanId };
    headers.set('traceparent', formatTraceparent(childContext));
  }

  return fetch(url, { ...options, headers });
}
```
:::

## Внутрішньопроцесне поширення контексту: механіка та пастки

Вилучення заголовка з HTTP-пакета — це лише перший крок. Головна інженерна складність полягає в тому, як зберегти та зробити доступним вилучений `TraceContext` для всіх подальших функцій у глибині стека викликів без явної передачі об'єкта контексту в кожен метод системи (англ. *parameter drilling*).

### 1. Локальна пам'ять потоку (Thread-Local Storage)
У традиційних синхронних багатопотокових серверах (наприклад, Java Servlet containers, C++ thread pools) кожен клієнтський запит обслуговується виділеним потоком операційної системи. Для прив'язки контексту використовується механізм Thread-Local Storage (TLS):
* У C/C++: ключове слово `thread_local` або виклики POSIX `pthread_setspecific()`;
* У Java: `ThreadLocal<TraceContext>`;
* У .NET: `AsyncLocal<T>` або `ThreadStatic`.

Коли потік починає обробку запиту, він записує вказівник на поточний `TraceContext` у свою локальну пам'ять. Будь-який внутрішній компонент (наприклад, клієнт бази даних або логер) звертається до статичного методу `Tracer::current_context()`, який зчитує змінні потоку з нульовими накладними витратами на блокування м'ютексів.

**Пастка пулів потоків:** якщо потік після завершення запиту повертається в пул (англ. *thread pool*) і не очищує свою локальну пам'ять (`thread_local`), наступний абсолютно сторонній запит, призначений цьому ж потоку, успадкує застарілий `TraceID`. Це призводить до катастрофічного спотворення телеметрії, коли операції різних клієнтів зливаються в один фальшивий гігантський трейс. Тому будь-яка інструментація на базі TLS зобов'язана мати блок гарантованого очищення (`finally` або RAII-деструктор).

### 2. Асинхронні рантайми та втрата контексту
У подієво-орієнтованих асинхронних рантаймах (Node.js event loop, Go goroutines, Rust `tokio`, Python `asyncio`) модель «один потік на запит» не працює: один потік ОС одночасно перемикається між тисячами асинхронних корутин.

* **Втрата контексту на `await`:** якщо зберегти контекст у статичній змінній потоку, то в момент, коли функція виконує неблокуючий виклик введення-виведення (наприклад, очікує відповіді від бази даних), потік перемикається на обробку іншого запиту і перезаписує змінну. Після відновлення виконання перша функція прочитає чужий контекст.
* **Рішення в Node.js:** використання `AsyncLocalStorage` із модуля `node:async_hooks`. Двигунець V8 автоматично прив'язує посилання на контекст до внутрішнього дерева асинхронних дескрипторів і відновлює його під час кожного спрацьовування колбеку чи продовження промісу.
* **Рішення в Go:** вбудована бібліотека Go не підтримує неявного контексту потоку (goroutine local storage свідомо заборонено авторами мови). Єдиний ідіоматичний шлях — явна передача першим параметром функції `ctx context.Context`.

## Робота з додатковими заголовками: tracestate та baggage

Крім базового `traceparent`, стандарт W3C визначає два взаємодоповнюючі механізми передачі розподілених метаданих:

### 1. Заголовок tracestate
Заголовок `tracestate` призначений для пропуску специфічної для окремих систем телеметрії інформації (наприклад, внутрішніх ідентифікаторів маршрутизації вендора `rojo=1,congo=2`) через гетерогенні мережі.

Правила обробки `tracestate`:
* **Формат:** список пар `vendor_key=opaque_value`, розділених комами (згідно з RFC 7230).
* **Кількісні ліміти:** не більше ніж 32 пари ключ-значення, а сумарна довжина рядка не повинна перевищувати 512 символів.
* **Порядок мутації:** якщо система (наприклад, проксі Envoy або моніторинг Datadog) оновлює власне значення в `tracestate`, оновлена пара `key=value` **зобов'язана бути переміщена на першу позицію списку** (лівий край рядка).
* **Незмінність чужих ключів:** будь-які незнайомі ключі інших вендорів повинні зберігатися без змін та транслюватися наступним вузлам. Якщо ліміт у 32 елементи перевищено під час додавання нового ключа, видаляється найправіший (найстаріший) елемент списку.

### 2. Заголовок baggage
На відміну від спан-атрибутів, які існують виключно в межах одного локального спана, **Baggage** — це розподілений контекст бізнес-рівня, який автоматично копіюється у всі наступні дочірні спани та передається за мережевими викликами.

Типові сценарії використання Baggage:
* Передача ідентифікатора клієнтського облікового запису (`tenant_id=enterprise_42`) для динамічного білінгу та маршрутизації на виділені сервери баз даних;
* Передача прапорця синтетичного трафіку (`synthetic_test=true`), щоб фонові аналітичні сервіси відфільтровували роботів навантажувального тестування;
* Передача версії клієнтського додатка (`client_version=ios_17.4`) для аналізу збоїв конкретного мобільного релізу.

**Специфікація кодування Baggage:**
Пари ключ-значення записуються у форматі `key1=value1,key2=value2;property1=val`. Значення ключів та властивостей підлягають обов'язковому URL-кодуванню (Percent-encoding), якщо вони містять пробіли, коми, крапки з комою або символи за межами діапазону US-ASCII. Загальний розмір заголовка Baggage рекомендується обмежувати 8192 байтами, щоб запобігти помилкам веб-серверів `431 Request Header Fields Too Large`.

**Безпека та санітизація на зовнішньому периметрі:** Оскільки заголовок `baggage` може бути надісланий зловмисником із публічного Інтернету, зовнішній API Gateway зобов'язаний очищати (англ. *sanitize*) або повністю скидати вхідний заголовок `baggage` від неавторизованих клієнтів. Якщо цього не зробити, сторонній користувач може примусово підставити параметр на зразок `tenant_id=admin` чи `routing_tier=vip`, скомпрометувавши внутрішню логіку маршрутизації та безпеки бекенд-сервісів.

## Генерація ідентифікаторів: ентропія та пастка fork()

Коректність відновлення дерева трейсу цілком залежить від унікальності 128-бітних Trace ID та 64-бітних Span ID. Колізія двох ідентифікаторів призводить до катастрофічного злиття двох незалежних запитів в один пошкоджений граф.

### Криптографічні генератори проти швидких PRNG
* **Системні виклики `getrandom(2)` / `/dev/urandom`:** забезпечують криптографічну стійкість та гарантують відсутність колізій, але системний виклик перемикає контекст ядра ОС (близько 100–150 нс). На частоті 200 000 спанів на секунду це створює помітний оверхед.
* **Потоко-локальні PRNG (Xoshiro256++ / Mersenne Twister):** виконуються за 2–4 нс у просторі користувача. Проте вимагають правильної ініціалізації унікальним зерном (seed) для кожного потоку.

### Пастка fork() у багатовузлових серверах
У середовищах із моделлю префоркінгу процесів (наприклад, Python Gunicorn, Ruby Unicorn, Node.js Cluster, PHP-FPM, C/C++ prefork daemons) головний процес ініціалізує генератор псевдовипадкових чисел (PRNG), після чого викликає системний виклик `fork()`.

Якщо після виклику `fork()` дочірні процеси не перевизначають стан генератора випадкових чисел, **усі дочірні воркери отримують ідентичний внутрішній стан PRNG**. У результаті різні процеси на різних ядрах процесора починають генерувати абсолютно однакові послідовності `TraceID` та `SpanID`. Щоб уникнути цього критичного збою, SDK трейсингу зобов'язаний реєструвати обробник `pthread_atfork()` у C/C++ або переініціалізувати зерно генератора випадкових чисел відразу після форку у дочірньому процесі (замішуючи поточний PID та таймстемп наносекундної точності).

## Передача крізь не-HTTP транспорти

Розподілені транзакції рідко обмежуються протоколом HTTP. Сучасні системи активно використовують двійкові RPC-протоколи та брокери повідомлень:

### 1. gRPC та Protocol Buffers
У gRPC метадані передаються як HTTP/2 фрейми заголовків (`HEADERS frame`). Окрім стандартного текстового заголовка `traceparent`, gRPC підтримує компактний двійковий формат `grpc-trace-bin`. Двійковий формат кодує ті самі 16 байтів Trace ID, 8 байтів Span ID та прапорці у вигляді компактного 29-байтного бінарного буфера, зменшуючи накладні витрати на передачу ASCII-символів у внутрішньокластерному трафіку.

### 2. Черги повідомлень (Kafka, RabbitMQ, SQS)
Під час публікації повідомлення в брокер (наприклад, подію `OrderPlaced` у топік Kafka) Producer сервісу зобов'язаний зберегти поточний `TraceContext` у масиві заголовків повідомлення (Kafka Record Headers):

```
Record Header:
  Key:   "traceparent"
  Value: "00-4bf92f3577b34da6a3ce929d0e0e4736-a8b2c1d0e9f80712-01"
```

Коли фоновий Consumer зчитує повідомлення через хвилину або годину, він вилучає заголовок і створює дочірній спан обробки. Завдяки цьому інженер бачить на графіку, скільки часу повідомлення очікувало в черзі між моментом публікації та початком виконання воркером.

## Асинхронний збір: безблокувальні черги (Disruptor)

Якщо кожен створений спан синхронно серіалізувати та надсилати по мережі у фоновий колектор, продуктивність сервісу впаде в рази. Справжній високопродуктивний рушій трейсингу використовує двохетапну модель:

1. **Гарячий шлях (Worker Thread):** у момент завершення операції створюється компактна структура спана (фіксовані 64 байти) і записується в закільцьований буфер у пам'яті (Ring Buffer) через атомарні операції без блокування м'ютексів (Lock-Free MPSC Queue).
2. **Фоновий експортер (Background Batcher):** окремий фоновий потік періодично (наприклад, кожні 500 мілісекунд або при накопиченні 512 спанів) забирає пачку записів, серіалізує їх у формат OTLP Protobuf і надсилає через одне стійке gRPC-з'єднання.

Якщо закільцьований буфер переповнюється під час пікового сплеску навантаження, рушій зобов'язаний скидати нові спани (Drop on overflow), збільшуючи лічильник внутрішньої метрики `telemetry.spans.dropped`, але в жодному разі не блокувати бізнес-потоки обробки клієнтських запитів.

## Безінвазивна інструментація через eBPF

Найновішим напрямком розвитку інструментації розподіленого трейсингу є використання розширених фільтрів пакетів ядра Linux (eBPF). Замість модифікації прикладного коду або підключення бібліотек SDK, інженер завантажує eBPF-програми безпосередньо в ядро ОС.

Механіка роботи eBPF-трейсингу:
* **Точки перехоплення uretprobes:** eBPF перехоплює виклики бібліотек SSL/TLS (наприклад, `libssl.so` або `BoringSSL`) у момент розшифрування вхідного HTTP-трафіку і зчитує заголовок `traceparent` до того, як байти потраплять у простір користувача.
* **Трасування сокетів (sockops / tc):** програми ядра аналізують дескриптори сокетів і пов'язують вхідні мережеві пакети з ідентифікаторами процесів (PID) та потоків (TID), автоматично реконструюючи граф взаємодії сервісів навіть для закритих сторонніх бінарних файлів або застарілих легасі-систем на C/Fortran.

## Компенсація розходження системних годинників (Clock Skew)

У розподілених системах кожен сервер має власний апаратний генератор тактових імпульсів. Навіть за використання протоколу синхронізації часу NTP (Network Time Protocol) між серверами неминуче виникає розходження годинників (англ. *clock skew*) величиною від 1 до 50 мілісекунд.

Це створює оптичні аномалії при побудові графіка трейсу:
* **Ефект випередження батька:** дочірній спан на сервері Б за часовою міткою починається раніше, ніж батьківський спан на сервері А надіслав мережевий виклик.
* **Від'ємна тривалість мережі:** час завершення виклику на клієнті менший за час старту обробки на сервері.

### Алгоритм коригування дерева за Dapper:
Сервери бекенду аналізу та візуалізації (Jaeger/Tempo) застосовують коригування часових шкал за принципом включення (Envelope Bounding):
1. Якщо `child.start_time < parent.start_time`, час старту дочірнього спана примусово зсувається вперед до `parent.start_time + network_latency_estimate`.
2. Якщо `child.end_time > parent.end_time` для синхронного блокуючого виклику, тривалість дочірнього спана стискається або зсувається так, щоб гарантовано вкладатися між точками відправки запиту та отримання відповіді батьківським вузлом.

## Аналіз продуктивності та оптимізація гарячого шляху

У реальних проксі-серверах (наприклад, Envoy або Nginx), що обслуговують понад 100 000 запитів на секунду на ядро, наївний парсинг рядків через регулярні вирази або `sscanf()` створює неприпустиме навантаження на процесор.

Розглянемо оптимізації, використані у наведених C/C++ реалізаціях:

### 1. Табличний парсинг шістнадцяткових чисел (Lookup Table)
Замість умовних розгалужень (`if (c >= '0' && c <= '9') ... else if ...`), таблиця `hex_table[256]` використовує прямий доступ за індексом символу в пам'яті L1-кешу процесора. Це усуває невдалі передбачення переходів (англ. *branch mispredictions*) під час обробки кожного символу.

### 2. Побітова перевірка на нульові ідентифікатори
Перевірка 16 байтів Trace ID на повну рівність нулю наївним циклом `for` із внутрішнім розгалуженням `if (arr[i] != 0)` створює до 16 перевірок. Використання кумулятивного побітового «АБО»:

:::tabs
```c
uint8_t acc = 0;
for (size_t i = 0; i < 16; ++i) {
    acc |= trace_id[i];
}
if (acc == 0) return false;
```
```cpp
const bool is_all_zeros = std::ranges::all_of(trace_id, [](uint8_t b) noexcept {
    return b == 0;
});
if (is_all_zeros) return false;
```
:::

дозволяє компілятору згорнути цикл у векторні SIMD-інструкції (наприклад, `_mm_testz_si128` в архітектурі x86-64 або `VORR` у ARM NEON), перевіряючи весь 128-бітний масив за одну асемблерну інструкцію без жодного умовного переходу.

### 3. Відсутність динамічних алокацій (Zero-Heap Allocation)
Структура `TraceContext` займає рівно 28 байтів у пам'яті та передається по стеку або у регістрах CPU. Жоден етап валідації чи форматування не викликає `malloc()` або `new`, усуваючи фрагментацію купи та накладні витрати на збирач сміття (Garbage Collector).

### 4. Запобігання хибному розділенню кеш-ліній (False Sharing)
Коли сотні робочих потоків одночасно створюють спани, розміщення структур у суміжних ділянках пам'яті може призвести до того, що різні ядра процесора конкуруватимуть за одну 64-байтну лінію кешу L1/L2. Застосування вирівнювання `alignas(64)` для потоко-локальних структур унеможливлює Cache Line Bouncing та забезпечує лінійне масштабування за кількістю процесорних ядер.

Порівняльна таблиця продуктивності різних підходів до вилучення контексту на процесорі Intel Xeon x86-64:

| Метод парсингу | Наносекунди на операцію (ns/op) | Споживання пам'яті (Heap B/op) | Пропускна здатність на ядро (ops/sec) |
|---|---|---|---|
| Регулярні вирази (RegEx) | 480.0 ns | 128 B | ~ 2.08 млн |
| `sscanf()` зі стандартної C-бібліотеки | 185.0 ns | 0 B | ~ 5.40 млн |
| Ручний посимвольний парсинг із розгалуженнями | 42.0 ns | 0 B | ~ 23.8 млн |
| Табличний LUT + SIMD валідація (наш код) | 6.8 ns | 0 B | ~ 147.0 млн |

Завдяки оптимізації парсингу до 6.8 наносекунд на операцію, накладні витрати на обробку розподіленого контексту стають абсолютно непомітними навіть на мережевих інтерфейсах 100 Gbps.
