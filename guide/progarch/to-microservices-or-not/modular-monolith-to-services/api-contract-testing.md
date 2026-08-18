# 📋 Специфікація та довідник контрактного тестування (Consumer-Driven Contracts)

Під час виділення мікросервісів з модульного моноліта за патерном Strangler Fig найгострішим архітектурним ризиком є непомітний розрив сумісності між монолітом (або суміжними сервісами) та новим виділеним сервісом. Коли межа між модулями пересувається з пам'яті в мережу, виклики функцій перетворюються на HTTP/gRPC запити з JSON або Protobuf payload. Будь-яка неузгодженість у назві поля, типі даних чи форматі дати спричиняє помилки серіалізації в продакшні.

Традиційне end-to-end (E2E) тестування в спільних тестових середовищах (Staging / QA) не вирішує цю проблему з трьох причин:
1. **Повільний зворотний зв'язок:** Запуск повного E2E-комплексу займає від 30 хвилин до кількох годин, що гальмує CI/CD конвеєр розробки та створює черги на деплой.
2. **Ненадійність середовищ (Flaky Tests):** Нестабільність мережі, тимчасові падіння суміжних сервісів або конфлікти тестових даних у спільній базі призводять до хибних спрацьовувань, через що інженери перестають довіряти результатам тестів і починають ігнорувати провали збірок.
3. **Комбінаторний вибух станів:** Перевірити всі крайові випадки та аномалії відповідей через зовнішні E2E-сценарії практично неможливо, бо підготовка складних станів даних у реальній БД вимагає великих часових витрат.

**Контрактне тестування на основі вимог споживача (Consumer-Driven Contract Testing, CDC)** пропонує альтернативний підхід. Воно відокремлює перевірку схеми та сумісності API від тестування бізнес-логіки. Споживач (Consumer) фіксує точні вимоги до API у вигляді машиночитаного документа — **файлу контракту (Pact file)** — під час виконання своїх швидких unit-тестів. Провайдер (Provider) автоматично зчитує цей контракт у своєму CI/CD конвеєрі та перевіряє, чи здатна його реалізація задовольнити всі вимоги Споживача без запуску реального мережевого середовища та без звернення до зовнішніх баз даних.

Цей довідник містить повну специфікацію формату контрактів Pact (v3/v4), алгоритми структурних матчрів, мапу сумісності API-змін, конфігурацію CLI-інструментів Pact Broker та шаблони інтеграції в автоматизовані ворота деплою.

---

## 1. Порівняльний аналіз підходів до перевірки API

Існує три основних архітектурних підходи до верифікації зворотної сумісності між сервісами. Кожен підхід має свою сферу застосування та обмеження.

```
       [ E2E Integration Tests ]      ──► Повільно, крихко, висока вартість інфраструктури
       [ OpenAPI / Schema Validation ] ──► Перевіряє лише схему, не перевіряє поведінку під станами
       [ Consumer-Driven Contracts ]   ──► Швидко, локально, перевіряє точні вимоги Споживача
```

### Матриця порівняння технологій перевірки API

| Критерій порівняння | E2E Інтеграційні тести | OpenAPI / Swagger Schema Validation | Consumer-Driven Contracts (Pact) |
| :--- | :--- | :--- | :--- |
| **Точка перевірки** | Спільне QA / Staging середовище | Статична аналізація документації | CI/CD конвеєр (Isolation Unit Stage) |
| **Швидкість прогону** | Десятки хвилин / години | Мілісекунди | Кілька секунд |
| **Хибні спрацьовування** | Високі (через мережу та стан БД) | Нуль | Нуль (детерміновані фікстури станів) |
| **Хто формує вимоги** | Інженери з якості (QA) | Автори Провайдера API | Споживачі API (Consumer-Driven) |
| **Перевірка неприйнятих полів** | Ні (ігнорує незнайомі виклики) | Ні (перевіряє лише оголошені поля) | Так (ловить видалення полів, які використовує клієнт) |

---

## 2. Еволюція та версії специфікації Pact (Pact Specification Versions)

Специфікація Pact развивалася від простих JSON-строк до універсального стандарту опису REST, gRPC та асинхронних подій.

