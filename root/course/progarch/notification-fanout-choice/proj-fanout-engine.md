# ⚙️ Практична реалізація: Трирівневий Fan-Out роутер Digital Homes

У цьому практичному проєкті ми будуємо виробничий рушій розсилки сповіщень (англ. *Fan-Out Router*) для платформи Digital Homes. Завдання роутера — прийняти сиру подію, швидко визначити розмір її аудиторії `N` та рівень критичності, і спрямувати її за однією з трьох траєкторій виконання (On-Write, Hybrid з батчингом або On-Read Broadcast), запобігаючи вибуху навантаження та гарантуючи SLA доставки.

## Архітектурний контракт роутера

Роутер обробляє об'єкти подій `NotificationEvent` і на основі двох критеріїв — прапорця аварійності `is_emergency` та кількості підписників `recipient_count` — обирає оптимальний маршрут:

```
                        ┌──> Tier 1: Fast-Track On-Write (N <= 10 або Emergency)
                        │    (Миттєвий розсип у персональні inboxes)
                        │
NotificationEvent ─── Router ──> Tier 2: Hybrid Community (10 < N <= 5000)
                        │    (1 запис у стрічку ЖК + push-батчі по 500)
                        │
                        └──> Tier 3: On-Read Broadcast (N > 5000)
                             (1 запис у глобальну стрічку + FCM Topic)
```

## Критерії прийняття архітектурних рішень

Коли сира подія надходить до `FanOutRouter`, код має прийняти рішення за менш ніж 1 мікросекунду без звернення до зовнішніх баз даних чи диска. Для цього інформація про кількість підписників `recipient_count` підгортається на етапі аутентифікації джерела події або зчитується з високошвидкісного кешу в пам'яті.

