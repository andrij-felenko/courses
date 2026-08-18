# ⚙️ Прокидання контексту телеметрії та кореляція в бекенді Digital Homes

Ця практична вставка демонструє повну виробничу реалізацію наскрізного прокидання W3C `traceparent` контексту, автоматичного збагачення JSON-логів та зв'язування гістограм метрик Prometheus із трейсами OpenTelemetry у високонавантажених мікросервісах Digital Homes.

---

## 1. Архітектурна задача прокидання контексту

Для забезпечення цілісної кореляції (від лат. *correlatio* — співвідношення) між трьома стовпами спостережуваності будь-який мікросервіс бекенду зобов'язаний послідовно виконувати три етапи обробки телеметричного контексту:

1. **Витягання (Extraction)**: Отримати вхідний заголовок W3C `traceparent` із мережевого HTTP-запиту або з масиву бінарних gRPC-метаданих. Якщо заголовок відсутній (наприклад, для первинного запиту від мобільного застосунку на зовнішній Edge Proxy) або пошкоджений — сервіс зобов'язаний згенерувати новий унікальний 128-бітний `TraceID`.
2. **Локальна асинхронна пропагація (Propagation)**: Зафіксувати отриманий `trace_id` та згенерований `span_id` поточного сервісу у спеціальній структурі пам'яті, прив'язаній до поточного потоку або асинхронного циклу обробки (Event Loop). Це дозволяє всім внутрішнім логерам, бібліотекам баз даних та клієнтам зовнішніх сервісів витягати `trace_id` інпліцитно, без незграбного прокидання аргументів крізь усю доменну логіку.
3. **Ін'єкція (Injection)**: Під час формування вихідного мережевого виклику (HTTP/gRPC) або запиту до реляційної бази даних PostgreSQL сервіс генерує новий заголовок `traceparent` із новим `span_id`, але з **збереженим `trace_id`**. Одночасно логер форматує структурований JSON-рядок із полями `trace_id` та `span_id`, а гістограма Prometheus реєструє `Exemplar`.

---

## 2. Реалізація кореляційного модуля для мікросервісів

Нижче наведено повноцінні виробничі реалізації кореляційного middleware для C++, TypeScript та Go.