| Версія специфікації | Ключові спроможності | Сфера застосування |
| :--- | :--- | :--- |
| **Pact v1 / v2** | Базові HTTP запити/відповіді, точна відповідність рядків та простих типів. | Ранні REST API, прості JSON-структури. |
| **Pact v3** | Запровадження динамічних структурних матчрів (`matchingRules`), підтримка Provider States із параметрами, підтримка **асинхронних повідомлень** (Message Pacts для Kafka, RabbitMQ). | Сучасні REST API, Event-Driven сервіси, черги повідомлень. |
| **Pact v4** | Об'єднання HTTP та Message контрактів в один специфікатор, підтримка gRPC/Protobuf через плагіни, розширені правила генераторів тестових даних (`generators`). | Поліглотні мікросервіси, gRPC, Protobuf, WebSockets. |

---

## 3. Повна структура файлу контракту (Pact v3/v4 Schema Reference)

Файл контракту — це JSON-документ, який створюється тестовим фреймворком Споживача. Він має бути самодостатнім, детермінованим та містити всі дані, необхідні Провайдеру для відтворення запиту.

### Опис верхньорівневих полів JSON-схеми

- `consumer`: Об'єкт з єдиним обов'язковим полем `name`. Визначає точну ідентифікувальну назву сервісу-споживача у реєстрі (наприклад, `"DigitalHomes-MonolithBackend"`).
- `provider`: Об'єкт з полем `name`. Визначає назву сервісу-провайдера (наприклад, `"Telemetry-Microservice"`).
- `interactions`: Масив об'єктів сценаріїв взаємодії. Кожен елемент описує один конкретний HTTP-запит або асинхронне повідомлення.
- `metadata`: Метадані про інструмент, що згенерував файл, та версію специфікації Pact.

### Деталізований еталонний приклад файлу контракту: `telemetry-consumer-telemetry-service.json`

```json
{
  "consumer": {
    "name": "DigitalHomes-MonolithBackend"
  },
  "provider": {
    "name": "Telemetry-Microservice"
  },
  "interactions": [
    {
      "description": "a request for historical device telemetry readings",
      "providerStates": [
        {
          "name": "device with ID 105 has historical telemetry readings",
          "params": {
            "deviceId": 105,
            "minReadingsCount": 1
          }
        }
      ],
      "request": {
        "method": "GET",
        "path": "/api/v1/devices/105/telemetry",
        "query": {
          "limit": ["50"],
          "from_timestamp": ["1700000000"]
        },
        "headers": {
          "Accept": "application/json",
          "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
      },
      "response": {
        "status": 200,
        "headers": {
          "Content-Type": "application/json; charset=utf-8"
        },
        "body": {
          "device_id": 105,
          "total_count": 1,
          "readings": [
            {
              "reading_id": "550e8400-e29b-41d4-a716-446655440000",
              "temperature": 22.5,
              "humidity": 48.2,
              "timestamp": 1700000050
            }
          ]
        },
        "matchingRules": {
          "body": {
            "$.device_id": {
              "combine": "AND",
              "matchers": [{ "match": "integer" }]
            },
            "$.total_count": {
              "combine": "AND",
              "matchers": [{ "match": "integer" }]
            },
            "$.readings": {
              "combine": "AND",
              "matchers": [{ "match": "type", "min": 1 }]
            },
            "$.readings[*].reading_id": {
              "combine": "AND",
              "matchers": [{ "match": "regex", "regex": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$" }]
            },
            "$.readings[*].temperature": {
              "combine": "AND",
              "matchers": [{ "match": "decimal" }]
            },
            "$.readings[*].humidity": {
              "combine": "AND",
              "matchers": [{ "match": "decimal" }]
            },
            "$.readings[*].timestamp": {
              "combine": "AND",
              "matchers": [{ "match": "integer" }]
            }
          },
          "header": {
            "Content-Type": {
              "combine": "AND",
              "matchers": [{ "match": "regex", "regex": "application/json.*" }]
            }
          }
        }
      }
    },
    {
      "description": "a request for non-existent device telemetry history",
      "providerStates": [
        {
          "name": "device with ID 99999 does not exist",
          "params": {
            "deviceId": 99999
          }
        }
      ],
      "request": {
        "method": "GET",
        "path": "/api/v1/devices/99999/telemetry"
      },
      "response": {
        "status": 404,
        "headers": {
          "Content-Type": "application/json"
        },
        "body": {
          "code": "DEVICE_NOT_FOUND",
          "message": "Device with ID 99999 was not found in registry"
        },
        "matchingRules": {
          "body": {
            "$.code": {
              "combine": "AND",
              "matchers": [{ "match": "type" }]
            },
            "$.message": {
              "combine": "AND",
              "matchers": [{ "match": "type" }]
            }
          }
        }
      }
    }
  ],
  "metadata": {
    "pactSpecification": {
      "version": "3.0.0"
    },
    "pactRust": {
      "version": "0.4.0"
    }
  }
}
```

