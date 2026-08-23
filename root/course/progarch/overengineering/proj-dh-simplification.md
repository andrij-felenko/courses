# ⚙️ Спрощення архітектури Digital Home: від розподілених саг до модульного моноліту

Практичний рефакторинг реальної підсистеми розрахунку щогодинних агрегатів телеметрії та сповіщень у системі розумного дому Digital Home демонструє, як надмірно спроєктоване рішення на чотирьох мікросервісах із Kafka, gRPC-контрактами, Protobuf-схемами та розподіленими сагами спрощується до модульного моноліту із транзакційним Outbox та прямою чергою в PostgreSQL — скорочуючи кодову базу на 75%, усуваючи мережеві точки відмови, знімаючи інфраструктурний оверхед та знижуючи затримку обробки в 11 разів.

---

## Контекст задачі: Обробка та агрегація подій Digital Home

У системі Digital Home кожен із 50 000 домашніх хабів та прив'язані до нього датчики (термостати, лічильники електроенергії, давачі руху, розумні розетки) щохвилини відправляють виміри в центральну підсистему аналітики. Загальний потік телеметрії становить близько 830 запитів на секунду (rps) на інжест.

Завдання підсистеми агрегації та сповіщень складається з трьох послідовних кроків:
1. **Інжест та збереження:** Зібрати показники телеметрії й зберегти їх для подальшого аналізу.
2. **Щогодинна агрегація:** Розрахувати сумарну спожиту енергію у кіловат-годинах (кВт·год) та середню температуру за годину для кожного дому.
3. **Генерування сповіщень:** Якщо сумарне споживання перевищує встановлений користувачем поріг або середня температура виходить за межі безпечного діапазону — згенерувати сповіщення, записати його в історію та надіслати Push-повідомлення у мобільний застосунок.

З архітектурної точки зору 830 rps — це помірне навантаження, яке будь-яка сучасна реляційна база даних (на кшталт PostgreSQL) на одному екземплярі з 4 ядрами CPU обробляє з завантаженням не більше 3–5%.

---

## Варіант A: Перепроєктована сервісна архітектура (Анатомія складності)

На початковому етапі розробки команда вирішила побудувати «найсучаснішу подієво-орієнтовану мікросервісну архітектуру» (Event-Driven Microservices Architecture). Система була розбита на 4 окремі мікросервіси, розгорнуті в Kubernetes, що взаємодіяли через кластер Apache Kafka на дев'яти вузлах та синхронні gRPC-виклики:

```
[Hubs (830 rps)]
       │
       ▼ (HTTP/REST)
[Ingest-Service]
       │
       ▼ (Kafka: raw-telemetry)
[Aggregation-Service]
       │
       ▼ (Kafka: hourly-aggregates)
[Rule-Engine-Service] ──── (gRPC) ───► [User-Policy-Service]
       │
       ▼ (Kafka: alert-events)
[Notification-Service] ───► [Apple APNs / Google FCM]
```

### Покрокове простеження шляху даних у Варіанті A

1. **Інжест:** `Ingest-Service` приймає HTTP-пакет від хаба, валідує JSON, серіалізує об'єкт у Protobuf і публікує в Kafka-топік `raw-telemetry` (партиційований за `home_id`).
2. **Агрегація:** `Aggregation-Service` вичитує події з Kafka, накопичує стани у пам'яті (та кешує транзитний стан у Redis), кожної години формує агрегат і публікує Protobuf-повідомлення в топік `hourly-aggregates`.
3. **Перевірка правил:** `Rule-Engine-Service` вичитає агрегат з Kafka, робить синхронний gRPC-виклик до `User-Policy-Service`, щоб отримати індивідуальні ліміти користувача, перевіряє поріг і публікує сповіщення в топік `alert-events`.
4. **Сповіщення:** `Notification-Service` вичитає `alert-events` і надсилає Push-запит до APNs/FCM.

### Точки зламу та операційний податок Варіанта A

У продакшені ця система створила п'ять важких інженерних проблем:

1. **Серіалізаційний та мережевий оверхед:** Кожен вимір трьохкратно долав мережу та піддавався серіалізації/десеріалізації у Protobuf на чотирьох різних вузлах. Мережева затримка (p99) досягала 140 мс.
2. **Пастка подвійного запису (Dual Writes):** У `Aggregation-Service` виникла необхідність одночасно зберегти агрегат у БД і опублікувати подію в Kafka. Якщо сервіс падав після запису в БД, але до виклику `kafkaProducer.send()`, подія втрачалася. Для розв'язання цього команда змушена була будувати розподілену сагу із подвійною перевіркою ідемпотентного ключа у Redis.
3. **Каскадне підсилення змін:** Додавання нового параметра (наприклад, вологості повітря) вимагало редагування 4 файлів `.proto`, перекомпіляції кодогенераторів, оновлення DTO у 4 репозиторіях та синхронного канаркового розгортання чотирьох сервісів.
4. **Проблема ребалансування партицій:** Під час тимчасового збою одного Pod-а Kafka починала тривалий процес rebalance партицій, зупиняючи обробку телеметрії для тисяч хабів на 30–60 секунд.

---

## Варіант B: Модульний моноліт з транзакційним Outbox

У прагматичному варіанті весь конвеєр об'єднано в **один процес модульного моноліту**. Замість Kafka та мережевих gRPC-викликів використовуються:
- Внутрішньопроцесні виклики між чітко ізольованими модулями (`IngestModule`, `AggregationModule`, `RuleModule`, `NotificationModule`).
- База даних PostgreSQL з підтримкою транзакційного патерна **Transactional Outbox**: обчислення агрегатів і запис сповіщення відбуваються в **одній БД-транзакції**.

### Механіка патерна Transactional Outbox

Замість публікації події у зовнішній брокер повідомлень (що створює ризик розсинхронізації через мережеві збо збої), додаток зберігає бізнес-результат та сповіщення в єдиній транзакції реляційної бази даних:

```sql
-- Таблиці модульного моноліту
CREATE TABLE hourly_aggregates (
    id BIGSERIAL PRIMARY KEY,
    home_id VARCHAR(64) NOT NULL,
    total_energy_kwh NUMERIC(10, 3) NOT NULL,
    avg_temperature_c NUMERIC(5, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE outbox_events (
    id BIGSERIAL PRIMARY KEY,
    aggregate_type VARCHAR(64) NOT NULL,
    aggregate_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_outbox_unprocessed ON outbox_events (created_at) WHERE processed_at IS NULL;

-- Атомарне збереження агрегату й події сповіщення
BEGIN TRANSACTION;
  INSERT INTO hourly_aggregates (home_id, total_energy_kwh, avg_temperature_c) 
  VALUES ('home-42', 3.650, 21.80);

  INSERT INTO outbox_events (aggregate_type, aggregate_id, event_type, payload) 
  VALUES ('HomeAggregate', 'home-42', 'HIGH_ENERGY_ALERT', '{"home_id": "home-42", "energy_kwh": 3.650}');
COMMIT;
```

Цей підхід забезпечує **100% транзакційну консистентність (ACID)**: сповіщення виникне у таблиці `outbox_events` тоді й тільки тоді, коли збережено агрегат у `hourly_aggregates`.

### Воркер обробки Outbox (Outbox Poller Worker)

Фоновий воркер читає необроблені події з БД за допомогою інструкції `FOR UPDATE SKIP LOCKED`. Це дозволяє горизонтально масштабувати екземпляри додатку без гонки за товари та без блокувань між паралельними воркерами:

```sql
-- Безпечне паралельне вичитання подій декількома екземплярами воркерів
SELECT id, event_type, payload 
FROM outbox_events 
WHERE processed_at IS NULL 
ORDER BY id ASC 
LIMIT 100 
FOR UPDATE SKIP LOCKED;
```

Після успішної відправки Push-сповіщення через APNs/FCM воркер проставляє `processed_at = NOW()`. Якщо зовнішній сервіс сповіщень тимчасово недоступний, транзакція відкочується, і подія буде повторно оброблена під час наступного ітераційного кроку воркера з експоненційним запізненням.

Очищення оброблених подій здійснюється простим нічним крон-запитом:
`DELETE FROM outbox_events WHERE processed_at < NOW() - INTERVAL '7 days';`

---

## Порівняльний код реалізації підсистеми

Нижче наведено робочий прагматичний код обробки телеметрії та транзакційного формування сповіщень мовами C++, TypeScript та Python.