:::tabs
```cpp
// C++20 / OpenTelemetry C++ SDK / Prometheus-cpp
#include <iostream>
#include <string>
#include <memory>
#include <thread>
#include <optional>
#include <random>
#include <sstream>
#include <iomanip>
#include <chrono>

// Структура W3C Trace Context
struct TraceContext {
    std::string trace_id;
    std::string span_id;
    bool sampled{true};

    static std::string generate_hex(size_t bytes) {
        thread_local std::mt19937 generator{std::random_device{}()};
        std::uniform_int_distribution<uint32_t> dist(0, 255);
        std::stringstream ss;
        for (size_t i = 0; i < bytes; ++i) {
            ss << std::hex << std::setw(2) << std::setfill('0') << dist(generator);
        }
        return ss.str();
    }

    static TraceContext parse_or_create(const std::string& traceparent_header) {
        // Формат W3C: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
        if (traceparent_header.size() >= 55 && traceparent_header.substr(0, 2) == "00") {
            TraceContext ctx;
            ctx.trace_id = traceparent_header.substr(3, 32);
            ctx.span_id = traceparent_header.substr(36, 16);
            ctx.sampled = (traceparent_header.substr(53, 2) == "01");
            return ctx;
        }
        // Генерація нового TraceID, якщо заголовок відсутній або пошкоджений
        return TraceContext{generate_hex(16), generate_hex(8), true};
    }

    std::string to_traceparent() const {
        return "00-" + trace_id + "-" + span_id + "-" + (sampled ? "01" : "00");
    }
};

// Thread-local зберігання контексту для поточного потоку обробки
thread_local std::optional<TraceContext> g_current_trace_context;

// RAII обгортка для безпечного керування часом життя контексту в потоці
class TraceScope {
public:
    explicit TraceScope(TraceContext ctx) : prev_ctx_(g_current_trace_context) {
        g_current_trace_context = std::move(ctx);
    }
    ~TraceScope() {
        g_current_trace_context = prev_ctx_;
    }
    TraceScope(const TraceScope&) = delete;
    TraceScope& operator=(const TraceScope&) = delete;

private:
    std::optional<TraceContext> prev_ctx_;
};

// Структурований JSON-логер із автоматичним прокиданням TraceID
class CorrelatedLogger {
public:
    static void log_info(const std::string& service, const std::string& msg) {
        emit_log("INFO", service, msg);
    }
    static void log_error(const std::string& service, const std::string& msg, const std::string& err_detail) {
        emit_log("ERROR", service, msg, err_detail);
    }

private:
    static void emit_log(const std::string& level, const std::string& service, 
                         const std::string& msg, const std::string& err = "") {
        auto now = std::chrono::system_clock::now().time_since_epoch();
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now).count();

        std::string tid = g_current_trace_context ? g_current_trace_context->trace_id : "none";
        std::string sid = g_current_trace_context ? g_current_trace_context->span_id : "none";

        std::cout << "{"
                  << "\"timestamp_ms\":" << ms << ","
                  << "\"level\":\"" << level << "\","
                  << "\"service\":\"" << service << "\","
                  << "\"trace_id\":\"" << tid << "\","
                  << "\"span_id\":\"" << sid << "\","
                  << "\"message\":\"" << msg << "\"";
        if (!err.empty()) {
            std::cout << ",\"error\":\"" << err << "\"";
        }
        std::cout << "}\n";
    }
};

// Приклад сервісу обробки телеметрії
class DeviceTelemetryService {
public:
    void handle_request(const std::string& raw_traceparent) {
        TraceContext ctx = TraceContext::parse_or_create(raw_traceparent);
        TraceScope scope(ctx); // Записує контекст у thread_local

        CorrelatedLogger::log_info("device-telemetry-svc", "Прийнято запит телеметрії давача");

        // Симуляція виклику бази даних із розширеним спаном
        execute_db_query();
    }

private:
    void execute_db_query() {
        // У реальному коді тут створюється Child Span і передається Exemplar у Prometheus
        CorrelatedLogger::log_info("device-telemetry-svc", "Виконання SQL запиту до PostgreSQL");
    }
};
```
```ts
// TypeScript / Node.js / Express / Pino / AsyncLocalStorage
import express, { Request, Response, NextFunction } from 'express';
import { AsyncLocalStorage } from 'async_hooks';
import pino from 'pino';
import { randomBytes } from 'crypto';

interface TraceStore {
  traceId: string;
  spanId: string;
  sampled: boolean;
}

const traceStorage = new AsyncLocalStorage<TraceStore>();

// Парсинг або генерація W3C traceparent
function getOrGenerateTraceContext(req: Request): TraceStore {
  const header = req.headers['traceparent'] as string;
  if (header && header.startsWith('00-')) {
    const parts = header.split('-');
    if (parts.length >= 4) {
      return {
        traceId: parts[1],
        spanId: parts[2],
        sampled: parts[3] === '01'
      };
    }
  }
  return {
    traceId: randomBytes(16).toString('hex'),
    spanId: randomBytes(8).toString('hex'),
    sampled: true
  };
}

// Pino логер, що динамічно витягує trace_id з AsyncLocalStorage
const logger = pino({
  mixin() {
    const store = traceStorage.getStore();
    return {
      trace_id: store?.traceId ?? 'none',
      span_id: store?.spanId ?? 'none'
    };
  },
  base: { service: 'device-telemetry-service' }
});

const app = express();

// Middleware прокидання контексту
app.use((req: Request, res: Response, next: NextFunction) => {
  const context = getOrGenerateTraceContext(req);

  // Прокидаємо traceparent у вихідні заголовки відповіді
  res.setHeader('traceparent', `00-${context.traceId}-${context.spanId}-${context.sampled ? '01' : '00'}`);

  // Запускаємо ланцюг обробників всередині AsyncLocalStorage
  traceStorage.run(context, () => {
    logger.info({ path: req.path }, 'HTTP запит прийнято в обробку');
    next();
  });
});

app.get('/api/v2/telemetry/history', async (req: Request, res: Response) => {
  try {
    logger.info('Виконання запиту агрегації телеметрії');
    // Симуляція запиту до БД
    res.json({ status: 'ok', data: [] });
  } catch (err: any) {
    logger.error({ err }, 'Помилка виконання запиту агрегації');
    res.status(500).json({ code: 'internal_error' });
  }
});
```
```go
// Go 1.22 / OpenTelemetry Go SDK / net/http
package main

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"
)

type traceKey struct{}

type TraceContext struct {
	TraceID string
	SpanID  string
	Sampled bool
}

func generateHex(bytes int) string {
	b := make([]byte, bytes)
	rand.Read(b)
	return hex.EncodeToString(b)
}

func ExtractTraceContext(r *http.Request) TraceContext {
	header := r.Header.Get("traceparent")
	if strings.HasPrefix(header, "00-") {
		parts := strings.Split(header, "-")
		if len(parts) >= 4 {
			return TraceContext{
				TraceID: parts[1],
				SpanID:  parts[2],
				Sampled: parts[3] == "01",
			}
		}
	}
	return TraceContext{
		TraceID: generateHex(16),
		SpanID:  generateHex(8),
		Sampled: true,
	}
}

func TelemetryMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		tc := ExtractTraceContext(r)
		ctx := context.WithValue(r.Context(), traceKey{}, tc)

		w.Header().Set("traceparent", fmt.Sprintf("00-%s-%s-01", tc.TraceID, tc.SpanID))

		LogJSON(ctx, "INFO", "device-telemetry-svc", "Запит прийнято в HTTP middleware")
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

func LogJSON(ctx context.Context, level, service, msg string) {
	tc, _ := ctx.Value(traceKey{}).(TraceContext)
	logData := map[string]interface{}{
		"timestamp": time.Now().UTC().Format(time.RFC3339Nano),
		"level":     level,
		"service":   service,
		"trace_id":  tc.TraceID,
		"span_id":   tc.SpanID,
		"message":   msg,
	}
	bytes, _ := json.Marshal(logData)
	fmt.Println(string(bytes))
}
```
:::