---

## 4. Матчери типів та семантичні правила (Pact Matchers Reference)

Найважливіший принцип контрактних тестів: **Споживач перевіряє форму й типи полів, а не конкретні тестові значення**. Фіксація конкретного числа (наприклад `22.5`) робить тест крихким, адже реальний Провайдер може повернути `19.8`, що є повністю коректним із точки зору бізнес-логіки.

Для цього використовується селекція полів за допомогою JSONPath та правила `matchingRules`.

### Довідник правил відповідності Pact Matchers

| Назва матчера | JSON-конфігурація | Опис семантики та алгоритм перевірки |
| :--- | :--- | :--- |
| **Type Matcher** | `{"match": "type"}` | Перевіряє лише базовий тип даних (string, number, boolean). Значення може бути довільним. |
| **Integer Matcher** | `{"match": "integer"}` | Вимагає цілочисельне значення без десяткової крапки (`int32`, `int64`, `long`). |
| **Decimal Matcher** | `{"match": "decimal"}` | Вимагає число з плаваючою крапкою або фіксованою точністю (`float`, `double`, `decimal`). |
| **Regex Matcher** | `{"match": "regex", "regex": "..."}` | Перевіряє відповідність рядка регулярному виразу (наприклад UUID, ISO date, Email). |
| **Include Matcher** | `{"match": "include", "value": "..."}` | Перевіряє, що підрядок присутній у цільовому рядковому полі. |
| **Timestamp Matcher** | `{"match": "timestamp", "format": "..."}` | Перевіряє відповідність рядка конкретному формату дати/часу (наприклад `yyyy-MM-dd'T'HH:mm:ssZ`). |
| **Array Min/Max Matcher** | `{"match": "type", "min": 1}` | Перевіряє, що масив містить не менше `min` (і не більше `max`) елементів заданого типу. |
| **Nullability Matcher** | `{"match": "null"}` | Дозволяє полю набувати значення `null` або бути відсутнім без провалу тесту. |

---

## 5. Матриця сумісності API-змін (Breaking vs Non-Breaking API Changes)

Під час паралельної розробки моноліта й нового мікросервісу схеми даних неминуче змінюються. Інструментарій Pact оперує концепцією **закону Постеля (Robustness Principle)**: *"Будь обережним у тому, що надсилаєш, і ліберальним у тому, що приймаєш"*.

### Класифікація змін в API

```
                     Зміна в API Провайдера
                               │
       ┌───────────────────────┴───────────────────────┐
       ▼                                               ▼
NON-BREAKING CHANGES                            BREAKING CHANGES
(Сумісно з існуючими клієнтами)               (Злам клієнтських застосунків)
 ── Додавання нового поля у відповідь           ── Видалення поля з відповіді
 ── Додавання optional query-параметра          ── Зміна типу поля (number -> string)
 ── Зміна порядку елементів у масиві            ── Додавання mandatory поля у запит
 ── Додавання нового HTTP-ендпоінту              ── Зміна HTTP статус-коду (200 -> 201)
```

### Деталізований статус сумісності змін

| Конкретна зміна в контракті API | Вплив на Споживача | Статус сумісності | Результат CI/CD Gate |
| :--- | :--- | :--- | :--- |
| **Додавання полів у відповідь** | Споживач ігнорує нові поля при десеріалізації JSON | **NON-BREAKING** | **Деплой дозволено** |
| **Видалення поля з відповіді** | Споживач отримає `null` або `KeyError` при десеріалізації | **BREAKING** | **Деплой заблоковано** |
| **Зміна типу поля (`int` -> `string`)** | Помилка парсингу типів в об'єктно-орієнтованих мовах | **BREAKING** | **Деплой заблоковано** |
| **Перейменування поля (`temp` -> `temperature`)** | Рівносильно видаленню старого поля та додаванню нового | **BREAKING** | **Деплой заблоковано** |
| **Новий обов'язковий header у запиті** | Старий клієнт не надсилає header -> сервер поверне 400 Bad Request | **BREAKING** | **Деплой заблоковано** |
| **Новий опціональний query-параметр** | Сервер використовує дефолтне значення якщо параметр відсутній | **NON-BREAKING** | **Деплой дозволено** |
| **Зміна формату дати (Unix epoch -> ISO-8601)** | Регулярний вираз або парсер дати споживача впаде | **BREAKING** | **Деплой заблоковано** |

