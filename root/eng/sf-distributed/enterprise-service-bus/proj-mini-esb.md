# ⚙️ Реалізація конвеєра посередництва: нормалізація, маршрутизація та трансформація

Ця вставка розкриває внутрішню інженерну анатомію інтеграційної шини: від перехоплення сирого вхідного запиту та загортання його в нормалізований конверт до ланцюгової фільтрації, контентної маршрутизації, трансляції схем даних і ізоляції збоїв у мертву чергу (Dead-Letter Queue).

## Архітектура міні-рушія посередництва

В основі будь-якого посередника повідомлень (Message Broker, ESB або сучасного API Gateway) лежить концепція **обміну повідомленнями** (англ. *Message Exchange*). На відміну від прямого виклику функції або RPC, де клієнт жорстко зв'язаний із сигнатурою сервера, посередник розриває цей зв'язок на часовому, протокольному та семантичному рівнях.

Конвеєр посередництва виконує роль конвеєрної стрічки, якою рухається конверт обміну. Обробка складається з п'яти послідовних фаз:

1. **Нормалізація (Normalization)**: перетворення вхідного повідомлення, отриманого через специфічний транспортний протокол (HTTP, AMQP, TCP-сокет або чергу повідомлень), у внутрішній протокольно-нейтральний конверт — `NormalizedMessage`. Конверт чітко відокремлює метадані (заголовки, ідентифікатори, мітки часу) від основного корисного навантаження (payload).
2. **Перехоплення та фільтрація (Interception & Filtering)**: попередня валідація прав доступу, перевірка криптографічних підписів або токенів, відсікання дублікатів за ідентифікатором повідомлення та фіксація вхідної події в журналі аудиту.
3. **Маршрутизація за змістом (Content-Based Routing — CBR)**: динамічне визначення цільового сервісу-одержувача. Замість статичної IP-адреси конвеєр аналізує атрибути заголовків або поля тіла повідомлення, обираючи кінцевий маршрут на основі таблиці правил.
4. **Трансляція схеми (Schema Translation & Enrichment)**: адаптація внутрішньої канонічної моделі до формату, якого очікує цільова система (наприклад, перетворення загального замовлення у специфічний JSON чи XML платіжного шлюзу).
5. **Обробка винятків і мертва черга (Dead-Letter Channel)**: безпечне перехоплення будь-якого збою на будь-якому кроці конвеєра, формування конверта помилки та збереження проблемного повідомлення для ручного аналізу або відкладеного повтору без зупинки роботи системи.

## Структури даних і метадані нормалізованого конверта