---

## 3. Детальний розбір механізмів за мовами програмування

### 3.1. C++20: Безпечне керування пам'яттю через RAII та Thread-Local Storage

У високонавантажених C++ сервісах обробки телеметрії (наприклад, крайових контролерах або драйверах IoT-протоколів) виділення пам'яті під контекст на кожному запиті мусить бути максимальним швидким та позбавленим системних блокувань м'ютексів (lock-free).

1. **Ізоляція потоків через `thread_local`**: Змінна `g_current_trace_context` декларується із класифікатором `thread_local std::optional<TraceContext>`. Кожен потік із пулу обробників отримує власну виділену комірку пам'яті. Це гарантує абсолютну відсутність конфліктів у пам'яті при паралельній обробці тисяч запитів.
2. **Генерація випадкових Hex-рядків без контеншну**: Метод `TraceContext::generate_hex` використовує виклик `std::mt19937` з потоковою локалізацією `thread_local std::mt19937 generator{std::random_device{}()}`. Ініціалізація висхідного зерна робиться один раз при старті потоку, після чого генерування 16 випадкових байтів виконується за лічені наносекунди без звернення до ядерного системного виклику.
3. **RAII-обгортка `TraceScope`**: Клас `TraceScope` реалізує ідіому RAII (Resource Acquisition Is Initialization). У конструкторі він зберігає попередній контекст у приватне поле `prev_ctx_` і встановлює новий. При виході з зони видимості (блоку `try/catch` або функції) деструктор `~TraceScope` автоматично відновлює попередній стан. Це унеможливлює отруєння контексту потоку (thread pool poisoning), коли наступний запит у тому ж потоці міг би успадкувати застарілий `trace_id`.