---

## 6. Патерн Provider State (Фікстури станів Провайдера)

Провайдер під час виконання контрактних тестів не повинен звертатися до реальної бази даних продакшну або зовнішніх залежностей. Для створення детермінованого середовища специфікація Pact передбачає **Provider States (Стани Провайдера)**.

Перед відтворенням кожного HTTP-запиту інструмент верифікації викликає спеціальний ендпоінт або кодовий хук провайдера, передаючи туди назву стану (`providerState`).

### Схема взаємодії верифікатора з Провайдером

```
 [ Pact Verifier CLI ] ─── (1. State Setup: "device 105 exists") ───► [ State Handler ]
         │                                                                   │
         │                                                        (Вставляє фікстуру в DB)
         │                                                                   │
         ├─── (2. Відтворює HTTP GET /api/v1/devices/105) ──────► [ Provider API ]
         │                                                                   │
         │                                                        (Повертає реальний JSON)
         │                                                                   │
         └─── (3. Порівнює отриманий JSON з правилами Pact) ◄───────────────┘
```

:::tabs
```c
/* C: Обробник станів Провайдера (Provider State Callbacks) */
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

typedef struct {
    const char *state_name;
    bool (*setup_func)(const char *params_json);
} provider_state_entry_t;

/* Хук підготовки даних для існуючого пристрою 105 */
static bool setup_device_105_exists(const char *params_json) {
    printf("[PACT STATE SETUP] Clearing test DB & inserting device_id=105 with telemetry...\n");
    /* Виконання SQL: INSERT INTO telemetry (device_id, temp) VALUES (105, 22.5); */
    return true;
}

/* Хук підготовки даних для відсутнього пристрою 99999 */
static bool setup_device_99999_absent(const char *params_json) {
    printf("[PACT STATE SETUP] Ensuring device_id=99999 is DELETED from test DB...\n");
    /* Виконання SQL: DELETE FROM telemetry WHERE device_id = 99999; */
    return true;
}

/* Таблиця реєстрації станів провайдера */
static provider_state_entry_t STATE_REGISTRY[] = {
    { "device with ID 105 has historical telemetry readings", setup_device_105_exists },
    { "device with ID 99999 does not exist", setup_device_99999_absent }
};

/* Головний обробник State Setup HTTP запиту від pact-verifier */
bool handle_pact_state_setup(const char *requested_state, const char *params_json) {
    size_t count = sizeof(STATE_REGISTRY) / sizeof(STATE_REGISTRY[0]);
    for (size_t i = 0; i < count; i++) {
        if (strcmp(STATE_REGISTRY[i].state_name, requested_state) == 0) {
            return STATE_REGISTRY[i].setup_func(params_json);
        }
    }
    printf("[PACT STATE ERROR] Unknown provider state requested: %s\n", requested_state);
    return false;
}
```
```cpp
// C++17: Обробник станів Провайдера (Provider States) з використанням std::unordered_map та std::function
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <functional>

class ProviderStateRegistry {
public:
    using StateSetupHandler = std::function<bool(std::string_view params_json)>;

    void register_state(std::string state_name, StateSetupHandler handler) {
        handlers_[std::move(state_name)] = std::move(handler);
    }

    bool handle_state_setup(std::string_view requested_state, std::string_view params_json) const {
        auto it = handlers_.find(std::string(requested_state));
        if (it != handlers_.end()) {
            return it->second(params_json);
        }
        std::cerr << "[PACT STATE ERROR] Unknown provider state requested: " << requested_state << "\n";
        return false;
    }

private:
    std::unordered_map<std::string, StateSetupHandler> handlers_;
};

// Приклад підключення станів у контролері Провайдера
inline void register_telemetry_provider_states(ProviderStateRegistry& registry) {
    registry.register_state("device with ID 105 has historical telemetry readings", [](std::string_view params) {
        std::cout << "[PACT STATE SETUP] Seeding DB: INSERT INTO telemetry (device_id, temp) VALUES (105, 22.5);\n";
        return true;
    });

    registry.register_state("device with ID 99999 does not exist", [](std::string_view params) {
        std::cout << "[PACT STATE SETUP] Seeding DB: DELETE FROM telemetry WHERE device_id = 99999;\n";
        return true;
    });
}
```
:::

