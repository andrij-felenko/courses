# ⚙️ Практична реалізація Dark Launching та Branch by Abstraction

Ця вставка містить інженерні шаблони коду та детальний розбір механізмів для двох фундаментальних паттернів безпечної міграції: **Traffic Shadow Router** (асинхронне дублювання та валідація трафіку на мережевому рівні) та **Branch by Abstraction** (внутрішнє перемикання реалізацій у коді за допомогою Feature Flags).

Перехід від теоретичних архітектурних схем до практичної реалізації вимагає розв'язання двох принципових задач: забезпечення абсолютної ізоляції побічних ефектів при дублюванні трафіку та мінімізації накладних витрат на перемикання реалізацій всередині високозавантаженого процесу.

## 1. Real-time Traffic Shadow Router & Diff Engine

Тіньовий маршрутизатор функціонує як зворотний проксі (Reverse Proxy) або middleware на API-шлюзі. Головне правило його роботи — гарантувати, що додаткове асинхронне навантаження та можливі збої в тіньовому сервісі ніколи не впливають на показники латентності й доступності продуктивного моноліту (Legacy).

Механізм роботи складається з чотирьох послідовних кроків:
1. **Буферизація вхідного тіла запиту:** Оскільки потік `r.Body` в HTTP-серверах є одноразовим для читання, шлюз зчитує вміст у буфер пам'яті `[]byte` та створює два незалежних потіки-клони.
2. **Синхронне виконання продуктивного запиту:** Передається в legacy-систему. Результат відповіді (заголовки, статус, тіло) миттєво відправляється назад клієнту.
3. **Асинхронний тіньовий запуск (Fire-and-Forget):** У фоновій горутині або потоці створюється новий контекст із таймаутом. До запиту додається ідентифікаційний заголовок `X-Dark-Launch-Shadow: true`.
4. **Валідація та розрахунок метрик (Diff Engine):** Порівнюються HTTP-коди відповідей, латентність обробки та JSON-структури. Для уникнення хибних спрацювань алгоритм порівняння свідомо видаляє часові мітки (`timestamp`), ідентифікатори екземплярів серверів (`server_id`) та nonce-токени.

Нижче наведено реалізацію проксі-маршрутизатора мовами Go та TypeScript:

:::tabs
```go
package shadow

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"log/slog"
	"net/http"
	"reflect"
	"time"
)

type DiffResult struct {
	Match        bool          `json:"match"`
	LatencyLegacy time.Duration `json:"latency_legacy_ms"`
	LatencyShadow time.Duration `json:"latency_shadow_ms"`
	MismatchPath string        `json:"mismatch_path,omitempty"`
}

type ShadowRouter struct {
	LegacyURL string
	ShadowURL string
	Client    *http.Client
	Logger    *slog.Logger
}

func NewShadowRouter(legacyURL, shadowURL string, logger *slog.Logger) *ShadowRouter {
	return &ShadowRouter{
		LegacyURL: legacyURL,
		ShadowURL: shadowURL,
		Client: &http.Client{
			Timeout: 2 * time.Second,
		},
		Logger: logger,
	}
}

func (sr *ShadowRouter) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	bodyBytes, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "bad request body", http.StatusBadRequest)
		return
	}
	r.Body = io.NopCloser(bytes.NewBuffer(bodyBytes))

	// 1. Синхронний виклик до Legacy
	startLegacy := time.Now()
	legacyReq, _ := http.NewRequestWithContext(r.Context(), r.Method, sr.LegacyURL+r.URL.Path, bytes.NewBuffer(bodyBytes))
	copyHeaders(r.Header, legacyReq.Header)

	legacyResp, err := sr.Client.Do(legacyReq)
	latencyLegacy := time.Since(startLegacy)

	if err != nil {
		http.Error(w, "legacy upstream failure", http.StatusBadGateway)
		return
	}
	defer legacyResp.Body.Close()

	legacyBody, _ := io.ReadAll(legacyResp.Body)

	// 2. Асинхронний тіньовий виклик (Dark Launch)
	go func(reqBody []byte, headers http.Header, path string) {
		ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
		defer cancel()

		shadowReq, _ := http.NewRequestWithContext(ctx, r.Method, sr.ShadowURL+path, bytes.NewBuffer(reqBody))
		copyHeaders(headers, shadowReq.Header)
		shadowReq.Header.Set("X-Dark-Launch-Shadow", "true")

		startShadow := time.Now()
		shadowResp, err := sr.Client.Do(shadowReq)
		latencyShadow := time.Since(startShadow)

		if err != nil {
			sr.Logger.Warn("shadow service unavailable", "error", err)
			return
		}
		defer shadowResp.Body.Close()

		shadowBody, _ := io.ReadAll(shadowResp.Body)

		// 3. Порівняння відповідей (Diff Engine)
		diff := comparePayloads(legacyBody, shadowBody, latencyLegacy, latencyShadow)
		if !diff.Match {
			sr.Logger.Error("shadow payload mismatch",
				"path", path,
				"mismatch", diff.MismatchPath,
				"latency_legacy_ms", diff.LatencyLegacy.Milliseconds(),
				"latency_shadow_ms", diff.LatencyShadow.Milliseconds(),
			)
		}
	}(bodyBytes, r.Header.Clone(), r.URL.Path)

	// 4. Повернення відповіді споживачеві від Legacy
	copyHeaders(legacyResp.Header, w.Header())
	w.WriteHeader(legacyResp.StatusCode)
	w.Write(legacyBody)
}

func comparePayloads(legacy, shadow []byte, tLeg, tShd time.Duration) DiffResult {
	var mapLegacy, mapShadow map[string]any
	if err := json.Unmarshal(legacy, &mapLegacy); err != nil {
		return DiffResult{Match: bytes.Equal(legacy, shadow), LatencyLegacy: tLeg, LatencyShadow: tShd}
	}
	if err := json.Unmarshal(shadow, &mapShadow); err != nil {
		return DiffResult{Match: false, LatencyLegacy: tLeg, LatencyShadow: tShd, MismatchPath: "shadow_json_parse_error"}
	}

	// Ігноруємо сольові/волатильні поля (наприклад, timestamp, request_id)
	delete(mapLegacy, "timestamp")
	delete(mapLegacy, "server_id")
	delete(mapShadow, "timestamp")
	delete(mapShadow, "server_id")

	match := reflect.DeepEqual(mapLegacy, mapShadow)
	path := ""
	if !match {
		path = "json_structure_or_values_differ"
	}
	return DiffResult{Match: match, LatencyLegacy: tLeg, LatencyShadow: tShd, MismatchPath: path}
}

func copyHeaders(src, dst http.Header) {
	for k, vv := range src {
		for _, v := range vv {
			dst.Add(k, v)
		}
	}
}
```
```ts
import http from 'http';
import fetch from 'node-fetch';

export class ShadowProxy {
  constructor(
    private legacyUrl: string,
    private shadowUrl: string
  ) {}

  public async handleRequest(req: http.IncomingMessage, res: http.ServerResponse): Promise<void> {
    const chunks: Buffer[] = [];
    for await (const chunk of req) {
      chunks.push(chunk);
    }
    const bodyBuffer = Buffer.concat(chunks);

    // 1. Синхронний виклик на Legacy
    const legacyStart = Date.now();
    const legacyResponse = await fetch(`${this.legacyUrl}${req.url}`, {
      method: req.method,
      headers: req.headers as Record<string, string>,
      body: req.method !== 'GET' ? bodyBuffer : undefined,
    });
    const legacyLatency = Date.now() - legacyStart;
    const legacyBody = await legacyResponse.buffer();

    // 2. Асинхронне тіньове дублювання (Fire-and-forget)
    setImmediate(async () => {
      try {
        const shadowStart = Date.now();
        const shadowResponse = await fetch(`${this.shadowUrl}${req.url}`, {
          method: req.method,
          headers: { ...req.headers, 'x-dark-launch-shadow': 'true' } as Record<string, string>,
          body: req.method !== 'GET' ? bodyBuffer : undefined,
        });
        const shadowLatency = Date.now() - shadowStart;
        const shadowBody = await shadowResponse.buffer();

        this.validateDiff(legacyBody, shadowBody, legacyLatency, shadowLatency, req.url || '');
      } catch (err) {
        console.warn('[ShadowProxy] Shadow call failed:', err);
      }
    });

    // 3. Повертаємо відповідь legacy-системи клієнту
    res.writeHead(legacyResponse.status, Object.fromEntries(legacyResponse.headers.entries()));
    res.end(legacyBody);
  }

  private validateDiff(legBody: Buffer, shdBody: Buffer, legLat: number, shdLat: number, url: string): void {
    try {
      const legJson = JSON.parse(legBody.toString('utf-8'));
      const shdJson = JSON.parse(shdBody.toString('utf-8'));
      delete legJson.timestamp;
      delete shdJson.timestamp;

      if (JSON.stringify(legJson) !== JSON.stringify(shdJson)) {
        console.error(`[ShadowDiffMismatch] URL: ${url} | Legacy: ${legLat}ms | Shadow: ${shdLat}ms`);
      }
    } catch {
      if (!legBody.equals(shdBody)) {
        console.error(`[ShadowRawMismatch] URL: ${url}`);
      }
    }
  }
}
```
:::