Щоб конвеєр працював передбачувано, структура `NormalizedMessage` повинна підтримувати ключові заголовки розподіленого контексту:
- `Message-ID`: унікальний ідентифікатор конкретного фізичного повідомлення.
- `Correlation-ID`: наскрізний ідентифікатор бізнес-транзакції, що зв'язує запит і відповідь або ланцюжок асинхронних подій через десятки проміжних сервісів.
- `Causation-ID`: ідентифікатор повідомлення, яке безпосередньо спричинило появу поточного повідомлення (необхідний для побудови дерева причинно-наслідкових зв'язків у складних оркестраціях).
- `Timestamp`: час входження повідомлення в інтеграційний контур для розрахунку часу перебування в системі (Latency SLA).

Контекст `Exchange` містить як вхідне повідомлення (`in_msg`), так і результат обробки (`out_msg`), цільову адресу (`target_endpoint`) та стан помилки (`is_fault`, `fault_reason`). Це дозволяє кожній стадії конвеєра або модифікувати повідомлення на місці, або створювати нову версію, не руйнуючи початковий контекст відправника.

## Робочий код конвеєра: C, C++ та TypeScript

Нижче наведено повну самодостатню реалізацію міні-шини трьома мовами. Кожна реалізація дотримується суворих ідіом своєї платформи:
- **C99**: детерміноване керування пам'яттю, фіксовані буфери для запобігання фрагментації купи на гарячому шляху, таблиці покажчиків на функції для поліморфізму стадій.
- **C++20**: суворе слідування RAII, безпечні представлення `std::string_view` для уникнення зайвих алокацій рядків, розумні вказівники `std::unique_ptr` для керування життєвим циклом стадій, строго типізовані `enum class` та форматування рядків через `std::format`.
- **TypeScript**: сучасна асинхронна декларативна композиція конвеєра з використанням типізованих інтерфейсів та промісів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_HEADERS 16
#define KEY_LEN 32
#define VAL_LEN 64
#define PAYLOAD_MAX 512
#define MAX_STAGES 8

/* Статуси виконання стадії конвеєра */
typedef enum {
    STAGE_OK = 0,
    STAGE_FILTERED = 1,
    STAGE_ERROR = 2
} StageStatus;

/* Метадані заголовка */
typedef struct {
    char key[KEY_LEN];
    char value[VAL_LEN];
} Header;

/* Нормалізований конверт повідомлення */
typedef struct {
    char message_id[KEY_LEN];
    char correlation_id[KEY_LEN];
    Header headers[MAX_HEADERS];
    size_t header_count;
    char payload[PAYLOAD_MAX];
    size_t payload_len;
} NormalizedMessage;

/* Контекст обміну повідомленням (Exchange) */
typedef struct {
    NormalizedMessage in_msg;
    NormalizedMessage out_msg;
    char target_endpoint[VAL_LEN];
    char fault_reason[VAL_LEN];
    bool is_fault;
} Exchange;

/* Попереднє оголошення інтерфейсу стадії */
typedef struct PipelineStage PipelineStage;
typedef StageStatus (*StageFunc)(PipelineStage *self, Exchange *ex);

struct PipelineStage {
    const char *name;
    StageFunc process;
    void *context;
};

/* Допоміжні функції роботи з заголовками */
void set_header(NormalizedMessage *msg, const char *key, const char *val) {
    if (msg->header_count < MAX_HEADERS) {
        strncpy(msg->headers[msg->header_count].key, key, KEY_LEN - 1);
        msg->headers[msg->header_count].key[KEY_LEN - 1] = '\0';
        strncpy(msg->headers[msg->header_count].value, val, VAL_LEN - 1);
        msg->headers[msg->header_count].value[VAL_LEN - 1] = '\0';
        msg->header_count++;
    }
}

const char* get_header(const NormalizedMessage *msg, const char *key) {
    for (size_t i = 0; i < msg->header_count; i++) {
        if (strcmp(msg->headers[i].key, key) == 0) {
            return msg->headers[i].value;
        }
    }
    return NULL;
}

/* 1. Стадія перевірки автентифікації */
StageStatus auth_stage_process(PipelineStage *self, Exchange *ex) {
    (void)self;
    const char *token = get_header(&ex->in_msg, "X-Auth-Token");
    if (!token || strcmp(token, "secret-token-123") != 0) {
        strncpy(ex->fault_reason, "AUTH_REJECTED: Invalid or missing token", VAL_LEN - 1);
        ex->is_fault = true;
        return STAGE_ERROR;
    }
    return STAGE_OK;
}

/* 2. Стадія маршрутизації за змістом (CBR) */
StageStatus routing_stage_process(PipelineStage *self, Exchange *ex) {
    (void)self;
    const char *type = get_header(&ex->in_msg, "X-Message-Type");
    if (!type) {
        strncpy(ex->fault_reason, "ROUTING_FAILED: Missing message type", VAL_LEN - 1);
        ex->is_fault = true;
        return STAGE_ERROR;
    }

    if (strcmp(type, "ORDER_PAYMENT") == 0) {
        strncpy(ex->target_endpoint, "billing.service.v1", VAL_LEN - 1);
    } else if (strcmp(type, "INVENTORY_SYNC") == 0) {
        strncpy(ex->target_endpoint, "warehouse.service.v2", VAL_LEN - 1);
    } else {
        strncpy(ex->fault_reason, "ROUTING_FAILED: Unknown route", VAL_LEN - 1);
        ex->is_fault = true;
        return STAGE_ERROR;
    }
    return STAGE_OK;
}

/* 3. Стадія трансформації канонічного формату */
StageStatus transform_stage_process(PipelineStage *self, Exchange *ex) {
    (void)self;
    memcpy(&ex->out_msg, &ex->in_msg, sizeof(NormalizedMessage));
    
    char formatted_payload[PAYLOAD_MAX];
    snprintf(formatted_payload, sizeof(formatted_payload),
             "{\"target\":\"%s\",\"id\":\"%s\",\"data\":\"%s\"}",
             ex->target_endpoint, ex->in_msg.message_id, ex->in_msg.payload);

    strncpy(ex->out_msg.payload, formatted_payload, PAYLOAD_MAX - 1);
    ex->out_msg.payload[PAYLOAD_MAX - 1] = '\0';
    ex->out_msg.payload_len = strlen(ex->out_msg.payload);
    set_header(&ex->out_msg, "Content-Type", "application/json");
    return STAGE_OK;
}

/* Рушій конвеєра шини */
typedef struct {
    PipelineStage stages[MAX_STAGES];
    size_t stage_count;
} BusPipeline;

void bus_add_stage(BusPipeline *bus, const char *name, StageFunc func) {
    if (bus->stage_count < MAX_STAGES) {
        bus->stages[bus->stage_count].name = name;
        bus->stages[bus->stage_count].process = func;
        bus->stages[bus->stage_count].context = NULL;
        bus->stage_count++;
    }
}

void bus_execute(BusPipeline *bus, Exchange *ex) {
    printf("[BUS] Початок обробки повідомлення ID=%s\n", ex->in_msg.message_id);
    for (size_t i = 0; i < bus->stage_count; i++) {
        PipelineStage *stage = &bus->stages[i];
        StageStatus st = stage->process(stage, ex);
        if (st == STAGE_ERROR) {
            printf("[BUS] Збій на стадії '%s': %s -> Відправка в DLQ\n",
                   stage->name, ex->fault_reason);
            return;
        } else if (st == STAGE_FILTERED) {
            printf("[BUS] Повідомлення відфільтровано на стадії '%s'\n", stage->name);
            return;
        }
    }
    printf("[BUS] Успішна доставка до '%s': payload=%s\n",
           ex->target_endpoint, ex->out_msg.payload);
}

int main(void) {
    BusPipeline bus = {0};
    bus_add_stage(&bus, "AuthValidator", auth_stage_process);
    bus_add_stage(&bus, "ContentRouter", routing_stage_process);
    bus_add_stage(&bus, "JsonTransformer", transform_stage_process);

    /* Тест 1: Валідне платіжне повідомлення */
    Exchange ex1 = {0};
    strncpy(ex1.in_msg.message_id, "MSG-001", KEY_LEN - 1);
    set_header(&ex1.in_msg, "X-Auth-Token", "secret-token-123");
    set_header(&ex1.in_msg, "X-Message-Type", "ORDER_PAYMENT");
    strncpy(ex1.in_msg.payload, "amount=150.00;currency=USD", PAYLOAD_MAX - 1);
    ex1.in_msg.payload_len = strlen(ex1.in_msg.payload);
    bus_execute(&bus, &ex1);

    /* Тест 2: Повідомлення без валідного токена */
    Exchange ex2 = {0};
    strncpy(ex2.in_msg.message_id, "MSG-002", KEY_LEN - 1);
    set_header(&ex2.in_msg, "X-Auth-Token", "wrong-token");
    set_header(&ex2.in_msg, "X-Message-Type", "ORDER_PAYMENT");
    strncpy(ex2.in_msg.payload, "amount=500.00", PAYLOAD_MAX - 1);
    bus_execute(&bus, &ex2);

    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>
#include <memory>
#include <format>

/* Статуси обробки повідомлення */
enum class StageStatus {
    Continue,
    Filtered,
    Fault
};

/* Нормалізований конверт повідомлення */
struct NormalizedMessage {
    std::string message_id;
    std::string correlation_id;
    std::unordered_map<std::string, std::string> headers;
    std::string payload;

    [[nodiscard]] std::string_view get_header(std::string_view key) const {
        if (auto it = headers.find(std::string(key)); it != headers.end()) {
            return it->second;
        }
        return {};
    }

    void set_header(std::string key, std::string value) {
        headers.insert_or_assign(std::move(key), std::move(value));
    }
};

/* Контекст обміну повідомленнями (Exchange) */
struct Exchange {
    NormalizedMessage request;
    NormalizedMessage response;
    std::string target_endpoint;
    std::string fault_reason;
    bool is_fault{false};
};

/* Інтерфейс стадії конвеєра */
class IPipelineStage {
public:
    virtual ~IPipelineStage() = default;
    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
    virtual StageStatus process(Exchange& exchange) = 0;
};

/* 1. Стадія автентифікації */
class AuthValidatorStage final : public IPipelineStage {
public:
    [[nodiscard]] std::string_view name() const noexcept override {
        return "AuthValidator";
    }

    StageStatus process(Exchange& exchange) override {
        auto token = exchange.request.get_header("X-Auth-Token");
        if (token != "secret-token-123") {
            exchange.fault_reason = "AUTH_REJECTED: Invalid or missing token";
            exchange.is_fault = true;
            return StageStatus::Fault;
        }
        return StageStatus::Continue;
    }
};

/* 2. Стадія маршрутизації за змістом */
class ContentBasedRouterStage final : public IPipelineStage {
public:
    [[nodiscard]] std::string_view name() const noexcept override {
        return "ContentBasedRouter";
    }

    StageStatus process(Exchange& exchange) override {
        auto type = exchange.request.get_header("X-Message-Type");
        if (type == "ORDER_PAYMENT") {
            exchange.target_endpoint = "billing.service.v1";
        } else if (type == "INVENTORY_SYNC") {
            exchange.target_endpoint = "warehouse.service.v2";
        } else {
            exchange.fault_reason = "ROUTING_FAILED: Unknown message type";
            exchange.is_fault = true;
            return StageStatus::Fault;
        }
        return StageStatus::Continue;
    }
};

/* 3. Стадія трансформації канонічної моделі */
class JsonTransformerStage final : public IPipelineStage {
public:
    [[nodiscard]] std::string_view name() const noexcept override {
        return "JsonTransformer";
    }

    StageStatus process(Exchange& exchange) override {
        exchange.response = exchange.request;
        exchange.response.payload = std::format(
            "{{\"target\":\"{}\",\"id\":\"{}\",\"data\":\"{}\"}}",
            exchange.target_endpoint,
            exchange.request.message_id,
            exchange.request.payload
        );
        exchange.response.set_header("Content-Type", "application/json");
        return StageStatus::Continue;
    }
};

/* Ядро інтеграційного конвеєра (ESB Core) */
class MediationPipeline {
public:
    void add_stage(std::unique_ptr<IPipelineStage> stage) {
        stages_.push_back(std::move(stage));
    }

    void dispatch(Exchange& exchange) const {
        std::cout << std::format("[BUS-CPP] Обробка ID={}\n", exchange.request.message_id);
        for (const auto& stage : stages_) {
            StageStatus status = stage->process(exchange);
            if (status == StageStatus::Fault) {
                std::cout << std::format("[BUS-CPP] Збій на '{}': {} -> Направлено в DLQ\n",
                                         stage->name(), exchange.fault_reason);
                return;
            }
            if (status == StageStatus::Filtered) {
                std::cout << std::format("[BUS-CPP] Повідомлення відфільтровано на '{}'\n", stage->name());
                return;
            }
        }
        std::cout << std::format("[BUS-CPP] Успіх -> Ендпоінт '{}': payload={}\n",
                                 exchange.target_endpoint, exchange.response.payload);
    }

private:
    std::vector<std::unique_ptr<IPipelineStage>> stages_;
};

int main() {
    MediationPipeline bus;
    bus.add_stage(std::make_unique<AuthValidatorStage>());
    bus.add_stage(std::make_unique<ContentBasedRouterStage>());
    bus.add_stage(std::make_unique<JsonTransformerStage>());

    /* Тест 1: Успішний платіж */
    Exchange ex1;
    ex1.request.message_id = "CPP-MSG-101";
    ex1.request.set_header("X-Auth-Token", "secret-token-123");
    ex1.request.set_header("X-Message-Type", "ORDER_PAYMENT");
    ex1.request.payload = "order_id=4590;total=89.50";
    bus.dispatch(ex1);

    /* Тест 2: Відмова в автентифікації */
    Exchange ex2;
    ex2.request.message_id = "CPP-MSG-102";
    ex2.request.set_header("X-Auth-Token", "bad-token");
    ex2.request.set_header("X-Message-Type", "ORDER_PAYMENT");
    ex2.request.payload = "order_id=9999";
    bus.dispatch(ex2);

    return 0;
}
```
```ts
interface NormalizedMessage {
  messageId: string;
  correlationId: string;
  headers: Map<string, string>;
  payload: string;
}

interface Exchange {
  request: NormalizedMessage;
  response?: NormalizedMessage;
  targetEndpoint?: string;
  faultReason?: string;
  isFault: boolean;
}

type StageResult = 'CONTINUE' | 'FILTERED' | 'FAULT';

interface PipelineStage {
  name: string;
  process(exchange: Exchange): Promise<StageResult>;
}

class AuthValidatorStage implements PipelineStage {
  name = 'AuthValidator';
  async process(exchange: Exchange): Promise<StageResult> {
    const token = exchange.request.headers.get('X-Auth-Token');
    if (token !== 'secret-token-123') {
      exchange.faultReason = 'AUTH_REJECTED: Invalid or missing token';
      exchange.isFault = true;
      return 'FAULT';
    }
    return 'CONTINUE';
  }
}

class ContentBasedRouterStage implements PipelineStage {
  name = 'ContentBasedRouter';
  async process(exchange: Exchange): Promise<StageResult> {
    const type = exchange.request.headers.get('X-Message-Type');
    if (type === 'ORDER_PAYMENT') {
      exchange.targetEndpoint = 'billing.service.v1';
    } else if (type === 'INVENTORY_SYNC') {
      exchange.targetEndpoint = 'warehouse.service.v2';
    } else {
      exchange.faultReason = 'ROUTING_FAILED: Unknown message type';
      exchange.isFault = true;
      return 'FAULT';
    }
    return 'CONTINUE';
  }
}

class JsonTransformerStage implements PipelineStage {
  name = 'JsonTransformer';
  async process(exchange: Exchange): Promise<StageResult> {
    exchange.response = {
      ...exchange.request,
      headers: new Map(exchange.request.headers),
      payload: JSON.stringify({
        target: exchange.targetEndpoint,
        id: exchange.request.messageId,
        data: exchange.request.payload
      })
    };
    exchange.response.headers.set('Content-Type', 'application/json');
    return 'CONTINUE';
  }
}

class BusPipeline {
  private stages: PipelineStage[] = [];

  addStage(stage: PipelineStage): this {
    this.stages.push(stage);
    return this;
  }

  async dispatch(exchange: Exchange): Promise<void> {
    console.log(`[BUS-TS] Обробка ID=${exchange.request.messageId}`);
    for (const stage of this.stages) {
      const result = await stage.process(exchange);
      if (result === 'FAULT') {
        console.log(`[BUS-TS] Збій на '${stage.name}': ${exchange.faultReason} -> DLQ`);
        return;
      }
      if (result === 'FILTERED') {
        console.log(`[BUS-TS] Відфільтровано на '${stage.name}'`);
        return;
      }
    }
    console.log(`[BUS-TS] Доставлено до '${exchange.targetEndpoint}': ${exchange.response?.payload}`);
  }
}
```
:::

## Покроковий розбір стадій конвеєра

Розгляньмо, як кожен компонент реалізує ключові принципи інтеграційного посередництва:

### 1. Стадія фільтрації та автентифікації (`AuthValidator`)
Цей компонент є першим рубежем захисту інтеграційного периметра. Замість того, щоб кожен внутрішній бекенд-сервіс самостійно реалізовував перевірку безпеки, конвеєр централізовано перевіряє заголовок `X-Auth-Token`.

Якщо токен відсутній або не збігається з очікуваним значенням, стадія повертає `STAGE_ERROR` (у C) або `StageStatus::Fault` (у C++). Конвеєр негайно припиняє передачу повідомлення наступним стадіям, записує причину відхилення в поле `fault_reason` і спрямовує обмін до маршруту обробки збоїв.

### 2. Стадія маршрутизації за змістом (`ContentBasedRouter`)
Цей крок демонструє ключову перевагу шини перед статичними зв'язками. Замість того, щоб клієнт знав точну мережеву адресу платіжного сервісу (`billing.service.v1`) чи складу (`warehouse.service.v2`), клієнт вказує лише абстрактний тип операції в заголовку `X-Message-Type`.

Маршрутизатор інспектує заголовок і динамічно встановлює `target_endpoint`. Якщо надходить невідомий тип повідомлення, маршрутизатор сигналізує про помилку конфігурації маршруту, ізолюючи систему від непередбачених запитів.

### 3. Стадія канонічної трансформації (`JsonTransformer`)
Більшість інтегрованих систем мають різні вимоги до формату даних. Вхідний запит надходить у простому рядковому вигляді `key=value`, тоді як кінцевий сервіс очікує структурований JSON-документ з метаданими та ідентифікатором замовлення. 

Стадія трансформації зчитує поля нормалізованого конверта і формує результуючий вихідний пакет `out_msg`, одночасно виставляючи стандартний заголовок `Content-Type: application/json`.

## Патерни інтеграції підприємства (EIP) у коді конвеєра

Продемонстрований конвеєр є практичним втіленням класичних патернів Enterprise Integration Patterns:

- **Нормалізатор (Normalizer)**: перетворює різнорідні формати вхідних повідомлень на єдину канонічну структуру `NormalizedMessage`. Це усуває необхідність писати `N*(N-1)/2` парних конвертерів між системами.
- **Маршрутизатор за змістом (Content-Based Router)**: приймає рішення про напрямок руху повідомлення на основі його змісту, а не на основі фіксованої мережевої адреси.
- **Транслятор повідомлення (Message Translator)**: змінює структуру або схему даних під час проходження між двома несумісними протоколами.
- **Канал мертвої черги (Dead-Letter Channel)**: гарантує, що повідомлення, які не вдалося обробити, не блокують чергу і не втрачаються, а зберігаються для подальшого аналізу.
- **Перехоплювач (Message Interceptor)**: дозволяє прозоро вбудовувати наскрізну функціональність (аудит, безпеку, метрики) без зміни бізнес-логіки обробників.

## Ідемпотентний прийом та усунення дублікатів (Idempotent Consumer)

У розподілених мережах гарантія доставки точно-один-раз (Exactly-Once) є теоретично неможливою без компромісів у доступності або координації. Більшість черг повідомлень забезпечують гарантію **щонайменше один раз (At-Least-Once)**. Це означає, що у разі тимчасового обриву мережі в момент передачі підтвердження (ACK) відправник надішле копію повідомлення повторно.

Якщо конвеєр двічі спише кошти з банківської картки через отримання дубліката, система зазнає фінансових збитків. Конвеєр посередництва вбудовує патерн **ідемпотентного споживача (Idempotent Consumer)**:
1. При вході повідомлення конвеєр витягує унікальний `Message-ID` або бізнес-ключ ідемпотентності (`Idempotency-Key`).
2. Здійснюється швидка атомарна перевірка в розподіленому сховищі ключ-значення (наприклад, Redis з операцією `SET NX EX 86400` або RocksDB).
3. Якщо ключ уже існує, повідомлення негайно позначається як дублікат, стадії модифікації стану пропускаються, а клієнту повертається збережений попередній результат обробки без повторного виконання бізнес-операції.

## Декларативний синтаксис конфігурації маршрутів (DSL)

У реальних виробничих інтеграційних платформах (наприклад, Apache Camel або Spring Integration) розробники рідко компонують конвеєри ручним викликом функцій у коді `main()`. Замість цього використовують декларативний Fluent API або конфігураційні схеми:

```java
// Приклад декларативного опису маршруту в Apache Camel
from("kafka:incoming_orders")
    .routeId("order-mediation-pipeline")
    .process(new AuthTokenValidator())
    .idempotentConsumer(header("Message-ID"), redisIdempotentRepository)
    .choice()
        .when(header("X-Message-Type").isEqualTo("ORDER_PAYMENT"))
            .process(new JsonOrderTransformer())
            .to("http://billing-service.internal/v1/charge")
        .when(header("X-Message-Type").isEqualTo("INVENTORY_SYNC"))
            .to("amqp:queue:warehouse_updates")
        .otherwise()
            .to("jms:queue:dead_letter_queue");
```

Декларативне проектування відокремлює топологію маршрутизації від деталей виконання (потоків, буферів, сокетів). Це дозволяє адміністраторам та інтеграторам змінювати правила перенаправлення трафіку та адреси сервісів динамічно без перекомпіляції основного виконуваного файлу шини.

## Наскрізне трасування та контекст кореляції (Distributed Tracing)

У розподілених середовищах одне клієнтське замовлення може ініціювати десятки внутрішніх викликів між різними сервісами через шину. Без єдиного контексту трасування з'ясувати причину помилки чи повільної відповіді практично неможливо.

Конвеєр посередництва підтримує поширення контексту за стандартом W3C Trace Context через спеціальні метадані:
- `traceparent`: містить версію протоколу, 16-байтний глобальний ідентифікатор траси (`Trace-ID`), 8-байтний ідентифікатор батьківського спана (`Parent-Span-ID`) та бітові прапорці трекінгу.
- `tracestate`: список пар ключ-значення для передачі специфічних метаданих постачальників систем моніторингу (Dynatrace, Jaeger, Datadog).

Під час входу повідомлення конвеєр зчитує `traceparent`, фіксує початок обробки вхідного адаптера і генерує новий дочірній спан для кожної стадії конвеєра. При передачі повідомлення у вихідний адаптер конвеєр оновлює поле `Parent-Span-ID`, забезпечуючи безперервний ланцюг простеження графа викликів у системі розподіленого аудиту.

## Регулювання швидкості та зворотний тиск (Backpressure)

Нерівномірність навантаження є однією з головних причин падіння інтеграційних систем. Якщо вхідний шлюз приймає 50 000 HTTP-запитів на секунду, а цільова реляційна база даних або мейнфрейм здатні опрацьовувати лише 2 000 транзакцій на секунду, неконтрольована буферизація в оперативній пам'яті швидко призведе до падіння процесу з помилкою `OutOfMemoryError`.

Конвеєр посередництва застосовує кілька рівнів зворотного тиску (англ. *Backpressure*):
1. **Кредитна модель AMQP / Reactive Streams**: одержувач явно видає брокеру дозвіл на доставку фіксованої кількості повідомлень (Credits). Брокер не надсилає наступний пакет, доки попередні не будуть підтверджені.
2. **Дискове буферизування та Watermark-ліміти**: коли розмір вхідної черги перевищує порогове значення (High Watermark), конвеєр тимчасово призупиняє читання з TCP-сокетів або повертає клієнтам HTTP 429 Too Many Requests, даючи споживачам час розвантажити чергу до досягнення безпечного рівня (Low Watermark).

## Інженерний аналіз: підводні камені та оптимізація продуктивності

Практична експлуатація подібних конвеєрів у високонавантажених корпоративних системах відкриває низку неочевидних архітектурних пасток, з якими стикаються інженери розподілених систем:

### 1. Потоковий розбір (Streaming) проти повної матеріалізації DOM
У наведеному міні-рушії заголовки та корисне навантаження представлені рядками у пам'яті. У класичних корпоративних ESB тіло повідомлення часто являло собою XML-документ розміром від кількох сотень кілобайтів до десятків мегабайтів. 

Якщо кожна стадія конвеєра (маршрутизатор XPath, валідатор XSD, транслятор XSLT) здійснює повний парсинг повідомлення у важке DOM-дерево в оперативній пам'яті:
- Обсяг пам'яті, зайнятий одним повідомленням, збільшується у 5–10 разів порівняно з сирим розміром байтів у мережевому буфері.
- Збирач сміття (Garbage Collector) у керованих середовищах зазнає колосального навантаження, що призводить до тривалих пауз Stop-the-World і різкого зростання хвостової затримки (p99 latency).

**Інженерне рішення**: Сучасні конвеєри використовують **потокову обробку (Streaming / StAX / SAX)** або поверхневе декодування лише необхідних полів заголовка (Zero-copy header inspection), не торкаючись основного тіла корисного навантаження аж до моменту фінальної доставки або реальної потреби в трансформації.

### 2. Ізоляція пулів потоків (Bulkhead) між адаптерами
Коли шина взаємодіє з повільною або нестабільною застарілою системою (наприклад, банківським мейнфреймом, час відгуку якого коливається від 500 мс до 10 секунд), синхронне очікування виклику в загальному пулі потоків конвеєра призводить до ефекту вичерпання ресурсів (Thread Starvation). 

Якщо всі робочі потоки заблоковані очікуванням мейнфрейма, нові повідомлення для швидких внутрішніх мікросервісів (які могли б обробитися за 2 мс) опиняються заблокованими у вхідній черзі.

**Інженерне рішення**: Застосування патерну [перебірок (Bulkhead)](root:sf-distributed/bulkhead-isolation) — виділення окремих ізольованих черг і пулів потоків для кожного вихідного адаптера з жорсткими лімітами конкурентності та неблокуючим асинхронним вводом-виводом (Non-blocking I/O).

### 3. Гарантії доставки та транзакційні межі (Dead-Letter Channel)
Якщо стадія трансляції зазнає краху (наприклад, некоректний формат числа в полі суми платежу), вхідне повідомлення не повинно безслідно зникати. Інтеграційний конвеєр повинен гарантувати виконання трьох кроків:
1. Зафіксувати стан збою у внутрішній структурі `Exchange`.
2. Направити проблемне повідомлення до мертвої черги (Dead-Letter Queue — DLQ) разом із повним дампом вхідних байтів, міткою часу та стеком викликів помилки.
3. Підтвердити прийом вхідному брокеру (ACK), щоб запобігти безкінечним циклам повторів (Poison Message loops), коли одне пошкоджене повідомлення нескінченно перечитується і перезавантажує сервіс.

### 4. Оркестрація проти хореографії та компенсаційні транзакції
Спроби виконувати важкі розподілені транзакції (Two-Phase Commit, XA) через конвеєр централізованої шини призводять до жорсткого блокування таблиць бази даних та катастрофічного падіння пропускної здатності при будь-яких мережевих коливаннях.

На практиці розподілені операції реалізують через патерн [Сага (Saga)](root:sf-distributed/saga-pattern) — ланцюжок незалежних локальних транзакцій, де кожна дія має чітко визначену компенсуючу операцію (наприклад, повернення зарезервованих коштів у разі відмови складу під час відвантаження товару).

### 5. Класифікація помилок і стратегії повторів
При реалізації виробничого конвеєра помилки поділяють на дві принципові категорії:
- **Тимчасові (Transient Errors)**: мережевий таймаут, тимчасова недоступність бази даних, перевантаження віддаленого сервісу. Такі збої обробляються повторними спробами (Retry) з алгоритмом експоненційного відступу (Exponential Backoff) та випадковим тремтінням (Jitter), щоб уникнути ефекту синхронної навали запитів (Thundering Herd).
- **Постійні (Permanent Errors)**: помилки схеми валідації, невірний токен доступу, відсутність обов'язкових бізнес-полів. Повторна відправка таких повідомлень безглузда — вони негайно спрямовуються в DLQ для аналізу розробниками або операторами.

### 6. Детермінізм та нульові алокації (Zero-Allocation Pipeline)
У критично важливих фінансових і телекомунікаційних системах конвеєр посередництва не повинен здійснювати динамічне виділення пам'яті (`malloc` або `new`) під час проходження транзакції. 

Використання статично виділених кілець буферів (Ring Buffer / LMAX Disruptor) та попередньо створених пулів структур `Exchange` дозволяє досягти стабільної затримки p99 на рівні субмікросекунд і повністю усунути затримки, пов'язані з конкуренцією блокувань менеджера пам'яті ядра або збирача сміття.

### 7. Бюджет затримок конвеєра (Latency Budget)
Інженерний аналіз витрат часу на проходження повідомлення крізь стадії конвеєра дозволяє локалізувати вузькі місця:
- Зчитування заголовків з мережевого буфера: ~30–80 наносекунд.
- Пошук маршруту в хеш-таблиці або дереві префіксів: ~20–50 наносекунд.
- Серіалізація JSON / бінарного протоколу: ~300–1200 наносекунд.
- Вихідний мережевий I/O (системний виклик `write`/`sendmsg` ядра): ~5–25 мікросекунд.

У класичних монолітних ESB на базі XML/XSLT та SOAP повний прохід повідомлення через DOM-трансформатори та розподілені XA-координатори займав від 15 до 120 мілісекунд, що перевищувало час мережевого транспорту на кілька порядків. Сучасні легковажні брокери та шлюзи зводять накладні витрати посередництва до часток мілісекунди.