---

## 7. Інтеграція в CI/CD Конвеєр та команда `can-i-deploy`

Центральним компонентом управління контрактами у компанії є **Pact Broker** — спеціалізований реєстр, який зберігає версії контрактів, результати їх перевірок провайдерами та будує матрицю сумісності сервісів (Matrix of Compatibility).

### Повний сценарій CI/CD конвеєра

```bash
#!/usr/bin/env bash
# ==============================================================================
# Сценарій автоматичної перевірки контрактів у CI/CD пайплайні
# ==============================================================================
set -euo pipefail

BROKER_URL="http://pact-broker.internal.net"
CONSUMER_NAME="DigitalHomes-MonolithBackend"
PROVIDER_NAME="Telemetry-Microservice"
GIT_COMMIT=$(git rev-parse HEAD)
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "=== 1. ЗАПУСК КЛІЄНТСЬКИХ ТЕСТІВ ТА ГЕНЕРАЦІЯ КОНТРАКТІВ ==="
# Виконання unit-тестів моноліта, які генерують файли в ./pacts/
npm test -- --grep "PactContractTests"

echo "=== 2. ПУБЛІКАЦІЯ КОНТРАКТУ В PACT BROKER ==="
pact-broker publish ./pacts \
  --consumer-app-version="${GIT_COMMIT}" \
  --branch="${GIT_BRANCH}" \
  --broker-base-url="${BROKER_URL}"

echo "=== 3. ПЕРЕВІРКА МАТРИЦІ СУМІСНОСТІ (CAN-I-DEPLOY) ==="
# Команда запитує в Broker: "Чи безпечно розгортати цю версію моноліта на Production?"
# Broker перевіряє, чи верифікував Провайдер, розгорнутий на Production, саме цей коміт.
if pact-broker can-i-deploy \
    --pacticipant "${CONSUMER_NAME}" \
    --version "${GIT_COMMIT}" \
    --to-environment production \
    --broker-base-url="${BROKER_URL}"; then
  echo "[SUCCESS] Матриця сумісна! Розпочинаємо розгортання на Production."
else
  echo "[FAILURE] Злам сумісності контрактів! Деплой заблоковано."
  exit 1
fi
```

### Довідник кодів завершення CLI `can-i-deploy`

| Код завершення | Статус | Інтерпретація результату | Необхідна дія розробника |
| :--- | :--- | :--- | :--- |
| **`0`** | `SUCCESS` | Повна сумісність. Провайдер продакшну підтвердив контракт. | Продовжити деплой у продакшн середовище. |
| **`1`** | `FAILED` | Виявлено несумісність або провал тесту верифікації провайдером. | Зупинити деплой, виправити код API або оновити Споживач. |
| **`2`** | `UNKNOWN` | Провайдер ще не запускав верифікацію для цієї нової версії контракту. | Запустити верифікаційний пайплайн Провайдера в CI. |

---

## 8. Чекліст впровадження контрактного тестування при розпилі моноліта

- [ ] **Крок 1: Ізоляція клієнтських викликів.** Виділити всі вихідні HTTP/gRPC виклики з моноліта до виділеного сервісу в окремі клієнтські модулі.
- [ ] **Крок 2: Покриття Pact-тестами.** Написати unit-тести для клієнтських модулів із використанням фреймворку Pact, зафіксувавши всі успішні та помилкові сценарії.
- [ ] **Крок 3: Розгортання Pact Broker.** Розгорнути Pact Broker (або підключити PactFlow SaaS) та налаштувати ролі доступу для CI/CD засобів.
- [ ] **Крок 4: Автоматизація публікації.** Додати крок `pact-broker publish` у CI пайплайн моноліта при кожному злитті в головну гілку.
- [ ] **Крок 5: Верифікація Провайдера.** У коді нового мікросервісу налаштувати запуск `pact-provider-verifier` із реалізацією `Provider States` під час збірки.
- [ ] **Крок 6: Встановлення воріт деплою (Deploy Gates).** Додати обов'язкову перевірку `pact-broker can-i-deploy --to-environment production` перед початком канарейкового або повного розгортання будь-якого із сервісів.