### Пояснення деталей реалізації Shadow Router та керування пам'яттю

1. **Копіювання заголовків та контексту:** Важливо копіювати всі вхідні заголовки HTTP (наприклад, `Authorization`, `User-Agent`, `Accept-Language`), щоб тіньовий запит виконувався в ідентичних контекстних умовах.
2. **Обробка таймаутів та воркер-пули:** Тіньовий запит завжди повинен мати суворий таймаут (у прикладі 2 секунди). У високозавантажених Go-системах виклики `go func(...)` для кожного запиту можуть створювати тиск на Garbage Collector. У продакшн-реалізаціях використовується обмежений воркер-пул (Worker Pool) та повторне використання буферів через `sync.Pool`.
3. **Обробка помилок JSON та логіка Diffing:** Якщо відповідь від одного із сервісів не є валідним JSON (наприклад, сервер повернув HTML 502 Bad Gateway), алгоритм переключається на сирове побайтове порівняння `bytes.Equal()`.

## 2. Branch by Abstraction: Внутрішній шов коду

Паттерн Branch by Abstraction вирішує задачу заміни монолітної підсистеми або драйвера без винесення коду в окремий мережевий сервіс. У цьому прикладі показано підсистему розрахунку вартості енергоспоживання платформи Digital Homes (DH).

Процес реалізації у коді включає створення чистого абстрактного інтерфейсу (Seam), реалізацію двох паралельних класів (Legacy та NextGen), та використання обгортки з атомарним прапорцем (`std::atomic<bool>` у C++ або `atomic.Bool` у Go). Це гарантує нульові блокування потоків (Lock-free thread safety) при високій частоті викликів.

Приклад ілюструє повний цикл C++ та Go реалізацій, із застосуванням ідіоматичних системних конструкцій: `std::expected` для безвиняткової обробки помилок, `std::string_view` для уникнення аллокацій у пам'яті, та RAII для управління ресурсами.