1. **Критерій пріоритету (Emergency Fast-Path)**: Якщо `is_emergency == true`, обчислення класичної економічної ефективності скасовується. Навіть якщо аудиторія події складає 500 осіб (наприклад, пожежна тривога в під'їзді), подія спрямовується через On-Write Fast-Track з високим пріоритетом. Життя людей і безпека майна мають абсолютний пріоритет над економно збереженими дисковими I/O.
2. **Критерій малоабонентного дому (`N <= 10`)**: Для окремої квартири чи приватного будинку кількість мешканців не перевищує 10 осіб. На такій кількості витрати на On-Write розсип є незначними (10 записів у пам'яті Redis займають < 2 кілобайти), тоді як користь від миттєвого відображення в застосунку без складних JOIN-запитів є максимальною.
3. **Критерій середнього масштабу (`10 < N <= 5000`)**: Масштаб під'їзду або житлового комплексу. Оголошення про ремонт чи відключення комунікацій стосуються сотень людей. Наїна розсилка створює тисячі записів, тому застосовується гібридна модель: збереження 1 запису в стрічці ЖК (On-Read) + розбиття push-сповіщень на батчі по 500 отримувачів.
4. **Критерій масового системного масштабу (`N > 5000`)**: Масштаб всієї платформи або великого мікрорайону. Публікація нових правил або статусу сервісу. Застосовується чистий On-Read без записів в inboxes + єдиний broadcast push у FCM/APNs топік.

## Реалізація гібридного роутера

Подивимося на реалізацію роутера трьома мовами: C++, Go та TypeScript.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <variant>
#include <span >
#include <chrono>

// Структура сповіщення в Digital Homes
struct NotificationEvent {
    std::string id;
    std::string title;
    std::string body;
    std::string scope_id;        // ID дому, ЖК або глобальної системи
    size_t recipient_count{0};   // Кількість підписників (N)
    bool is_emergency{false};    // Критична тривога (дим, злом, витік)
};

// Результати рішення роутингу
enum class FanOutStrategy {
    FastTrackOnWrite,  // Tier 1: On-Write без злиття, миттєво
    HybridBatched,     // Tier 2: On-Read стрічка + push-батчі
    BroadcastOnRead    // Tier 3: On-Read broadcast feed + topic push
};

struct DispatchDecision {
    FanOutStrategy strategy;
    size_t batch_size;
    std::string route_reason;
};

// Клас трирівневого Fan-Out роутера
class FanOutRouter {
public:
    static constexpr size_t K_MAX_DIRECT_ONWRITE = 10;
    static constexpr size_t K_MAX_COMMUNITY_HYBRID = 5000;
    static constexpr size_t K_PUSH_BATCH_CHUNK = 500;

    [[nodiscard]] DispatchDecision route(const NotificationEvent& event) const noexcept {
        // Критичні тривоги або малоабонентні доми завжди йдуть через Fast-Track On-Write
        if (event.is_emergency || event.recipient_count <= K_MAX_DIRECT_ONWRITE) {
            return {
                FanOutStrategy::FastTrackOnWrite,
                event.recipient_count,
                "Tier 1: Аварійний або локальний доступ (N <= 10). Пряма On-Write розсилка."
            };
        }

        // Середні масиви (будинок, ЖК) — гібридний розсип
        if (event.recipient_count <= K_MAX_COMMUNITY_HYBRID) {
            return {
                FanOutStrategy::HybridBatched,
                K_PUSH_BATCH_CHUNK,
                "Tier 2: Подія ЖК (10 < N <= 5000). On-Read стрічка + push-батчі."
            };
        }

        // Глобальні сповіщення — чистий On-Read + Broadcast Topic
        return {
            FanOutStrategy::BroadcastOnRead,
            1,
            "Tier 3: Системна масова подія (N > 5000). Чистий On-Read + FCM Topic."
        };
    }

    void execute_dispatch(const NotificationEvent& event) const {
        const auto decision = route(event);
        std::cout << "[ROUTER] Подія ID: " << event.id 
                  << " | Стратегія: " << static_cast<int>(decision.strategy)
                  << " | Опис: " << decision.route_reason << "\n";

        switch (decision.strategy) {
            case FanOutStrategy::FastTrackOnWrite:
                dispatch_on_write_fastpath(event);
                break;
            case FanOutStrategy::HybridBatched:
                dispatch_hybrid_community(event, decision.batch_size);
                break;
            case FanOutStrategy::BroadcastOnRead:
                dispatch_broadcast_onread(event);
                break;
        }
    }

private:
    void dispatch_on_write_fastpath(const NotificationEvent& event) const {
        std::cout << "  └─ [Tier 1] Запис " << event.recipient_count 
                  << " персональних inboxes у пам'ять + Push з високим пріоритетом.\n";
    }

    void dispatch_hybrid_community(const NotificationEvent& event, size_t chunk_size) const {
        const size_t num_chunks = (event.recipient_count + chunk_size - 1) / chunk_size;
        std::cout << "  └─ [Tier 2] Збережено 1 запис стрічки ЖК " << event.scope_id 
                  << ". Згенеровано " << num_chunks << " push-батчів по " << chunk_size << " рецепторів.\n";
    }

    void dispatch_broadcast_onread(const NotificationEvent& event) const {
        std::cout << "  └─ [Tier 3] Збережено 1 глобальний запис у системну стрічку. "
                  << "Відправлено 1 multicast push у топік: root://" << event.scope_id << "\n";
    }
};

int main() {
    FanOutRouter router;

    // Сценарій 1: Пожежна тривога в квартирі (2 мешканці)
    NotificationEvent fire_alert{
        "evt-001", "Виявлено дим!", "Датчик у кухні спрацював", "home-1402", 2, true
    };

    // Сценарій 2: Оголошення ОСББ про воду (1200 мешканців ЖК)
    NotificationEvent water_notice{
        "evt-002", "Відключення води", "Завтра з 09:00 ремонтні роботи", "complex-oak", 1200, false
    };

    // Сценарій 3: Оновлення правил сервісу (500 000 користувачів)
    NotificationEvent system_update{
        "evt-003", "Оновлення оферти", "Змінилися умови обслуговування", "global-dh", 500000, false
    };

    router.execute_dispatch(fire_alert);
    router.execute_dispatch(water_notice);
    router.execute_dispatch(system_update);

    return 0;
}
```
```go
package main

import (
	"fmt"
	"math"
)

type NotificationEvent struct {
	ID             string
	Title          string
	Body           string
	ScopeID        string
	RecipientCount int
	IsEmergency    bool
}

type FanOutStrategy int

const (
	FastTrackOnWrite FanOutStrategy = iota
	HybridBatched
	BroadcastOnRead
)

type DispatchDecision struct {
	Strategy    FanOutStrategy
	BatchSize   int
	RouteReason string
}

type FanOutRouter struct{}

const (
	MaxDirectOnWrite  = 10
	MaxCommunityHybrid = 5000
	PushBatchChunk    = 500
)

func (r *FanOutRouter) Route(event NotificationEvent) DispatchDecision {
	if event.IsEmergency || event.RecipientCount <= MaxDirectOnWrite {
		return DispatchDecision{
			Strategy:    FastTrackOnWrite,
			BatchSize:   event.RecipientCount,
			RouteReason: "Tier 1: Аварійний або локальний доступ (N <= 10). Пряма On-Write розсилка.",
		}
	}

	if event.RecipientCount <= MaxCommunityHybrid {
		return DispatchDecision{
			Strategy:    HybridBatched,
			BatchSize:   PushBatchChunk,
			RouteReason: "Tier 2: Подія ЖК (10 < N <= 5000). On-Read стрічка + push-батчі.",
		}
	}

	return DispatchDecision{
		Strategy:    BroadcastOnRead,
		BatchSize:   1,
		RouteReason: "Tier 3: Системна масова подія (N > 5000). Чистий On-Read + FCM Topic.",
	}
}

func (r *FanOutRouter) ExecuteDispatch(event NotificationEvent) {
	decision := r.Route(event)
	fmt.Printf("[ROUTER] Подія ID: %s | Стратегія: %d | Опис: %s\n", event.ID, decision.Strategy, decision.RouteReason)

	switch decision.Strategy {
	case FastTrackOnWrite:
		fmt.Printf("  └─ [Tier 1] Запис %d персональних inboxes у пам'ять + High-Priority Push.\n", event.RecipientCount)
	case HybridBatched:
		numChunks := int(math.Ceil(float64(event.RecipientCount) / float64(decision.BatchSize)))
		fmt.Printf("  └─ [Tier 2] Збережено 1 запис стрічки ЖК %s. Згенеровано %d push-батчів по %d рецепторів.\n",
			event.ScopeID, numChunks, decision.BatchSize)
	case BroadcastOnRead:
		fmt.Printf("  └─ [Tier 3] Збережено 1 глобальний запис у системну стрічку. Multicast push у root://%s\n", event.ScopeID)
	}
}

func main() {
	router := &FanOutRouter{}

	router.ExecuteDispatch(NotificationEvent{
		ID: "evt-001", Title: "Виявлено дим!", ScopeID: "home-1402", RecipientCount: 2, IsEmergency: true,
	})
	router.ExecuteDispatch(NotificationEvent{
		ID: "evt-002", Title: "Відключення води", ScopeID: "complex-oak", RecipientCount: 1200, IsEmergency: false,
	})
	router.ExecuteDispatch(NotificationEvent{
		ID: "evt-003", Title: "Оновлення оферти", ScopeID: "global-dh", RecipientCount: 500000, IsEmergency: false,
	})
}
```
```ts
interface NotificationEvent {
  id: string;
  title: string;
  body: string;
  scopeId: string;
  recipientCount: number;
  isEmergency: boolean;
}

enum FanOutStrategy {
  FastTrackOnWrite = "FastTrackOnWrite",
  HybridBatched = "HybridBatched",
  BroadcastOnRead = "BroadcastOnRead",
}

interface DispatchDecision {
  strategy: FanOutStrategy;
  batchSize: number;
  routeReason: string;
}

class FanOutRouter {
  private static readonly MAX_DIRECT_ONWRITE = 10;
  private static readonly MAX_COMMUNITY_HYBRID = 5000;
  private static readonly PUSH_BATCH_CHUNK = 500;

  public route(event: NotificationEvent): DispatchDecision {
    if (event.isEmergency || event.recipientCount <= FanOutRouter.MAX_DIRECT_ONWRITE) {
      return {
        strategy: FanOutStrategy.FastTrackOnWrite,
        batchSize: event.recipientCount,
        routeReason: "Tier 1: Аварійний або локальний доступ (N <= 10). Пряма On-Write розсилка.",
      };
    }

    if (event.recipientCount <= FanOutRouter.MAX_COMMUNITY_HYBRID) {
      return {
        strategy: FanOutStrategy.HybridBatched,
        batchSize: FanOutRouter.PUSH_BATCH_CHUNK,
        routeReason: "Tier 2: Подія ЖК (10 < N <= 5000). On-Read стрічка + push-батчі.",
      };
    }

    return {
      strategy: FanOutStrategy.BroadcastOnRead,
      batchSize: 1,
      routeReason: "Tier 3: Системна масова подія (N > 5000). Чистий On-Read + FCM Topic.",
    };
  }

  public executeDispatch(event: NotificationEvent): void {
    const decision = this.route(event);
    console.log(`[ROUTER] Подія ID: ${event.id} | Стратегія: ${decision.strategy} | Опис: ${decision.routeReason}`);

    if (decision.strategy === FanOutStrategy.FastTrackOnWrite) {
      console.log(`  └─ [Tier 1] Запис ${event.recipientCount} персональних inboxes у пам'ять + High-Priority Push.`);
    } else if (decision.strategy === FanOutStrategy.HybridBatched) {
      const numChunks = Math.ceil(event.recipientCount / decision.batchSize);
      console.log(`  └─ [Tier 2] Збережено 1 запис стрічки ЖК ${event.scopeId}. Згенеровано ${numChunks} push-батчів по ${decision.batchSize}.`);
    } else {
      console.log(`  └─ [Tier 3] Збережено 1 глобальний запис у системну стрічку. Multicast push у root://${event.scopeId}`);
    }
  }
}

// Запуск прикладу
const router = new FanOutRouter();
router.executeDispatch({ id: "evt-001", title: "Виявлено дим!", body: "", scopeId: "home-1402", recipientCount: 2, isEmergency: true });
router.executeDispatch({ id: "evt-002", title: "Відключення води", body: "", scopeId: "complex-oak", recipientCount: 1200, isEmergency: false });
router.executeDispatch({ id: "evt-003", title: "Оновлення оферти", body: "", scopeId: "global-dh", recipientCount: 500000, isEmergency: false });
```
:::

## Детальний розбір механіки воркерів та вибору батчингу

Розгляньмо, чому для Tier 2 (Community Scope) обрано саме розмір батчу `500` і як воркери обробляють ці пакети в реальному середовищі:

### 1. HTTP/2 мультиплексування та обмеження APNs/FCM

Зовнішні провайдери push-сповіщень (Apple APNs та Google FCM) підтримують протокол HTTP/2, який дозволяє відправляти до 500–1000 сповіщень у межах одного мультиплексованого з'єднання без закриття сокета. Розмір батчу 500 ідеально лягає на один мережевий кадр (DATA frame) протоколу HTTP/2.

Якщо намагатися розсилати 1200 повідомлень по одному HTTP/1.1 з'єднанню, на кожен запит витрачається TCP 3-way handshake + TLS negotiation (~50 мс RTT). 1200 записів займуть 60 секунд. При батчингу по 500 отримувачів ті самі 1200 повідомлень відправляються за 3 пакети за 150 мілісекунд.

### 2. Запобігання частковим збоям (Partial Failures) та повторам

Під час відправки батчу з 500 адресатів мережевий збій може статися після того, як APNs прийняв перші 300 повідомлень. Якщо роутер не підтримує стан обробки батчу, ретрай відправить весь батч знову, викликавши дублювання 300 повідомлень.

Для захисту від часткових збоїв у батчингу використовуються дві техніки:

- **Chunk Delivery ID**: Кожен батч отримує свій унікальний `batch_id = hash(event_id + chunk_index)`.
- **Client-Side Deduplication Token**: Кожне сповіщення всередині батчу містить `delivery_id = hash(event_id + recipient_id)`. Навіть якщо дубльований батч надійде на телефон мешканця, операційна система (iOS/Android) відкине другий push з тим самим `delivery_id`.

## Налаштування пулів робітників (Worker Pool Tuning)

Для запобігання взаємному впливу навантаження в системі Digital Homes будуються три ізольовані пули воркерів (метод Bulkheading):

```
+-------------------------------------------------------------------+
|                        Пул воркерів DH                            |
|                                                                   |
|  [Emergency Pool] ────> 8 threads (High Priority, Non-blocking)   |
|  [Community Pool] ────> 16 threads (Rate-limited, Batched)        |
|  [Broadcast Pool] ────> 4 threads (Low Priority, Background)      |
+-------------------------------------------------------------------+
```

- **Emergency Pool (8 потоків)**: Обслуговує виключно Tier 1. Воркери працюють із високим пріоритетом (CPU nice level -10). Вхідна черга має фіксовану місткість (bounded queue) з нульовою затримкою.
- **Community Pool (16 потоків)**: Обслуговує Tier 2. Налаштований на роботу з батчами та обмеженням темпу (Rate-Limiter: не більше 2000 push/сек на один вузол), що захищає від HTTP 429 від Google FCM.
- **Broadcast Pool (4 потоки)**: Обслуговує Tier 3. Працює в фоновому режимі з низьким пріоритетом (CPU nice level +10). Якщо Emergency Pool відчуває дефіцит ресурсів, Broadcast Pool тимчасово призупиняє виконання (throttled).

## Обробка помилок та експоненційне запізнення (Exponential Backoff + Jitter)

Під час відправки батчів push-сповіщень мережа або зовнішні сервіси можуть повертати тимчасові помилки `503 Service Unavailable` або `429 Too Many Requests`. Для уникнення синхронного перевантаження (thundering herd problem) роутер застосовує експоненційне запізнення із додаванням випадкового шуму (jitter):

```
t_backoff = min(t_max, t_base · 2^attempt) + random_jitter(0, t_jitter)
```

Якщо базовий інтервал складає 100 мс, то перша спроба повтору виконується через ~200 мс, друга — через ~400 мс, третя — через ~800 мс. Це дозволяє провайдеру відновити роботу без отримання нової лавини запитів від усіх воркерів одночасно.

## Метрики спостережливості OpenTelemetry

Усі операції роутингу та розсилу інструментуються стандартом OpenTelemetry. У кожен батч додається контекст трасування (`traceparent`), що дозволяє інженерам бачити наскрізну траєкторію сповіщення: від кліку оператора до підтвердження доставки на конкретний пристрій.

Метрика `fanout_routing_duration_seconds` відстежує час прийняття рішення роутером (p99 < 1 мкс), а `push_batch_delivery_latency_seconds` дає чітку картину пропускної спроможності зовнішніх каналів.

## Часті пастки під час обробки fan-out

1. **Відсутність ізоляції черг для аварійних сповіщень**: Якщо аварійні сигналізації про протікання води потрапляють у ту саму асинхронну чергу, що й масова розсилка квитанцій за комунальні послуги, затримка тривоги зростає з мілісекунд до десятків хвилин.
2. **Відсутність механізму Backpressure**: Під час масової розсилки push-сповіщень зовнішні сервіси (FCM/APNs) повертають помилку `429 Too Many Requests`. Якщо воркери роутера намагаються повторювати виклики без експоненційного запізнення (backoff), роутер моментально вичерпує пули з'єднань.
3. **Наївне повторення батчів без ідемпотентності**: Якщо під час відправки батчу з 500 нотифікацій стався таймаут мережі на 499-му сповіщенні, повторна відправка всього батчу призведе до дублювання 498 повідомлень у користувачів.