:::tabs
```cpp
// ============================================================================
// ВАРІАНТ B (Прагматичний): Модульний моноліт на C++20
// Одне транзакційне коло: агрегація + перевірка правил + Outbox усередині БД
// ============================================================================

#include <iostream>
#include <vector>
#include <string>
#include <optional>
#include <expected>
#include <memory>
#include <chrono>

struct TelemetryMetric {
    std::string device_id;
    std::string home_id;
    double energy_kwh;
    double temperature_c;
    int64_t timestamp;
};

struct AggregateResult {
    std::string home_id;
    double total_energy_kwh;
    double avg_temperature_c;
    bool threshold_exceeded;
};

// Модель Outbox-події для транзакційного збереження
struct OutboxEvent {
    std::string aggregate_type;
    std::string aggregate_id;
    std::string event_type;
    std::string payload_json;
};

// Чіткий доменний сервіс без мережевого оверхеду
class HomeAnalyticsAggregator {
public:
    enum class Error { DatabaseError, InvalidMetrics };

    // Транзакційна обробка: обчислення й формування сповіщення в єдиній сесії
    std::expected<AggregateResult, Error> process_hourly_batch(
        const std::string& home_id,
        const std::vector<TelemetryMetric>& metrics,
        double max_energy_threshold) 
    {
        if (metrics.empty()) {
            return std::unexpected(Error::InvalidMetrics);
        }

        double total_energy = 0.0;
        double temp_sum = 0.0;

        for (const auto& m : metrics) {
            total_energy += m.energy_kwh;
            temp_sum += m.temperature_c;
        }

        double avg_temp = temp_sum / static_cast<double>(metrics.size());
        bool alert_needed = (total_energy > max_energy_threshold);

        // Симуляція атомарної БД-транзакції:
        // db.transaction([&](auto& tx) {
        //     tx.execute("INSERT INTO hourly_aggregates ...", home_id, total_energy, avg_temp);
        //     if (alert_needed) {
        //         tx.execute("INSERT INTO outbox_events ...", "HomeAggregate", home_id, "HIGH_ENERGY_ALERT");
        //     }
        // });

        return AggregateResult{
            .home_id = home_id,
            .total_energy_kwh = total_energy,
            .avg_temperature_c = avg_temp,
            .threshold_exceeded = alert_needed
        };
    }
};

int main() {
    HomeAnalyticsAggregator aggregator;
    std::vector<TelemetryMetric> sample = {
        {"dev-1", "home-42", 1.8, 21.5, 1700000000},
        {"dev-2", "home-42", 2.1, 22.1, 1700000060}
    };

    auto res = aggregator.process_hourly_batch("home-42", sample, 3.0);
    if (res) {
        std::cout << "[Оптимум] Успішно обчислено для дому " << res->home_id 
                  << ": сумарна енергія = " << res->total_energy_kwh 
                  << " кВт·год, поріг перевищено = " << (res->threshold_exceeded ? "ТАК" : "НІ") 
                  << "\n";
    }
    return 0;
}
```
```ts
// ============================================================================
// ВАРІАНТ B (Прагматичний): Модульний моноліт на TypeScript
// Пряма обробка в межах одного процесу з транзакційною гарантією
// ============================================================================

interface TelemetryMetric {
  deviceId: string;
  homeId: string;
  energyKwh: number;
  temperatureC: number;
  timestamp: number;
}

interface AggregateResult {
  homeId: string;
  totalEnergyKwh: number;
  avgTemperatureC: number;
  thresholdExceeded: boolean;
}

export class HomeAnalyticsService {
  // Обробка пачки телеметрії в межах однієї транзакції бази даних
  public async processHourlyBatch(
    homeId: string,
    metrics: TelemetryMetric[],
    maxEnergyThreshold: number
  ): Promise<AggregateResult> {
    if (metrics.length === 0) {
      throw new Error("Empty metrics payload");
    }

    let totalEnergy = 0;
    let tempSum = 0;

    for (const m of metrics) {
      totalEnergy += m.energyKwh;
      tempSum += m.temperatureC;
    }

    const avgTemp = tempSum / metrics.length;
    const alertNeeded = totalEnergy > maxEnergyThreshold;

    // Прямий запис у базу даних у межах однієї ACID-транзакції:
    // await db.transaction(async (tx) => {
    //   await tx.query(
    //     "INSERT INTO hourly_aggregates (home_id, total_energy_kwh, avg_temperature_c) VALUES ($1, $2, $3)",
    //     [homeId, totalEnergy, avgTemp]
    //   );
    //   if (alertNeeded) {
    //     await tx.query(
    //       "INSERT INTO outbox_events (aggregate_type, aggregate_id, event_type, payload) VALUES ($1, $2, $3, $4)",
    //       ["HomeAggregate", homeId, "HIGH_ENERGY_ALERT", JSON.stringify({ homeId, totalEnergy })]
    //     );
    //   }
    // });

    return {
      homeId,
      totalEnergyKwh: totalEnergy,
      avgTemperatureC: avgTemp,
      thresholdExceeded: alertNeeded,
    };
  }
}
```
```py
# ============================================================================
# ВАРІАНТ B (Прагматичний): Модульний моноліт на Python
# Пряма обробка пачки без Kafka та gRPC
# ============================================================================

from dataclasses import dataclass
from typing import List, Dict, Any
import json

@dataclass(frozen=True)
class TelemetryMetric:
    device_id: str
    home_id: str
    energy_kwh: float
    temperature_c: float
    timestamp: int

@dataclass(frozen=True)
class AggregateResult:
    home_id: str
    total_energy_kwh: float
    avg_temperature_c: float
    threshold_exceeded: bool

class HomeAnalyticsService:
    def process_hourly_batch(
        self,
        home_id: str,
        metrics: List[TelemetryMetric],
        max_energy_threshold: float
    ) -> AggregateResult:
        if not metrics:
            raise ValueError("Empty metrics batch")

        total_energy = sum(m.energy_kwh for m in metrics)
        avg_temp = sum(m.temperature_c for m in metrics) / len(metrics)
        alert_needed = total_energy > max_energy_threshold

        # Атомарне збереження в БД й додавання події в outbox:
        # with db.transaction():
        #     db.execute(
        #         "INSERT INTO hourly_aggregates (home_id, total_energy_kwh, avg_temperature_c) VALUES (%s, %s, %s)",
        #         (home_id, total_energy, avg_temp)
        #     )
        #     if alert_needed:
        #         db.execute(
        #             "INSERT INTO outbox_events (aggregate_type, aggregate_id, event_type, payload) VALUES (%s, %s, %s, %s)",
        #             ("HomeAggregate", home_id, "HIGH_ENERGY_ALERT", json.dumps({"home_id": home_id, "energy": total_energy}))
        #         )

        return AggregateResult(
            home_id=home_id,
            total_energy_kwh=total_energy,
            avg_temperature_c=avg_temp,
            threshold_exceeded=alert_needed
        )
```
:::