:::tabs
```cpp
#include <iostream>
#include <memory>
#include <string_view>
#include <atomic>
#include <expected>
#include <chrono>

struct TariffContext {
    uint64_t device_id;
    double kilowatt_hours;
    uint32_t zone_code;
};

struct CalculationResult {
    double total_cost;
    std::string_view tariff_name;
};

// 1. Abstraction Interface (Шов абстракції)
class ITariffCalculator {
public:
    virtual ~ITariffCalculator() = default;
    [[nodiscard]] virtual std::expected<CalculationResult, std::string> 
    calculate(const TariffContext& ctx) const noexcept = 0;
};

// 2. Legacy Implementation (Старий монолітний розрахунок)
class LegacyTariffCalculator final : public ITariffCalculator {
public:
    std::expected<CalculationResult, std::string> calculate(const TariffContext& ctx) const noexcept override {
        if (ctx.kilowatt_hours < 0) {
            return std::unexpected("Invalid negative kWh in legacy calculator");
        }
        // Застарілий алгоритм із лінійним коефіцієнтом
        double cost = ctx.kilowatt_hours * 2.45;
        if (ctx.zone_code == 2) {
            cost *= 0.5; // Нічний тариф
        }
        return CalculationResult{.total_cost = cost, .tariff_name = "Legacy-Flat-v1"};
    }
};

// 3. New Implementation (Новий модуль з підтримкою динамічних сіток)
class DynamicGridTariffCalculator final : public ITariffCalculator {
public:
    std::expected<CalculationResult, std::string> calculate(const TariffContext& ctx) const noexcept override {
        if (ctx.kilowatt_hours < 0) {
            return std::unexpected("Invalid negative kWh in new calculator");
        }
        // Новий високопродуктивний алгоритм із градацією зон
        double base_rate = (ctx.zone_code == 2) ? 1.20 : 2.80;
        double cost = ctx.kilowatt_hours * base_rate;
        if (ctx.kilowatt_hours > 500.0) {
            cost += (ctx.kilowatt_hours - 500.0) * 0.40; // Прогресивна шкала
        }
        return CalculationResult{.total_cost = cost, .tariff_name = "DynamicGrid-v2"};
    }
};

// 4. Branch Router (Динамічний перемикач на основі Feature Flag)
class TariffServiceBoundary final {
private:
    std::unique_ptr<ITariffCalculator> legacy_calc_;
    std::unique_ptr<ITariffCalculator> new_calc_;
    std::atomic<bool> use_new_engine_{false};

public:
    TariffServiceBoundary(std::unique_ptr<ITariffCalculator> legacy,
                          std::unique_ptr<ITariffCalculator> next_gen)
        : legacy_calc_(std::move(legacy)), new_calc_(std::move(next_gen)) {}

    void set_use_new_engine(bool enable) noexcept {
        use_new_engine_.store(enable, std::memory_order_release);
    }

    [[nodiscard]] std::expected<CalculationResult, std::string> 
    process_billing(const TariffContext& ctx) const noexcept {
        if (use_new_engine_.load(std::memory_order_acquire)) {
            return new_calc_->calculate(ctx);
        }
        return legacy_calc_->calculate(ctx);
    }
};

int main() {
    auto boundary = std::make_unique<TariffServiceBoundary>(
        std::make_unique<LegacyTariffCalculator>(),
        std::make_unique<DynamicGridTariffCalculator>()
    );

    TariffContext sample_ctx{.device_id = 4091, .kilowatt_hours = 620.0, .zone_code = 1};

    // Обробка legacy-двигуном
    auto res1 = boundary->process_billing(sample_ctx);
    if (res1) {
        std::cout << "Legacy Cost: " << res1->total_cost << " (" << res1->tariff_name << ")\n";
    }

    // Динамічне канарейкове перемикання на новий двигун
    boundary->set_use_new_engine(true);

    auto res2 = boundary->process_billing(sample_ctx);
    if (res2) {
        std::cout << "New Engine Cost: " << res2->total_cost << " (" << res2->tariff_name << ")\n";
    }

    return 0;
}
```
```go
package abstraction

import (
	"errors"
	"sync/atomic"
)

type TariffContext struct {
	DeviceID      uint64
	KilowattHours float64
	ZoneCode      uint32
}

type CalculationResult struct {
	TotalCost  float64
	TariffName string
}

// 1. Abstraction Interface
type TariffCalculator interface {
	Calculate(ctx TariffContext) (CalculationResult, error)
}

// 2. Legacy Implementation
type LegacyTariffCalculator struct{}

func (l *LegacyTariffCalculator) Calculate(ctx TariffContext) (CalculationResult, error) {
	if ctx.KilowattHours < 0 {
		return CalculationResult{}, errors.New("negative kWh")
	}
	cost := ctx.KilowattHours * 2.45
	if ctx.ZoneCode == 2 {
		cost *= 0.5
	}
	return CalculationResult{TotalCost: cost, TariffName: "Legacy-Flat-v1"}, nil
}

// 3. New Implementation
type DynamicGridTariffCalculator struct{}

func (d *DynamicGridTariffCalculator) Calculate(ctx TariffContext) (CalculationResult, error) {
	if ctx.KilowattHours < 0 {
		return CalculationResult{}, errors.New("negative kWh")
	}
	baseRate := 2.80
	if ctx.ZoneCode == 2 {
		baseRate = 1.20
	}
	cost := ctx.KilowattHours * baseRate
	if ctx.KilowattHours > 500.0 {
		cost += (ctx.KilowattHours - 500.0) * 0.40
	}
	return CalculationResult{TotalCost: cost, TariffName: "DynamicGrid-v2"}, nil
}

// 4. Branch Router з атомарним прапорцем
type TariffServiceBoundary struct {
	legacy TariffCalculator
	newEng TariffCalculator
	useNew atomic.Bool
}

func NewTariffServiceBoundary() *TariffServiceBoundary {
	return &TariffServiceBoundary{
		legacy: &LegacyTariffCalculator{},
		newEng: &DynamicGridTariffCalculator{},
	}
}

func (b *TariffServiceBoundary) SetUseNewEngine(enable bool) {
	b.useNew.Store(enable)
}

func (b *TariffServiceBoundary) ProcessBilling(ctx TariffContext) (CalculationResult, error) {
	if b.useNew.Load() {
		return b.newEng.Calculate(ctx)
	}
	return b.legacy.Calculate(ctx)
}
```
:::