---

### 3.2. TypeScript / Node.js: Асинхронна пропагація через `AsyncLocalStorage`

У середовищі Node.js однопотоковий цикл подій (Event Loop) почергово обробляє крок за кроком тисячі асинхронних операцій від різних користувачів. Звичайна глобальна змінна або властивість модуля призвела б до того, що `trace_id` останнього запиту негайно перезаписав би контекст усіх інших активних з'єднань.

1. **Механіка `AsyncLocalStorage`**: Клас `AsyncLocalStorage` з системного модуля Node.js `async_hooks` дозволяє прив'язувати довільний об'єкт даних до асинхронного ресурсу (Promise, I/O callback, `setTimeout`). Метод `traceStorage.run(context, callback)` створює новий ізольований контекст для всього деревоподібного графу асинхронних викликів, які народжуються всередині `callback`.
2. **Динамічна міксин-ін'єкція в Pino**: Конфігурація логера Pino містить параметр `mixin()`. Під час кожного виклику `logger.info()` або `logger.error()` Pino автоматично викликає цю функцію, яка витягає активні `trace_id` та `span_id` з `traceStorage.getStore()`. Завдяки цьому розробнику не потрібно передавати об'єкт логера або контексту через десятки функцій доменного шару.

---

### 3.3. Go 1.22: Незмінні дерева контекстів через `context.Context`

У мові Go контекст обробки запиту прокидається першим аргументом у кожну функцію (`ctx context.Context`).

1. **Запобігання колізіям ключів у контексті**: Для збереження значень у `context.Context` використовується приватний порожній тип структуры `type traceKey struct{}`. Оскільки тип приватний для даного пакета, жодна зовнішня бібліотека не може випадково перезаписати або зчитати `TraceContext` за тим самим ключем.
2. **Гарантія незмінності (Immutability)**: Виклик `context.WithValue(parentCtx, key, val)` повертає новий екземпляр контексту, який посилається на батьківський контекст як на незмінне дерево (immutable tree). Це гарантує повну відсутність гонок даних (data races) при запуску паралельних асинхронних горутин (`go func()`).

---

## 4. Виробничі пастки та крайові випадки

Під час впровадження кореляційного модуля у бекенд Digital Homes розробники стикаються з трьома критичними крайовими випадками:

### 4.1. Втрата контексту при передачі задачи у фоновий пучок потоків
Якщо C++ сервіс приймає HTTP-запит у потік-приймач (acceptor thread), а потім передає обробку в чергу фонового пучка потоків (Worker Thread Pool), звичайний `TraceScope` припиняє свою дію при виході з функції приймача. Якщо робітник пучка потоків не відтворить `TraceScope(ctx)` всередині виконання задачі, усі виклики до бази даних та логування у фоновому потоці будуть згенеровані з `trace_id = "none"`.

### 4.2. Втрата асинхронного зв'язку в Node.js через сторонні C-аддони
Деякі застарілі сторонні бібліотеки Node.js, написані на C++ (наприклад, неоптимізовані драйвери баз даних або бібліотеки шифрування), можуть виконувати обробку у власних потоках libuv без збереження асинхронних зв'язків `async_hooks`. У таких місцях функцію зворотного виклику необхідно явно повертати в контекст через `traceStorage.bind(callback)`.

### 4.3. Неприпустима мутація TraceID проміжними сервісами
Проміжний мікросервіс при виконанні вихідного виклику повинен генерувати новий унікальний `SpanID`, але **ніколи не змінювати отриманий `TraceID`**. Зміна `TraceID` у середині ланцюга мікросервісів розриває єдине розподілене дерево трасування на неузгоджені фрагменти, унеможливлюючи пошук причин збою за первинним ідентифікатором запиту.