---

## Детальний порівняльний аналіз результатів спрощення

У результаті міграції з розподіленої сервісної схеми (Варіант A) на модульний моноліт (Варіант B) команда Digital Home отримала такі вимірювані інженерні та бізнес-результати:

| Метрика | Варіант A (Мікросервіси + Kafka) | Варіант B (Модульний моноліт) | Виграш / Ефект |
| :--- | :--- | :--- | :--- |
| **Обсяг коду (LoC)** | 8 400 рядків (4 репо + Protobuf) | 2 100 рядків (1 репо) | **−75% коду** |
| **Кількість інфраструктурних вузлів** | 12 (4 Pods, 3 Kafka nodes, 3 Zookeeper/KRaft, 2 Redis) | 2 (1 App Instance, 1 PostgreSQL primary/replica) | **−83% вузлів** |
| **Середня затримка (Latency p99)** | 140 мс (мережеві хопи + Kafka commit) | 12 мс (внутрішньопроцесний виклик + 1 DB commit) | **у 11 разів швидше** |
| **Місячний чек за хмару (Cloud Cost)** | \$1 450 / місяць | \$120 / місяць | **−91% витрат** |
| **Час додавання нового поля** | 2,5 дні (4 PR, синхронне розгортання) | 45 хвилин (1 PR, 1 міграція) | **у 26 разів швидше** |
| **Гарантія консистентності** | Eventual Consistency + DLQ | ACID / Strong Consistency | **усунуто розсинхронізацію** |
| **Час відновлення після збою (MTTR)** | 4 години (налагодження 4 логів та офсетів) | 15 хвилин (аналіз одного стектрейсу) | **у 16 разів швидше** |

Прагматичне спрощення не просто зменшило витрати на хмару, а вивільнило інженерний ресурс команди для створення фіч, потрібних користувачам розумного дому, замість боротьби з мережевими відмовами та розсинхронізацією черг.