### Пояснення системних аспектів C++ та Go реалізацій

1. **Атомарний порядок пам'яті (Memory Ordering) у C++:** У виклику `store(enable, std::memory_order_release)` та `load(std::memory_order_acquire)` застосовуються аквайр-реліз семантики. Це гарантує, що при зміні прапорця в одному потоці всі інші потоки миттєво бачать оновлений стан без використання дорогих м'ютексів (Lock-free thread safety).
2. **Безвиняткова обробка помилок (`std::expected`):** У сучасній C++23 розробці повернення `std::expected<T, E>` є ідіоматичною заміною C++ виняткам або C-структурам із кодами помилок. Це дає гарантію `noexcept` та передбачувану латентність без overhead на розкрутку стеку (Stack Unwinding).
3. **Використання `std::string_view`:** Запобігає зайвим динамічним аллокаціям рядків у купі (Heap Allocation) під час повернення назв тарифів.
4. **Продуктивність віртуального виклику (vtable overhead):** Виклик через абстрактний інтерфейс у C++ додає незначний оверхед віртуальної таблиці (vtable lookup, ~1–2 нс). Для систем обробки високочастотної телеметрії це є нехтувано малою ціною за абсолютну безпеку міграції.

## 3. Практична ізоляція побічних ефектів при Dark Launching

При реалізації тіньового запуску (Dark Launching) найкритичнішим інженерним викликом є запобігання дублюванню дій, які модифікують стан зовнішнього світу або випускають незворотні транзакції. Помилка на цьому рівні може призвести до повторного списання коштів клієнтів або подвійної відправки сповіщень.

Для гарантії безпеки тіньового виконання застосовуються наступні обов'язкові правила:

1. **Маркування запитів (Header Inspection & Context Injection):**
   Будь-який запит, продубльований проксі-шаром, отримує обов'язковий заголовок `X-Dark-Launch-Shadow: true`. Всі сервісні клієнти та зовнішні адаптери всередині нового сервісу аналізують наявність цього заголовка й автоматично переключаються у тестовий режим.

2. **Застосування Mock/Dry-Run адаптерів:**
   Зовнішні інтеграції (SMS-шлюзи, платіжні системи, виклики аппаратних смарт-реле) під час тіньового виконання підміняються мок-реалізаціями або виконуються в режимі `dry-run`, коли бізнес-логіка перевіряє контракти та будує тіло запиту, але реальне мережеве з'єднання з зовнішнім провайдером зупиняється.

3. **Ізоляція записів у бази даних (Database Write Sandbox):**
   При дублюванні мутуючих запитів (`POST`/`PUT`/`DELETE`) тіньовий сервіс спрямовує транзакції у тимчасову пісочницю (Sandbox DB) або у схему з автоматичним відкатом транзакцій (`ROLLBACK` після завершення перевірки). Це запобігає забрудненню первинних таблиць БД некоректними або дубльованими даними.

4. **Простеження крізь OpenTelemetry correlation ID:**
   Для швидкої діагностики розходжень кожному тіньовому запиту присвоюється той самий correlation ID, що й у продуктивного запиту. Це дозволяє в інструментах типу Jaeger/Grafana Tempo поруч зіставити два дерева викликів і відразу виявити точки, де новий сервіс робить зайві або уповільнені виклики.

### Схема ізоляції адаптерів при Dark Launching

```text
[Incoming Shadow Request (Header: X-Dark-Launch-Shadow=true)]
                         │
                         ▼
             [New Service Core Logic]
                         │
         ┌───────────────┴───────────────┐
  (Read Query)                    (Write Mutation / Side Effect)
         │                               │
         ▼                               ▼
 [Production Read Replica DB]    [Dry-Run / Mock Adapter]
                                 • Fake Billing Charge
                                 • Log Payload to Jaeger
                                 • Skip Hardware Socket Write
```
